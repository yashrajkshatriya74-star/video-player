# Yashraj Player - Windows app (PySide6 + libmpv)
# Plays every common video/audio format through mpv, with the same tools as the web demo.
import sys, os, time, math, shutil, tempfile, datetime, subprocess, threading, urllib.request
from functools import reduce
from operator import or_
from pathlib import Path

# ---- find bundled DLLs (libmpv-2.dll, ffmpeg.exe) before importing mpv ----
BASE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
os.environ["PATH"] = BASE + os.pathsep + os.environ.get("PATH", "")
if hasattr(os, "add_dll_directory"):
    try:
        os.add_dll_directory(BASE)
    except Exception:
        pass

from PySide6.QtCore import Qt, QTimer, QPoint, QRect, Signal, QObject, QPropertyAnimation, QAbstractAnimation, QEasingCurve
from PySide6.QtGui import QColor, QPainter, QPen, QCursor
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QPushButton, QLabel, QSlider, QComboBox, QFrame, QFileDialog, QStackedWidget,
                               QScrollArea, QMessageBox)

MPV_ERR = None
try:
    import mpv
except Exception as ex:  # libmpv-2.dll missing
    mpv = None
    MPV_ERR = str(ex)

APP = "Yashraj Player"
CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0
DATA = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "YashrajPlayer"
PICS = Path.home() / "Pictures" / "Yashraj Player"
VIDS = Path.home() / "Videos" / "Yashraj Player"
FFMPEG = os.path.join(BASE, "ffmpeg.exe") if os.path.exists(os.path.join(BASE, "ffmpeg.exe")) else "ffmpeg"
MEDIA_FILTER = ("Media files (*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm *.m4v *.ts *.m2ts *.mpg *.mpeg *.3gp *.ogv "
                "*.mp3 *.flac *.wav *.aac *.m4a *.ogg *.opus);;All files (*.*)")

FX_PRE = {"Original": (1, 1, 1, 0), "Blu-ray": (1.02, 1.12, 1.15, .8), "Cinema": (.98, 1.15, .95, .4),
          "Vivid": (1.05, 1.15, 1.4, .5), "Soft": (.92, 1.05, 1, 0)}
EQ_PRE = {"Normal": [0, 0, 0, 0, 0, 1], "Pop": [-1, 2, 4, 2, -1, 1], "Bass": [8, 5, 0, 0, 0, 1],
          "Rock": [5, 3, -2, 3, 5, 1], "Vocal": [-3, -1, 4, 4, 1, 1], "Treble": [-2, 0, 0, 4, 7, 1],
          "Movie": [5, 2, -1, 2, 4, 1.2]}
EQ_F = [60, 230, 910, 3600, 14000]
EQ_NAMES = ["60 Hz", "230 Hz", "910 Hz", "3.6 kHz", "14 kHz"]
SPEEDS = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 4, 8, 16, 32, 50, 100]
FITS = ["Fit to screen", "Fill (crop edges)", "Stretch", "Original size", "16:9", "4:3", "21:9"]
LANGS = [("Auto-detect", "auto"), ("Hindi", "hi"), ("English", "en"), ("Urdu", "ur"), ("Punjabi", "pa"),
         ("Bengali", "bn"), ("Tamil", "ta"), ("Telugu", "te"), ("Marathi", "mr"), ("Gujarati", "gu"),
         ("Kannada", "kn"), ("Malayalam", "ml"), ("Spanish", "es"), ("French", "fr"), ("German", "de"),
         ("Portuguese", "pt"), ("Russian", "ru"), ("Arabic", "ar"), ("Japanese", "ja"), ("Korean", "ko"),
         ("Chinese", "zh"), ("Turkish", "tr"), ("Indonesian", "id")]
MODELS = [("Small (~470 MB, recommended)", "ggml-small.bin"), ("Base (~140 MB, faster)", "ggml-base.bin"),
          ("Medium (~1.5 GB, most accurate)", "ggml-medium.bin")]
SUB_COLORS = [("White", "#FFFFFF"), ("Yellow", "#FFE14D"), ("Cyan", "#6EE7FF")]

QSS = """
QWidget{color:#e8ecf2;font-family:'Segoe UI';font-size:13px}
QPushButton{background:#171c24;border:1px solid #2a323f;border-radius:8px;padding:6px 11px}
QPushButton:hover{border-color:#ff9f1c}
QPushButton#close:hover{background:#ef476f;border-color:#ef476f}
QFrame#panel,QFrame#tools{background:#171c24;border:1px solid #2a323f;border-radius:12px}
QFrame#bar{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 rgba(0,0,0,0),stop:1 rgba(0,0,0,215))}
QWidget#wc QPushButton{background:rgba(0,0,0,170)}
QLabel{background:transparent}
QLabel#dim{color:#8a95a6;font-size:12px}
QLabel#lb{color:#8a95a6;font-size:12px}
QLabel#toast{background:rgba(0,0,0,215);border:1px solid #2a323f;border-radius:8px;padding:8px 14px}
QLabel#badge{background:rgba(0,0,0,185);border:1px solid #ef476f;border-radius:14px;padding:5px 12px}
QSlider::groove:horizontal{height:4px;background:#2a323f;border-radius:2px}
QSlider::sub-page:horizontal{background:#ff9f1c;border-radius:2px}
QSlider::handle:horizontal{background:#ff9f1c;width:14px;height:14px;margin:-6px 0;border-radius:7px}
QSlider::groove:vertical{width:4px;background:#2a323f;border-radius:2px}
QSlider::add-page:vertical{background:#ff9f1c;border-radius:2px}
QSlider::handle:vertical{background:#ff9f1c;width:14px;height:14px;margin:0 -6px;border-radius:7px}
QComboBox{background:#171c24;border:1px solid #2a323f;border-radius:8px;padding:5px 8px}
QComboBox QAbstractItemView{background:#171c24;selection-background-color:#ff9f1c;selection-color:#111}
QScrollBar:vertical{width:8px;background:transparent}
QScrollBar::handle:vertical{background:#2a323f;border-radius:4px}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0}
"""


def fmt(t):
    if t is None:
        return "0:00"
    t = max(0, int(t))
    h, m, s = t // 3600, (t % 3600) // 60, t % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


# ---------------------------------------------------------------- small UI helpers
class CSlider(QSlider):
    """Slider that jumps to the clicked spot and reports user movement through `scrub`."""
    scrub = Signal(int)

    def __init__(self, orient=Qt.Horizontal):
        super().__init__(orient)
        self.drag = False

    def _v(self, e):
        r = self.maximum() - self.minimum()
        if self.orientation() == Qt.Horizontal:
            f = e.position().x() / max(1, self.width())
        else:
            f = 1 - e.position().y() / max(1, self.height())
        return self.minimum() + int(round(max(0.0, min(1.0, f)) * r))

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.drag = True
            self.setValue(self._v(e))
            self.scrub.emit(self.value())
            e.accept()

    def mouseMoveEvent(self, e):
        if self.drag:
            self.setValue(self._v(e))
            self.scrub.emit(self.value())
            e.accept()

    def mouseReleaseEvent(self, e):
        self.drag = False
        e.accept()

    def wheelEvent(self, e):
        e.ignore()


