# Documentation

Start with the root [README](../README.md) for the overview and [Setup and configuration](configuration.md) for running it.

| Task | Guide |
|---|---|
| Install, configure, deploy, troubleshoot | [Setup and configuration](configuration.md) |
| Run the real model with the dashboard camera | [Camera setup](camera-setup.md) |
| Receive posture alerts on another iPhone | [iPhone alerts](iphone-alerts.md) |
| Run the model directly against a webcam | [Model bridge](model-bridge.md) |
| Mount and frame the camera | [Hardware](hardware.md) |
| Understand API contracts | [API notes](api.md), [OpenAPI](openapi.yaml) |
| Prepare a demonstration | [Demo script](demo-script.md), [Pitch](../pitch.md) |
| Understand evidence and product limits | [Health claims](health-claims.md) |
| Develop the native iOS app | [iOS README](../ios/README.md) |
| Find source files | [Code map](../codemap.md) |
| Make and verify changes | [Contributing](../CONTRIBUTING.md) |

The active web camera flow uses an upright reference without calibration. Legacy calibration APIs
remain for the native app and existing bridge clients; they are not part of dashboard setup.
