# Changelog

## 1.3.12

- Authenticate each camera session with the O-KAM account (eye4_authentication) right after login, like the official PC client. Multi-sensor cameras send video only to authenticated sessions.
- The live-stream summary log now includes `eye4_auth` (-1 not sent, 0 not confirmed, 1 confirmed).

## 1.3.11

- Multi-sensor (VUID) cameras: after starting live view, send the same camera-parameters, VUID status and light-state queries the official PC client sends before its first video frame.

## 1.3.10

- Registers a camera's virtual device id (VUID) on the P2P client with
  `client_setvuid` right after creating it, as the official app does, when the
  account lists the camera under a virtual id. VUID cameras accepted commands
  but sent no video without it.

## 1.3.9

- Sends the O-KAM account's user id as `userId` with camera commands, and the
  `DevActiveTime` keep-alive before a live start, as the official PC client
  does. Newer cameras bound to the account may stream only to commands that
  carry it. The id never appears in logs or process arguments.

## 1.3.8

- Supports multi-sensor cameras that sent no video. A trace of the official
  O-KAM Pro PC client showed it sends `trans_cmd_string.cgi?cmd=8000&command=0`
  right before `livestream.cgi`; the bridge now does the same for every camera
  (the reply is ignored).
- Forwards a bare Annex-B video stream when a camera sends one without the
  usual 32-byte frame header on the video channel.
- The channel probe sends the same pre-live command first.

## 1.3.7

- The `probe_camera` diagnostic now reads the camera's `get_status.cgi`
  multi-sensor capability flags (only an allow-listed set of integer flags)
  and, for every live-start attempt, how many command responses came back
  and the last command id and `result` code.

## 1.3.6

- The `probe_camera` diagnostic also tries the multi-channel live start the
  official app uses for NVR-style devices, `{"live_start":{"chns":N,
  "streammask":M}}` through `client_write_cgi_nvr`, and logs the result as
  `nvr_chns=... streammask=...` lines.

## 1.3.5

- The `probe_camera` diagnostic also tries substreams 3, 100, 5 and 6. The
  official app's live command uses the selected resolution's index (1-4) and
  100 for super HD, which the first probe did not cover.

## 1.3.4

- Adds the optional `probe_camera` diagnostic. At startup it tries live
  substreams 2, 1, 0 and 4 on that camera and logs, per substream, which P2P
  channels carried data, how much, and each channel's first frame-header word
  and type. It is meant for multi-lens cameras that authenticate but send no
  video on the usual channel.

## 1.3.3

- Keeps each camera's stream URL valid across app restarts and updates. The
  media token was random per start, so every camera answered 401 after an
  update until the integration was reloaded.
- Makes H.265 cameras play. The bundled FFmpeg had no H.265 support, so 1.3.2
  could not mux their video. It now decodes H.265 and re-encodes it to H.264
  (at most 1280 px wide), which every browser and Home Assistant's WebRTC
  path can play. This uses more CPU while such a camera is being viewed.
  The bundled FFmpeg is now built with x264 and is therefore GPL-licensed.

## 1.3.2

- Streams cameras that encode H.265. The native helper now forwards H.265
  frames instead of dropping them, and the bridge detects the codec from the
  stream and muxes it accordingly. Live view and snapshots work for these
  cameras; whether H.265 live view plays depends on the browser or app.
- The `stream_ended` log line adds `stream_end_reason`, `last_magic` and
  `last_frame_type`, which say why a camera's video stopped.

## 1.3.1

- Adds an optional `password` to each `cameras` entry, for cameras on the same
  account that use different local passwords. It overrides `camera_password`
  for that camera only.
- Logs one `stream_ended` line per live session with the camera alias and the
  sanitized login and frame counters (including H.265 frames the bridge does
  not forward yet), so a failing camera can be diagnosed without the startup
  diagnostics.
- Stops a camera session that delivers no H.264 within 60 seconds. Viewers of
  such a camera were never released and kept the camera connected.
- Startup diagnostics now test every camera and report each by alias instead
  of stopping the app at the first camera that fails.

## 1.3.0