def mk(text, cb=None, pri=False, tip="", w=None, h=None, name=None):
    b = QPushButton(text)
    b.setFocusPolicy(Qt.NoFocus)
    b.setCursor(Qt.PointingHandCursor)
    if tip:
        b.setToolTip(tip)
    b._extra = ""
    if pri:
        style_btn(b, True)
    if name:
        b.setObjectName(name)
    if w:
        b.setFixedWidth(w)
    if h:
        b.setFixedHeight(h)
    if cb:
        b.clicked.connect(lambda _=False, f=cb: f())
    return b


def sl(lo, hi, val, cb=None, orient=Qt.Horizontal):
    s = CSlider(orient)
    s.setRange(lo, hi)
    s.setValue(val)
    s.setFocusPolicy(Qt.NoFocus)
    if cb:
        s.valueChanged.connect(lambda v, f=cb: f(v))
    return s


def lab(text, kind=None):
    l = QLabel(text)
    if kind:
        l.setObjectName(kind)
    if kind == "dim":
        l.setWordWrap(True)
    return l


def combo(items, cb=None, fit=False):
    c = QComboBox()
    c.setFocusPolicy(Qt.NoFocus)
    c.addItems(items)
    if fit:
        c.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
    else:
        c.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        c.setMinimumContentsLength(8)
    if cb:
        c.currentIndexChanged.connect(lambda i, f=cb: f(i))
    return c


def style_btn(b, active):
    """Orange 'active' look, or the normal look. Always readable, also on hover."""
    extra = getattr(b, "_extra", "")
    if active:
        css = ("QPushButton{background:#ff9f1c;color:#111111;border:1px solid #ff9f1c;border-radius:8px;"
               "font-weight:600;" + extra + "}QPushButton:hover{background:#ffb84d;border-color:#ffb84d;color:#111111}")
    else:
        css = ("QPushButton{" + extra + "}") if extra else ""
    b.setStyleSheet(css)


def mark(group, name):
    for n, b in group.items():
        style_btn(b, n == name)


def wrap_scroll(w):
    sa = QScrollArea()
    sa.setWidget(w)
    sa.setWidgetResizable(True)
    sa.setFrameShape(QFrame.NoFrame)
    sa.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    sa.setStyleSheet("QScrollArea{background:transparent}")
    sa.viewport().setStyleSheet("background:transparent")
    return sa


class Bus(QObject):
    toast = Signal(str)
    sub_ready = Signal(str)
    rec_saved = Signal(str)


# ---------------------------------------------------------------- mpv engine wrapper
class Engine:
    def _log(self, level, comp, msg):
        try:
            DATA.mkdir(parents=True, exist_ok=True)
            with open(DATA / "mpv.log", "a", encoding="utf-8", errors="replace") as f:
                f.write(f"[{level}] {comp}: {msg}")
        except Exception:
            pass

    def __init__(self, wid, on_error=None):
        try:
            (DATA / "mpv.log").unlink()
        except Exception:
            pass
        opts = dict(vo="gpu", hwdec="no", hr_seek="yes", keep_open="yes", idle="yes", input_default_bindings="no",
                    input_vo_keyboard="no", input_cursor="no", osc="no", osd_level=0, cursor_autohide="no",
                    sub_auto="fuzzy", screenshot_format="png", volume_max=200, ytdl="no")
        try:
            self.m = mpv.MPV(wid=str(wid), log_handler=self._log, loglevel="info", **opts)
        except Exception:
            self.m = mpv.MPV(wid=str(wid), log_handler=self._log, loglevel="info")
        self.cur = ""
        self.vals = {}
        for name in ("time-pos", "duration", "pause", "idle-active", "eof-reached"):
            try:
                self.m.observe_property(name, self._observed)
            except Exception:
                pass
        try:
            @self.m.event_callback("end-file")
            def _eof(ev):
                try:
                    d = ev.as_dict() if hasattr(ev, "as_dict") else dict(ev)
                    r = d.get("reason")
                    r = r.decode() if isinstance(r, bytes) else r
                    if r == "error" and on_error:
                        on_error("This file could not be played. Details are saved in mpv.log (Local AppData, YashrajPlayer).")
                except Exception:
                    pass
        except Exception:
            pass

    def _observed(self, name, value):
        self.vals[name] = value

    def prop(self, k, default=None):
        v = self.vals.get(k)
        if v is not None:
            return v
        try:
            v = self.m[k]
            return default if v is None else v
        except Exception:
            return default

    def setp(self, k, v):
        try:
            self.m[k] = v
            return True
        except Exception:
            return False

    def cmd(self, *a):
        try:
            self.m.command(*[str(x) for x in a])
            return True
        except Exception:
            return False

    def open(self, path):
        self.cur = path
        self.m.play(path)
        self.setp("pause", "no")

    def set_fit(self, i):
        self.setp("keepaspect", "yes")
        self.setp("panscan", 0.0)
        self.setp("video-unscaled", "no")
        self.setp("video-aspect-override", "-1")
        if i == 1:
            self.setp("panscan", 1.0)
        elif i == 2:
            self.setp("keepaspect", "no")
        elif i == 3:
            self.setp("video-unscaled", "yes")
        elif i >= 4:
            self.setp("video-aspect-override", ["16:9", "4:3", "21:9"][i - 4])

    def set_zoom(self, z, px, py):
        self.setp("video-zoom", math.log2(max(1.0, z)))
        self.setp("video-pan-x", px)
        self.setp("video-pan-y", py)

    def set_filters(self, b, c, s, sharp):
        self.setp("brightness", round((b - 1) * 100))
        self.setp("contrast", round((c - 1) * 100))
        self.setp("saturation", round((s - 1) * 100))
        self.cmd("vf", "remove", "@sharp")
        if sharp > 0:
            self.cmd("vf", "add", f"@sharp:lavfi=[unsharp=5:5:{sharp * 0.8:.2f}:5:5:0]")

    def set_eq(self, gains, boost):
        parts = [f"equalizer=f={f}:t=q:w=1:g={g}" for f, g in zip(EQ_F, gains) if g]
        if abs(boost - 1) > 0.01:
            parts.append(f"volume={boost}")
        if parts:
            self.cmd("af", "set", "lavfi=[" + ",".join(parts) + "]")
        else:
            self.cmd("af", "clr", "")

    def screenshot(self):
        PICS.mkdir(parents=True, exist_ok=True)
        f = PICS / f"shot-{datetime.datetime.now():%Y%m%d-%H%M%S}.png"
        ok = self.cmd("screenshot-to-file", str(f), "video")
        return f if ok else None

    def sub_style(self, scale, delay, color, box, pos):
        self.setp("sub-scale", scale)
        self.setp("sub-delay", delay)
        self.setp("sub-color", color)
        self.setp("sub-border-style", "opaque-box" if box else "outline-and-shadow")
        self.setp("sub-back-color", "#A6000000" if box else "#00000000")
        self.setp("sub-pos", pos)


