import os
import sys
import random
import tkinter as tk
from datetime import date
import math
import pyfiglet

# Optional VLC import — graceful fallback if not installed
try:
    import vlc
    VLC_AVAILABLE = True
except ImportError:
    VLC_AVAILABLE = False
    print("Warning: python-vlc not found. Video and music playback disabled.")

# ══════════════════════════════════════════════════════════════
# Configuration  ← edit here
# ══════════════════════════════════════════════════════════════
BIRTHDAY_NAME    = "SAMUEL"
DATE_OF_BIRTH    = date(2000, 3, 24)           # 29-03-2000 → date(YYYY, MM, DD)

IMAGE_FILES      = ["aa.jpg", "bb.jpg", "cc.jpg"]
VIDEO_FILE       = "Rayvanny_Happy Birthday.mp4"
MUSIC_FILE       = "Rayvanny_Happy Birthday.mp3"
COUNTDOWN_START  = 5
IMAGE_DISPLAY_MS = 2000
TEXT_DISPLAY_MS  = 2000
WINDOW_SIZE      = "960x640"
CONFETTI_COUNT   = 120
CONFETTI_COLORS  = ["red", "gold", "green", "deepskyblue", "purple", "orange", "hotpink"]

# Sequence stage constants
STAGE_COUNTDOWN  = 1
STAGE_HAPPY_BDAY = 2
STAGE_NAME       = 3
STAGE_SLIDESHOW  = 4
STAGE_VIDEO      = 5
STAGE_FINALE     = 6


# ══════════════════════════════════════════════════════════════
# Birthday maths
# ══════════════════════════════════════════════════════════════

def birthday_stats(dob: date) -> dict:
    """
    Return a dict with:
      is_today      – True if today is the birthday
      next_birthday – date of next (or current) birthday
      days_to       – int days until next birthday (0 if today)
      turning       – age they will be on next birthday
      age_years     – completed years as of today
      age_months    – total completed months from dob to today
      age_weeks     – total completed weeks from dob to today
      age_days      – total days from dob to today
      age_hours     – approx total hours
      age_seconds   – approx total seconds
    """
    today = date.today()

    # Next (or current) birthday
    try:
        this_year_bday = dob.replace(year=today.year)
    except ValueError:
        # Feb 29 on non-leap year → Mar 1
        this_year_bday = date(today.year, 3, 1)

    if this_year_bday >= today:
        next_bday = this_year_bday
        turning   = today.year - dob.year
    else:
        try:
            next_bday = dob.replace(year=today.year + 1)
        except ValueError:
            next_bday = date(today.year + 1, 3, 1)
        turning = today.year + 1 - dob.year

    days_to  = (next_bday - today).days
    is_today = days_to == 0

    total_days    = (today - dob).days
    total_weeks   = total_days // 7
    total_hours   = total_days * 24
    total_seconds = total_days * 86400

    months = (today.year - dob.year) * 12 + (today.month - dob.month)
    if today.day < dob.day:
        months -= 1

    years = today.year - dob.year
    if (today.month, today.day) < (dob.month, dob.day):
        years -= 1

    return {
        "is_today":      is_today,
        "next_birthday": next_bday,
        "days_to":       days_to,
        "turning":       turning,
        "age_years":     years,
        "age_months":    months,
        "age_weeks":     total_weeks,
        "age_days":      total_days,
        "age_hours":     total_hours,
        "age_seconds":   total_seconds,
    }


def fmt(n: int) -> str:
    """Format a large integer with comma separators."""
    return f"{n:,}"


# ══════════════════════════════════════════════════════════════
# File validation
# ══════════════════════════════════════════════════════════════

def check_files(files: list) -> set:
    missing = {f for f in files if not os.path.exists(f)}
    if missing:
        print("Warning: missing files (will be skipped):")
        for m in sorted(missing):
            print(f"  - {m}")
    return missing


