# Kokoro TTS — Terminal UI

A lightweight, fully **offline** Text-to-Speech app for Linux. Choose from **26 high-quality voices**, type or load a script, and play or save audio — all from your terminal. No internet connection or API key required.

![Python](https://img.shields.io/badge/python-3.11-blue)
![Platform](https://img.shields.io/badge/platform-Linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ⚠️ Platform Note

This app is **Linux only**. It uses a terminal interface and will not work on Windows or macOS without significant modifications.

---

## Features

- 🎙️ **26 voices** — American & British, male & female
- ⌨️ **Built-in text editor** — type directly in the terminal
- 📂 **Open `.txt` files** for batch narration
- 💾 **Save output as `.wav`** to `~/kokoro_outputs/`
- 🔇 **Fully offline** — no API keys, no internet required
- 🚀 **Launches without manually activating a virtual environment**

---

## Prerequisites

Before you begin, you need a few things installed. Open a terminal first:

> **How to open a terminal:** Press `Ctrl + Alt + T` on most Linux desktops, or search for "Terminal" in your app menu.

### 1. Install system dependencies

```bash
sudo apt update
sudo apt install git curl wget make build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev libffi-dev
```

> If you're not on Ubuntu/Debian, replace `apt` with your distro's package manager (e.g. `dnf` on Fedora, `pacman` on Arch).

### 2. Install pyenv

`pyenv` lets you install and manage multiple Python versions side by side without affecting your system.

```bash
curl https://pyenv.run | bash
```

Then add pyenv to your shell by running these three commands:

```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
```

Reload your terminal:

```bash
source ~/.bashrc
```

Verify it worked:

```bash
pyenv --version
```

---

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/amtechguy/kokoro-tts.git
cd kokoro-tts
```

### 2. Install Python 3.11 and create a virtual environment

```bash
pyenv install 3.11.9
pyenv virtualenv 3.11.9 kokoro-env
```

> This may take a few minutes the first time as it compiles Python.

### 3. Install Python dependencies

```bash
~/.pyenv/versions/kokoro-env/bin/pip install -r requirements.txt
```

### 4. Download the model files

The AI model files are too large to store on GitHub. Download them and place them **inside the `kokoro-tts` folder**:

| File | Size | Download |
| ---- | ---- | -------- |
| `kokoro-v1.0.onnx` | ~311 MB | [Download from Hugging Face](https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/kokoro-v1.0.onnx) |
| `voices-v1.0.bin` | ~27 MB | [Download from Hugging Face](https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices/voices-v1.0.bin) |

Or download them directly from the terminal (make sure you're inside the `kokoro-tts` folder):

```bash
wget https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/kokoro-v1.0.onnx
wget https://huggingface.co/hexgrad/Kokoro-82M/resolve/main/voices/voices-v1.0.bin
```

### 5. Make the launcher executable

```bash
chmod +x kokoro-tts
```

> `chmod +x` simply gives the file permission to be run as a program. You only need to do this once.

### 6. (Optional) Launch from anywhere

If you want to type `kokoro-tts` from any folder instead of navigating to the project directory each time:

```bash
echo 'export PATH="$HOME/kokoro-tts:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

## Running the App

```bash
# If you added it to PATH:
kokoro-tts

# Or from inside the project folder:
./kokoro-tts
```

You'll see a two-panel interface appear in your terminal.

---

## How to Use

The app has two panels:

- **Left panel** — Voice selector (browse with arrow keys)
- **Right panel** — Text editor (type your script here)

Switch between panels with `TAB`.

### Keybindings

| Key     | Action                                 |
| ------- | -------------------------------------- |
| `TAB`   | Switch between Voice and Script panels |
| `↑ / ↓` | Navigate voices                        |
| `ENTER` | Generate & play audio                  |
| `S`     | Save last audio as `.wav`              |
| `O`     | Open a `.txt` file into the editor     |
| `C`     | Clear the script                       |
| `Q`     | Quit                                   |

---

## Project Structure

```
kokoro-tts/
├── kokoro-tts          # Launcher script (handles Python environment automatically)
├── kokoro_tui.py       # Main TUI application
├── requirements.txt    # Python dependencies
├── kokoro-v1.0.onnx    # ← download separately (not included in repo)
└── voices-v1.0.bin     # ← download separately (not included in repo)
```

---

## Troubleshooting

**"kokoro-env not found" error**
→ Make sure you ran steps 2 and 3 of the installation correctly. Run `pyenv versions` to check that `kokoro-env` appears in the list.

**"kokoro-v1.0.onnx not found" error**
→ The model files weren't downloaded or weren't placed in the right folder. Make sure both files are inside the `kokoro-tts/` project folder.

**No audio plays**
→ Make sure your system audio is working and not muted. The app uses `sounddevice` which relies on your system's audio drivers.

**Terminal too small**
→ The app will show a warning if your terminal window is too small. Resize it and the UI will adjust automatically.

---

## License

MIT
