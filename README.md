# Sitwise

**A posture coach that learns how *you* sit.** A camera on your chair watches from the side, a pose model
measures your posture, and Sitwise nudges you in real time, then turns weeks of private data into a coaching
profile. Built at **UCSD SanD Hacks, November 2026**.

**Live:** [fixsit.health](https://fixsit.health) · [Pitch](pitch.md) · [Docs](docs/README.md)

Most posture apps spot a slouch and buzz you, with no memory and no idea what "good" means for your body.
Sitwise keeps a private history and uses it: when you slouch, how you slouch, how fast you recover, and which
nudges work for you.

## Features

- **Live coaching.** A state machine (Good → Drifting → Slouching → Away) driven by your own threshold,
  cooldown and quiet hours. Alerts arrive as desktop web push or an iPhone notification, then stop escalating.
- **Your own goal posture.** Only an upright posture (back within 10° of vertical) is accepted as the goal.
- **Analytics.** Score, streaks, an hour-by-weekday heatmap, time to recover and week-over-week goals.
- **Coach.** A profile built in your browser from your own numbers: how you slouch (head forward or leaning),
  when in a sit your posture slips, and how you respond to each kind of nudge. Optional Gemini version after you
  preview exactly what would be sent and consent.
- **Honest health context.** A weekly pain check-in set against your slouch data, plus an evidence meter that
  says what research does and doesn't show. Every health figure is cited ([`docs/health-claims.md`](docs/health-claims.md)).
- **Private by construction.** Frames are analysed on your own device and dropped. The API has no field that
  could carry an image, there are no accounts (anonymous pairing code), and collection needs explicit opt-in.

## How it works

```
Camera (iPhone via Camo, or webcam)        Flask API (Vercel)             Tiger Cloud (Postgres + TimescaleDB)
 -> pose model on your computer  --label + angles, ~1 Hz-->  state machine + alerts  -->  events / samples hypertables
    (frames never leave)                                     |        \
                          <-- push notification -------------'         '--> React dashboard
```

- **Model:** MediaPipe Pose landmarks plus a deterministic side-view angle rule that labels upright / leaning
  forward / leaning back ([`posture_pipeline-main/`](posture_pipeline-main), wired in through [`bridge/`](bridge)).
- **State machine:** a pure, unit-tested function, so it runs on stateless serverless functions.
- **Storage:** posture is a time series, so `events` and `samples` are TimescaleDB hypertables with compression
  and retention policies.

## Tech stack

| Layer | Tools |
|---|---|
| Dashboard | React 19, TypeScript, Vite, Tailwind, service worker for Web Push |
| API | Flask (Python), pywebpush, APNs, Vercel serverless |
| Data | Postgres on Tiger Cloud (TimescaleDB hypertables), in-memory store for local dev |
| Model | Python 3.12, MediaPipe Pose Landmarker, OpenCV |
| AI (optional) | Google Gemini via `google-genai`, de-identified inputs only, 6 calls/hour/user |
| Mobile | SwiftUI iOS app (stub model; not yet built) |

## Quick start

No accounts, database or phone needed. Requires Python 3.12+ and Node 20.19+ (or 22.12+).

```bash
python -m venv .venv
.venv\Scripts\activate               # macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
cd web && npm install && cd ..
cp .env.example .env                 # Windows: copy .env.example .env
```

Then, in separate terminals:

```bash
flask --app api.index run --debug --port 5001    # API
cd web && npm run dev                            # dashboard on http://localhost:5173
python scripts/seed.py                           # six weeks of demo data; prints a login link and pairing code
python scripts/simulate.py --code <CODE> --loop  # fake phone streaming posture readings
```

Open the link `seed.py` printed. Tests: `pytest api bridge` and `cd web && npm test`.

## Run the real model on a camera

The dashboard's **Camera** page reads any webcam (for example an iPhone through [Camo](https://camo.com)),
sends one frame per second to a model server on `127.0.0.1`, and shows the label. Turn on **Send readings to the
dashboard** and the tab acts as the phone. Setup: [`docs/camera-setup.md`](docs/camera-setup.md). Webcam without
a browser: [`docs/model-bridge.md`](docs/model-bridge.md).

## Repository layout

| Path | What |
|---|---|
| [`api/`](api) | Flask API. `core/` is pure, tested logic (state machine, scoring, seed data); `db.py` is the only file that touches the database; `push/` is APNs + Web Push; `ai/` is Gemini |
| [`web/`](web) | React + TypeScript dashboard |
| [`bridge/`](bridge) | Adapter from the pose model to Sitwise readings |
| [`posture_pipeline-main/`](posture_pipeline-main) | The posture model and its evaluation |
| [`ios/`](ios) | SwiftUI app |
| [`scripts/`](scripts) | Seeding, phone simulator, DB setup, local model server |
| [`docs/`](docs) | Setup, API reference ([OpenAPI](docs/openapi.yaml)), hardware, demo script |

More: [Setup and configuration](docs/configuration.md) (env vars, database, notifications, deploy,
troubleshooting) · [Code map](codemap.md) · [Contributing](CONTRIBUTING.md).

## Status and limits

- The posture rule is a heuristic, not a validated clinical classifier, and it can't see sideways leaning.
- The iPhone app is written but not yet built, and still uses a stub model. The laptop camera path is the working demo.
- Demo history and pain check-ins are synthetic, generated for the demo.
- Sitwise coaches habits and ergonomics. It gives no medical advice and makes no claim that slouching causes disease.

Built for UCSD SanD Hacks, November 2026.
