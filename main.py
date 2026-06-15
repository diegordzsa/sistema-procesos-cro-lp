from datetime import datetime, timezone

from config import validate_config, is_aprobado
from clickup_client import get_tasks
from state import load_state, save_state
from slack_client import send_alert


def main():
    validate_config()

    previous_state = load_state()
    previous_tasks = previous_state.get("tasks", {})

    print("Consultando ClickUp...")
    current_tasks = get_tasks()
    print(f"  {len(current_tasks)} tareas encontradas")

    new_alerts = []

    for task_id, task_data in current_tasks.items():
        if not is_aprobado(task_data["status"]):
            continue

        prev_status = previous_tasks.get(task_id)
        if prev_status and is_aprobado(prev_status):
            continue

        new_alerts.append((task_id, task_data))

    if new_alerts:
        print(f"\n{len(new_alerts)} nueva(s) alerta(s):")
        for task_id, task_data in new_alerts:
            send_alert(task_data)
    else:
        print("\nSin nuevas alertas")

    new_state = {
        "last_check": datetime.now(timezone.utc).isoformat(),
        "tasks": {
            tid: tdata["status"] for tid, tdata in current_tasks.items()
        },
    }
    save_state(new_state)

    print("\nEstado guardado")


if __name__ == "__main__":
    main()
