# 🎂 Birthday Surprise App

A multi-platform birthday surprise application for **Samuel** — featuring an animated countdown, photo slideshow, video playback, confetti, and interactive age statistics.

Three versions exist — desktop (Python/Tkinter), web, and Android. This README covers all of them.

---

## 📁 Project Structure

```
Birthday/
├── birth.py                           # Desktop app (Python)
├── birth.spec                         # PyInstaller build spec
├── index.html                         # Web & Android app
├── aa.jpg                             # Slideshow image 1
├── bb.jpg                             # Slideshow image 2
├── cc.jpg                             # Slideshow image 3
├── Rayvanny_Happy Birthday.mp4        # Birthday video
└── Rayvanny_Happy Birthday.mp3        # Background music
```

> **Note:** Media files (images, video, music) are **not** included in the repository. Add your own files with the exact names above, or update the filenames in the config section of `birth.py` / `index.html`.

---

## ✨ Features

| Feature | Desktop | Web / Android |
|---|:---:|:---:|
| Animated star-field waiting screen | ✅ | ✅ |
| Days-to-birthday countdown | ✅ | ✅ |
| Interactive age stat cards | ✅ | ✅ |
| Animated figlet/large text countdown | ✅ | ✅ |
| Photo slideshow | ✅ | ✅ |
| Video playback | ✅ | ✅ |
| Background music | ✅ | ✅ |
| Confetti finale | ✅ | ✅ |
| Age in years / months / weeks / days / hours / seconds | ✅ | ✅ |
| Skip button | ✅ | ✅ |
| Replay | ✅ | ✅ |
| Keyboard shortcuts | ✅ | — |
| Works offline | ✅ | ✅ |
| Installable on Android | — | ✅ |

---

---

# 🖥️ Desktop Version (Python)

