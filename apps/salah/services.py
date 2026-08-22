"""
Service helper for Aladhan Prayer Times API.
Provides permanent, accurate prayer times for any city worldwide with offline fallback.
"""
import json
import logging
import urllib.parse
import urllib.request
from datetime import datetime, time

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
                # Clean timings strings (remove timezones like ' (IST)' if present)
                clean_timings = {}
                timings_12h = {}
                for k, v in timings.items():
                    raw_t = v.split(" ")[0]
                    clean_timings[k] = raw_t
                    timings_12h[k] = format_to_12hr(raw_t)

                hijri = data["data"]["date"]["hijri"]
                month_en = hijri["month"]["en"]
                if month_en == "Rabī' al-awwal" or month_en == "Rabi' al-awwal":
                    month_display = "Rab Awal"
                else:
                    month_display = month_en

                hijri_formatted = f"{hijri['day']} {month_display} {hijri['year']} AH"
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
        "hijri_date": "8 Rab Awal 1448 AH",
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


def calculate_next_prayer(timings):
    """
    Calculates which prayer is next and how much time is remaining.
    """
    now = datetime.now()
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
        "minutes_remaining": minutes_left or 0,
        "formatted_remaining": f"{hours}h {mins}m" if hours > 0 else f"{mins}m",
    }
