import requests
from datetime import datetime, timezone
from config import CLICKUP_TOKEN, CLICKUP_FOLDER_ID

BASE_URL = "https://api.clickup.com/api/v2"
HEADERS = {
    "Authorization": CLICKUP_TOKEN,
    "Content-Type": "application/json",
}


def _ms_to_iso(ms_value):
    if not ms_value:
        return None
    try:
        ms = int(ms_value)
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()
    except (ValueError, TypeError):
        return None


def _format_date_es(iso_string):
    if not iso_string:
        return "Sin fecha"
    try:
        dt = datetime.fromisoformat(iso_string)
        months = {
            1: "ene", 2: "feb", 3: "mar", 4: "abr", 5: "may", 6: "jun",
            7: "jul", 8: "ago", 9: "sep", 10: "oct", 11: "nov", 12: "dic",
        }
        return f"{dt.day} {months[dt.month]} {dt.year}"
    except (ValueError, TypeError):
        return "Sin fecha"


def get_tasks_from_list(list_id, include_closed=True):
    all_tasks = []
    page = 0
    while True:
        url = f"{BASE_URL}/list/{list_id}/task"
        params = {
            "page": page,
            "include_closed": str(include_closed).lower(),
            "subtasks": "true",
        }
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code != 200:
            raise Exception(
                f"Error fetching tasks from list {list_id}: "
                f"{response.status_code} - {response.text}"
            )
        data = response.json()
        tasks = data.get("tasks", [])
        if not tasks:
            break
        all_tasks.extend(tasks)
        if data.get("last_page", False):
            break
        page += 1
    return all_tasks


def get_tasks():
    url = f"{BASE_URL}/folder/{CLICKUP_FOLDER_ID}/list"
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        raise Exception(
            f"Error fetching lists from folder {CLICKUP_FOLDER_ID}: "
            f"{response.status_code} - {response.text}"
        )

    lists = response.json().get("lists", [])
    result = {}

    for lst in lists:
        list_id = lst["id"]
        list_name = lst["name"]
        tasks = get_tasks_from_list(list_id)

        for task in tasks:
            task_id = task["id"]
            assignees = task.get("assignees", [])
            if assignees:
                assignee_names = ", ".join(a.get("username", "?") for a in assignees)
            else:
                assignee_names = "Sin asignar"

            due_date_raw = task.get("due_date")
            due_date_iso = _ms_to_iso(due_date_raw)

            result[task_id] = {
                "name": task.get("name", "Sin nombre"),
                "status": task.get("status", {}).get("status", ""),
                "assignees": assignee_names,
                "due_date": _format_date_es(due_date_iso),
                "due_date_iso": due_date_iso,
                "url": task.get("url", ""),
                "list": list_name,
            }

    return result
