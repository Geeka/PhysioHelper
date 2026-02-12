#!/usr/bin/env python3
"""
Voice Counting Program - Terminal Version
Works without a graphical display environment.
"""

import time
import json
import os
import sys
import threading

# ── Try to import pyttsx3, fall back to print-only mode ──────────────────────
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

# ── Terminal colours (works on Linux/macOS/WSL) ───────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BLUE   = "\033[94m"
WHITE  = "\033[97m"
DIM    = "\033[2m"

SETTINGS_FILE = "voice_counter_settings.json"

DEFAULT_PRESETS = [
    {"label": "Push-ups",      "icon": "💪", "maxCount": 20, "repeatCount": 3, "speed": 2, "interval": 30, "customText": "Set"},
    {"label": "Squats",        "icon": "🦵", "maxCount": 25, "repeatCount": 4, "speed": 2, "interval": 45, "customText": "Round"},
    {"label": "Jumping Jacks", "icon": "🤸", "maxCount": 30, "repeatCount": 3, "speed": 3, "interval": 30, "customText": "Set"},
    {"label": "Plank",         "icon": "🧘", "maxCount": 60, "repeatCount": 3, "speed": 5, "interval": 60, "customText": "Hold"},
    {"label": "Burpees",       "icon": "🏃", "maxCount": 15, "repeatCount": 3, "speed": 2, "interval": 60, "customText": "Set"},
    {"label": "Sit-ups",       "icon": "🔥", "maxCount": 30, "repeatCount": 3, "speed": 3, "interval": 45, "customText": "Set"},
]

# ── Text-to-Speech ────────────────────────────────────────────────────────────
_engine = None

def _init_tts():
    global _engine, TTS_AVAILABLE
    if not TTS_AVAILABLE:
        return
    try:
        _engine = pyttsx3.init()
        voices = _engine.getProperty('voices')
        for v in voices:
            if 'female' in v.name.lower():
                _engine.setProperty('voice', v.id)
                break
        _engine.setProperty('rate', 150)
    except Exception:
        TTS_AVAILABLE = False

def speak(text):
    """Speak text aloud."""
    print(f"  {CYAN}🔊 {text}{RESET}")
    if not TTS_AVAILABLE or _engine is None:
        return
    try:
        _engine.say(str(text))
        _engine.runAndWait()
    except Exception:
        pass

# ── Settings ──────────────────────────────────────────────────────────────────
def load_presets():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                data = json.load(f)
                return data.get("presets", DEFAULT_PRESETS)
        except Exception:
            pass
    return [p.copy() for p in DEFAULT_PRESETS]

def save_presets(presets):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"presets": presets}, f, indent=2)
    except Exception:
        pass

# ── UI Helpers ────────────────────────────────────────────────────────────────
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def bar(pct, width=40):
    filled = int(width * pct / 100)
    return f"[{GREEN}{'█' * filled}{DIM}{'░' * (width - filled)}{RESET}] {pct:3d}%"

def fmt_time(seconds):
    return f"{seconds // 60:02d}:{seconds % 60:02d}"

def print_header(title="Voice Counter"):
    print(f"\n{BOLD}{BLUE}{'═' * 52}{RESET}")
    print(f"{BOLD}{WHITE}  🏋  {title}{RESET}")
    print(f"{BOLD}{BLUE}{'═' * 52}{RESET}\n")

def input_int(prompt, default, lo, hi):
    while True:
        raw = input(f"  {prompt} [{default}]: ").strip()
        if raw == "":
            return default
        try:
            val = int(raw)
            if lo <= val <= hi:
                return val
            print(f"  {YELLOW}Enter a number between {lo} and {hi}.{RESET}")
        except ValueError:
            print(f"  {YELLOW}Please enter a number.{RESET}")

# ── Counting Engine ───────────────────────────────────────────────────────────
def get_numbers_to_say(max_count, speed):
    if speed <= 2:
        return set(range(1, max_count + 1))
    elif speed <= 4:
        return set(range(2, max_count + 1, 2))
    elif speed <= 6:
        return set(range(3, max_count + 1, 3))
    else:
        return set(range(5, max_count + 1, 5))