# ---------------------------------------------------------------- background jobs
def run(cmd):
    return subprocess.run(cmd, capture_output=True, creationflags=CREATE_NO_WINDOW)


def record_job(src, segs, bus):
    try:
        VIDS.mkdir(parents=True, exist_ok=True)
        out = VIDS / f"clip-{datetime.datetime.now():%Y%m%d-%H%M%S}.mp4"
        tmp = Path(tempfile.mkdtemp())
        parts, last_err = [], []
        for i, (a, b) in enumerate(segs):
            if b - a < 0.3:
                continue
            o = tmp / f"p{i}.mp4"
            r = run([FFMPEG, "-y", "-ss", f"{a:.3f}", "-i", src, "-t", f"{b - a:.3f}", "-c:v", "libx264",
                     "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", str(o)])
            if o.exists():
                parts.append(o)
            else:
                last_err = (r.stderr or b"").decode("utf-8", "replace").strip().splitlines()[-1:] or ["unknown error"]
        if not parts:
            bus.toast.emit("Recording could not be saved: " + (last_err[0] if last_err else "clip too short"))
            return
        if len(parts) == 1:
            shutil.move(str(parts[0]), str(out))
        else:
            lst = tmp / "list.txt"
            lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
            run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
        if out.exists():
            bus.toast.emit(f"Recording saved: {out.name}")
            bus.rec_saved.emit(str(out))
        else:
            bus.toast.emit("Could not save the recording.")
    except Exception as ex:
        bus.toast.emit(f"Recording failed: {ex}")