# ══════════════════════════════════════════════════════════════
# Image helper
# ══════════════════════════════════════════════════════════════

try:
    from PIL import Image, ImageTk

    def fit_image(path: str, max_w: int, max_h: int):
        img = Image.open(path)
        img.thumbnail((max_w, max_h), Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    def fit_image(path, max_w, max_h):
        raise RuntimeError("Pillow not installed")


def platform_set_video_window(player, widget):
    wid = widget.winfo_id()
    if sys.platform.startswith("win"):
        player.set_hwnd(wid)
    elif sys.platform == "darwin":
        player.set_nsobject(wid)
    else:
        player.set_xwindow(wid)


# ══════════════════════════════════════════════════════════════
# Pre-birthday Waiting Screen
# ══════════════════════════════════════════════════════════════

class WaitingScreen:
    """
    Shown when today is NOT the birthday.
    Animated night-sky canvas with pulsing countdown and
    interactive stat cards the user can click through.
    """

    STAR_COUNT  = 60
    FLOAT_ITEMS = ["🎂", "🎁", "🎈", "🎊", "🎉"]

    def __init__(self, root: tk.Tk, stats: dict):
        self.root   = root
        self.stats  = stats

        self.root.title(f"Birthday Countdown — {BIRTHDAY_NAME}")
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(bg="#0a0a1a")
        self.root.resizable(True, True)

        self._after_ids   = []
        self._stars       = []
        self._sparkles    = []
        self._float_items = []
        self._tick        = 0

        # Cycling stat cards
        self._stat_labels = [
            ("Current age",  f"{stats['age_years']} years"),
            ("Months lived", fmt(stats['age_months'])),
            ("Weeks lived",  fmt(stats['age_weeks'])),
            ("Days lived",   fmt(stats['age_days'])),
            ("Hours lived",  fmt(stats['age_hours'])),
            ("Seconds lived",fmt(stats['age_seconds'])),
        ]
        self._stat_idx  = 0
        self._card_ids  = []   # list of (bg, lbl, val) tuples

        self._build_ui()
        # Defer animated elements until the window has actually rendered
        self.root.after(100, self._init_animated_elements)
        self.root.after(150, self._animate)

    def _init_animated_elements(self):
        self._make_stars()
        self._make_floats()
        self._layout()

    def _build_ui(self):
        s = self.stats

        self.canvas = tk.Canvas(self.root, bg="#0a0a1a", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.root.update_idletasks()  # flush geometry so winfo_* returns real values

        # Title
        self.title_id = self.canvas.create_text(
            0, 0, text=f"✨  {BIRTHDAY_NAME}'s Birthday Countdown  ✨",
            fill="#ffe066", font=("Courier", 20, "bold"), anchor="n"
        )

        # Next birthday line
        next_str = s["next_birthday"].strftime("%B %d, %Y")
        self.sub_id = self.canvas.create_text(
            0, 0, text=f"{next_str}  —  turning {s['turning']}",
            fill="#9090cc", font=("Courier", 13), anchor="n"
        )

        # Big pulsing day counter
        self.big_num_id = self.canvas.create_text(
            0, 0, text=str(s["days_to"]),
            fill="#ff6eb4", font=("Courier", 80, "bold"), anchor="center"
        )
        self.big_lbl_id = self.canvas.create_text(
            0, 0, text="days to go",
            fill="#cc88aa", font=("Courier", 15), anchor="n"
        )

        # Hint
        self.hint_id = self.canvas.create_text(
            0, 0, text="Click any card to cycle through stats  •  Esc to quit",
            fill="#444466", font=("Courier", 10), anchor="s"
        )

        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<Configure>", self._on_resize)

    def _make_stars(self):
        w = max(self.root.winfo_width(),  200)
        h = max(self.root.winfo_height(), 300)
        for _ in range(self.STAR_COUNT):
            x = random.randint(0, w)
            y = random.randint(0, h)
            r = random.uniform(0.8, 2.5)
            phase = random.uniform(0, 6.28)
            sid = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="#ffffff", outline="")
            self._stars.append({"id": sid, "phase": phase})

    def _make_floats(self):
        w = max(self.root.winfo_width(),  200)
        h = max(self.root.winfo_height(), 300)
        for _ in range(8):
            x  = random.randint(40, max(41, w - 40))
            y  = random.randint(40, max(41, h - 40))
            sym = random.choice(self.FLOAT_ITEMS)
            fid = self.canvas.create_text(x, y, text=sym, font=("Arial", 18), fill="#ffffff")
            self._float_items.append({
                "id": fid, "x": x, "y": y,
                "dx": random.uniform(-0.4, 0.4),
                "dy": random.uniform(-0.3, 0.3),
            })

    def _make_cards(self):
        for ids in self._card_ids:
            for cid in ids:
                self.canvas.delete(cid)
        self._card_ids = []

        w  = self.root.winfo_width()  or 960
        h  = self.root.winfo_height() or 640
        n  = 4
        cw, ch = 170, 78
        gap   = 18
        total = n * cw + (n - 1) * gap
        sx    = (w - total) // 2
        cy    = int(h * 0.80)

        for i in range(n):
            idx        = (self._stat_idx + i) % len(self._stat_labels)
            label, val = self._stat_labels[idx]
            cx         = sx + i * (cw + gap)

            bg  = self.canvas.create_rectangle(
                cx, cy - ch//2, cx + cw, cy + ch//2,
                fill="#1a1a3a", outline="#3333aa", width=1
            )
            lbl = self.canvas.create_text(
                cx + cw//2, cy - 14,
                text=label, fill="#7777bb",
                font=("Courier", 10), anchor="center"
            )
            val_id = self.canvas.create_text(
                cx + cw//2, cy + 12,
                text=val, fill="#ffdd88",
                font=("Courier", 13, "bold"), anchor="center"
            )
            ids = (bg, lbl, val_id)
            self._card_ids.append(ids)

            for cid in ids:
                self.canvas.tag_bind(cid, "<Button-1>", self._on_card_click)
                self.canvas.tag_bind(cid, "<Enter>",
                    lambda e, b=bg: self.canvas.itemconfig(b, fill="#252550", outline="#6666ff"))
                self.canvas.tag_bind(cid, "<Leave>",
                    lambda e, b=bg: self.canvas.itemconfig(b, fill="#1a1a3a", outline="#3333aa"))

    def _on_card_click(self, event):
        self._stat_idx = (self._stat_idx + 1) % len(self._stat_labels)
        self._make_cards()

    def _layout(self):
        w = self.root.winfo_width()  or 960
        h = self.root.winfo_height() or 640
        cx = w // 2

        self.canvas.coords(self.title_id,   cx, 28)
        self.canvas.coords(self.sub_id,     cx, 62)
        self.canvas.coords(self.big_num_id, cx, int(h * 0.37))
        self.canvas.coords(self.big_lbl_id, cx, int(h * 0.37) + 50)
        self.canvas.coords(self.hint_id,    cx, h - 10)
        self._make_cards()

    def _on_resize(self, event=None):
        self._layout()

    def _animate(self):
        self._tick += 1
        t = self._tick

        # Twinkle stars
        for i, star in enumerate(self._stars):
            a     = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(star["phase"] + t * 0.055))
            grey  = int(a * 255)
            self.canvas.itemconfig(star["id"], fill=f"#{grey:02x}{grey:02x}{grey:02x}")

        # Pulse big counter colour
        r = int(200 + 55  * abs(math.sin(t * 0.04)))
        g = int(80  + 30  * abs(math.sin(t * 0.04 + 1.0)))
        b = int(140 + 60  * abs(math.sin(t * 0.04 + 2.0)))
        self.canvas.itemconfig(self.big_num_id, fill=f"#{r:02x}{g:02x}{b:02x}")

        # Drift emoji floats
        w = self.root.winfo_width()  or 960
        h = self.root.winfo_height() or 640
        for fi in self._float_items:
            fi["x"] += fi["dx"]
            fi["y"] += fi["dy"]
            if fi["x"] < 20 or fi["x"] > w - 20:
                fi["dx"] *= -1
            if fi["y"] < 60 or fi["y"] > h - 60:
                fi["dy"] *= -1
            self.canvas.coords(fi["id"], fi["x"], fi["y"])

        # Occasional sparkle
        if t % 35 == 0:
            for _ in range(5):
                x  = random.randint(0, w)
                y  = random.randint(0, h)
                r2 = random.uniform(1.5, 4)
                ml = random.randint(8, 20)
                sid = self.canvas.create_oval(x-r2, y-r2, x+r2, y+r2, fill="#ddddff", outline="")
                self._sparkles.append({"id": sid, "life": ml, "max": ml})

        # Fade sparkles
        dead = []
        for sp in self._sparkles:
            sp["life"] -= 1
            if sp["life"] <= 0:
                self.canvas.delete(sp["id"])
                dead.append(sp)
            else:
                a    = sp["life"] / sp["max"]
                grey = int(a * 220)
                self.canvas.itemconfig(sp["id"], fill=f"#{grey:02x}{grey:02x}{min(255,grey+40):02x}")
        for sp in dead:
            self._sparkles.remove(sp)

        self._after_ids.append(self.root.after(50, self._animate))


