#!/usr/bin/env python3
"""Convert Sessionize /view/All JSON to the iosched ConferenceData schema.

Usage: python3 sessionize_to_iosched.py <all.json> <out.json>

- Sessionize times are naive event-local (EAT, UTC+3); iosched wants epoch
  millis UTC.
- The 2026 Sessionize event has no categories, so topic tags are authored
  per session (see TOPIC_FOR_SESSION) so the schedule filters work.
"""

import json
import sys
import uuid
from datetime import datetime, timedelta, timezone

EAT = timezone(timedelta(hours=3))
NS = uuid.UUID("a11ce5ee-0000-4000-8000-droidcon2026".replace("droidcon2026", "00000000000c"))


def stable_uuid(name: str) -> str:
    return str(uuid.uuid5(NS, name))


def epoch_ms(naive_iso: str) -> int:
    dt = datetime.fromisoformat(naive_iso).replace(tzinfo=EAT)
    return int(dt.timestamp() * 1000)


# topic-tag palette
TAGS = {
    "topic_android": ("Android", "#3DDC84"),
    "topic_kotlin": ("Kotlin", "#7F52FF"),
    "topic_flutter": ("Flutter", "#027DFD"),
    "topic_kmp": ("Kotlin Multiplatform", "#B388FF"),
    "topic_ai": ("AI & ML", "#FF7043"),
    "topic_web": ("Web", "#29B6F6"),
    "topic_opensource": ("Open Source", "#8D6E63"),
    "topic_tools": ("Tools & Infra", "#5C6BC0"),
    "topic_career": ("Career & Leadership", "#AB47BC"),
    "topic_iot": ("IoT & Devices", "#26A69A"),
    "topic_research": ("UX Research", "#EC407A"),
}

# sessionize session id -> topic tags (authored; keys on a distinctive title word)
TOPIC_FOR_SESSION = {
    "Your Android Projects Aren’t Helping You": ["topic_android"],
    "Build Smarter Android Apps": ["topic_android", "topic_ai"],
    "Build Your First Full-Stack Flutter App": ["topic_flutter"],
    "Building for Ourselves": ["topic_opensource"],
    "Remote Theme Engine for Flutter": ["topic_flutter"],
    "From Android Forms to First-Person Capture": ["topic_ai"],
    "Optimizing Your Flutter App for the Web": ["topic_flutter", "topic_web"],
    "Building Lightning-Fast Search with Typesense": ["topic_tools"],
    "Go Beyond the Prompt": ["topic_ai", "topic_android"],
    "Leading with Trust": ["topic_career"],
    "Running Android on your Raspberry": ["topic_iot"],
    "Sanarei: Offline Web Browsing": ["topic_web"],
    "Shipping KMP with Confidence": ["topic_kmp"],
    "Effective App Architecture & State Management in Flutter": ["topic_flutter"],
    "One Language, Full Stack": ["topic_flutter"],
    "Bridging the Gap: How We Built Hybrid Mobile AI": ["topic_ai", "topic_android"],
    "On-Device AI with Flutter & Gemma": ["topic_ai", "topic_flutter"],
    "Migrating a webapp to Kotlin Multiplatform": ["topic_kmp"],
    "The Code Passed. Is It Right?": ["topic_tools"],
    "Kotlin Multiplatform: What I Learned Prototyping": ["topic_kmp"],
    "Building a Music DAW on Android": ["topic_android"],
    "Beyond the hype: What user research tells us": ["topic_research"],
}


def topics_for(title: str):
    for prefix, tags in TOPIC_FOR_SESSION.items():
        if title.startswith(prefix) or prefix in title:
            return tags
    return ["topic_android"]


def main(src: str, dst: str) -> None:
    data = json.load(open(src))

    rooms = []
    for r in data["rooms"]:
        rooms.append({
            "id": str(r["id"]),
            "name": r["name"],
            "filter": "true",
        })

    speakers = {}
    for s in data["speakers"]:
        twitter = next(
            (l["url"] for l in s.get("links", []) if "witter" in l.get("linkType", "")),
            None,
        )
        social = {"twitter": twitter} if twitter else {}
        speakers[s["id"]] = {
            "id": s["id"],
            "name": s["fullName"],
            "bio": s.get("bio") or "",
            "company": s.get("tagLine") or "",
            "thumbnailUrl": s.get("profilePicture") or "",
            "socialLinks": social,
        }

    sessions = []
    for s in data["sessions"]:
        sessions.append({
            "id": s["id"],
            "title": s["title"],
            "description": s.get("description") or "",
            "startTimestamp": epoch_ms(s["startsAt"]),
            "endTimestamp": epoch_ms(s["endsAt"]),
            "room": str(s["roomId"]),
            "speakers": s.get("speakers", []),
            "tagNames": topics_for(s["title"]),
            "type": "Session",
            "livestreamed": False,
            "relatedSessions": [],
            "youtubeUrl": "",
        })

    tags = []
    for order, (tag, (name, color)) in enumerate(TAGS.items()):
        tags.append({
            "id": stable_uuid(tag),
            "tag": tag,
            "category": "topic",
            "name": name,
            "color": color,
            "fontColor": "#FFFFFF",
            "order_in_category": order,
        })
    tags.append({
        "id": stable_uuid("type_session"),
        "tag": "type_session",
        "category": "type",
        "name": "Session",
        "color": "#616161",
        "fontColor": "#FFFFFF",
        "order_in_category": 0,
    })

    out = {"rooms": rooms, "sessions": sessions, "speakers": speakers, "tags": tags}
    with open(dst, "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {dst}: {len(sessions)} sessions, {len(speakers)} speakers, "
          f"{len(rooms)} rooms, {len(tags)} tags")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