def run_exercise(preset):
    """Run a single preset exercise with live terminal output."""
    m          = preset["maxCount"]
    n          = preset["repeatCount"]
    speed      = preset["speed"]
    interval   = preset["interval"]
    label      = preset["label"]
    icon       = preset["icon"]
    ctext      = preset["customText"]
    delay      = 1.0 / speed
    to_say     = get_numbers_to_say(m, speed)
    stop_flag  = threading.Event()
    start_time = time.time()

    # Key-press listener (press Q to stop)
    def key_listener():
        try:
            import tty, termios
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                while not stop_flag.is_set():
                    ch = sys.stdin.read(1)
                    if ch.lower() == 'q':
                        stop_flag.set()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
        except Exception:
            pass  # Windows / environments without tty

    listener = threading.Thread(target=key_listener, daemon=True)
    listener.start()

    def redraw(rep, count, status, pct):
        clear()
        elapsed = int(time.time() - start_time)
        print_header(f"{icon}  {label}")
        print(f"  {BOLD}Timer:{RESET}   {CYAN}{fmt_time(elapsed)}{RESET}")
        print(f"  {BOLD}Status:{RESET}  {YELLOW}{status}{RESET}")
        print(f"  {BOLD}{ctext}:{RESET}   {WHITE}{rep} / {n}{RESET}")
        print()
        if count:
            print(f"  {BOLD}{CYAN}{'Count':^10}{RESET}")
            print(f"  {BOLD}{GREEN}{str(count):^10}{RESET}")
        print()
        print(f"  {bar(pct)}")
        print()
        print(f"  {DIM}Press  Q  to stop{RESET}\n")

    total_counts = m * n
    completed    = 0

    for rep in range(1, n + 1):
        if stop_flag.is_set():
            break

        pct = int(completed / total_counts * 100)
        redraw(rep, "", f"Starting {ctext} {rep}...", pct)
        speak(f"{ctext} {rep}")
        time.sleep(delay * 2)

        for num in range(1, m + 1):
            if stop_flag.is_set():
                break

            completed += 1
            pct = int(completed / total_counts * 100)
            redraw(rep, num, "Counting...", pct)

            if num in to_say:
                speak(num)

            time.sleep(delay)

        if stop_flag.is_set():
            break

        # Rest between sets
        if rep < n:
            for remaining in range(interval, 0, -1):
                if stop_flag.is_set():
                    break
                clear()
                elapsed = int(time.time() - start_time)
                print_header(f"{icon}  {label}")
                print(f"  {BOLD}Timer:{RESET}   {CYAN}{fmt_time(elapsed)}{RESET}")
                print(f"  {BOLD}Status:{RESET}  {YELLOW}Rest — next {ctext} in {remaining}s{RESET}")
                print(f"  {BOLD}{ctext}:{RESET}   {WHITE}{rep} / {n}  completed{RESET}")
                print()
                print(f"  {bar(int(completed / total_counts * 100))}")
                print()
                print(f"  {DIM}Press  Q  to stop{RESET}\n")
                time.sleep(1)

    stop_flag.set()

    # Final screen
    if completed >= total_counts:
        clear()
        elapsed = int(time.time() - start_time)
        print_header(f"{icon}  {label}")
        print(f"  {BOLD}Timer:{RESET}   {CYAN}{fmt_time(elapsed)}{RESET}")
        print(f"  {BOLD}{GREEN}✓  Workout complete!{RESET}")
        print(f"  {BOLD}{ctext}s:{RESET}  {WHITE}{n} / {n}{RESET}")
        print()
        print(f"  {bar(100)}")
        print()
        speak("All complete")
        input(f"\n  {DIM}Press Enter to return to the menu...{RESET}")
    else:
        clear()
        print_header(f"{icon}  {label}")
        print(f"  {RED}■  Stopped.{RESET}\n")
        input(f"\n  {DIM}Press Enter to return to the menu...{RESET}")

# ── Settings Menu ─────────────────────────────────────────────────────────────
def settings_menu(presets):
    while True:
        clear()
        print_header("Settings — Edit Presets")
        for i, p in enumerate(presets, 1):
            print(f"  {BOLD}{i}.{RESET} {p['icon']} {p['label']:<16} "
                  f"{DIM}{p['maxCount']} reps x {p['repeatCount']} sets  "
                  f"speed={p['speed']}  rest={p['interval']}s{RESET}")
        print(f"\n  {BOLD}0.{RESET} Back\n")

        choice = input(f"  Select preset to edit (1-{len(presets)}): ").strip()
        if choice == "0" or choice == "":
            break
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(presets):
                edit_preset(presets, idx)
            else:
                print(f"  {YELLOW}Invalid choice.{RESET}")
                time.sleep(1)
        except ValueError:
            pass

def edit_preset(presets, idx):
    p = presets[idx]
    clear()
    print_header(f"Edit: {p['icon']} {p['label']}")

    label      = input(f"  Label         [{p['label']}]: ").strip() or p['label']
    max_count  = input_int("Max count (reps)", p['maxCount'],  1, 9999)
    repeat_cnt = input_int("Repeat count    ", p['repeatCount'], 1, 100)
    speed      = input_int("Speed (1-10)    ", p['speed'],       1, 10)
    interval   = input_int("Rest (seconds)  ", p['interval'],    0, 600)
    ctext      = input(f"  Set label     [{p['customText']}]: ").strip() or p['customText']

    presets[idx].update({
        "label": label, "maxCount": max_count, "repeatCount": repeat_cnt,
        "speed": speed, "interval": interval, "customText": ctext,
    })
    save_presets(presets)
    print(f"\n  {GREEN}Saved!{RESET}")
    time.sleep(1)

# ── Main Menu ─────────────────────────────────────────────────────────────────
def main():
    _init_tts()
    presets = load_presets()

    if not TTS_AVAILABLE:
        print(f"\n{YELLOW}  Warning: pyttsx3 not found - running in silent mode.")
        print(f"  Install it with:  pip install pyttsx3{RESET}\n")
        time.sleep(2)

    while True:
        clear()
        print_header()
        print(f"  {BOLD}Choose an exercise:{RESET}\n")

        for i, p in enumerate(presets, 1):
            print(f"  {BOLD}{CYAN}{i}.{RESET} {p['icon']} {p['label']:<16} "
                  f"{DIM}{p['maxCount']} reps x {p['repeatCount']} sets{RESET}")

        print(f"\n  {BOLD}S.{RESET} Settings")
        print(f"  {BOLD}Q.{RESET} Quit\n")

        choice = input(f"  Your choice: ").strip().lower()

        if choice == 'q':
            clear()
            print(f"\n  {GREEN}Goodbye! Stay active!{RESET}\n")
            break
        elif choice == 's':
            settings_menu(presets)
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(presets):
                    run_exercise(presets[idx])
                else:
                    print(f"  {YELLOW}Invalid choice.{RESET}")
                    time.sleep(1)
            except ValueError:
                print(f"  {YELLOW}Invalid choice.{RESET}")
                time.sleep(1)

if __name__ == "__main__":
    main()
