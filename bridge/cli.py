"""python -m bridge: run the teammate's side-camera model and stream its readings to Sitwise.

Run it with the model's Python 3.12 environment (posture_pipeline-main/.venv), from the repo root:

  .\\posture_pipeline-main\\.venv\\Scripts\\python.exe -m bridge --facing right --code ABC234 --display

See docs/model-bridge.md. Frames never leave this computer; only numbers and a label are sent.
"""
from __future__ import annotations

import argparse
import os
import sys
from functools import partial
from pathlib import Path
from typing import Optional, Sequence

from bridge.client import DEFAULT_BASE, Api, BridgeError, load_saved, save_token

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PIPELINE = ROOT / "posture_pipeline-main"

SETUP_HELP = """Couldn't load the posture pipeline ({err}).
Run this with the model's Python 3.12 environment, from the repo root:
  py -3.12 -m venv posture_pipeline-main\\.venv
  posture_pipeline-main\\.venv\\Scripts\\python.exe -m pip install numpy==1.26.4 mediapipe==0.10.21 opencv-contrib-python==4.11.0.86
  posture_pipeline-main\\.venv\\Scripts\\python.exe -m bridge --facing right --code <PAIRING_CODE>
(the model needs Python 3.12 exactly; see docs/model-bridge.md)"""


say = partial(print, flush=True)   # line-by-line even when output is redirected to a file or pipe


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m bridge", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--facing", choices=["left", "right", "auto"], default=os.environ.get("SITWISE_FACING"),
                   help="Which way you face in the camera image: where your nose points (left or right) when you sit. "
                        "'auto' lets the model guess from your face and feet (needs your feet in view). Required.")
    p.add_argument("--code", help="Pairing code from the dashboard (Pair page). Needed once; the token is then remembered.")
    p.add_argument("--base", help=f"API address (default: saved one, else $SITWISE_BASE, else {DEFAULT_BASE})")
    p.add_argument("--token", default=os.environ.get("SITWISE_DEVICE_TOKEN"), help="Device token (instead of --code)")
    p.add_argument("--source", default="0", help="Camera index (default 0) or a video file path")
    p.add_argument("--display", action="store_true", help="Show a local preview window (Q/Esc quits, L/F = facing left/right)")
    p.add_argument("--dry-run", action="store_true", help="Run the model and print readings, but send nothing")
    p.add_argument("--interval", type=float, default=1.0, help="Seconds between readings sent to the server (default 1)")
    p.add_argument("--fps", type=float, default=5.0, help="Max frames analyzed per second (default 5; 0 = no cap)")
    p.add_argument("--smoothing-window", type=int, default=3, help="Frames averaged for the torso angle (default 3)")
    p.add_argument("--lean-threshold-deg", type=float, default=10.0, help="The model's own upright band, +/- degrees (default 10)")
    p.add_argument("--camera-roll-deg", type=float, default=0.0, help="Known camera tilt, clockwise degrees (default 0)")
    p.add_argument("--loop-video", action="store_true", help="With a video file: start over when it ends (demos and tests)")
    p.add_argument("--max-seconds", type=float, help="Stop after this many seconds")
    p.add_argument("--pipeline-dir", default=str(DEFAULT_PIPELINE), help="The teammate's repo folder (default posture_pipeline-main)")
    p.add_argument("--model", help="Pose model file (default <pipeline>/models/pose_landmarker_heavy.task)")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.facing:
        print("error: --facing is required (left or right: where your nose points in the camera image; or auto). "
              "A wrong value flips forward and backward.", file=sys.stderr)
        return 2
    facing = "unknown" if args.facing == "auto" else args.facing

    from bridge.engine import Engine
    from bridge.runner import Bridge

    try:
        import cv2
        engine = Engine.load(args.pipeline_dir, args.model, args.lean_threshold_deg, args.smoothing_window)
    except ImportError as e:
        print(SETUP_HELP.format(err=e), file=sys.stderr)
        return 2
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    api: Optional[Api] = None
    base = args.base or os.environ.get("SITWISE_BASE") or load_saved().get("base") or DEFAULT_BASE
    if not args.dry_run:
        token = args.token or (load_saved().get("deviceToken") if load_saved().get("base", base) == base else None)
        api = Api(base, token)
        try:
            if args.code:
                token = api.claim(args.code)
                save_token(base, token)
                say(f"Paired. (Pairing replaces any phone that was paired; the token is saved in {Path.home() / '.sitwise'}.)")
            elif not token:
                print("error: not paired yet. Create a pairing code on the dashboard's Pair page and run again with --code <CODE>.", file=sys.stderr)
                return 2
        except BridgeError as e:
            print(f"error: {e.message}", file=sys.stderr)
            return 1

    src = str(args.source)
    is_camera = src.isdigit()
    if is_camera and sys.platform == "win32":
        # DirectShow first: virtual cameras such as Camo can open through Windows' default backend
        # (Media Foundation) and then deliver no frames. Camera numbers match scripts/camera_test.py.
        capture = cv2.VideoCapture(int(src), cv2.CAP_DSHOW)
        if not capture.isOpened():
            capture = cv2.VideoCapture(int(src))
    else:
        capture = cv2.VideoCapture(int(src) if is_camera else src)
    if not capture.isOpened():
        print(f"error: can't open {'camera ' if is_camera else ''}{src}", file=sys.stderr)
        return 2

    preview = None
    if args.display:
        from bridge import preview as preview_module
        from posture.pose import CONNECTIONS      # the teammate's skeleton, importable now that the engine loaded
        preview = preview_module.make_preview(CONNECTIONS)

    say(f"Sitwise model bridge. Facing: {args.facing}. Camera frames stay on this computer; only numbers "
          f"and a label are sent to {base if api else '(nowhere: dry run)'}. Ctrl+C to stop.")
    status = 0
    try:
        bridge = Bridge(
            capture=capture, engine=engine, api=api, facing=facing, camera_roll_deg=args.camera_roll_deg,
            interval_s=args.interval, fps=args.fps, is_file=not is_camera, loop_video=args.loop_video,
            rewind=lambda: capture.set(cv2.CAP_PROP_POS_FRAMES, 0), preview=preview, log=say)
        summary = bridge.run(max_seconds=args.max_seconds)
        say(f"Stopped. {summary}")
    except KeyboardInterrupt:
        say("Stopped.")
    except BridgeError as e:
        hint = " Pair again with --code." if e.status == 401 else ""
        print(f"error: {e.message}.{hint}", file=sys.stderr)
        status = 1
    finally:
        engine.close()
        capture.release()
        if args.display:
            preview_module.close()
    return status
