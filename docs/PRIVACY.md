# PRIVACY · Perception Consent (product-level)

> Self-use can rely on promises. A shipped agent app must make consent a **product mechanism**.

## Default state: everything off
- semantic reading: off · recording: off · accessibility: not enabled · usage access: not granted
- every perception capability is enabled **item-by-item, explicitly, revocably**; no "install = consent"

## Three perception levels
| level | meaning | requirement |
|---|---|---|
| L0 off | no perception; local TTS/timers only | default |
| L1 allowlist | read only user-named apps | show foreground app while active |
| L2 all apps | any foreground app text | persistent indicator + explicit confirmation |

## Indicators (hard product requirement)
- persistent dot/notification while perception is on; tap = immediate off
- recording: notification "recording", with stop
- screen reading: "reading screen text" badge that cannot be hidden

## Data rules (defaults, not options)
- semantic text lives in RAM only (~600s); never written to disk, never uploaded, never in logs/backups
- audio used only for local STT; raw recordings deleted after processing
- audit stores counters and on/off timestamps only — never content
- one-tap "clear perception data" in the app

## API surface (implemented in the reference app)
```
GET /语义 (state) · /语义开?级别=1|2 (enable; level 2 requires confirm) · /语义关 (disable)
GET /触觉 (user presence — let automations yield) · /树 (semantic nodes, within granted level)
```

## Withdrawal
- user can disable anytime (indicator / notification / settings) — immediate release of a11y sampling
- uninstall revokes all grants; provide data-deletion notes
