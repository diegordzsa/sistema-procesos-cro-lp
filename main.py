from datetime import datetime, timezone

from config import validate_config, is_aprobado
from clickup_client import get_tasks
from state import load_state, save_state, cleanup_alerted
from slack_client import send_alert


def main():
    validate_config()

    previous_state = load_state()
    previous_tasks = previous_state.get("tasks", {})
    alerted = set(previous_state.get("alerted", []))

    print("Consultando ClickUp...")
    current_tasks = get_tasks()
    print(f"  {len(current_tasks)} tareas encontradas")

    new_alerts = []

    for task_id, task_data in current_tasks.items():
        if not is_aprobado(task_data["status"]):
            continue

        if task_id in alerted:
            continue

        was_aprobado_before = (
            task_id in previous_tasks
            and is_aprobado(previous_tasks[task_id])
        )
        if was_aprobado_before:
            alerted.add(task_id)
            continue

        new_alerts.append((task_id, task_data))

    if new_alerts:
        print(f"\n{len(new_alerts)} nueva(s) alerta(s):")
        for task_id, task_data in new_alerts:
            send_alert(task_data)
            alerted.add(task_id)
    else:
        print("\nSin nuevas alertas")

    cleaned_alerted = cleanup_alerted(list(alerted), current_tasks, is_aprobado)

    new_state = {
        "last_check": datetime.now(timezone.utc).isoformat(),
        "tasks": {
            tid: tdata["status"] for tid, tdata in current_tasks.items()
        },
        "alerted": cleaned_alerted,
    }
    save_state(new_state)

    print(f"\nEstado guardado - {len(cleaned_alerted)} task(s) en alerted")


if __name__ == "__main__":
    main()