- Exposes every camera in the O-KAM account from one app instead of requiring
  an account with exactly one camera.
- Adds the optional `cameras` list to choose cameras by name and give each a
  stable alias.
- Lets the integration be added once per camera on the same bridge.

## 1.2.1

- Shows the release notes in the app update dialog. The supervisor reads a
  changelog from the app directory, so updating previously reported that none
  was found.

## 1.2.0

- Adds native `amd64` support alongside the existing `aarch64` runtime.
- Implements the camera's encrypted CS2/PPPP UDP transport and command framing
  directly for x86-64 Home Assistant hosts.
- Publishes one prebuilt multi-architecture image with architecture-correct
  Home Assistant labels.
- Keeps the account, wake, bridge API, streaming, snapshot, and lifecycle logic
  shared across both architectures.
- Stops reporting a disconnected client as a crash. The supervisor polls the
  bridge and closes connections abruptly, which filled the app log with
  ConnectionResetError tracebacks for normal behaviour (issue #5).
- Makes the camera password option genuinely optional. The bridge already fell
  back to the enumerated credential when it was empty, but the add-on schema
  still required a value, and its null default kept the key present and
  invalid, so the options could not be saved without one and no placeholder
  was safe (issue #5).
- Handles accounts that omit the camera-level credential, with an optional
  local camera-password override for changed device passwords.
- Uses the configured camera alias as the exact suggested entity ID on a fresh
  Home Assistant installation, for example `camera.cabin`.
- Reaches the camera's media over its relay session. A direct UDP punch yields
  a session that authenticates and acknowledges live-start but never delivers
  video, and it previously hid the relay path by winning the race.
- Addresses the relay request to the directory servers rather than to the relay
  itself, which is what makes the relay rendezvous complete.
- Notifies every endpoint a session touched when closing, and acknowledges a
  declined direct readiness request, so a camera does not hold a stale binding
  that blocks the next connection.
- Accepts relay media when NAT renumbers the peer's source port, which
  previously discarded the entire media channel while control traffic
  continued to work.
- Serves the live stream as MPEG-TS with timestamps, so Home Assistant's
  stream worker can build HLS. A raw elementary stream was rejected with
  "No dts in consecutive packets", so live view never played while snapshots
  kept working.
- Starts a newly opened live view on a decodable boundary by caching the
  stream's parameter sets and newest keyframe. Opening a second view of an
  already-streaming camera no longer waits for the camera's next keyframe.
- Adds protocol-vector, wire-format, reliable-channel, H.264, helper-contract,
  metadata, architecture-selection, relay-negotiation, session-teardown, and
  live-view priming tests.

## 1.1.1

- Refreshes the Home Assistant camera image as soon as native H.264 media
  becomes ready, preventing the waking-up image from remaining on screen.
- Reuses the last successful snapshot if a later still-image request briefly
  fails.
- Increases the default idle disconnect delay from 30 seconds to 120 seconds so
  normal page changes can reuse the warm camera connection.
- Reports the effective runtime idle timeout in camera and readiness status.

## 1.1.0

- Accepts the normal camera-owner account as well as an account with a shared
  camera, provided the account exposes exactly one camera.
- Makes the app available to all 64-bit ARM (`aarch64`) Home Assistant systems.
- Shows informative sleeping and waking-up images while live video is inactive
  or the battery camera is waking.
- Reports the distinct `camera_waking` phase and native-media readiness.
- Clarifies hardware compatibility and stream wake behavior throughout the
  installation documentation.

## 1.0.0

- Provides native ARM64 live video and snapshots for O-KAM Pro cameras.
- Supports 64-bit Home Assistant OS on Raspberry Pi 4 and Raspberry Pi 5.
- Adds automatic camera wake-up and clean idle disconnect.
- Shares one native stream between simultaneous Home Assistant viewers.
- Includes the HACS-compatible O-KAM Native Bridge integration.
- Adds authenticated local configuration, status, snapshot, and stream APIs.
- Enables automatic app startup and production release metadata.
- Documents complete installation, operation, updating, diagnostics,
  troubleshooting, security, and removal procedures.
