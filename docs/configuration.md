# Setup and configuration

Full setup reference for Sitwise: local quick start, environment variables, database, notifications, the phone simulator, deployment and troubleshooting. The project overview is in the [root README](../README.md).

## Quick start (no accounts, no phone needed)

Needs Python 3.12+ and Node 20.19+ (or 22.12+; Vite 8 requires it). From the repo root:

```bash
# one-time
python -m venv .venv                 # skip if .venv already exists
.venv\Scripts\activate               # macOS/Linux: source .venv/bin/activate   PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
cd web
npm install
cd ..
copy .env.example .env               # macOS/Linux: cp .env.example .env   (skip if you already have a .env)
```

Then three terminals (activate the venv in each Python one):

```bash
# 1. API: in-memory store, saved to .devdb.json, so nothing external is needed
flask --app api.index run --debug --port 5001

# 2. dashboard on http://localhost:5173 (Vite proxies /api to port 5001)
cd web
npm run dev

# 3. six weeks of demo data + a fake phone (see "Simulate the phone")
python scripts/seed.py               # prints a login link and a pairing code
python scripts/simulate.py --code <PAIRING_CODE> --loop
```

Open the link `seed.py` printed. Tests: `pytest api bridge` (pure logic, end-to-end API, the model bridge) and, for the dashboard's
on-device analysis and calendar parsing, `cd web && npm test`. **Run `npm test` from PowerShell or cmd.exe, not Git
Bash**: vitest fails there on Windows with a path-case error (`Cannot read properties of undefined (reading 'config')`).

**Try the Coach:** open the dashboard's **Coach** tab. With demo data it shows your fatigue curve, how you slouch,
how you respond to nudges and a coaching profile built on your own device. Add `GEMINI_API_KEY` (see below) to also
get the optional Gemini version.

## Configure everything

You only need this section to go beyond the quick start: a real database, desktop and iPhone
notifications, or running the iPhone app.

### How configuration works