> Source: `birth.py` · Build spec: `birth.spec` · [GitHub Repository](https://github.com/Samuel-Muli/Birthday)

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.10+ | 3.14 tested |
| VLC media player 64 bit | Latest | Must be installed system-wide |
| pip packages | — | See below |

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

**2. Create a virtual environment (recommended)**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install pillow python-vlc pyfiglet
```

**4. Add your media files**

Place the following files in the same folder as `birth.py`:
```
aa.jpg
bb.jpg
cc.jpg
Rayvanny_Happy Birthday.mp4
Rayvanny_Happy Birthday.mp3
```

**5. Run**
```bash
python birth.py
```

## Configuration

Open `birth.py` and edit the block at the top:

```python
BIRTHDAY_NAME    = "SAMUEL"            # Name to display
DATE_OF_BIRTH    = date(2000, 3, 29)   # date(YYYY, MM, DD)

IMAGE_FILES      = ["aa.jpg", "bb.jpg", "cc.jpg"]
VIDEO_FILE       = "Rayvanny_Happy Birthday.mp4"
MUSIC_FILE       = "Rayvanny_Happy Birthday.mp3"
COUNTDOWN_START  = 5                   # seconds in countdown
IMAGE_DISPLAY_MS = 2000                # ms per slideshow image
TEXT_DISPLAY_MS  = 2000                # ms each text message shows
```

## Keyboard Shortcuts

| Key | Action |
|---|---|
| `Esc` | Quit |
| `Space` | Pause / resume video |
| `F` | Toggle fullscreen |
| `P` | Pause / resume slideshow |
| `M` | Toggle background music |

## Building a Standalone Executable (.exe / binary)

Uses the included `birth.spec` file with PyInstaller:

```bash
pip install pyinstaller
pyinstaller birth.spec
```

The executable will be in `dist/birth.exe` (Windows) or `dist/birth` (Linux/macOS).

> **Windows note:** If VLC is not found automatically, uncomment and set the path in `birth.py`:
> ```python
> os.add_dll_directory(r"C:\Program Files\VideoLAN\VLC")
> ```

---

---

# 🌐 Web Version

> Source: `index.html` (single self-contained file — no server, no build step)

## Quick Start (local)

1. Place `index.html` in the same folder as your media files
2. Open `index.html` directly in any modern browser

```
Birthday/
├── index.html
├── aa.jpg
├── bb.jpg
├── cc.jpg
├── Rayvanny_Happy Birthday.mp4
└── Rayvanny_Happy Birthday.mp3
```

> **Chrome note:** Chrome blocks local media autoplay. Use Firefox for local testing, or run a simple local server:
> ```bash
> # Python (any OS)
> python -m http.server 8080
> # then open http://localhost:8080
> ```

## Hosting Online (recommended)

Any static host works. The easiest free options:

### Netlify Drop (drag and drop, no account needed)
1. Go to **[netlify.com/drop](https://app.netlify.com/drop)**
2. Drag your entire `Birthday/` folder onto the page
3. Netlify gives you a live URL instantly (e.g. `https://amazing-name-123.netlify.app`)
4. Share the link — it opens in any browser, on any device

### GitHub Pages (if files are in the repo)
1. Push all files including media to your GitHub repo
2. Go to **Settings → Pages → Source: main branch / root**
3. Your app is live at `https://your-username.github.io/your-repo`

### Other options
- **Vercel** — `npx vercel` in the project folder
- **Cloudflare Pages** — drag and drop at pages.cloudflare.com
- **Firebase Hosting** — `firebase deploy`
-**onrender** - i personally use this and has been good

## Configuration

Open `index.html` and edit the `CFG` object near the top of the `<script>` tag:

```javascript
const CFG = {
  name:          "SAMUEL",
  dob:           new Date(2000, 2, 29),   // month is 0-indexed: 2 = March
  images:        ["aa.jpg","bb.jpg","cc.jpg"],
  video:         "Rayvanny_Happy Birthday.mp4",
  music:         "Rayvanny_Happy Birthday.mp3",
  countdownFrom:  5,
  slideMs:        3000,    // ms per image
  textMs:         2500,    // ms per text screen
};
```

> ⚠️ JavaScript months are 0-indexed: January = 0, February = 1, March = 2, etc.

---

---

# 📱 Android Version
>I have not done this one but this are the steps incase you are really in to it
> Built from `index.html` using **Capacitor** (recommended) or Cordova. No code changes needed — the web app is the Android app.

## Option A — Add to Home Screen (PWA, easiest)

No APK, no build tools. Works instantly.

1. Host `index.html` + media files online (see Web → Hosting above)
2. Open the URL in **Chrome** on the Android phone
3. Tap **⋮ → Add to Home screen**
4. The app installs as a full-screen icon with no browser UI

This is the recommended path for personal use.

---

## Option B — Build a Real APK with Capacitor

### Prerequisites

- [Node.js 18+](https://nodejs.org)
- [Android Studio](https://developer.android.com/studio) (includes Java 17 & SDK)
- A USB cable or Wi-Fi ADB for installation

### Step 1 — Create the project

```bash
mkdir birthday-android && cd birthday-android
npm init -y
npm install @capacitor/core @capacitor/cli @capacitor/android
npx cap init "Birthday Surprise" "com.samuel.birthday" --web-dir www
```

### Step 2 — Add your files

```bash
mkdir www
cp /path/to/index.html                        www/
cp /path/to/aa.jpg                            www/
cp /path/to/bb.jpg                            www/
cp /path/to/cc.jpg                            www/
cp "/path/to/Rayvanny_Happy Birthday.mp4"     www/
cp "/path/to/Rayvanny_Happy Birthday.mp3"     www/
```

### Step 3 — Add Android platform

```bash
npx cap add android
npx cap sync
```

### Step 4 — Configure `capacitor.config.json`

```json
{
  "appId": "com.samuel.birthday",
  "appName": "Birthday Surprise",
  "webDir": "www",
  "server": { "androidScheme": "https" },
  "android": {
    "allowMixedContent": true,
    "backgroundColor": "#000000"
  }
}
```

### Step 5 — Build in Android Studio

```bash
npx cap open android
```

Inside Android Studio:
- **Build → Build Bundle(s) / APK(s) → Build APK(s)**
- APK saved to: `android/app/build/outputs/apk/debug/app-debug.apk`

### Step 6 — Install on phone

**Via USB (ADB)**
```bash
adb install android/app/build/outputs/apk/debug/app-debug.apk
```

**Via file transfer**
Copy the APK to the phone and open it. If prompted, enable **Install from unknown sources** in Settings → Security.

---

## Option C — Apache Cordova (alternative)

```bash
npm install -g cordova
cordova create birthday com.samuel.birthday "Birthday Surprise"
cd birthday

cp /path/to/index.html                    www/
cp /path/to/*.jpg                         www/
cp "/path/to/Rayvanny_Happy Birthday.mp4" www/
cp "/path/to/Rayvanny_Happy Birthday.mp3" www/

cordova platform add android
cordova build android
# APK: platforms/android/app/build/outputs/apk/debug/app-debug.apk
```

---

## Android Tips

**Lock to portrait orientation**

In `android/app/src/main/AndroidManifest.xml`, find the `<activity>` tag and add:
```xml
android:screenOrientation="portrait"
```

**Full immersive mode (hide status bar)**

In `android/app/src/main/java/.../MainActivity.java`:
```java
import android.view.WindowManager;
// inside onCreate():
getWindow().setFlags(
  WindowManager.LayoutParams.FLAG_FULLSCREEN,
  WindowManager.LayoutParams.FLAG_FULLSCREEN
);
```

**Custom app icon**

Use Android Studio's **Image Asset** tool:
Right-click `res/` → New → Image Asset → upload your image.

**Splash screen**
```bash
npm install @capacitor/splash-screen
npx cap sync
```

---

---

## 🐛 Troubleshooting

| Problem | Solution |
|---|---|
| App crashes on first run (Python) | Known Python 3.14 / Tkinter quirk — just run again, fixed in latest code |
| No sound / video on web (local) | Browser blocks local media. Use a local server or host online |
| VLC not found (Windows) | Uncomment `os.add_dll_directory(...)` in `birth.py` and set path |
| APK won't install | Enable "Install from unknown sources" in Android Settings → Security |
| Images not loading | Check filenames match exactly (case-sensitive on Linux/Android) |
| Slideshow shows blank on Android | Ensure images are inside the `www/` folder before `npx cap sync` |
| `randint` error on waiting screen | Update to latest `birth.py` — fixed with deferred window init |

---

## 📄 License

Personal use. Media files (images, video, music) are not included and remain the property of their respective owners.

---

*Made with ❤️ for Samuel's birthday.*
