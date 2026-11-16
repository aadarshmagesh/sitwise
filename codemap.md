# Code map

The browser sends camera frames to the local model server; only numeric readings go to the API.
The API applies collection consent and the alert policy, then dispatches notifications. Gemini is a
separate server-side, per-request opt-in. See [docs](docs/README.md) for setup.

## Vendored model

| Path | Purpose |
|---|---|
| `posture_pipeline-main/` | Model code, weights, data and upstream documentation; managed as one vendored component |

## .claude

| Path | Purpose |
|---|---|
| `.claude/launch.json` | launch |

## Root

| Path | Purpose |
|---|---|
| `.env.example` | .env |
| `.gitignore` | .gitignore |
| `CONTRIBUTING.md` | Documentation: CONTRIBUTING |
| `README.md` | Documentation: README |
| `codemap.md` | Repository navigation (validated by scripts/check_codemap.py) |
| `index.py` | index |
| `package-lock.json` | package lock |
| `package.json` | package |
| `pitch.md` | Documentation: pitch |
| `requirements-dev.txt` | requirements dev |
| `requirements.txt` | requirements |
| `vercel.json` | vercel |

## api

| Path | Purpose |
|---|---|
| `api/ai/evidence_facts.py` | evidence facts |
| `api/ai/gemini.py` | Server-only Gemini client and rate limiting |
| `api/ai/prompts.py` | prompts |
| `api/ai/schemas.py` | schemas |
| `api/app.py` | Flask application and route registration |
| `api/auth.py` | auth |
| `api/core/calibration_feed.py` | calibration feed |
| `api/core/calibration_gate.py` | calibration gate |
| `api/core/coach_pack.py` | coach pack |
| `api/core/coach_stats.py` | coach stats |
| `api/core/insights.py` | insights |
| `api/core/posture_profile.py` | posture profile |
| `api/core/scoring.py` | scoring |
| `api/core/seedgen.py` | seedgen |
| `api/core/settings.py` | settings |
| `api/core/state_machine.py` | Posture transitions, grace period and cooldown |
| `api/core/test_calibration_feed.py` | Tests: test calibration feed |
| `api/core/test_calibration_gate.py` | Tests: test calibration gate |
| `api/core/test_coach_stats.py` | Tests: test coach stats |
| `api/core/test_insights.py` | Tests: test insights |
| `api/core/test_posture_profile.py` | Tests: test posture profile |
| `api/core/test_scoring.py` | Tests: test scoring |
| `api/core/test_settings.py` | Tests: test settings |
| `api/core/test_state_machine.py` | Tests: test state machine |
| `api/db.py` | db |
| `api/db_memory.py` | db memory |
| `api/errors.py` | errors |
| `api/index.py` | index |
| `api/push/apns.py` | apns |
| `api/push/dispatch.py` | dispatch |
| `api/push/webpush.py` | webpush |
| `api/routes/calibration.py` | API routes: calibration |
| `api/routes/checkins.py` | API routes: checkins |
| `api/routes/coach.py` | API routes: coach |
| `api/routes/dev.py` | API routes: dev |
| `api/routes/export.py` | API routes: export |
| `api/routes/metrics.py` | API routes: metrics |
| `api/routes/model_stubs.py` | API routes: model stubs |
| `api/routes/pair.py` | API routes: pair |
| `api/routes/posture.py` | Consent-gated posture ingestion and alert dispatch |
| `api/routes/push.py` | API routes: push |
| `api/routes/settings.py` | API routes: settings |
| `api/routes/status.py` | API routes: status |
| `api/schema.sql` | schema |
| `api/tests/conftest.py` | Tests: conftest |
| `api/tests/test_ai.py` | Tests: test ai |
| `api/tests/test_api.py` | Tests: test api |
| `api/tests/test_coach_api.py` | Tests: test coach api |
| `api/tests/test_collection_consent.py` | Tests: test collection consent |
| `api/tests/test_model_live.py` | Tests: test model live |
| `api/tests/test_phone_alerts.py` | Tests: test phone alerts |
| `api/tests/test_push_messages.py` | Tests: test push messages |
| `api/tests/test_store.py` | Tests: test store |
| `api/util.py` | util |

## bridge

| Path | Purpose |
|---|---|
| `bridge/__main__.py` |   main   |
| `bridge/adapter.py` | adapter |
| `bridge/cli.py` | cli |
| `bridge/client.py` | client |
| `bridge/engine.py` | MediaPipe and posture adapter |
| `bridge/fakes.py` | fakes |
| `bridge/preview.py` | preview |
| `bridge/runner.py` | runner |
| `bridge/test_adapter.py` | Tests: test adapter |
| `bridge/test_client.py` | Tests: test client |
| `bridge/test_engine.py` | Tests: test engine |
| `bridge/test_model_server.py` | Tests: test model server |
| `bridge/test_real_model.py` | Tests: test real model |
| `bridge/test_runner.py` | Tests: test runner |

## docs

| Path | Purpose |
|---|---|
| `docs/README.md` | Documentation: README |
| `docs/api.md` | Documentation: api |
| `docs/camera-setup.md` | Documentation: camera setup |
| `docs/configuration.md` | Documentation: setup, configuration, deploy, troubleshooting |
| `docs/demo-script.md` | Documentation: demo script |
| `docs/hardware.md` | Documentation: hardware |
| `docs/health-claims.md` | Documentation: health claims |
| `docs/iphone-alerts.md` | Documentation: iphone alerts |
| `docs/model-bridge.md` | Documentation: model bridge |
| `docs/openapi.yaml` | openapi |