All server settings are environment variables. For local dev put them in a **`.env`** file in the
repo root (copy [`.env.example`](../.env.example); it's gitignored, never commit real values).

- The **`flask` command** loads `.env` automatically (via `python-dotenv`, installed by
  `requirements-dev.txt`). **Run it from the repo root and restart it after editing `.env`.**
- `pytest` and the `scripts/` do **not** read `.env` (the scripts take flags or their own env vars).
- No `.env`? You can set variables in the shell instead. Set it on its own line first:
  bash `export ENABLE_DEV_ROUTES=1` · PowerShell `$env:ENABLE_DEV_ROUTES=1` · cmd.exe
  `set "ENABLE_DEV_ROUTES=1"` (keep the quotes: without them cmd stores a trailing space, `"1 "`, and the flag stays off).
- `.env` format: one `KEY=value` per line, no spaces around `=`.

| Variable | Needed for | Notes |
|---|---|---|
| `DATABASE_URL` | A real database (Tiger Cloud) | Unset = in-memory store. Contains the database password: server-only secret |
| `VAPID_PUBLIC_KEY`, `VAPID_PRIVATE_KEY`, `VAPID_SUBJECT` | Desktop notifications | `python scripts/gen_vapid.py` |
| `APNS_KEY_ID`, `APNS_TEAM_ID`, `APNS_AUTH_KEY`, `APNS_BUNDLE_ID`, `APNS_USE_SANDBOX` | iPhone notifications | From your Apple Developer account |
| `GEMINI_API_KEY`, `GEMINI_MODEL` | Optional Gemini coaching profile, "ask about your habits", "describe your day" | Unset = those buttons say Gemini isn't on, and the on-device profile still works. **Use a key from a billing-enabled (paid) Google project**: Google's terms for the free tier allow using inputs to improve its products and forbid personal or sensitive data. Default model `gemini-3.8-flash` |
| `ENABLE_DEV_ROUTES` | Demo seeding + the dashboard's "Load demo data" button | `1` to enable. Leave unset on anything public |
| `DEV_DB_FILE` | Where the in-memory store saves | Optional. Default `.devdb.json` (delete it to reset local data) |

Not in `.env` (set in the shell): `API_PROXY`, `VITE_BASE` (dashboard, see below) and
`SITWISE_BASE`, `SITWISE_DEVICE_TOKEN` (simulator).

**Check what the API is using:** `curl http://127.0.0.1:5001/api/health` returns
`{"ok":true,"devRoutes":true,"store":"memory","db":{"ok":true,"problem":null}}`. `store` is `memory` or
`postgres`; `db.problem` is `schema_missing`, `connect_failed` or `error` when the database check fails;
`devRoutes` is whether `ENABLE_DEV_ROUTES` took effect.

### Gemini coaching profile (optional)

The **Coach** tab builds a personal profile (how you slouch, when your posture slips, how you respond to nudges, what to
try next). **Without any key it is built in your browser from your own numbers** and saved only in that browser's
localStorage; the server never stores it. Setting `GEMINI_API_KEY` adds an "Improve with Gemini" option, plus
"Ask about your habits" and "Describe your day" (turns a sentence into a settings change you confirm).

What happens when someone uses it: the dashboard first shows the **exact** de-identified payload and a plain-language
disclosure, and nothing is sent until they tick consent. Gemini receives habit numbers only: no name, email, account
ID, dates, images or pain check-ins. The result goes back to the browser and is not stored on the server. Calls are
rate-limited (6 per hour per user, per server instance) and failures fall back to the on-device profile.

- **Paid tier required for real users.** Google's Gemini API terms say that on the free tier, inputs may be used to
  improve its products and reviewed by humans, and that you must not send personal or sensitive information. Use a key
  from a billing-enabled project, and re-read the current terms before relying on this.
- Default model `gemini-3.8-flash`; override with `GEMINI_MODEL`. The Gemini call has a 30 s timeout, so
  `vercel.json` gives the function 45 s.
- It has **not been run against the live Gemini API** in this repo (no key was available); the tests use a fake client
  and the real SDK's config types. Try it once with your key before demoing it.

### Tiger Cloud database (Tiger Data)

The API stores everything in Postgres. [Tiger Data](https://www.tigerdata.com) (Tiger Cloud) is managed
Postgres with TimescaleDB, and `events` (the posture time series) becomes a **hypertable**. Any Postgres
works too. Without `DATABASE_URL` you get the in-memory store.

1. Sign up at [tigerdata.com](https://www.tigerdata.com) and create a service (their free plan is fine for development; check the current plan and any hackathon credits on their site).
2. From **Tiger Console**, copy the service's connection string. It looks like `postgres://tsdbadmin:<password>@<host>:<port>/tsdb?sslmode=require`. The password is shown once (or in the downloaded credentials file).
3. Put it in `.env` as `DATABASE_URL`, then create the tables with the **direct** string (not a pooler): `python scripts/init_db.py`. It's safe to re-run and prints whether `events` became a hypertable.
4. Restart Flask and check `/api/health`: `"store":"postgres"` and `"db":{"ok":true}`.
5. **On Vercel use the transaction pooler string.** In Tiger Console add a pooler (**Operations → Connection pooling**); the *transaction* pool uses the same pooler port but database `tsdb_transaction`. Serverless functions open many short connections, which is what the pooler is for. The app keeps a small client pool (`DB_POOL_MAX`, default 4) and turns off prepared statements so it works through the pooler.

`DATABASE_URL` contains the password: server-only (`.env` locally, Vercel env vars when deployed), never in the web app or the iPhone app.
Data from the in-memory store does **not** carry over: run `python scripts/seed.py` again and re-pair (old dashboard tokens stop working and the browser signs itself out).

**Status:** tested on plain Postgres (the same schema, all API and store tests). It has **not yet been run against a real Tiger Cloud service**, so the hypertable and compression steps in `api/schema.sql` are unverified until your first `init_db.py` there (a compression failure only prints a notice).
Running the tests against Postgres: start a **local** database and run `TEST_DATABASE_URL=postgresql://... pytest api`. That run drops and recreates the tables, so it refuses non-local hosts.

### Desktop notifications (Web Push)

1. `python scripts/gen_vapid.py` prints three lines. Paste them into `.env` and set `VAPID_SUBJECT` to a `mailto:` address you're happy to share with browser push services. Restart Flask.
2. In the dashboard: **Settings → Enable on this computer** → allow the browser prompt → **Test desktop alert**. A notification should appear and the page says "Sent to 1 browser."

Works on `http://localhost` and on HTTPS (Chrome, Edge, Firefox). If the page says the server has no VAPID key, step 1 didn't take effect (check `.env` and restart).

### iPhone app and push (APNs)

Needs a Mac with Xcode, a **physical iPhone** (the camera), and a paid **Apple Developer** account (push). The app is written but has not been built yet; expect small compile fixes (see [`ios/README.md`](../ios/README.md) for the build steps).

1. **APNs key:** in the Apple Developer portal go to **Certificates, Identifiers & Profiles → Keys**, create a key with **Apple Push Notifications service (APNs)** enabled, and download the `.p8` (Apple lets you download it once). Note the **Key ID**; your **Team ID** is under Membership. Never commit the `.p8` (it's gitignored).
2. **Server `.env`:** set `APNS_KEY_ID`, `APNS_TEAM_ID`, `APNS_BUNDLE_ID` (`com.sitwise.app` unless you changed it in `ios/project.yml`), and `APNS_USE_SANDBOX=1` for Xcode dev builds (`0` for TestFlight/App Store). `APNS_AUTH_KEY` is the `.p8` contents on **one line** with `\n` for newlines, in double quotes. Print it ready to paste:

   ```
   python -c "import sys; print(open(sys.argv[1]).read().strip().replace(chr(10), chr(92)+'n'))" AuthKey_XXXXXXXXXX.p8
   ```
3. **Point the app at your server:** edit `Config.baseURL` in [`ios/Sitwise/Config.swift`](../ios/Sitwise/Config.swift). For local dev use your PC's LAN address, e.g. `http://192.168.1.20:5001` (`ipconfig` shows it); on a deployed app use the Vercel URL. The bundle ID in `ios/project.yml` must equal `APNS_BUNDLE_ID`.
4. **Let the phone reach your PC:** start Flask with `--host 0.0.0.0` (`flask --app api.index run --host 0.0.0.0 --port 5001`; **drop `--debug`** there, because the debugger would be reachable from your network), put the phone on the same Wi-Fi, and allow inbound TCP 5001 in Windows Firewall when prompted.
5. **Pair and test:** get a code from the dashboard's **Pair** page, enter it in the app, then **Settings → Test iPhone alert** in the dashboard. "Sent to 1 device." means it worked.

Without any of this the app still runs end to end on the stub model (or the webcam bridge); you just won't get real pushes.

### Dashboard options

Set these in the shell before `npm run dev` / `npm run build`:

| Variable | Default | Use |
|---|---|---|
| `API_PROXY` | `http://127.0.0.1:5001` | Where Vite forwards `/api` if Flask runs elsewhere |
| `VITE_BASE` | `/` | Serve the dashboard from a sub-path (it also becomes the router basename) |

## Use a laptop camera (Camo)

The dashboard's **Camera** page reads a webcam on this computer, for example the iPhone through
[Camo](https://camo.com), so the model can be developed against a real feed before the iOS app is
built. **Full setup guide, including where the trained model goes: [`docs/camera-setup.md`](camera-setup.md).**

In short:

1. Keep **Camo Studio** open with the phone connected and upright (closing it makes the feed black).
2. Start the API, the dashboard and `python scripts/model_server.py`, open **Camera** in Chrome or
   Edge, press **Start camera** and pick the Camo source. The page shows a vertical view.
3. About once a second a frame goes to `predict()` in `scripts/posture_model.py`, which runs the teammate's
   **MediaPipe pose model + side-view angle rule** (`posture_pipeline-main/`). Start the model server with the
   model's Python 3.12 venv: `posture_pipeline-main\.venv\Scripts\python.exe scripts/model_server.py`
   ([`docs/model-bridge.md`](model-bridge.md) has the one-time setup). With any other Python it serves a
   placeholder and says why.
4. Choose **which way you face** (Left or Right) on the page, then **Send readings to the dashboard**: the tab acts as
   the phone, so the readings go through the model into the database and Live, alerts, analytics and Coach run off
   them. Allow data collection before sending readings. The camera uses the upright reference and replaces any paired sensor.

Frames go from the browser tab to the model server on the same computer, are analysed in memory and
dropped; the hosted API still accepts no images.

## Simulate the phone

`scripts/simulate.py` acts as the iPhone. It claims a pairing code, then POSTs a posture sample every
second (good → slouch → recover), the same payload the real app sends. It uses only the Python
standard library. Use it to develop and demo the dashboard and alerts without a camera, a Mac or the
real model, and as the demo fallback.

1. **Start the API and the dashboard** (Quick start, terminals 1 and 2).
2. **Allow data collection and get a pairing code.** Enable consent on Pair or Settings before streaming readings. Either open the dashboard, go to **Pair → Create my dashboard**, or run `python scripts/seed.py` (also fills six weeks of history and weekly demo pain check-ins, and prints a login link). Codes last 10 minutes; **Pair → New code** makes another.
3. **Make nudges quick (optional).** In **Settings**, drag **Slouch threshold** to 5–10 s so you don't wait 30 s.
4. **Run the simulator** in a new terminal (venv active):

   ```
   python scripts/simulate.py --code ABC234 --good-for 10 --slouch-for 30 --loop
   ```

   You'll see the server's view of each sample:

   ```
   Paired. Reuse with:  SITWISE_DEVICE_TOKEN=...
   [good  ] server state: GOOD
   [slouch] server state: DEVIATING
   [slouch] server state: SLOUCHING   ALERT level 1 {"desktop": {...}, "phone": {...}}
   [good  ] server state: SLOUCHING
   [good  ] server state: GOOD
   ```
5. **Watch the dashboard Live page:** Good → Drifting (with a "nudge in N s" meter) → Slouching ("1 nudge sent") → back to Good about 3 s after the simulator sits up. **Analytics** fills in as it runs. If desktop push is configured you also get the notification. The `ALERT` line shows per channel whether it was sent or skipped and why (e.g. `no_device_registered`, `vapid_not_configured`).

**Options**

| Flag | Default | Meaning |
|---|---|---|
| `--code CODE` | | Pairing code from the dashboard (first run). Prints a device token |
| `--token T` / `SITWISE_DEVICE_TOKEN` | | Reuse a device token and skip pairing |
| `--base URL` / `SITWISE_BASE` | `http://127.0.0.1:5001` | API to talk to; use `https://<project>.vercel.app` for a deployed one |
| `--good-for` (alias `--slouch-after`) | 10 | Seconds of good posture at the start of each cycle |
| `--slouch-for` | 40 | Seconds of slouching (must exceed your slouch threshold to trigger a nudge) |
| `--recover-for` | 15 | Seconds of good posture after the slouch |
| `--interval` | 1.0 | Seconds between samples (keep ~1; the server treats > 15 s of silence as "phone offline") |
| `--loop` | off | Repeat the cycle until Ctrl-C |

To rerun without a new code, reuse the token. cmd.exe: `set "SITWISE_DEVICE_TOKEN=<token>"` then
`python scripts/simulate.py --loop`; PowerShell: `$env:SITWISE_DEVICE_TOKEN="<token>"`; or pass `--token`.

**Good to know**
- One phone per account: pairing a new device (or a second `--code`) invalidates the old token; the old simulator then fails with "no longer paired".
- Each run uses a fresh session ID, and starting one closes the previous session cleanly.
- **Test going offline:** stop the simulator. After about 15 s the Live page shows the "phone hasn't reported" banner and `Away`.
- The simulator sends synthetic readings. To test delivery, pair an external receiver using [iPhone alerts](iphone-alerts.md) and use **Test phone alert**.
- On a Mac, the iPhone app itself also runs in the Xcode Simulator on synthetic frames and the stub model (`ios/README.md`).

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `Can't reach http://127.0.0.1:5001` (simulator or seed) | The API isn't running, or it's on another port. Check `curl http://127.0.0.1:5001/api/health`. |
| `HTTP 404 ... invalid_code` | Code expired (10 min) or already used. Dashboard **Pair → New code**. |
| `HTTP 401` from the simulator | Token no longer valid (re-paired, or a different store). Run with a fresh `--code`. |
| Dashboard bounces to the Pair page | Its token isn't recognised (store changed, `.devdb.json` deleted). Create a new dashboard or open a fresh `seed.py` link. |
| No "Load demo data" button / `seed.py` says 404 | `ENABLE_DEV_ROUTES` isn't on. Check `/api/health` → `devRoutes`; for cmd use the quoted `set`. |
| `.env` seems ignored | Run `flask` from the repo root, restart it after editing, and make sure `python-dotenv` is installed (`pip install -r requirements-dev.txt`). `pytest`/scripts never read `.env`. |
| `/api/health` shows `memory` but you set `DATABASE_URL` | The variable isn't in the environment of the process running Flask. Run `flask` from the repo root, restart it after editing `.env`. |
| `/api/health` shows `"db":{"ok":false,"problem":"schema_missing"}` | The tables don't exist yet: `python scripts/init_db.py`. |
| `"problem":"connect_failed"` | Wrong URL/password, the service isn't reachable, or (on Vercel) you used the direct string where the pooler string is needed. |
| Live says "phone hasn't reported yet" | No samples for 15 s: simulator stopped or on another account. |
| `clock_skew` (HTTP 400) | The sending device's clock is more than 1 hour off server time. |
| Test says "not sent: ... not configured" / "no browser subscribed" | The VAPID/APNs variables are missing, or the browser/phone hasn't enabled notifications yet (see above). |
| iPhone can't reach the API | Same Wi-Fi? Flask started with `--host 0.0.0.0`? Firewall allowing TCP 5001? `Config.baseURL` has your LAN IP and `http://`? |

## Layout

| Path | What |
|---|---|
| `api/` | Flask API. `core/` is pure, tested logic (state machine, scoring, settings, seed generator); `db.py` is the only file that touches the database; `push/` is APNs + Web Push |
| `web/` | React + TypeScript + Tailwind dashboard (Vite) |
| `ios/` | SwiftUI app (see `ios/README.md`; **not yet built**) |
| `scripts/` | `seed.py`, `simulate.py`, `init_db.py`, `gen_vapid.py`, `check_codemap.py`; laptop camera path: `model_server.py`, `posture_model.py` (the model goes here), `camera_test.py` |
| `docs/` | `openapi.yaml`, `api.md`, `camera-setup.md`, `hardware.md`, `health-claims.md`, `demo-script.md` |
| `pitch.md` | The pitch: mission, demo flow, Data for Good sources, Tiger Data story, built-vs-next, expected Q&A |

[Code map](../codemap.md) lists source files by area. [Documentation index](README.md) links the setup guides.

## Deploy (Vercel + Tiger Cloud)

1. **Database:** set up Tiger Cloud as in [Configure everything](#tiger-cloud-database-tiger-data) and run `python scripts/init_db.py` once.
2. **Vercel:** new project from this repo with **Root Directory = the repo root** (and run the Vercel CLI from there). `vercel.json` uses **Vercel Services** (beta): service `api` (Flask; entrypoint root `index.py`, which re-exports `api/index.py`) is public at `/api/*`, and service `web` (the Vite dashboard in `web/`, built to `web/dist`, with a single-page-app fallback to `index.html`) is public at everything else. Requests keep their original path, so Flask sees `/api/...` exactly as it does locally. There are **no bindings**: the dashboard calls the API from the browser through the shared domain, not server to server. The teammate's `posture_pipeline-main/` is deliberately **not** a service (a local model, not something to host; see `docs/model-bridge.md`). Build and runtime keys (`functions`, `buildCommand`, ...) live inside each service, not at the top level of `vercel.json`.
3. **Env vars** (names in [`.env.example`](../.env.example)): `DATABASE_URL` (the **transaction pooler** string), `VAPID_*` (generate with `python scripts/gen_vapid.py`), `APNS_*`. Leave `ENABLE_DEV_ROUTES` unset on anything judges will use, unless you want the demo-data button. On Vercel the in-memory store is refused, so a missing `DATABASE_URL` fails loudly.
4. **Turn off Deployment Protection** for the project, or the phone and judges' browsers hit an auth wall.
5. Put the temporary `https://<project>.vercel.app` URL in `ios/Sitwise/Config.swift`.
6. To try both services together before pushing, `vercel dev` runs them locally; otherwise run Flask and Vite as in the quick start. If a deploy fails, the build log names the service (`api` or `web`).

### Data collection and Gemini suggestions

Posture collection starts disabled for new and existing dashboards without a saved opt-in.
Enable **Consent to data collection** on Pair, Camera, or Settings before sending readings.
Withdrawal blocks new readings at the API, including from an already paired phone; it does not delete history.
The dashboard and camera no longer require calibration. The camera uses the upright reference.

For **Coach → Profile → Gemini suggestor**, set `GEMINI_API_KEY` in the server's environment
(or local `.env` when running Flask), then restart the API. Never put the key in a Vite variable or browser code.
The suggestor previews the de-identified data, requires separate consent for each request, and calls
`POST /api/coach/analyze`. Suggestions are saved in this browser. Missing configuration and service
errors leave the local profile available. `GEMINI_MODEL` can override the default.
