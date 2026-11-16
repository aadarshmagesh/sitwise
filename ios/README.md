# Sitwise iOS app

SwiftUI app that sits on a chair mount, runs the posture model **on the phone**, and sends only
numbers to the API. Screens: pairing, calibration, live status, settings.

> **Status: written but not yet built.** This was authored without Xcode (Windows). Expect to fix
> a few compile errors on the first Mac build. It needs a **physical iPhone** (camera) and an
> **Apple Developer account** (push entitlement + a `.p8` APNs key). Its model is still the
> **stub**: the teammate's real model is Python and runs on the computer instead (see
> [Windows, or no Mac](#windows-or-no-mac) and [`../docs/model-bridge.md`](../docs/model-bridge.md)).

## Windows or Mac?

**Building and running this app needs a Mac** (Xcode and the iOS Simulator only run on macOS; XcodeGen just generates
the project for Xcode). Everything else works on Windows, including the real model with the iPhone as the camera.

| | Windows | Mac |
|---|---|---|
| Edit the Swift code, `project.yml`, these docs | Yes (VS Code is fine; it can't compile it) | Yes |
| API, dashboard, desktop notifications | Yes | Yes |
| **Real posture model** (MediaPipe) with the iPhone as the camera, via Camo | **Yes**: [`../docs/camera-setup.md`](../docs/camera-setup.md) | Likely (unverified: the model's lock file is Windows-only) |
| Fake the phone with `scripts/simulate.py` | Yes | Yes |
| Build, sign and run the iOS app, the Simulator (Xcode is macOS-only) | **No** | Yes |
| iPhone push notifications (APNs) | Server side yes; needs the app built on a Mac and an Apple Developer account | Yes |

## Run it (on a Mac)

```bash
brew install xcodegen
cd ios
xcodegen generate          # creates Sitwise.xcodeproj from project.yml
open Sitwise.xcodeproj
```

1. Set your **Team** (Signing & Capabilities) or `DEVELOPMENT_TEAM` in `project.yml`.
2. Set the API host in [`Sitwise/Config.swift`](Sitwise/Config.swift) (`Config.baseURL`): the one place to change it. For local dev use the LAN address of whatever computer runs the API (`http://192.168.x.x:5001`; your Mac's, or the Windows laptop's, see below); the Info.plist allows local-network HTTP.
3. Make sure the **bundle ID** (`com.sitwise.app` in `project.yml`) equals `APNS_BUNDLE_ID` on the server.
4. Run on a device. On the **Simulator** the app falls back to synthetic frames, so the stub flow still works end to end (push won't).

## Windows, or no Mac

You can't build the app on Windows, but you don't need to in order to work on or demo the product.

### Demo and develop the real flow without the app

The iPhone can be the camera without the iOS app: **Camo** (Windows and Mac) turns it into a webcam, the
dashboard's **Camera** page shows it, the teammate's model runs on the laptop, and the readings go into the
database exactly as the app's would. Follow [`../docs/camera-setup.md`](../docs/camera-setup.md). In PowerShell, from the repo root:

```powershell
# one time: API + dashboard
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
cd web; npm install; cd ..

# one time: the model's own Python 3.12 environment (MediaPipe has no 3.14 build; install 3.12 first if `py -0` doesn't list it)
py -3.12 -m venv posture_pipeline-main\.venv
posture_pipeline-main\.venv\Scripts\python.exe -m pip install numpy==1.26.4 mediapipe==0.10.21 opencv-contrib-python==4.11.0.86 flask

# every time, three terminals
python -m flask --app api.index run --debug --port 5001                          # API
posture_pipeline-main\.venv\Scripts\python.exe scripts\model_server.py           # model
cd web; npm run dev                                                              # dashboard on http://localhost:5173
```

Then open **Camera**, choose which way you face, turn on **Send readings to the dashboard**, and use
**Set my goal posture**. No phone and no Camo? `python scripts\simulate.py --code <PAIRING_CODE> --loop` fakes
the phone's readings ([root README](../docs/configuration.md#simulate-the-phone)).

### A real iPhone talking to an API on your Windows laptop

Use this when a teammate builds the app on a Mac and the API runs on your Windows machine, on the same Wi-Fi.
The simplest route is to deploy to Vercel and set `Config.baseURL` to that URL. To use the laptop directly:

1. Find its address: `ipconfig` (the IPv4 address of your Wi-Fi adapter, such as `192.168.1.23`).
2. Start the API so other devices can reach it (the default only listens on the laptop itself):
   `python -m flask --app api.index run --host 0.0.0.0 --port 5001`.
3. Allow it through Windows Firewall, in an **administrator** PowerShell, and remove the rule afterwards:
   `New-NetFirewallRule -DisplayName "Sitwise API 5001" -Direction Inbound -LocalPort 5001 -Protocol TCP -Action Allow -Profile Private`
   then `Remove-NetFirewallRule -DisplayName "Sitwise API 5001"`.
4. Set `Config.baseURL` to `http://192.168.1.23:5001` (your address) in the Mac build.

Windows treats most Wi-Fi networks as **Public** by default, where the rule above does not apply. Switch the network to Private in Settings (only on a network you trust) rather than opening the port on a public one. Either way this exposes the dev API (and `ENABLE_DEV_ROUTES` if you turned it on) to everyone on that Wi-Fi.

### Splitting the work between a Windows and a Mac machine

- Edit Swift on Windows and push; whoever has the Mac pulls, runs `xcodegen generate`, builds, and fixes compile errors (there will be some on the first build, since nothing here has been compiled).
- `Sitwise.xcodeproj` and `Sitwise/Info.plist` are **generated** by XcodeGen. Change `project.yml` instead of editing them, so Windows and Mac contributors don't conflict.
- Don't plan on a Windows virtual machine for macOS: Apple only licenses macOS on Apple hardware.
- Ways to get a Mac without owning one, **none of which has been tried here**: a rented cloud Mac, a borrowed one at the hackathon, or a CI macOS runner such as GitHub Actions (it can compile the project, and with an Apple Developer account upload to TestFlight, but it gives you no Simulator to click through).

## How it fits together

```
FrameSource (camera, or synthetic on Simulator)
   -> PostureModel.analyze(frame:)      <- the seam; StubPostureModel today
   -> PostureSample (numbers only)
   -> APIClient.ingest  (POST /api/posture/ingest, ~1 Hz, Bearer device token from the Keychain)
   <- state + whether an alert was sent -> in-app banner + haptic
```

- Background / locked: the server sends an **APNs push**; the system notification vibrates the phone. Foreground: in-app banner + `UINotificationFeedbackGenerator`.
- Dev builds register **sandbox** APNs tokens (`Config.apnsSandbox`, from `#if DEBUG`); the server uses the matching Apple host per token. TestFlight/App Store builds use production.
- The monitoring screen keeps the display awake (the phone is mounted); camera frames are processed in memory and dropped.

## For the model teammate

The teammate delivered a **Python 3.12 + MediaPipe** pipeline (`posture_pipeline-main/`), not OpenCV for iOS, so
this app still runs on `StubPostureModel` and the real model currently runs on a computer through the Camera
page or `bridge/` ([`../docs/model-bridge.md`](../docs/model-bridge.md)).

To put the model on the phone, implement `PostureModel` (`Sitwise/Model/PostureModel.swift`) and change **one line** in
[`AppState.swift`](Sitwise/AppState.swift): `let model: PostureModel = RealPostureModel()`. That means MediaPipe Tasks
for iOS for the landmarks plus a Swift port of the angle rule; see [`Model/OpenCV/README.md`](Sitwise/Model/OpenCV/README.md)
and `bridge/adapter.py` for the exact mapping to `PostureSample`. The angle conventions are settled (`docs/api.md`).
**Open question:** who ports it, and who edits the Xcode project? Agree before two people edit it.

## Not done yet

- The real model on the phone (above), and everything about the app compiling and running.
- Real camera preview / "ghost" goal-posture overlay (stretch).
- Time-sensitive notification entitlement (the server already sets `interruption-level: time-sensitive`; without the capability iOS treats it as a normal alert).
- Unit tests; everything has only been checked by reading.
