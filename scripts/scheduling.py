# scripts/scheduling.py
from datetime import datetime, time, timedelta, timezone
from typing import Dict, Any, Optional, List

# Fixed slots per format (UTC)
SLOT_BY_FORMAT = {
    "long": time(hour=9, minute=0),
    "short": time(hour=18, minute=0),
}
DAILY_CAP = 2  # strict maximum per UTC day

def parse_rfc3339(s: str) -> datetime:
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s)

def format_rfc3339(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    dt_utc = dt.astimezone(timezone.utc)
    return dt_utc.replace(microsecond=0).isoformat().replace("+00:00", "Z")

def slot_datetime_for_date(slot_time: time, date_obj) -> datetime:
    return datetime.combine(date_obj, slot_time).replace(tzinfo=timezone.utc)

def videos_on_date(manifest: Dict[str, Any], date_utc: datetime) -> List[Dict[str, Any]]:
    target_date = date_utc.date()
    results = []
    for v in manifest.get("videos", []):
        pa = v.get("publish_at") or v.get("scheduled_at")
        if pa:
            try:
                dt = parse_rfc3339(pa).astimezone(timezone.utc)
            except Exception:
                continue
            if dt.date() == target_date:
                results.append(v)
                continue
        pub = v.get("published_at")
        if pub:
            try:
                dt = parse_rfc3339(pub).astimezone(timezone.utc)
            except Exception:
                continue
            if dt.date() == target_date:
                results.append(v)
                continue
    return results

def count_scheduled_today(manifest: Dict[str, Any], now_utc: Optional[datetime] = None) -> int:
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)
    return len(videos_on_date(manifest, now_utc))

def is_slot_occupied(manifest: Dict[str, Any], candidate_date, slot_time: time) -> bool:
    for v in manifest.get("videos", []):
        pa = v.get("publish_at") or v.get("scheduled_at")
        if pa:
            try:
                dt = parse_rfc3339(pa).astimezone(timezone.utc)
            except Exception:
                continue
            if dt.date() == candidate_date and dt.time().replace(second=0, microsecond=0) == slot_time.replace(second=0, microsecond=0):
                return True
        pub = v.get("published_at")
        if pub:
            try:
                dtp = parse_rfc3339(pub).astimezone(timezone.utc)
            except Exception:
                continue
            if dtp.date() == candidate_date and dtp.time().replace(second=0, microsecond=0) == slot_time.replace(second=0, microsecond=0):
                return True
    return False

def next_available_slot_for_format(manifest: Dict[str, Any], fmt: str, now_utc: Optional[datetime] = None) -> datetime:
    if fmt not in SLOT_BY_FORMAT:
        raise ValueError(f"unknown format '{fmt}', expected one of {list(SLOT_BY_FORMAT.keys())}")

    slot_time = SLOT_BY_FORMAT[fmt]
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)

    day_offset = 0
    while True:
        candidate_date = (now_utc + timedelta(days=day_offset)).date()
        slot_dt = slot_datetime_for_date(slot_time, candidate_date)

        if day_offset == 0 and slot_dt <= now_utc + timedelta(seconds=30):
            day_offset += 1
            continue

        if len(videos_on_date(manifest, slot_dt)) >= DAILY_CAP:
            day_offset += 1
            continue

        if is_slot_occupied(manifest, candidate_date, slot_time):
            day_offset += 1
            continue

        return slot_dt

def enforce_cap_and_schedule_for_format(manifest: Dict[str, Any], video_entry: Dict[str, Any], now_utc: Optional[datetime]=None) -> Dict[str, Any]:
    fmt = video_entry.get("format")
    if not fmt:
        raise ValueError("video_entry missing required 'format' key (use 'long' or 'short')")

    target_dt = next_available_slot_for_format(manifest, fmt, now_utc=now_utc)
    video_entry["publish_at"] = format_rfc3339(target_dt)
    video_entry["status"] = "scheduled"
    return video_entry