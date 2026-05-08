#!/usr/bin/env python3
"""Kokoro TTS - Terminal UI"""

import curses, os, sys, threading
from pathlib import Path

try:
    import sounddevice as sd
    import soundfile as sf
except ImportError:
    print("Missing deps. Activate kokoro-env first.")
    sys.exit(1)

VOICES = [
    ("bm_george",   "British Male   - George"),
    ("bm_daniel",   "British Male   - Daniel"),
    ("bm_lewis",    "British Male   - Lewis"),
    ("bm_fable",    "British Male   - Fable"),
    ("am_adam",     "American Male  - Adam"),
    ("am_echo",     "American Male  - Echo"),
    ("am_eric",     "American Male  - Eric"),
    ("am_fenrir",   "American Male  - Fenrir"),
    ("am_liam",     "American Male  - Liam"),
    ("am_michael",  "American Male  - Michael"),
    ("am_onyx",     "American Male  - Onyx"),
    ("am_puck",     "American Male  - Puck"),
    ("bf_alice",    "British Female - Alice"),
    ("bf_emma",     "British Female - Emma"),
    ("bf_isabella", "British Female - Isabella"),
    ("bf_lily",     "British Female - Lily"),
    ("af_heart",    "Amer. Female   - Heart"),
    ("af_bella",    "Amer. Female   - Bella"),
    ("af_sarah",    "Amer. Female   - Sarah"),
    ("af_nicole",   "Amer. Female   - Nicole"),
    ("af_jessica",  "Amer. Female   - Jessica"),
    ("af_nova",     "Amer. Female   - Nova"),
    ("af_river",    "Amer. Female   - River"),
    ("af_sky",      "Amer. Female   - Sky"),
    ("af_aoede",    "Amer. Female   - Aoede"),
    ("af_kore",     "Amer. Female   - Kore"),
]

OUTPUT_DIR      = Path.home() / "kokoro_outputs"
kokoro_instance = None
is_playing      = False
play_lock       = threading.Lock()


def load_kokoro():
    global kokoro_instance
    script_dir  = Path(__file__).parent
    model_path  = script_dir / "kokoro-v1.0.onnx"
    voices_path = script_dir / "voices-v1.0.bin"
    if not model_path.exists():
        print(f"ERROR: kokoro-v1.0.onnx not found in {script_dir}"); sys.exit(1)
    if not voices_path.exists():
        print(f"ERROR: voices-v1.0.bin not found in {script_dir}"); sys.exit(1)
    from kokoro_onnx import Kokoro
    kokoro_instance = Kokoro(str(model_path), str(voices_path))


def generate_audio(text, voice):
    return kokoro_instance.create(text, voice=voice, speed=1.0, lang="en-us")


def play_audio(samples, sr):
    global is_playing
    with play_lock:
        is_playing = True
    try:
        sd.play(samples, sr); sd.wait()
    finally:
        with play_lock:
            is_playing = False


def save_audio(samples, sr, filename):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not filename.endswith(".wav"):
        filename += ".wav"
    path = OUTPUT_DIR / filename
    sf.write(str(path), samples, sr)
    return str(path)


