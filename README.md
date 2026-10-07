# Yashraj Player (Windows)

A fast video/movie player with built-in tools. Uses the **mpv** engine, so it plays
MP4, MKV, AVI, MOV, WMV, FLV, WebM, TS, HEVC/H.265, AV1 and almost every other format.

Built the same way as Audio Splitter Pro: Python + PySide6, packaged by GitHub Actions
into a Windows installer.

## Realistic expectations

I could not compile or run this on Windows from here (I work in a Linux sandbox without
internet), so the first build or first run may need one or two rounds of fixes.
If something fails, send me:
- the GitHub Actions log (the red step), or
- a screenshot / description of what happens when you open the app.

## How to build (same GitHub method, no terminal)

1. Upload **all files in this folder** to a new GitHub repo:
   `main.py`, `requirements.txt`, `installer.iss`, `README.md` and the
   `.github/workflows/build.yml` file.
2. Open the repo's **Actions** tab. The build starts on every push
   (or press **Run workflow**). It takes about 5 to 10 minutes.
3. When it is green, open the run and download from **Artifacts**:
   - **YashrajPlayer-Setup-Installer** - install this one (recommended)
   - **YashrajPlayer-Portable** - unzip and run `YashrajPlayer.exe`, no install

## Make it your default player

Windows never lets an installer silently take over defaults, so do this once:

1. Install with the Setup file (the portable version does not register formats).
2. Right-click any video, **Open with**, **Choose another app**, pick **Yashraj Player**,
   tick **Always**.
   Or: **Settings, Apps, Default apps**, search "Yashraj Player" and set the formats.

Double-clicking a video then opens it directly.

## What is inside

- Play/pause, seek bar, back/forward 10 s, volume, mute
- Speed 0.25x to **100x**, **Reverse** play
- Screen modes: Fit, Fill, Stretch, Original size, 16:9, 4:3, 21:9
- Side tools (hide/show with the arrow): Screenshot, Record, Zoom, Filters, Subtitles
- **Screenshot** saves a PNG to `Pictures\Yashraj Player` (orange frame flash)
- **Record** (Start / Pause / Stop) saves an MP4 clip to `Videos\Yashraj Player`
  (blinking red frame and REC badge while recording)
- **Filters**: Blu-ray, Cinema, Vivid, Soft, plus Brightness / Contrast / Color / Sharpness,
  and a Default button
- **Audio**: Pop, Bass, Rock, Vocal, Treble, Movie, 5-band equalizer, Boost up to 200%
- **Subtitles**: load .srt/.vtt/.ass, style them, or **Auto-generate** with the built-in
  Whisper AI (offline). The AI model downloads once, the first time you use it.
- Minimize, Mini player (always on top) and Close buttons
- Keyboard: Space, arrows, F, M, O, S, R, Z, E, U, C, A, J, [ ], P

## Notes

- The installer is large (about 100 MB) because it bundles the mpv engine and FFmpeg.
- Recording saves the original video segment (no filters or zoom).
- Reverse uses mpv's backward play when available, otherwise it steps backwards.
- Auto subtitles translate to English only for now. Other languages are a later step.
- Windows may show a SmartScreen warning for an unsigned app: **More info, Run anyway**.
