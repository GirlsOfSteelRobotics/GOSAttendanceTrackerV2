import requests
from django.conf import settings


def call_gos_admin_api(endpoint, method="GET", payload=None, params=None):
    url = f"{settings.GOS_ADMIN_API_URL}/{endpoint.lstrip('/')}"
    headers = {
        "X-API-KEY": settings.GOS_ADMIN_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        if method == "POST":
            response = requests.post(url, json=payload, headers=headers, timeout=10)
        else:
            response = requests.get(url, params=params, headers=headers, timeout=10)

        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API Error ({url}): {e}")
        return {"error": str(e)}


def record_tap_api(rfid_uid=None, name=None):
    payload = {"program_id": settings.GOS_ADMIN_PROGRAM_ID, "event_type": "AUTO"}
    if rfid_uid:
        payload["rfid_uid"] = str(rfid_uid)
    if name:
        payload["visitor_name"] = name

    return call_gos_admin_api("attendance/tap", method="POST", payload=payload)


def get_program_report_api():
    return call_gos_admin_api(
        f"attendance/program/{settings.GOS_ADMIN_PROGRAM_ID}/report"
    )


def lookup_student_api(name=None, rfid=None):
    params = {}
    if name:
        params["name"] = name
    if rfid:
        params["rfid"] = rfid

    return call_gos_admin_api("attendance/student/lookup", params=params)
