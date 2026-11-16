# Camera setup: iPhone feed on your laptop, through the model, into the dashboard

This gets an iPhone's camera showing in the dashboard on your laptop, runs the teammate's posture model
(MediaPipe pose + a side-view angle rule) on that feed, and stores the readings in the database like the phone
would. It is the laptop path until the model runs inside the iOS app. It takes about 15 minutes the first time.

How the pieces connect:

```
iPhone (Camo app)  ->  Camo Studio on the laptop  ->  shows up as a webcam
   ->  dashboard Camera page (browser)  --one frame per second, to 127.0.0.1 only-->  scripts/model_server.py
   ->  scripts/posture_model.py -> bridge/engine.py: MediaPipe pose + the angle rule (posture_pipeline-main/)
   ->  a label, a deviation and two angles come back to the page
   ->  the page posts them to /api/posture/ingest -> state machine -> database -> Live, alerts, Analytics, Coach
```

(`bridge/` can also read a webcam without a browser: [`model-bridge.md`](model-bridge.md). Both use the same model code.)

## What you need

- An iPhone, and a way to prop it upright, side-on to your chair (see [`hardware.md`](hardware.md)).
- A laptop (Windows or Mac) with **Python 3.12+** and **Node 20.19+ or 22.12+**.
- **Chrome or Edge.** Browsers embedded in other apps often block cameras.
- **Camo**, which turns the iPhone into a webcam. The free version is enough:
  - on the iPhone: the **Camo** app from the App Store (by Reincubate);
  - on the laptop: **Camo Studio** from <https://camo.com>.

## 1. Get the iPhone showing in Camo Studio

1. Install Camo on the iPhone and Camo Studio on the laptop, and open both.
2. Connect the phone. A USB cable is the most reliable; Camo Studio also offers Wi-Fi pairing. Follow
   the prompts in Studio, and allow camera access on the phone when it asks.
3. You should now see the phone's picture inside Camo Studio.
4. On the iPhone, turn **orientation lock off** (Control Center), and stand the phone **upright**.
5. **Leave Camo Studio open.** It is what feeds the picture to other apps; if you close it, every
   other app gets a black picture.

You do not need to change the profile, resolution or rotation in Camo Studio. The dashboard turns
the feed into a vertical view by itself (step 4).

## 2. Set up the repo

From the repo root, one time:

```bash
git pull
python -m venv .venv
.venv\Scripts\activate               # macOS/Linux: source .venv/bin/activate   PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt  # includes Flask and OpenCV
cd web
npm install
cd ..
```

The model needs **Python 3.12** (MediaPipe has no 3.14 build), kept separate from the API's Python. One time:

```powershell
py -3.12 -m venv posture_pipeline-main\.venv
posture_pipeline-main\.venv\Scripts\python.exe -m pip install -r scripts/requirements-model.txt
```

## 3. Start three things

Three terminals, from the repo root (activate the venv in the two Python ones):

```bash
# 1. API (port 5001)
python -m flask --app api.index run --debug --port 5001
```

```bash
# 2. model server (port 5002): runs the posture model on each frame (the model's Python 3.12 venv)
posture_pipeline-main\.venv\Scripts\python.exe scripts/model_server.py
```

```bash
# 3. dashboard (port 5173)
cd web
npm run dev
```

## 4. See the feed

1. Open <http://localhost:5173> in Chrome or Edge.
2. First time only: on the **Pair** page click **Create my dashboard**.
3. Go to **Camera** and click **Start camera**. Allow the camera when the browser asks.
4. Check the title above the video. If it names the laptop's own webcam, choose the Camo camera in
   the **Source** dropdown. The choice is remembered.

What you should see:

- **A vertical picture of you**, head to chair base. Webcam feeds are always wide, so the page trims
  the dark bars Camo adds either side of an upright phone, and crops anything still wide to its
  centre. The line above the video says what it did, for example `showing 405×720 of 1280×720`.
- **Model reading** says `Model: Local Python model: Side-angle rule on MediaPipe (...)`. Until you say
  which way you face (below) it shows `UNKNOWN` and tells you to pick. If it says `Placeholder` or
  `Stub (fixed mock data)` instead, the real model did not load or the server was not running when the camera
  started: see Troubleshooting, then **Stop camera** and **Start camera**.

## 5. Choose your facing direction

On the Camera page, to the right of the picture:

1. **Which way do you face?** Choose **Left** or **Right**: where your nose points in the picture above. This
   matters: from a side view the model can't tell leaning forward from leaning back without it, and a wrong choice
   flips them. (**Auto** only works when your feet are in view.) The choice is remembered.
2. Allow **Consent to data collection**, then turn on **Send readings to the dashboard**.
3. No calibration is needed. Readings use the upright reference.