# ══════════════════════════════════════════════════════════════
# Main Birthday Application
# ══════════════════════════════════════════════════════════════

class BirthdayApp:
    def __init__(self, root: tk.Tk, missing: set, stats: dict):
        self.root    = root
        self.missing = missing
        self.stats   = stats

        self.root.title("Birthday Surprise 🎉")
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(bg="black")
        self.root.resizable(True, True)

        self.label = tk.Label(
            root, text="", font=("Courier", 20), justify="center",
            bg="black", fg="white", wraplength=900,
        )
        self.label.pack(expand=True, fill="both")

        self.video_frame = tk.Frame(root, bg="black")

        # VLC
        self.vlc_instance   = None
        self.video_player   = None
        self.music_instance = None
        self.music_player   = None
        self.video_playing  = False
        self.music_enabled  = False

        if VLC_AVAILABLE:
            self.vlc_instance = vlc.Instance("--quiet", "--log-verbose=0")
            self.video_player = self.vlc_instance.media_player_new()
            effective_music   = MUSIC_FILE if MUSIC_FILE and MUSIC_FILE not in missing else None
            if effective_music:
                self.music_instance = vlc.Instance("--quiet", "--no-xlib")
                self.music_player   = self.music_instance.media_player_new()
                media = self.music_instance.media_new(effective_music)
                self.music_player.set_media(media)
                self.music_player.audio_set_volume(50)
                self.music_player.play()
                self.music_enabled = True

        # State
        self.step                  = 0
        self.in_slideshow          = False
        self.slideshow_paused      = False
        self.slideshow_after_id    = None
        self.current_slideshow_idx = 0
        self.shuffled_images       = []

        self.skip_button        = None
        self.replay_button      = None
        self.volume_slider      = None
        self.stats_canvas       = None
        self.confetti_canvas    = None
        self.confetti_after_id  = None
        self.confetti_particles = []

        for key, cb in {
            "<Escape>": self.quit_app,
            "<space>":  self.toggle_video_pause,
            "<F>":      self.toggle_fullscreen,
            "<f>":      self.toggle_fullscreen,
            "<P>":      self.toggle_slideshow_pause,
            "<p>":      self.toggle_slideshow_pause,
            "<M>":      self.toggle_music,
            "<m>":      self.toggle_music,
        }.items():
            self.root.bind(key, cb)

        self.root.bind("<Configure>", self._on_resize)
        self._create_skip_button()
        self.start_countdown()

    # ── UI ───────────────────────────────────────────────────────

    def _create_skip_button(self):
        self.skip_button = tk.Button(
            self.root, text="Skip →", command=self.skip_stage,
            bg="#333", fg="white", font=("Arial", 10), relief="flat",
            activebackground="#555", activeforeground="white",
        )
        self.skip_button.place(relx=1.0, x=-10, y=10, anchor="ne")

    def _create_replay_button(self):
        self.replay_button = tk.Button(
            self.root, text="▶  Play Again", command=self.replay,
            bg="#00c853", fg="black", font=("Arial", 14, "bold"),
            relief="flat", activebackground="#69f0ae", padx=16, pady=8,
        )
        self.replay_button.place(relx=0.5, rely=0.82, anchor="center")

    def _create_volume_slider(self):
        self.volume_slider = tk.Scale(
            self.root, from_=0, to=100, orient=tk.HORIZONTAL,
            command=self._on_volume_change, label="Volume 🔊",
            bg="black", fg="white", troughcolor="#444",
            highlightthickness=0, length=160,
        )
        self.volume_slider.set(50)
        self.volume_slider.place(relx=0.02, rely=0.02, anchor="nw")

    # ── Confetti ─────────────────────────────────────────────────

    def _create_confetti(self):
        self._stop_confetti()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        self.confetti_canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.confetti_canvas.place(x=0, y=0, width=w, height=h)
        self.confetti_particles = []
        for _ in range(CONFETTI_COUNT):
            x     = random.randint(0, w)
            y     = random.randint(-h, 0)
            speed = random.randint(3, 8)
            color = random.choice(CONFETTI_COLORS)
            size  = random.randint(4, 9)
            rect  = self.confetti_canvas.create_rectangle(
                x, y, x + size, y + size, fill=color, outline=""
            )
            self.confetti_particles.append([x, y, rect, speed, size])
        self._animate_confetti()

    def _animate_confetti(self):
        if not self.confetti_canvas:
            return
        try:
            if not self.confetti_canvas.winfo_exists():
                return
            h = self.root.winfo_height()
            for p in self.confetti_particles:
                p[1] += p[3]
                if p[1] > h:
                    p[1] = -p[4]
                self.confetti_canvas.coords(p[2], p[0], p[1], p[0] + p[4], p[1] + p[4])
            self.confetti_after_id = self.root.after(40, self._animate_confetti)
        except tk.TclError:
            pass

    def _stop_confetti(self):
        if self.confetti_after_id:
            self.root.after_cancel(self.confetti_after_id)
            self.confetti_after_id = None
        if self.confetti_canvas:
            try:
                self.confetti_canvas.destroy()
            except tk.TclError:
                pass
            self.confetti_canvas = None
        self.confetti_particles = []

    # ── Controls ─────────────────────────────────────────────────

    def skip_stage(self):
        if self.slideshow_after_id:
            self.root.after_cancel(self.slideshow_after_id)
            self.slideshow_after_id = None
        self.slideshow_paused = False
        self.in_slideshow     = False
        if self.video_playing and self.video_player:
            self.video_player.stop()
            self.video_playing = False
            self.video_frame.pack_forget()
            self.label.pack(expand=True, fill="both")
            if self.volume_slider:
                self.volume_slider.destroy()
                self.volume_slider = None
        if self.step < STAGE_FINALE:
            self.next_step()

    def replay(self):
        self._stop_confetti()
        self._destroy_finale_stats()
        for widget in (self.replay_button, self.volume_slider):
            if widget:
                widget.destroy()
        self.replay_button = None
        self.volume_slider = None
        if self.video_playing and self.video_player:
            self.video_player.stop()
            self.video_playing = False
            self.video_frame.pack_forget()
            self.label.pack(expand=True, fill="both")
        self.step             = 0
        self.slideshow_paused = False
        self.in_slideshow     = False
        if self.slideshow_after_id:
            self.root.after_cancel(self.slideshow_after_id)
            self.slideshow_after_id = None
        if self.music_player and self.music_enabled:
            self.music_player.audio_set_volume(50)
            self.music_player.play()
        self.start_countdown()

    def toggle_fullscreen(self, event=None):
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))

    def toggle_slideshow_pause(self, event=None):
        if not self.in_slideshow:
            return
        self.slideshow_paused = not self.slideshow_paused
        if self.slideshow_paused:
            if self.slideshow_after_id:
                self.root.after_cancel(self.slideshow_after_id)
                self.slideshow_after_id = None
            self.label.config(text="⏸  Paused\n\nPress P to resume", image="")
        else:
            self.slideshow(self.current_slideshow_idx)

    def toggle_music(self, event=None):
        if not self.music_player:
            return
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            self.music_player.play()
        else:
            self.music_player.pause()

    def _on_volume_change(self, val):
        if self.video_playing and self.video_player:
            self.video_player.audio_set_volume(int(val))

    def toggle_video_pause(self, event=None):
        if self.video_playing and self.video_player:
            self.video_player.pause()

    def quit_app(self, event=None):
        self._stop_confetti()
        if self.video_player:
            self.video_player.stop()
        if self.music_player:
            self.music_player.stop()
        self.root.destroy()

    def _on_resize(self, event=None):
        if self.confetti_canvas:
            try:
                self.confetti_canvas.place(
                    x=0, y=0,
                    width=self.root.winfo_width(),
                    height=self.root.winfo_height(),
                )
            except tk.TclError:
                pass

    # ── Sequence ─────────────────────────────────────────────────

    def start_countdown(self):
        self.step = 0
        self.next_step()

    def next_step(self):
        self.step += 1

        if self.step == STAGE_COUNTDOWN:
            self._run_countdown(COUNTDOWN_START)

        elif self.step == STAGE_HAPPY_BDAY:
            self._show_figlet("HAPPY\nBIRTHDAY", TEXT_DISPLAY_MS)

        elif self.step == STAGE_NAME:
            self._show_figlet(BIRTHDAY_NAME, TEXT_DISPLAY_MS)

        elif self.step == STAGE_SLIDESHOW:
            self.shuffled_images = [img for img in IMAGE_FILES if img not in self.missing]
            if not self.shuffled_images:
                print("No images available — skipping slideshow.")
                self.next_step()
                return
            random.shuffle(self.shuffled_images)
            self.current_slideshow_idx = 0
            self.in_slideshow = True
            self.slideshow(0)

        elif self.step == STAGE_VIDEO:
            self.in_slideshow = False
            self._play_video()

        else:
            # Finale — confetti first, then stat panel fades in on top
            self.in_slideshow = False
            self.label.config(text="", image="")
            self._create_confetti()
            if self.music_player:
                self.music_player.stop()
            # Short pause so confetti is visible before stats appear
            self.root.after(800, self._show_finale_stats)

    def _show_finale_stats(self):
        """Overlay the animated stat panel on top of the confetti canvas."""
        s  = self.stats
        w  = max(self.root.winfo_width(),  960)
        h  = max(self.root.winfo_height(), 640)

        # Semi-transparent overlay canvas sitting above confetti
        self.stats_canvas = tk.Canvas(
            self.root, bg="black", highlightthickness=0
        )
        self.stats_canvas.place(x=0, y=0, width=w, height=h)
        self.stats_canvas.configure(bg="black")

        # Use a low-alpha trick: draw a dark rectangle to give contrast
        # without hiding the confetti (confetti canvas is below this one
        # but we make the bg transparent via a stipple overlay)
        overlay = self.stats_canvas.create_rectangle(
            0, 0, w, h,
            fill="black", stipple="gray50", outline=""
        )

        # Title
        self.stats_canvas.create_text(
            w // 2, int(h * 0.10),
            text=f"🎉  Happy Birthday, {BIRTHDAY_NAME}!  🎉",
            fill="#ffe066", font=("Courier", 22, "bold"), anchor="center"
        )
        self.stats_canvas.create_text(
            w // 2, int(h * 0.18),
            text=f"You are now  {s['turning']}  years old!",
            fill="#ff9de0", font=("Courier", 16), anchor="center"
        )

        # Stat cards — 3 rows of 2
        card_data = [
            ("Months lived",  fmt(s["age_months"])),
            ("Weeks lived",   fmt(s["age_weeks"])),
            ("Days lived",    fmt(s["age_days"])),
            ("Hours lived",   fmt(s["age_hours"])),
            ("Seconds lived", fmt(s["age_seconds"])),
            ("Age",           f"{s['turning']} years"),
        ]

        cols, rows  = 3, 2
        cw, ch      = 220, 72
        gap_x, gap_y = 20, 16
        total_w     = cols * cw + (cols - 1) * gap_x
        total_h     = rows * ch + (rows - 1) * gap_y
        start_x     = (w - total_w) // 2
        start_y     = int(h * 0.28)

        self._stat_card_ids   = []
        self._finale_stat_idx = 0

        for i, (label, val) in enumerate(card_data):
            col = i % cols
            row = i // cols
            cx  = start_x + col * (cw + gap_x)
            cy  = start_y + row * (ch + gap_y)

            bg = self.stats_canvas.create_rectangle(
                cx, cy, cx + cw, cy + ch,
                fill="#1a1a3a", outline="#5555cc", width=1
            )
            lbl = self.stats_canvas.create_text(
                cx + cw // 2, cy + 22,
                text=label, fill="#8888cc",
                font=("Courier", 10), anchor="center"
            )
            val_id = self.stats_canvas.create_text(
                cx + cw // 2, cy + 46,
                text=val, fill="#ffdd88",
                font=("Courier", 15, "bold"), anchor="center"
            )
            ids = (bg, lbl, val_id)
            self._stat_card_ids.append(ids)

            # Hover + click to cycle
            for cid in ids:
                self.stats_canvas.tag_bind(
                    cid, "<Button-1>", self._on_finale_card_click
                )
                self.stats_canvas.tag_bind(
                    cid, "<Enter>",
                    lambda e, b=bg: self.stats_canvas.itemconfig(
                        b, fill="#252550", outline="#9999ff"
                    )
                )
                self.stats_canvas.tag_bind(
                    cid, "<Leave>",
                    lambda e, b=bg: self.stats_canvas.itemconfig(
                        b, fill="#1a1a3a", outline="#5555cc"
                    )
                )

        # Replay button sits below cards
        self._create_replay_button()

        # Hint
        self.stats_canvas.create_text(
            w // 2, h - 16,
            text="Click any card to cycle stats  •  P = pause slideshow  •  Esc = quit",
            fill="#444466", font=("Courier", 10), anchor="s"
        )

        # Store card_data for cycling
        self._all_stat_data = card_data

    def _on_finale_card_click(self, event):
        """Rotate which 6 stats are shown on each click."""
        self._finale_stat_idx = (self._finale_stat_idx + 1) % len(self._all_stat_data)
        s = self.stats
        all_stats = [
            ("Months lived",  fmt(s["age_months"])),
            ("Weeks lived",   fmt(s["age_weeks"])),
            ("Days lived",    fmt(s["age_days"])),
            ("Hours lived",   fmt(s["age_hours"])),
            ("Seconds lived", fmt(s["age_seconds"])),
            ("Age",           f"{s['turning']} years"),
        ]
        # Rotate the full list by the click index
        rotated = all_stats[self._finale_stat_idx:] + all_stats[:self._finale_stat_idx]
        for i, (ids) in enumerate(self._stat_card_ids):
            label, val = rotated[i]
            _, lbl_id, val_id = ids
            self.stats_canvas.itemconfig(lbl_id, text=label)
            self.stats_canvas.itemconfig(val_id, text=val)

    def _destroy_finale_stats(self):
        if hasattr(self, "stats_canvas") and self.stats_canvas:
            try:
                self.stats_canvas.destroy()
            except tk.TclError:
                pass
            self.stats_canvas = None

    def _show_figlet(self, text: str, delay_ms: int, font: str = "standard"):
        rendered = pyfiglet.figlet_format(text, font=font)
        self.label.config(text=rendered, image="", font=("Courier", 14))
        self.root.after(delay_ms, self.next_step)

    def _run_countdown(self, n: int):
        if n > 0:
            rendered = pyfiglet.figlet_format(str(n))
            self.label.config(text=rendered, image="", font=("Courier", 14))
            self.root.after(1000, lambda: self._run_countdown(n - 1))
        else:
            self.next_step()

    # ── Slideshow ─────────────────────────────────────────────────

    def slideshow(self, idx: int):
        if idx >= len(self.shuffled_images):
            self.in_slideshow = False
            self.next_step()
            return
        self.current_slideshow_idx = idx
        img_path = self.shuffled_images[idx]
        try:
            if not PIL_AVAILABLE:
                raise RuntimeError("Pillow not installed")
            w     = max(self.root.winfo_width(),  800)
            h     = max(self.root.winfo_height(), 450)
            photo = fit_image(img_path, w - 20, h - 20)
            self.label.config(image=photo, text="")
            self.label.image = photo
        except Exception as exc:
            print(f"Error loading image '{img_path}': {exc}")
            self.label.config(text=f"[Could not load: {img_path}]", image="")
        if not self.slideshow_paused:
            self.slideshow_after_id = self.root.after(
                IMAGE_DISPLAY_MS, lambda: self.slideshow(idx + 1)
            )
        else:
            self.slideshow_after_id = None

    # ── Video ─────────────────────────────────────────────────────

    def _play_video(self):
        if not VLC_AVAILABLE or not self.video_player:
            print("VLC unavailable — skipping video.")
            self.next_step()
            return
        if VIDEO_FILE in self.missing:
            print("Video file missing — skipping.")
            self.next_step()
            return
        self.label.pack_forget()
        self.video_frame.pack(expand=True, fill="both")
        self.root.update()
        platform_set_video_window(self.video_player, self.video_frame)
        media = self.vlc_instance.media_new(VIDEO_FILE)
        self.video_player.set_media(media)
        self.video_player.play()
        self.video_playing = True
        if self.music_player:
            self.music_player.stop()
        self._create_volume_slider()
        self._poll_video_state()

    def _poll_video_state(self):
        if not self.video_playing:
            return
        state = self.video_player.get_state()
        if VLC_AVAILABLE and state in (vlc.State.Ended, vlc.State.Error):
            self.video_playing = False
            self.video_player.stop()
            self.video_frame.pack_forget()
            self.label.pack(expand=True, fill="both")
            if self.volume_slider:
                self.volume_slider.destroy()
                self.volume_slider = None
            self.next_step()
        else:
            self.root.after(200, self._poll_video_state)


# ══════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    stats = birthday_stats(DATE_OF_BIRTH)

    all_media = list(IMAGE_FILES) + [VIDEO_FILE]
    if MUSIC_FILE:
        all_media.append(MUSIC_FILE)
    missing = check_files(all_media)

    root = tk.Tk()

    if stats["is_today"]:
        # It IS the birthday — launch the full surprise!
        app = BirthdayApp(root, missing=missing, stats=stats)
    else:
        # Not yet — show the animated waiting screen
        s = stats
        print(f"Not yet! Birthday is on {s['next_birthday']} ({s['days_to']} days away).")
        print(f"{BIRTHDAY_NAME} is currently {s['age_years']} years old.")
        WaitingScreen(root, stats=stats)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass