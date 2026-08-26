"""
Service helper for Aladhan Prayer Times API.
Provides permanent, accurate prayer times for any city worldwide with offline fallback.
"""
import json
import logging
import urllib.parse
import urllib.request
from datetime import date, datetime, time, timedelta

logger = logging.getLogger(__name__)

# Fallback timings for Jaunpur, UP if network is completely unreachable
DEFAULT_TIMINGS = {
    "Fajr": "04:15",
    "Sunrise": "05:35",
    "Dhuhr": "12:02",
    "Asr": "16:38",
    "Sunset": "18:29",
    "Maghrib": "18:29",
    "Isha": "19:49",
    "Imsak": "04:05",
    "Midnight": "00:02",
}

PRAYER_NAMES = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]


def format_to_12hr(time_str):
    """Converts 24-hour time string '16:38' to 12-hour '4:38 PM'."""
    try:
        clean_str = time_str.split(" ")[0]
        dt = datetime.strptime(clean_str, "%H:%M")
        return dt.strftime("%I:%M %p").lstrip("0")
    except Exception:
        return time_str


HIJRI_MONTHS = {
    1: "Muharram",
    2: "Safar",
    3: "Rabi' al-Awwal",
    4: "Rabi' al-Thani",
    5: "Jumada al-Awwal",
    6: "Jumada al-Thani",
    7: "Rajab",
    8: "Sha'ban",
    9: "Ramadan",
    10: "Shawwal",
    11: "Dhu al-Qi'dah",
    12: "Dhu al-Hijjah",
}


def get_prayer_timings(city="Jaunpur", country="India", state="Uttar Pradesh", method=1, school=1, date_str=None):
    """
    Fetches daily prayer timings and Hijri date from Aladhan API.
    Method 1 = University of Islamic Sciences, Karachi (Standard for India/Jaunpur).
    School 1 = Hanafi juristic method (Asr at ~4:38 PM).
    """
    params = {
        "city": city,
        "country": country,
        "method": method,
        "school": school,
    }
    if state:
        params["state"] = state
    if date_str:
        params["date"] = date_str

    url = f"https://api.aladhan.com/v1/timingsByCity?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PersonalApp-Salah/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            if data.get("code") == 200:
                timings = data["data"]["timings"]
                clean_timings = {}
                timings_12h = {}
                for k, v in timings.items():
                    raw_t = v.split(" ")[0]
                    clean_timings[k] = raw_t
                    timings_12h[k] = format_to_12hr(raw_t)

                # Fetch adjusted Hijri date (-1 day offset for India/Subcontinent moonsighting)
                target_dt = datetime.strptime(date_str, "%d-%m-%Y").date() if date_str else date.today()
                adj_date_str = (target_dt - timedelta(days=1)).strftime("%d-%m-%Y")
                hijri_formatted = f"12 Rabi' al-Awwal 1448 AH"
                hijri = data["data"]["date"]["hijri"]

                try:
                    gtoh_url = f"https://api.aladhan.com/v1/gToH?date={adj_date_str}"
                    gtoh_req = urllib.request.Request(gtoh_url, headers={"User-Agent": "PersonalApp-Salah/1.0"})
                    with urllib.request.urlopen(gtoh_req, timeout=3) as gtoh_resp:
                        gtoh_data = json.loads(gtoh_resp.read().decode("utf-8"))
                        if gtoh_data.get("code") == 200:
                            h = gtoh_data["data"]["hijri"]
                            m_num = int(h["month"]["number"])
                            m_name = HIJRI_MONTHS.get(m_num, h["month"]["en"])
                            hijri_formatted = f"{h['day']} {m_name} {h['year']} AH"
                            hijri = h
                except Exception:
                    # Fallback computation
                    day_num = max(1, int(hijri.get("day", 13)) - 1)
                    m_num = int(hijri.get("month", {}).get("number", 3))
                    m_name = HIJRI_MONTHS.get(m_num, "Rabi' al-Awwal")
                    hijri_formatted = f"{day_num} {m_name} {hijri.get('year', 1448)} AH"

                gregorian = data["data"]["date"]["readable"]
                next_prayer_info = calculate_next_prayer(clean_timings)

                return {
                    "success": True,
                    "timings": clean_timings,
                    "timings_12h": timings_12h,
                    "hijri_date": hijri_formatted,
                    "hijri_raw": hijri,
                    "gregorian_date": gregorian,
                    "meta": data["data"]["meta"],
                    "next_prayer": next_prayer_info,
                    "location": f"{city}, {state + ', ' if state else ''}{country}",
                }
    except Exception as e:
        logger.warning(f"Failed to fetch prayer times from Aladhan: {e}")

    # Return safe fallback if network error
    timings_12h = {k: format_to_12hr(v) for k, v in DEFAULT_TIMINGS.items()}
    next_prayer_info = calculate_next_prayer(DEFAULT_TIMINGS)
    return {
        "success": False,
        "timings": DEFAULT_TIMINGS,
        "timings_12h": timings_12h,
        "hijri_date": "12 Rabi' al-Awwal 1448 AH",
        "hijri_raw": {},
        "gregorian_date": datetime.now().strftime("%d %b %Y"),
        "meta": {"timezone": "Asia/Kolkata"},
        "next_prayer": next_prayer_info,
        "location": f"{city}, {state + ', ' if state else ''}{country}",
    }


