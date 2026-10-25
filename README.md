# Droidcon Uganda Conference Data

Open dataset of **Droidcon Uganda** speakers and sessions, used by the Carthigan
DroidconUganda app (`com.carthigan.droidconuganda`).

Data is sourced from the official Sessionize event APIs and re-published here as
versioned JSON so the app (and anyone else) can consume it without hitting
Sessionize directly.

## Event data

| Year | Sessionize event ID | Dates | Endpoint |
|------|--------------------|-------|----------|
| **2026** (current) | `bin6i3xe` | October 28–29, 2026 | `https://sessionize.com/api/v2/bin6i3xe/view/All` |
| 2025 (archive) | `re6do43h` | November 10–11, 2025 | `https://sessionize.com/api/v2/re6do43h/view/All` |

## Repository structure

```
data/
├── 2026/
│   ├── speakers.json   # 25 speakers (from /view/Speakers)
│   └── all.json        # full dataset: sessions, speakers, rooms, categories, questions (from /view/All)
└── 2025/
    ├── speakers.json   # 20 speakers (from /view/Speakers)
    └── all.json        # full dataset for the 2025 event
```

### Speaker object shape

Each speaker in `speakers.json` contains:

| Field | Description |
|-------|-------------|
| `id` | Sessionize speaker ID |
| `firstName`, `lastName`, `fullName` | Name |
| `bio` | Speaker biography |
| `tagLine` | One-line title/role |
| `profilePicture` | Headshot URL |
| `isTopSpeaker` | Featured speaker flag |
| `links` | Social/website links array |
| `sessions` | Session IDs this speaker presents |
| `questionAnswers` | Custom CFP question answers |

## Consuming from an app

Raw GitHub URLs serve JSON with the right `Content-Type` and can be fetched
directly:

```
https://raw.githubusercontent.com/Carthigan-Open-Source/droidcon-uganda-data/main/data/2026/speakers.json
https://raw.githubusercontent.com/Carthigan-Open-Source/droidcon-uganda-data/main/data/2026/all.json
```

Tip: `all.json` is the better single fetch — it includes speakers *and* the
schedule in one payload.

## Refreshing the data

Before each release (or when the Sessionize schedule changes), re-pull:

```bash
curl -s "https://sessionize.com/api/v2/bin6i3xe/view/Speakers" -o data/2026/speakers.json
curl -s "https://sessionize.com/api/v2/bin6i3xe/view/All"      -o data/2026/all.json
git commit -am "Refresh conference data" && git push
```

When the event ID changes for a new year, add a new `data/<year>/` folder and
move the previous year into the archive pattern used above.

## License

[MIT](LICENSE). Speaker bios and profile data belong to their respective authors
and are re-published from the public Sessionize API for the Droidcon Uganda app.