**What the model is.** The teammate's pipeline (`posture_pipeline-main/`): MediaPipe finds your joints, and for a
side camera a deterministic rule labels upright / leaning forward / leaning back using your torso angle (a +/-10
degree band around your goal). It's a heuristic, not a validated classifier, and it can't see sideways leaning. The
exact mapping to the stored fields, and every limit, are in [`model-bridge.md`](model-bridge.md).

**Swapping the model later.** Everything model-specific sits behind
[`scripts/posture_model.py`](../scripts/posture_model.py): `load()` once, `predict(frame_bgr, facing, goal)` about
once a second, returning `label` (`GOOD` / `SLOUCHING` / `AWAY` / `UNKNOWN`), `deviation` (0 = on goal, about 1 =
far off), `confidence`, `features` (`torsoAngle` in degrees from vertical, + = forward), and optionally `source` and
`note`. The server, the page and the dashboard don't change. If `predict` raises, the error text appears on the page
and the traceback in the model server's terminal.

## 6. Drive the dashboard from the camera

On the Camera page, allow **Consent to data collection**, then turn on **Send readings to the dashboard**. The browser tab then acts as the
phone: each reading is posted to the API, so **Live**, alerts, **Analytics** and **Coach** run off your real
posture, and the readings are stored in the database. Turning it on for the first time replaces any phone that is
currently paired. Only a label, a deviation, a confidence, the torso and neck angles and the model's name are
stored: never a picture.

## Check the camera without the browser

```bash
python scripts/camera_test.py --list
python scripts/camera_test.py --index 1
```

`--list` saves one snapshot per camera into `scripts/_camera_snapshots/` (ignored by git) so you can
see which number is the iPhone; `--index N` opens a live preview (`q` quits). Camo may show black
here while a browser tab is using it, so stop the camera on the page first.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Black picture | Camo Studio is closed, the phone disconnected, or the Camo app on the phone is not open. Reopen both. |
| "Camera permission was denied" | Click the camera icon in the browser's address bar, allow it for `localhost`, and try again. Use Chrome or Edge directly, not a browser inside another app. |
| The picture is the laptop's own webcam | Pick the Camo camera in **Source**. |
| "The camera is in use by another app" | Close Zoom, Teams, or a running `camera_test.py` preview. |
| Model reading says `Stub (fixed mock data)` | The model server was not running when the camera started. Start it, then stop and start the camera. |
| Model reading says `Placeholder` | The server was started with the wrong Python, so the real model did not load. Its terminal says why. Start it with `posture_pipeline-main\.venv\Scripts\python.exe scripts/model_server.py` (and `pip install flask` into that venv once). |
| Always `UNKNOWN`, "Pick which way you face" | Choose Left or Right under **Which way do you face?**. If it still abstains, the note under the label says why (nobody in view, two people, torso out of frame). |
| The goal posture is refused, "We couldn't see you clearly" | Sit fully in the picture, head to hips, alone, and make sure **Send readings to the dashboard** is on. |
| "Can't reach the local model server" | `python scripts/model_server.py` stopped or crashed. Check its terminal. |
| The vertical view cuts into the picture, or shows black | Note the `showing … of …` line above the video and how the picture looks in Camo Studio, and tell whoever maintains `web/src/pages/Camera.tsx` (`findPicture`). |
| You do not fit head to chair base | Move the phone further back. The page can only show what the phone sees. |
| `flask` is not recognised | Use `python -m flask …` as above, with the venv active. |

## Using the live site (fixsit.health) with the real model

The hosted Camera page can use the model too, because the model server runs on your own computer:

1. Start the model server as in step 3 (`scripts/model_server.py`, port 5002). The API and the local dashboard are not needed.
2. Open <https://fixsit.health/camera> in Chrome or Edge **on the same computer** and click **Start camera**. If the
   browser asks to let the site reach devices or apps on your local network, allow it.
3. **Model reading** should name the real model. If it says `Stub (fixed mock data)`, the model server isn't running or
   the browser blocked the request: check the server's terminal, then stop and start the camera.

The page calls `http://127.0.0.1:5002` directly, so frames still go no further than your computer. The model server
only answers pages from `https://fixsit.health` and local dev (`ALLOWED_ORIGINS` in `scripts/model_server.py`; add
others with the `MODEL_ALLOWED_ORIGINS` environment variable). Use either this page or `python -m bridge`
([`model-bridge.md`](model-bridge.md)), not both: they share one camera and one device pairing.

## Privacy

Frames go from the browser tab to the model server on the same computer (`127.0.0.1`), are analysed
in memory and dropped. Nothing is saved or uploaded, and the hosted API accepts no images. Only the
numbers `predict` returns leave the tab, and only when **Send readings to the dashboard** is on.
The model server listens on `127.0.0.1` only, and `bridge/adapter.py` refuses to pass on anything but
numbers and a label.