def get_monthly_calendar(city="Jaunpur", country="India", state="Uttar Pradesh", method=1, school=1, year=None, month=None):
    """
    Fetches monthly prayer calendar from Aladhan API.
    """
    now = datetime.now()
    year = year or now.year
    month = month or now.month

    params = {
        "city": city,
        "country": country,
        "method": method,
        "school": school,
    }
    if state:
        params["state"] = state

    url = f"https://api.aladhan.com/v1/calendarByCity/{year}/{month}?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PersonalApp-Salah/1.0"})
        with urllib.request.urlopen(req, timeout=7) as response:
            data = json.loads(response.read().decode("utf-8"))
            if data.get("code") == 200:
                calendar_days = []
                for day_data in data["data"]:
                    clean_timings = {k: v.split(" ")[0] for k, v in day_data["timings"].items()}
                    timings_12h = {k: format_to_12hr(v) for k, v in clean_timings.items()}
                    calendar_days.append({
                        "date": day_data["date"]["readable"],
                        "day": day_data["date"]["gregorian"]["day"],
                        "weekday": day_data["date"]["gregorian"]["weekday"]["en"],
                        "hijri": f"{day_data['date']['hijri']['day']} {day_data['date']['hijri']['month']['en']}",
                        "timings": clean_timings,
                        "timings_12h": timings_12h,
                    })
                return {"success": True, "days": calendar_days, "year": year, "month": month}
    except Exception as e:
        logger.warning(f"Failed to fetch monthly calendar: {e}")

    return {"success": False, "days": [], "year": year, "month": month}


def calculate_next_prayer(timings, tz_name="Asia/Kolkata"):
    """
    Calculates which prayer is next and how much time is remaining based on local location timezone.
    """
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo(tz_name))
    except Exception:
        from datetime import timezone as dt_timezone, timedelta
        ist = dt_timezone(timedelta(hours=5, minutes=30))
        now = datetime.now(ist)

    current_time_minutes = now.hour * 60 + now.minute

    # Ordered prayers to evaluate
    prayers = [
        ("Fajr", timings.get("Fajr", "04:15")),
        ("Sunrise", timings.get("Sunrise", "05:35")),
        ("Dhuhr", timings.get("Dhuhr", "12:02")),
        ("Asr", timings.get("Asr", "16:38")),
        ("Maghrib", timings.get("Maghrib", "18:29")),
        ("Isha", timings.get("Isha", "19:49")),
    ]

    prayer_times_minutes = []
    for name, time_str in prayers:
        try:
            parts = time_str.split(":")
            h, m = int(parts[0]), int(parts[1])
            prayer_times_minutes.append((name, h * 60 + m, time_str))
        except (ValueError, IndexError):
            continue

    next_prayer = None
    minutes_left = None
    target_time_str = "04:15"

    for name, p_minutes, time_str in prayer_times_minutes:
        if p_minutes > current_time_minutes:
            next_prayer = name
            minutes_left = p_minutes - current_time_minutes
            target_time_str = time_str
            break

    # If all prayers today have passed, next is tomorrow's Fajr
    if not next_prayer and prayer_times_minutes:
        first_name, first_minutes, first_time_str = prayer_times_minutes[0]
        next_prayer = first_name
        minutes_left = (24 * 60 - current_time_minutes) + first_minutes
        target_time_str = first_time_str

    hours = (minutes_left or 0) // 60
    mins = (minutes_left or 0) % 60

    return {
        "name": next_prayer or "Fajr",
        "time": format_to_12hr(target_time_str),
        "raw_time": target_time_str,
        "minutes_remaining": minutes_left or 0,
        "formatted_remaining": f"{hours}h {mins}m" if hours > 0 else f"{mins}m",
    }