def bordered(win, title=""):
    win.box()
    if title:
        _, w = win.getmaxyx()
        x = max(1, (w - len(title) - 2) // 2)
        try: win.addstr(0, x, f" {title} ", curses.A_BOLD)
        except curses.error: pass


def draw_voices(w, idx, active):
    w.erase()
    h, width = w.getmaxyx()
    bordered(w, "Voices")
    vis   = h - 2
    start = max(0, idx - vis + 1) if idx >= vis else 0
    for i, (_, label) in enumerate(VOICES[start:start+vis]):
        r = i + 1
        if r >= h - 1: break
        ai   = start + i
        text = label[:width-5]
        attr = (curses.A_REVERSE | curses.A_BOLD) if (ai == idx and active) else (curses.A_REVERSE if ai == idx else 0)
        try: w.addstr(r, 2, (">" if ai==idx else " ") + " " + text, attr)
        except curses.error: pass
    w.noutrefresh()


def draw_script(w, lines, cr, cc, active):
    w.erase()
    h, width = w.getmaxyx()
    bordered(w, "Script  (TAB to voice panel, ENTER to play)")
    ih = h - 2; iw = width - 4
    sl = max(0, cr - ih + 1) if cr >= ih else 0
    for i, line in enumerate(lines[sl:sl+ih]):
        r = i + 1
        if r >= h - 1: break
        try: w.addstr(r, 2, line[:iw])
        except curses.error: pass
    if active:
        rd = cr - sl + 1; cd = min(cc, iw) + 2
        if 1 <= rd < h - 1:
            try:
                ch = lines[cr][cc] if cc < len(lines[cr]) else " "
                w.addstr(rd, cd, ch, curses.A_REVERSE)
            except curses.error: pass
    w.noutrefresh()


def draw_help(w):
    w.erase()
    bordered(w)
    _, width = w.getmaxyx()
    items = [("TAB","Switch"),("↑↓","Voice"),("ENTER","Play"),("S","Save"),("O","Open"),("C","Clear"),("Q","Quit")]
    x = 2
    for k, d in items:
        seg = f"[{k}] {d}  "
        if x + len(seg) >= width - 2: break
        try:
            w.addstr(1, x, f"[{k}]", curses.A_BOLD)
            w.addstr(1, x+len(k)+2, f" {d}  ")
        except curses.error: pass
        x += len(seg)
    w.noutrefresh()


def draw_status(w, msg, err=False):
    w.erase()
    _, width = w.getmaxyx()
    attr = curses.color_pair(2) if err else curses.color_pair(1)
    try: w.addstr(0, 0, msg[:width-1], attr)
    except curses.error: pass
    w.noutrefresh()


def get_input(scr, prompt, max_h, max_w):
    curses.echo(); curses.curs_set(1)
    try:
        scr.addstr(max_h-1, 0, " "*(max_w-1))
        scr.addstr(max_h-1, 0, prompt)
    except curses.error: pass
    scr.refresh()
    val = scr.getstr(max_h-1, len(prompt), max_w-len(prompt)-1)
    curses.noecho(); curses.curs_set(0)
    return val.decode("utf-8", errors="replace").strip()


def main(scr):
    global is_playing
    curses.curs_set(0); curses.start_color(); curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_RED,   -1)
    scr.keypad(True); scr.timeout(100)

    vi   = 0; panel = 0
    lines = [""]; cr = 0; cc = 0
    smsg  = "Ready — TAB=switch panel  ENTER=play  Q=quit"
    serr  = False
    samp  = None; srate = None

    while True:
        H, W = scr.getmaxyx()
        vw = min(36, W//3); sw = W - vw; mh = H - 4

        if mh < 3 or vw < 8:
            scr.erase()
            try: scr.addstr(0, 0, "Terminal too small, please resize.")
            except: pass
            scr.refresh()
            if scr.getch() in (ord('q'), ord('Q')): break
            continue

        vwin  = curses.newwin(mh, vw,  0,  0)
        swin  = curses.newwin(mh, sw,  0,  vw)
        hwin  = curses.newwin(3,  W,   mh, 0)
        stwin = curses.newwin(1,  W,   H-1,0)

        draw_voices(vwin, vi, panel==0)
        draw_script(swin, lines, cr, cc, panel==1)
        draw_help(hwin)
        draw_status(stwin, smsg + ("  ♪ playing..." if is_playing else ""), serr)
        curses.doupdate()

        k = scr.getch()
        if k == -1: continue

        if k in (ord('q'), ord('Q')):
            sd.stop(); break

        elif k == ord('\t'):
            panel = 1 - panel
            smsg  = "Script panel — type/paste or [O]pen file" if panel==1 else "Voice panel — ↑↓ select, ENTER play"
            serr  = False

        elif k in (curses.KEY_ENTER, 10, 13) and panel == 0:
            text = "\n".join(lines).strip()
            if not text:
                smsg = "Script is empty — add text first."; serr = True
            else:
                smsg = f"Generating with {VOICES[vi][0]}..."; serr = False
                draw_status(stwin, smsg); curses.doupdate()
                try:
                    samp, srate = generate_audio(text, VOICES[vi][0])
                    threading.Thread(target=play_audio, args=(samp, srate), daemon=True).start()
                    smsg = f"Playing: {VOICES[vi][1]}  |  [S] to save"
                except Exception as e:
                    smsg = f"Error: {e}"; serr = True

        elif k in (ord('s'), ord('S')):
            if samp is None:
                smsg = "Nothing to save — generate audio first."; serr = True
            else:
                fn = get_input(scr, "Save as (filename): ", H, W)
                if fn:
                    try:
                        p = save_audio(samp, srate, fn)
                        smsg = f"Saved: {p}"; serr = False
                    except Exception as e:
                        smsg = f"Save error: {e}"; serr = True
                else:
                    smsg = "Save cancelled."; serr = False

        elif k in (ord('o'), ord('O')):
            fp = get_input(scr, "Open .txt file path: ", H, W)
            if fp:
                try:
                    with open(os.path.expanduser(fp), "r", encoding="utf-8") as f:
                        content = f.read()
                    lines = content.splitlines() or [""]
                    cr = cc = 0; panel = 1
                    smsg = f"Loaded: {fp}"; serr = False
                except Exception as e:
                    smsg = f"Cannot open: {e}"; serr = True

        elif k in (ord('c'), ord('C')):
            lines = [""]; cr = cc = 0
            smsg = "Script cleared."; serr = False

        elif panel == 0:
            if k == curses.KEY_UP:   vi = max(0, vi-1)
            elif k == curses.KEY_DOWN: vi = min(len(VOICES)-1, vi+1)

        elif panel == 1:
            if   k == curses.KEY_UP:
                if cr > 0: cr -= 1; cc = min(cc, len(lines[cr]))
            elif k == curses.KEY_DOWN:
                if cr < len(lines)-1: cr += 1; cc = min(cc, len(lines[cr]))
            elif k == curses.KEY_LEFT:
                if cc > 0: cc -= 1
                elif cr > 0: cr -= 1; cc = len(lines[cr])
            elif k == curses.KEY_RIGHT:
                if cc < len(lines[cr]): cc += 1
                elif cr < len(lines)-1: cr += 1; cc = 0
            elif k == curses.KEY_HOME: cc = 0
            elif k == curses.KEY_END:  cc = len(lines[cr])
            elif k in (curses.KEY_BACKSPACE, 127, 8):
                if cc > 0:
                    lines[cr] = lines[cr][:cc-1] + lines[cr][cc:]; cc -= 1
                elif cr > 0:
                    pl = len(lines[cr-1]); lines[cr-1] += lines[cr]; lines.pop(cr); cr -= 1; cc = pl
            elif k in (10, 13):
                rest = lines[cr][cc:]; lines[cr] = lines[cr][:cc]
                lines.insert(cr+1, rest); cr += 1; cc = 0
            elif 32 <= k <= 126:
                ch = chr(k); lines[cr] = lines[cr][:cc] + ch + lines[cr][cc:]; cc += 1


if __name__ == "__main__":
    print("Loading Kokoro model, please wait...")
    load_kokoro()
    print("Model loaded. Starting TUI...")
    curses.wrapper(main)
    print("Kokoro TTS closed.")