def whisper_job(video, lang, translate, model_file, bus):
    try:
        wdir = Path(BASE) / "whisper"
        exe = next((p for n in ("whisper-cli.exe", "main.exe") for p in wdir.rglob(n)), None)
        if exe is None:
            bus.toast.emit("Auto subtitles are not included in this build.")
            return
        model = DATA / "models" / model_file
        if not model.exists():
            model.parent.mkdir(parents=True, exist_ok=True)
            bus.toast.emit(f"Downloading the subtitle AI model ({model_file}). This happens only once...")
            url = f"https://huggingface.co/ggerganov/whisper.cpp/resolve/main/{model_file}"
            part = model.with_suffix(".part")
            with urllib.request.urlopen(url, timeout=60) as r, open(part, "wb") as f:
                total = int(r.headers.get("Content-Length", 0))
                got, last = 0, -1
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
                    got += len(chunk)
                    if total and got * 100 // total // 10 != last:
                        last = got * 100 // total // 10
                        bus.toast.emit(f"Downloading AI model... {got * 100 // total}%")
            part.replace(model)
        bus.toast.emit("Generating subtitles... this can take a few minutes.")
        tmp = Path(tempfile.mkdtemp())
        wav = tmp / "a.wav"
        run([FFMPEG, "-y", "-i", video, "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav)])
        if not wav.exists():
            bus.toast.emit("Could not read the audio of this video.")
            return
        prefix = tmp / "out"
        cmd = [str(exe), "-m", str(model), "-f", str(wav), "-osrt", "-of", str(prefix), "-l", lang]
        if translate:
            cmd.append("-tr")
        run(cmd)
        srt = Path(str(prefix) + ".srt")
        if not srt.exists():
            bus.toast.emit("Subtitle generation failed.")
            return
        tag = "en" if translate else lang
        dest = Path(video).with_suffix(f".{tag}.srt")
        try:
            shutil.copy(srt, dest)
        except Exception:
            (DATA / "subs").mkdir(parents=True, exist_ok=True)
            dest = DATA / "subs" / (Path(video).stem + f".{tag}.srt")
            shutil.copy(srt, dest)
        bus.sub_ready.emit(str(dest))
    except Exception as ex:
        bus.toast.emit(f"Auto subtitles failed: {ex}")


# ---------------------------------------------------------------- overlay (all on-screen controls)
class Overlay(QWidget):
    def __init__(self, main):
        super().__init__(main, Qt.Tool | Qt.FramelessWindowHint)
        self.main = main
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAcceptDrops(True)
        self._rev_s = False
        self.flash_t = -10.0
        self.rec_state = ""
        self.tool = None
        self.collapsed = False
        self.ui_on = True
        self.mini = False
        self._press = None
        self._moved = False
        self._pan0 = (0.0, 0.0)
        self._click = QTimer(self)
        self._click.setSingleShot(True)
        self._click.timeout.connect(main.toggle_play)
        self._build()
        self.anim = QTimer(self)
        self.anim.timeout.connect(self._anim)
        self.anim.start(50)

    # ---------- build
    def _build(self):
        m = self.main
        # window buttons (top right)
        self.wc = QWidget(self)
        self.wc.setObjectName("wc")
        h = QHBoxLayout(self.wc)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(6)
        h.addWidget(mk("\u2014  Minimize", m.showMinimized))
        h.addWidget(mk("\u2750  Mini player", m.toggle_mini, tip="Mini player (P)"))
        h.addWidget(mk("\u2715  Close", m.close, name="close"))
        # side tools
        self.tools = QFrame(self)
        self.tools.setObjectName("tools")
        v = QVBoxLayout(self.tools)
        v.setContentsMargins(6, 6, 6, 6)
        v.setSpacing(6)
        self.tool_btns = {}
        for key, txt, tip in (("shot", "\U0001F4F7\nScreenshot", "Screenshot (S)"), ("rec", "\u23FA\nRecord", "Record (R)"),
                              ("zoom", "\U0001F50D\nZoom", "Zoom (Z)"), ("fx", "\U0001F3A8\nFilters", "Filters (E)"),
                              ("sub", "\U0001F4AC\nSubtitles", "Subtitles (C)")):
            b = mk(txt, lambda k=key: self.set_tool(k), tip=tip, w=68, h=52)
            b._extra = "font-size:10px;padding:2px"
            style_btn(b, False)
            self.tool_btns[key] = b
            v.addWidget(b)
        self.arrow = mk("\u203A", self.toggle_collapse, tip="Hide / show tools", w=24, h=36)
        self.arrow._extra = "padding:0;font-size:18px;background:rgba(0,0,0,170)"
        style_btn(self.arrow, False)
        # panel
        self.panel = QFrame(self)
        self.panel.setObjectName("panel")
        pv = QVBoxLayout(self.panel)
        pv.setContentsMargins(0, 4, 0, 4)
        self.stack = QStackedWidget()
        pv.addWidget(self.stack)
        self.pages = {}
        for key, fn in (("shot", self.page_shot), ("rec", self.page_rec), ("zoom", self.page_zoom),
                        ("fx", self.page_fx), ("sub", self.page_sub), ("audio", self.page_audio)):
            w = fn()
            self.pages[key] = w
            self.stack.addWidget(wrap_scroll(w))
        self.panel.hide()
        # bottom bar
        self.bar = QFrame(self)
        self.bar.setObjectName("bar")
        bv = QVBoxLayout(self.bar)
        bv.setContentsMargins(14, 22, 14, 10)
        bv.setSpacing(6)
        self.seek = sl(0, 1000, 0)
        self.seek.scrub.connect(lambda v: m.seek_frac(v / 1000))
        bv.addWidget(self.seek)
        row = QHBoxLayout()
        row.setSpacing(8)
        self.play = mk("\u25B6 Play", m.toggle_play, pri=True, w=96)
        row.addWidget(self.play)
        row.addWidget(mk("\u23EA 10", lambda: m.seek_rel(-10), tip="Back 10s"))
        row.addWidget(mk("10 \u23E9", lambda: m.seek_rel(10), tip="Forward 10s"))
        self.time = lab("0:00 / 0:00", "lb")
        row.addWidget(self.time)
        row.addStretch()
        self.extra = QWidget()
        eh = QHBoxLayout(self.extra)
        eh.setContentsMargins(0, 0, 0, 0)
        eh.setSpacing(8)
        self.mute = mk("\U0001F50A", m.toggle_mute, tip="Mute (M)", w=40)
        eh.addWidget(self.mute)
        eh.addWidget(lab("Volume", "lb"))
        self.vol = sl(0, 100, 100, m.set_volume)
        self.vol.setFixedWidth(90)
        eh.addWidget(self.vol)
        eh.addWidget(mk("\U0001F39A Audio", lambda: self.set_tool("audio"), tip="Audio settings (U)"))
        self.rev = mk("\u25C0 Reverse", m.toggle_rev, tip="Reverse play (J)")
        eh.addWidget(self.rev)
        row.addWidget(self.extra)
        bv.addLayout(row)
        self.extra2 = QWidget()
        e2 = QHBoxLayout(self.extra2)
        e2.setContentsMargins(0, 0, 0, 0)
        e2.setSpacing(8)
        e2.addWidget(lab("Speed", "lb"))
        self.speed = combo([("%g\u00D7" % s) + (" (Normal)" if s == 1 else "") for s in SPEEDS],
                           lambda i: m.set_speed(SPEEDS[i]), fit=True)
        self.speed.setCurrentIndex(SPEEDS.index(1))
        e2.addWidget(self.speed)
        e2.addWidget(lab("Screen", "lb"))
        self.fit = combo(FITS, m.set_fit, fit=True)
        e2.addWidget(self.fit)
        e2.addStretch()
        e2.addWidget(mk("Open", m.open_dialog, tip="Open (O)"))
        e2.addWidget(mk("\u26F6 Fullscreen", m.toggle_fullscreen, tip="Fullscreen (F)"))
        bv.addWidget(self.extra2)
        # hint, badge, toast
        self.hint = QWidget(self)
        hv = QVBoxLayout(self.hint)
        t = QLabel("Yashraj Player")
        t.setStyleSheet("font-size:26px;font-weight:600")
        t.setAlignment(Qt.AlignCenter)
        hv.addWidget(t)
        hv.addWidget(lab("Drop a video here, or press O", "dim"))
        hb = mk("Open file", m.open_dialog, pri=True)
        hv.addWidget(hb, 0, Qt.AlignCenter)
        self.badge = QLabel("\u25CF REC 00:00", self)
        self.badge.setObjectName("badge")
        self.badge.hide()
        self.toast = QLabel("", self)
        self.toast.setObjectName("toast")
        self.toast.setAlignment(Qt.AlignCenter)
        self.toast.hide()
        self._toast_timer = QTimer(self)
        self._toast_timer.setSingleShot(True)
        self._toast_timer.timeout.connect(self.toast.hide)

    # ---------- panel pages
    def _page(self):
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(12, 8, 12, 10)
        v.setSpacing(8)
        return w, v

    def _head(self, v, title, cb=None, btn="\u21BA Default"):
        h = QHBoxLayout()
        h.addWidget(lab(f"<b>{title}</b>"))
        h.addStretch()
        if cb:
            h.addWidget(mk(btn, cb))
        v.addLayout(h)

    def _rows(self, v, rows):
        g = QGridLayout()
        g.setHorizontalSpacing(8)
        for i, (name, w) in enumerate(rows):
            g.addWidget(lab(name, "lb"), i, 0)
            g.addWidget(w, i, 1)
        g.setColumnStretch(1, 1)
        v.addLayout(g)

    def _presets(self, v, names, cb):
        g = QGridLayout()
        d = {}
        for i, n in enumerate(names):
            b = mk(n, lambda n=n: cb(n))
            b._extra = "padding:5px 8px;font-size:12px"
            style_btn(b, False)
            d[n] = b
            g.addWidget(b, i // 3, i % 3)
        v.addLayout(g)
        return d

    def page_shot(self):
        w, v = self._page()
        self._head(v, "Screenshot")
        v.addWidget(mk("Take screenshot", self.main.screenshot, pri=True))
        self.shot_info = lab("Saved to Pictures\\Yashraj Player", "dim")
        v.addWidget(self.shot_info)
        v.addWidget(mk("Open folder", lambda: self.main.open_folder(PICS)))
        v.addStretch()
        return w

    def page_rec(self):
        w, v = self._page()
        self._head(v, "Recorder")
        self.rec_time = lab("00:00")
        self.rec_time.setStyleSheet("font-size:22px")
        v.addWidget(self.rec_time)
        h = QHBoxLayout()
        self.rb_start = mk("Start", self.main.rec_start, pri=True)
        self.rb_pause = mk("Pause", self.main.rec_pause)
        self.rb_stop = mk("Stop", self.main.rec_stop)
        for b in (self.rb_start, self.rb_pause, self.rb_stop):
            h.addWidget(b)
        v.addLayout(h)
        self.rec_info = lab("Clips are saved to Videos\\Yashraj Player. The saved clip is the original video, without filters or zoom.", "dim")
        v.addWidget(self.rec_info)
        v.addWidget(mk("Open folder", lambda: self.main.open_folder(VIDS)))
        v.addStretch()
        return w

    def page_zoom(self):
        w, v = self._page()
        self._head(v, "Zoom")
        h = QHBoxLayout()
        self.zoom_s = sl(100, 500, 100, lambda x: self.main.zoom_set(x / 100), Qt.Vertical)
        self.zoom_s.setFixedHeight(130)
        h.addWidget(self.zoom_s)
        c = QVBoxLayout()
        self.zoom_l = lab("1.0\u00D7")
        self.zoom_l.setStyleSheet("font-size:26px")
        c.addWidget(self.zoom_l)
        c.addWidget(mk("\uFF0B", lambda: self.main.zoom_step(1)))
        c.addWidget(mk("\uFF0D", lambda: self.main.zoom_step(-1)))
        c.addWidget(mk("Reset", lambda: self.main.zoom_set(1)))
        h.addLayout(c)
        v.addLayout(h)
        v.addWidget(lab("Drag the video to move it when zoomed. The mouse wheel also zooms.", "dim"))
        v.addStretch()
        return w

    def page_fx(self):
        w, v = self._page()
        self._head(v, "Filters", lambda: self.fx_preset("Blu-ray"))
        self.fx_btns = self._presets(v, list(FX_PRE), self.fx_preset)
        self.fx_s = [sl(60, 140, 102, self.fx_changed), sl(60, 160, 112, self.fx_changed),
                     sl(0, 200, 115, self.fx_changed), sl(0, 200, 80, self.fx_changed)]
        self._rows(v, list(zip(["Brightness", "Contrast", "Color", "Sharpness"], self.fx_s)))
        v.addWidget(lab("Default is the Blu-ray look. Original shows the video untouched.", "dim"))
        v.addStretch()
        return w

    def page_audio(self):
        w, v = self._page()
        self._head(v, "Audio", lambda: self.eq_preset("Normal"))
        self.eq_btns = self._presets(v, list(EQ_PRE), self.eq_preset)
        self.eq_s = [sl(-12, 12, 0, self.eq_changed) for _ in EQ_F] + [sl(100, 200, 100, self.eq_changed)]
        self._rows(v, list(zip(EQ_NAMES + ["Boost"], self.eq_s)))
        v.addWidget(lab("Boost above 100% can distort at high volume.", "dim"))
        v.addStretch()
        return w

    def page_sub(self):
        w, v = self._page()
        self._head(v, "Subtitles", self.main.sub_off, "Off")
        v.addWidget(mk("Load subtitle file", self.main.sub_load, pri=True))
        v.addWidget(mk("\u2728 Auto-generate with AI", self.auto_subs))
        self.sub_info = lab("No subtitles loaded.", "dim")
        v.addWidget(self.sub_info)
        self.sub_lang = combo([n for n, _ in LANGS])
        self.sub_tr = combo(["No translation", "Translate to English"])
        self.sub_model = combo([n for n, _ in MODELS])
        self._rows(v, [("Speech", self.sub_lang), ("Translate", self.sub_tr), ("AI model", self.sub_model)])
        self.ss_size = sl(50, 200, 100, self.sub_changed)
        self.ss_delay = sl(-100, 100, 0, self.sub_changed)
        self.ss_color = combo([n for n, _ in SUB_COLORS], lambda i: self.sub_changed())
        self.ss_box = combo(["Dark box", "Outline only"], lambda i: self.sub_changed())
        self.ss_pos = sl(0, 40, 6, self.sub_changed)
        self.ss_dl = lab("0.0s", "lb")
        self._rows(v, [("Size", self.ss_size), ("Delay", self.ss_delay), ("", self.ss_dl), ("Color", self.ss_color),
                       ("Box", self.ss_box), ("Height", self.ss_pos)])
        v.addWidget(lab("Load an .srt/.vtt/.ass file, or let the built-in AI write subtitles (works offline).", "dim"))
        v.addStretch()
        return w

    # ---------- panel logic
    def fx_vals(self):
        s = self.fx_s
        return s[0].value() / 100, s[1].value() / 100, s[2].value() / 100, s[3].value() / 100

    def apply_fx(self):
        if self.main.eng:
            self.main.eng.set_filters(*self.fx_vals())

    def fx_preset(self, name):
        for s, val in zip(self.fx_s, FX_PRE[name]):
            s.blockSignals(True)
            s.setValue(int(round(val * 100)))
            s.blockSignals(False)
        mark(self.fx_btns, name)
        self.apply_fx()

    def fx_changed(self, _=None):
        mark(self.fx_btns, None)
        self.apply_fx()

    def apply_eq(self):
        if self.main.eng:
            vals = [s.value() for s in self.eq_s]
            self.main.eng.set_eq(vals[:5], vals[5] / 100)

    def eq_preset(self, name):
        for s, val in zip(self.eq_s, EQ_PRE[name]):
            s.blockSignals(True)
            s.setValue(int(round(val * 100)) if s is self.eq_s[5] else int(val))
            s.blockSignals(False)
        mark(self.eq_btns, name)
        self.apply_eq()

    def eq_changed(self, _=None):
        mark(self.eq_btns, None)
        self.apply_eq()

    def sub_changed(self, _=None):
        self.ss_dl.setText(f"{self.ss_delay.value() / 10:+.1f}s")
        if self.main.eng:
            self.main.eng.sub_style(self.ss_size.value() / 100, self.ss_delay.value() / 10,
                                    SUB_COLORS[self.ss_color.currentIndex()][1], self.ss_box.currentIndex() == 0,
                                    100 - self.ss_pos.value())

    def auto_subs(self):
        self.main.auto_subs(LANGS[self.sub_lang.currentIndex()][1], self.sub_tr.currentIndex() == 1,
                            MODELS[self.sub_model.currentIndex()][1])

    # ---------- tool open/close, collapse
    def set_tool(self, key):
        self.tool = None if self.tool == key else key
        if self.tool:
            self.stack.setCurrentIndex(list(self.pages).index(self.tool))
        for k, b in self.tool_btns.items():
            style_btn(b, k == self.tool)
        self.panel.setVisible(bool(self.tool) and self.ui_on and not self.mini)
        self.relayout()

    def toggle_collapse(self):
        self.collapsed = not self.collapsed
        self.arrow.setText("\u2039" if self.collapsed else "\u203A")
        if self.collapsed and self.tool:
            self.set_tool(self.tool)
        w, h = self.width(), self.height()
        x_open, x_closed = w - 24 - 4 - 72, w + 4
        self.tools.show()
        a = QPropertyAnimation(self.tools, b"pos", self)
        a.setDuration(250)
        a.setEasingCurve(QEasingCurve.OutCubic)
        a.setStartValue(self.tools.pos())
        a.setEndValue(QPoint(x_closed if self.collapsed else x_open, self.tools.y()))
        a.finished.connect(lambda: self.tools.setVisible(not self.collapsed))
        self._pa = a
        a.start()

    def show_ui(self, on):
        self.ui_on = on
        self.bar.setVisible(on)
        self.wc.setVisible(on)
        self.arrow.setVisible(on and not self.mini)
        self.tools.setVisible(on and not self.collapsed and not self.mini)
        self.panel.setVisible(on and bool(self.tool) and not self.mini)
        if on:
            self.unsetCursor()
        else:
            self.setCursor(Qt.BlankCursor)

    def set_mini(self, mini):
        self.mini = mini
        self.extra.setVisible(not mini)
        self.extra2.setVisible(not mini)
        self.show_ui(True)
        self.relayout()

    def relayout(self):
        w, h = self.width(), self.height()
        bh = self.bar.sizeHint().height()
        self.bar.setGeometry(0, h - bh, w, bh)
        self.wc.adjustSize()
        self.wc.move(w - self.wc.width() - 8, 8)
        th = self.tools.sizeHint().height()
        ty = max(52, (h - th) // 2 - 20)
        self.arrow.move(w - 24, ty)
        pa = getattr(self, "_pa", None)
        if not (pa and pa.state() == QAbstractAnimation.State.Running):
            self.tools.setGeometry(w + 4 if self.collapsed else w - 24 - 4 - 72, ty, 72, th)
        if self.tool:
            page = self.pages[self.tool]
            ph = min(page.sizeHint().height() + 14, max(120, h - 52 - bh - 12))
            px = w - 24 - 4 - 72 - 8 - 290
            self.panel.setGeometry(max(8, px), 52, 290, ph)
        hs = self.hint.sizeHint()
        self.hint.setGeometry((w - hs.width()) // 2, (h - hs.height()) // 2 - 30, hs.width(), hs.height())
        self.badge.adjustSize()
        self.badge.move(14, 14)
        self._place_toast()

    def _place_toast(self):
        self.toast.setMaximumWidth(max(200, self.width() - 40))
        self.toast.adjustSize()
        self.toast.move((self.width() - self.toast.width()) // 2, self.height() - self.bar.height() - self.toast.height() - 12)

    def say(self, msg):
        self.toast.setText(msg)
        self._place_toast()
        self.toast.show()
        self.toast.raise_()
        self._toast_timer.start(3500)

    def flash(self):
        self.flash_t = time.time()

    def _anim(self):
        if self.rec_state or time.time() - self.flash_t < 1.1:
            self.update()

    # ---------- state from the poll loop
    def update_state(self, pos, dur, paused, loaded, rev):
        self.hint.setVisible(not loaded)
        self.time.setText(f"{fmt(pos)} / {fmt(dur)}")
        if dur and pos is not None and not self.seek.drag:
            self.seek.blockSignals(True)
            self.seek.setValue(int(pos / dur * 1000))
            self.seek.blockSignals(False)
        self.play.setText("\u25B6 Play" if ((paused or not loaded) and not rev) else "\u23F8 Pause")
        if rev != self._rev_s:
            self._rev_s = rev
            style_btn(self.rev, rev)

    # ---------- painting and mouse
    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0, 0, 0, 1))  # almost invisible, but keeps the mouse working
        now = time.time()
        col = None
        if self.rec_state == "rec":
            col = QColor(239, 71, 111, 255 if ((now % 1.2) / 1.2) < 0.55 else 0)
        elif self.rec_state == "paused":
            col = QColor(239, 71, 111, 230)
        ft = now - self.flash_t
        if ft < 1.0:
            col = QColor(255, 159, 28, int(255 * (1 if ft < 0.4 else 1 - (ft - 0.4) / 0.6)))
        if col is not None and col.alpha() > 0:
            p.setPen(QPen(col, 7))
            p.drawRect(self.rect().adjusted(3, 3, -4, -4))

    def resizeEvent(self, e):
        self.relayout()

    def _edges(self, pos):
        m = self.main
        if m.isFullScreen() or m.mini or m.isMaximized():
            return []
        x, y, w, h, g = pos.x(), pos.y(), self.width(), self.height(), 6
        ed = []
        if x < g:
            ed.append(Qt.LeftEdge)
        if x > w - g:
            ed.append(Qt.RightEdge)
        if y < g:
            ed.append(Qt.TopEdge)
        if y > h - g:
            ed.append(Qt.BottomEdge)
        return ed

    def mousePressEvent(self, e):
        self.setFocus()
        if e.button() == Qt.LeftButton:
            ed = self._edges(e.position().toPoint())
            if ed:
                self.main.windowHandle().startSystemResize(reduce(or_, ed))
                return
            self._press = e.globalPosition().toPoint()
            self._moved = False
            self._pan0 = (self.main.pan_x, self.main.pan_y)

    def mouseMoveEvent(self, e):
        m = self.main
        if self._press is not None and (e.buttons() & Qt.LeftButton):
            d = e.globalPosition().toPoint() - self._press
            if not self._moved and d.manhattanLength() > 6:
                self._moved = True
                if m.zoom <= 1 and not m.isFullScreen() and not m.mini:
                    self._press = None
                    m.windowHandle().startSystemMove()
                    return
            if self._moved and m.zoom > 1:
                m.pan_to(self._pan0[0] + d.x() / max(1, self.width()), self._pan0[1] + d.y() / max(1, self.height()))
            return
        ed = self._edges(e.position().toPoint())
        if ed:
            s = set(ed)
            if s in ({Qt.LeftEdge}, {Qt.RightEdge}):
                self.setCursor(Qt.SizeHorCursor)
            elif s in ({Qt.TopEdge}, {Qt.BottomEdge}):
                self.setCursor(Qt.SizeVerCursor)
            elif s in ({Qt.LeftEdge, Qt.TopEdge}, {Qt.RightEdge, Qt.BottomEdge}):
                self.setCursor(Qt.SizeFDiagCursor)
            else:
                self.setCursor(Qt.SizeBDiagCursor)
        elif self.ui_on:
            self.unsetCursor()

    def mouseReleaseEvent(self, e):
        if self._press is not None and not self._moved and e.button() == Qt.LeftButton:
            self._click.start(260)
        self._press = None

    def mouseDoubleClickEvent(self, e):
        self._click.stop()
        self.main.toggle_fullscreen()

    def wheelEvent(self, e):
        self.main.zoom_step(1 if e.angleDelta().y() > 0 else -1)

    def keyPressEvent(self, e):
        self.main.handle_key(e)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        for u in e.mimeData().urls():
            if u.isLocalFile():
                self.main.open(u.toLocalFile())
                break


# ---------------------------------------------------------------- main window
class Main(QMainWindow):
    def __init__(self, path=None):
        super().__init__()
        self.setWindowTitle(APP)
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.resize(1100, 650)
        self.setMinimumSize(360, 220)
        self.video = QWidget()
        self.video.setAttribute(Qt.WA_NativeWindow)
        self.video.setStyleSheet("background:#000")
        self.setCentralWidget(self.video)
        self.setAcceptDrops(True)
        self.eng = None
        self.start_path = path
        self.zoom, self.pan_x, self.pan_y = 1.0, 0.0, 0.0
        self.mini, self._normal_geo = False, None
        self.muted = False
        self.rev_on, self.rev_step = False, False
        self._open_t, self._warned = 0.0, True
        self.segs, self.seg_start, self.rec_t0, self.rec_acc = [], None, 0.0, 0.0
        self.bus = Bus()
        self.ov = Overlay(self)
        self.bus.toast.connect(self.ov.say)
        self.bus.sub_ready.connect(self._sub_ready)
        self.bus.rec_saved.connect(lambda p: self.ov.rec_info.setText("Last clip: " + p))
        self.last_cursor, self.last_move = QCursor.pos(), time.time()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(100)
        QTimer.singleShot(50, self._init_engine)

    # ---------- startup
    def _init_engine(self):
        if mpv is None:
            QMessageBox.critical(self, APP, "The video engine (libmpv-2.dll) could not be loaded.\n\n" + str(MPV_ERR))
            QApplication.quit()
            return
        try:
            self.eng = Engine(int(self.video.winId()), lambda msg: self.bus.toast.emit(msg))
        except Exception as ex:
            QMessageBox.critical(self, APP, "The video engine could not start.\n\n" + str(ex))
            QApplication.quit()
            return
        self.ov.fx_preset("Blu-ray")
        self.ov.eq_preset("Normal")
        self.ov.sub_changed()
        self.eng.set_fit(0)
        if self.start_path:
            self.open(self.start_path)

    def showEvent(self, e):
        super().showEvent(e)
        if hasattr(self, "ov"):
            self.sync_overlay()
            self.ov.show()

    def sync_overlay(self):
        if not hasattr(self, "ov"):
            return
        g = self.video.mapToGlobal(QPoint(0, 0))
        self.ov.setGeometry(QRect(g, self.video.size()))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.sync_overlay()

    def moveEvent(self, e):
        super().moveEvent(e)
        self.sync_overlay()

    def changeEvent(self, e):
        super().changeEvent(e)
        if not hasattr(self, "ov"):
            return
        vis = (not self.isMinimized()) and self.isVisible()
        if self.ov.isVisible() != vis:
            self.ov.setVisible(vis)
        self.sync_overlay()

    def closeEvent(self, e):
        try:
            self.ov.hide()
            self.hide()
        except Exception:
            pass
        os._exit(0)  # leave at once: waiting for the video engine to stop can hang and leave a ghost window

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        self.ov.dropEvent(e)

    def keyPressEvent(self, e):
        self.handle_key(e)

    # ---------- poll loop
    def tick(self):
        cp = QCursor.pos()
        if cp != self.last_cursor:
            self.last_cursor, self.last_move = cp, time.time()
            if not self.ov.ui_on:
                self.ov.show_ui(True)
        e = self.eng
        if not e:
            return
        pos, dur = e.prop("time-pos"), e.prop("duration")
        paused = bool(e.prop("pause", True))
        loaded = bool(e.cur)
        if (loaded and not self._warned and time.time() - self._open_t > 2.0 and e.vals.get("idle-active") is True):
            self._warned = True
            self.ov.say("This file could not be played. Press I for details.")
        if self.rev_on and pos is not None and pos <= 0.2:
            self.toggle_rev()
        elif self.rev_step and pos is not None:
            e.cmd("seek", -self.cur_speed() * 0.1, "relative+keyframes")
        self.ov.update_state(pos, dur, paused, loaded, self.rev_on)
        if self.ov.rec_state:
            secs = self.rec_acc + (time.time() - self.rec_t0 if self.ov.rec_state == "rec" else 0)
            txt = f"{int(secs // 60):02d}:{int(secs % 60):02d}"
            self.ov.rec_time.setText(txt)
            self.ov.badge.setText(f"\u25CF REC {txt}")
            self.ov.badge.adjustSize()
        playing = loaded and (not paused or self.rev_on)
        busy = any(w.underMouse() for w in (self.ov.bar, self.ov.tools, self.ov.panel))
        if playing and not busy and self.ov.ui_on and time.time() - self.last_move > 2.5 and not self.ov.tool:
            self.ov.show_ui(False)

    def cur_speed(self):
        return SPEEDS[self.ov.speed.currentIndex()]

    # ---------- playback
    def open_dialog(self):
        f, _ = QFileDialog.getOpenFileName(self, "Open video", str(Path.home() / "Videos"), MEDIA_FILTER)
        if f:
            self.open(f)

    def open(self, path):
        if not self.eng:
            self.start_path = path
            return
        if self.rev_on:
            self.toggle_rev()
        self.eng.open(path)
        self._open_t, self._warned = time.time(), False
        self.setWindowTitle(f"{Path(path).name} - {APP}")
        self.zoom_set(1)
        self.ov.sub_info.setText("No subtitles loaded.")
        self.ov.show_ui(True)

    def toggle_play(self):
        if not (self.eng and self.eng.cur):
            return
        if self.rev_on:
            self.toggle_rev()
            self.eng.setp("pause", "yes")
            return
        self.eng.setp("pause", "no" if self.eng.prop("pause", False) else "yes")

    def seek_rel(self, s):
        if self.eng and self.eng.cur:
            self.eng.cmd("seek", s, "relative+exact")

    def seek_frac(self, f):
        if self.eng and self.eng.cur:
            self.eng.cmd("seek", f * 100, "absolute-percent")

    def set_volume(self, v):
        if self.eng:
            self.eng.setp("volume", v)

    def toggle_mute(self):
        self.muted = not self.muted
        if self.eng:
            self.eng.setp("mute", "yes" if self.muted else "no")
        self.ov.mute.setText("\U0001F507" if self.muted else "\U0001F50A")

    def set_speed(self, r):
        if self.eng:
            self.eng.setp("speed", float(r))
            self.ov.say(f"Speed {r:g}\u00D7")

    def step_speed(self, d):
        i = max(0, min(len(SPEEDS) - 1, self.ov.speed.currentIndex() + d))
        self.ov.speed.setCurrentIndex(i)

    def toggle_rev(self):
        if not (self.eng and self.eng.cur):
            return
        if not self.rev_on:
            self.rev_on = True
            if self.eng.setp("play-direction", "-"):
                self.rev_step = False
            else:  # older mpv: step backwards with seeks
                self.rev_step = True
            self.eng.setp("pause", "yes" if self.rev_step else "no")
            self.ov.say(f"\u25C0\u25C0 Reverse {self.cur_speed():g}\u00D7")
        else:
            self.rev_on, self.rev_step = False, False
            self.eng.setp("play-direction", "+")
            self.eng.setp("pause", "no")

    def set_fit(self, i):
        if self.eng:
            self.eng.set_fit(i)

    # ---------- zoom
    def zoom_set(self, z):
        self.zoom = max(1.0, min(5.0, z))
        if self.zoom <= 1:
            self.pan_x = self.pan_y = 0.0
        self.ov.zoom_s.blockSignals(True)
        self.ov.zoom_s.setValue(int(round(self.zoom * 100)))
        self.ov.zoom_s.blockSignals(False)
        self.ov.zoom_l.setText(f"{self.zoom:.1f}\u00D7")
        if self.eng:
            self.eng.set_zoom(self.zoom, self.pan_x, self.pan_y)

    def zoom_step(self, d):
        self.zoom_set(self.zoom + 0.15 * d)

    def pan_to(self, x, y):
        self.pan_x, self.pan_y = max(-1.5, min(1.5, x)), max(-1.5, min(1.5, y))
        if self.eng:
            self.eng.set_zoom(self.zoom, self.pan_x, self.pan_y)

    # ---------- window actions
    def toggle_fullscreen(self):
        if self.mini:
            self.toggle_mini()
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _topmost(self, on):
        if os.name == "nt":
            try:
                import ctypes
                ctypes.windll.user32.SetWindowPos(int(self.winId()), -1 if on else -2, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0010)
            except Exception:
                pass

    def toggle_mini(self):
        if self.isFullScreen():
            self.showNormal()
        if not self.mini:
            self._normal_geo = self.geometry()
            self.mini = True
            scr = QApplication.primaryScreen().availableGeometry()
            self.setGeometry(scr.right() - 500, scr.bottom() - 300, 480, 270)
            self._topmost(True)
        else:
            self.mini = False
            self._topmost(False)
            if self._normal_geo:
                self.setGeometry(self._normal_geo)
        self.ov.set_mini(self.mini)

    def open_folder(self, p):
        try:
            Path(p).mkdir(parents=True, exist_ok=True)
            os.startfile(str(p))
        except Exception:
            pass

    # ---------- screenshot / recording
    def screenshot(self):
        if not (self.eng and self.eng.cur):
            return self.ov.say("Open a video first.")
        f = self.eng.screenshot()
        self.ov.flash()
        if f:
            self.ov.shot_info.setText("Saved: " + str(f))
            self.ov.say("Screenshot saved: " + f.name)
        else:
            self.ov.say("Could not save the screenshot.")

    def _seg_end(self):
        p = self.eng.prop("time-pos")
        if p is not None and p > self.seg_start:
            return p
        return self.seg_start + (time.time() - self.rec_t0) * self.cur_speed()

    def rec_start(self):
        if not (self.eng and self.eng.cur) or self.ov.rec_state:
            return
        self.segs, self.rec_acc = [], 0.0
        self.seg_start = float(self.eng.prop("time-pos", 0.0))
        self.rec_t0 = time.time()
        self.ov.rec_state = "rec"
        self.ov.badge.show()
        self.eng.setp("pause", "no")

    def rec_pause(self):
        if self.ov.rec_state == "rec":
            self.segs.append((self.seg_start, self._seg_end()))
            self.rec_acc += time.time() - self.rec_t0
            self.ov.rec_state = "paused"
            self.ov.rb_pause.setText("Resume")
        elif self.ov.rec_state == "paused":
            self.seg_start = self.eng.prop("time-pos", 0.0)
            self.rec_t0 = time.time()
            self.ov.rec_state = "rec"
            self.ov.rb_pause.setText("Pause")

    def rec_stop(self):
        if not self.ov.rec_state:
            return
        if self.ov.rec_state == "rec":
            self.segs.append((self.seg_start, self._seg_end()))
        self.ov.rec_state = ""
        self.ov.badge.hide()
        self.ov.rb_pause.setText("Pause")
        self.ov.update()
        self.ov.say("Saving the recording...")
        threading.Thread(target=record_job, args=(self.eng.cur, list(self.segs), self.bus), daemon=True).start()

    # ---------- subtitles
    def sub_load(self):
        f, _ = QFileDialog.getOpenFileName(self, "Open subtitles", str(Path(self.eng.cur).parent if self.eng and self.eng.cur else Path.home()),
                                           "Subtitles (*.srt *.vtt *.ass *.ssa *.sub);;All files (*.*)")
        if f:
            self._sub_ready(f)

    def _sub_ready(self, path):
        if self.eng and self.eng.cur:
            self.eng.cmd("sub-add", path, "select")
            self.ov.sub_info.setText("Loaded: " + Path(path).name)
            self.ov.say("Subtitles ready: " + Path(path).name)

    def sub_off(self):
        if self.eng:
            self.eng.setp("sid", "no")
        self.ov.sub_info.setText("Subtitles off.")

    def auto_subs(self, lang, translate, model_file):
        if not (self.eng and self.eng.cur):
            return self.ov.say("Open a video first.")
        threading.Thread(target=whisper_job, args=(self.eng.cur, lang, translate, model_file, self.bus), daemon=True).start()

    def show_info(self):
        if not self.eng:
            return
        g = self.eng.prop
        txt = (f"File: {Path(self.eng.cur).name if self.eng.cur else '-'}\n"
               f"Position {g('time-pos')}  Duration {g('duration')}  Paused {g('pause')}\n"
               f"Video {g('video-codec')}  Audio {g('audio-codec-name')}  Format {g('file-format')}\n"
               f"Decoder {g('hwdec-current')}  Output {g('current-vo')}\n"
               f"Log: %LOCALAPPDATA%\\YashrajPlayer\\mpv.log")
        self.ov.say(txt)

    # ---------- keyboard
    def handle_key(self, e):
        k, ov = e.key(), self.ov
        if k == Qt.Key_Space:
            self.toggle_play()
        elif k == Qt.Key_Left:
            self.seek_rel(-10)
        elif k == Qt.Key_Right:
            self.seek_rel(10)
        elif k in (Qt.Key_Up, Qt.Key_Down):
            v = max(0, min(100, ov.vol.value() + (5 if k == Qt.Key_Up else -5)))
            ov.vol.setValue(v)
        elif k == Qt.Key_F:
            self.toggle_fullscreen()
        elif k == Qt.Key_Escape:
            if self.isFullScreen():
                self.showNormal()
        elif k == Qt.Key_M:
            self.toggle_mute()
        elif k == Qt.Key_O:
            self.open_dialog()
        elif k == Qt.Key_S:
            self.screenshot()
        elif k == Qt.Key_R:
            ov.set_tool("rec")
        elif k == Qt.Key_Z:
            ov.set_tool("zoom")
        elif k == Qt.Key_E:
            ov.set_tool("fx")
        elif k == Qt.Key_U:
            ov.set_tool("audio")
        elif k == Qt.Key_C:
            ov.set_tool("sub")
        elif k == Qt.Key_A:
            ov.fit.setCurrentIndex((ov.fit.currentIndex() + 1) % len(FITS))
        elif k == Qt.Key_J:
            self.toggle_rev()
        elif k == Qt.Key_BracketRight:
            self.step_speed(1)
        elif k == Qt.Key_BracketLeft:
            self.step_speed(-1)
        elif k == Qt.Key_P:
            self.toggle_mini()
        elif k == Qt.Key_I:
            self.show_info()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP)
    app.setStyleSheet(QSS)
    try:
        import locale
        locale.setlocale(locale.LC_NUMERIC, "C")  # libmpv needs this
    except Exception:
        pass
    w = Main(sys.argv[1] if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) else None)
    w.show()
    code = app.exec()
    os._exit(code)


if __name__ == "__main__":
    main()
