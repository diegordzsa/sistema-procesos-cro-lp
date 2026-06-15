import requests
from config import SLACK_WEBHOOK_URL


def send_alert(task):
    name = task["name"]
    assignees = task["assignees"]
    due_date = task["due_date"]
    url = task["url"]
    list_name = task.get("list", "")

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Listo para lanzar",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f":rocket: *<{url}|{name}>*\n\n"
                    f":bust_in_silhouette: *Asignado:* {assignees}\n"
                    f":calendar: *Fecha limite:* {due_date}\n"
                    f":file_folder: *Lista:* {list_name}"
                ),
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Ver en ClickUp",
                        "emoji": True,
                    },
                    "url": url,
                    "style": "primary",
                },
            ],
        },
    ]

    payload = {
        "text": f"Listo para lanzar: {name}",
        "blocks": blocks,
    }

    response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=15)
    if response.status_code != 200:
        raise Exception(
            f"Error enviando a Slack: {response.status_code} - {response.text}"
        )

    print(f"  Alerta enviada: {name}")
