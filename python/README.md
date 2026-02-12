# Voice Counting Program (Python Version)

A Python-based voice counting program for exercise routines with text-to-speech functionality.

## Features

- 6 preset exercise programs (Push-ups, Squats, Jumping Jacks, Plank, Burpees, Sit-ups)
- Voice counting with configurable speed
- Customizable exercise parameters
- Progress tracking with visual progress bar
- Timer to track workout duration
- Settings persistence (saves your custom configurations)

## Requirements

- Python 3.7 or higher
- tkinter (usually comes with Python)
- pyttsx3 (text-to-speech library)

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

On Linux, you may also need to install espeak:
```bash
# Ubuntu/Debian
sudo apt-get install espeak

# Fedora
sudo dnf install espeak

# Arch Linux
sudo pacman -S espeak
```

On macOS and Windows, pyttsx3 uses the built-in speech engines.

## Usage

1. Run the program:
```bash
python voice_counter.py
```

2. Click on any preset button to start an exercise

3. The program will:
   - Announce each set number
   - Count out loud based on the speed setting
   - Show progress with a visual progress bar
   - Pause between sets according to the interval setting

4. Use the "Stop" button to stop the exercise at any time

5. Click the "Back" button to return to the main screen

## Customization

Click the ⚙ (settings) button to:
- Edit preset labels
- Change max count (number of reps per set)
- Change repeat count (number of sets)
- Adjust speed (1-10, affects counting speed and which numbers are spoken)
- Modify interval (rest time between sets in seconds)

### Speed Settings:
- Speed 1-2: Says every number
- Speed 3-4: Says every 2nd number
- Speed 5-6: Says every 3rd number
- Speed 7+: Says every 5th number

## Settings Storage

Your custom preset configurations are automatically saved to `voice_counter_settings.json` in the same directory as the program.

## Troubleshooting

**No sound:**
- On Linux: Make sure espeak is installed
- Check your system volume settings
- Verify that pyttsx3 is properly installed

**Window doesn't appear:**
- Make sure tkinter is installed with your Python distribution
- Try: `python -m tkinter` to test if tkinter works

**Text-to-speech errors:**
- Reinstall pyttsx3: `pip install --upgrade --force-reinstall pyttsx3`
- On macOS: System Preferences → Accessibility → Spoken Content → System Voice

## Default Presets

1. **Push-ups** 💪: 20 reps × 3 sets, 30s rest
2. **Squats** 🦵: 25 reps × 4 sets, 45s rest
3. **Jumping Jacks** 🤸: 30 reps × 3 sets, 30s rest
4. **Plank** 🧘: 60 seconds × 3 sets, 60s rest
5. **Burpees** 🏃: 15 reps × 3 sets, 60s rest
6. **Sit-ups** 🔥: 30 reps × 3 sets, 45s rest

## Notes

- The program runs counting in a separate thread to keep the UI responsive
- Settings are automatically saved when you edit presets
- The timer shows elapsed time since the exercise started
- Progress bar shows percentage completion of the entire workout