## ios

| Path | Purpose |
|---|---|
| `ios/README.md` | Documentation: README |
| `ios/Sitwise/AppState.swift` | AppState |
| `ios/Sitwise/Config.swift` | Config |
| `ios/Sitwise/Model/OpenCV/README.md` | Documentation: README |
| `ios/Sitwise/Model/PostureModel.swift` | PostureModel |
| `ios/Sitwise/Models/Types.swift` | Types |
| `ios/Sitwise/Services/APIClient.swift` | APIClient |
| `ios/Sitwise/Services/FrameSource.swift` | FrameSource |
| `ios/Sitwise/Services/Keychain.swift` | Keychain |
| `ios/Sitwise/Services/PostureMonitor.swift` | PostureMonitor |
| `ios/Sitwise/Services/PushManager.swift` | PushManager |
| `ios/Sitwise/SitwiseApp.swift` | SitwiseApp |
| `ios/Sitwise/Views/CalibrationView.swift` | CalibrationView |
| `ios/Sitwise/Views/LiveStatusView.swift` | LiveStatusView |
| `ios/Sitwise/Views/PairingView.swift` | PairingView |
| `ios/Sitwise/Views/RootView.swift` | RootView |
| `ios/Sitwise/Views/SettingsView.swift` | SettingsView |
| `ios/project.yml` | project |

## scripts

| Path | Purpose |
|---|---|
| `scripts/camera_test.py` | Tests: camera test |
| `scripts/check_codemap.py` | check codemap |
| `scripts/gen_vapid.py` | gen vapid |
| `scripts/init_db.py` | init db |
| `scripts/model_server.py` | Local model HTTP server on port 5002; called by the dev proxy and directly by the hosted Camera page (origin allowlist) |
| `scripts/posture_model.py` | posture model |
| `scripts/requirements-model.txt` | requirements model |
| `scripts/seed.py` | seed |
| `scripts/simulate.py` | simulate |

## web

| Path | Purpose |
|---|---|
| `web/index.html` | index |
| `web/package-lock.json` | package lock |
| `web/package.json` | package |
| `web/public/favicon.svg` | favicon |
| `web/public/manifest.webmanifest` | manifest |
| `web/public/receiver.webmanifest` | receiver |
| `web/public/sw.js` | sw |
| `web/src/App.tsx` | App |
| `web/src/api.ts` | api |
| `web/src/auth.ts` | auth |
| `web/src/coach/ics.test.ts` | Tests: ics.test |
| `web/src/coach/ics.ts` | ics |
| `web/src/coach/localAnalysis.test.ts` | Tests: localAnalysis.test |
| `web/src/coach/localAnalysis.ts` | localAnalysis |
| `web/src/coach/profile.ts` | profile |
| `web/src/components/DataConsent.tsx` | Collection consent and withdrawal controls |
| `web/src/components/Evidence.tsx` | UI component: Evidence |
| `web/src/components/Layout.tsx` | UI component: Layout |
| `web/src/components/PainInsights.tsx` | UI component: PainInsights |
| `web/src/components/charts/Heatmap.tsx` | UI component: Heatmap |
| `web/src/components/charts/Timeline.tsx` | UI component: Timeline |
| `web/src/components/charts/TrendChart.tsx` | UI component: TrendChart |
| `web/src/components/coach/CoachingPanel.tsx` | UI component: CoachingPanel |
| `web/src/components/coach/HabitsPanel.tsx` | UI component: HabitsPanel |
| `web/src/components/coach/NudgeStyle.tsx` | UI component: NudgeStyle |
| `web/src/components/coach/PatternsPanel.tsx` | UI component: PatternsPanel |
| `web/src/components/coach/ProfilePanel.tsx` | UI component: ProfilePanel |
| `web/src/components/coach/ShareCard.tsx` | UI component: ShareCard |
| `web/src/components/coach/ToolsPanel.tsx` | UI component: ToolsPanel |
| `web/src/components/coach/charts.tsx` | UI component: charts |
| `web/src/components/coach/shared.tsx` | UI component: shared |
| `web/src/components/ui.tsx` | UI component: ui |
| `web/src/evidence.ts` | evidence |
| `web/src/format.ts` | format |
| `web/src/hooks.ts` | hooks |
| `web/src/index.css` | index |
| `web/src/main.tsx` | main |
| `web/src/model.ts` | Picks the Camera page's model: local Python model server (dev proxy, or 127.0.0.1:5002 from the hosted site), else the stub |
| `web/src/pages/Analytics.tsx` | Dashboard page: Analytics |
| `web/src/pages/Camera.tsx` | Local camera feed and model integration |
| `web/src/pages/Coach.tsx` | Dashboard page: Coach |
| `web/src/pages/Live.tsx` | Dashboard page: Live |
| `web/src/pages/Pair.tsx` | Dashboard page: Pair |
| `web/src/pages/Receive.tsx` | External phone push receiver setup |
| `web/src/pages/Report.tsx` | Dashboard page: Report |
| `web/src/pages/Settings.tsx` | Dashboard page: Settings |
| `web/src/push.ts` | push |
| `web/src/types.ts` | types |
| `web/tsconfig.json` | tsconfig |
| `web/vite.config.ts` | vite.config |
| `web/vitest.config.ts` | Tests: vitest.config |
