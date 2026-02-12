import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pyttsx3
import json
import os
from datetime import datetime, timedelta
import threading
import time

class VoiceCountingProgram:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Counting Program")
        self.root.geometry("500x700")
        self.root.configure(bg='#667eea')
        
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        # Try to set female voice
        for voice in voices:
            if 'female' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('pitch', 1.2)
        
        # State variables
        self.is_running = False
        self.running_preset_index = -1
        self.current_repeat = 0
        self.current_number = 0
        self.timer_running = False
        self.elapsed_time = 0
        self.start_time = None
        
        # Settings file
        self.settings_file = 'voice_counter_settings.json'
        
        # Initialize presets
        self.presets = [
            {"label": "Push-ups", "icon": "💪", "maxCount": 20, "repeatCount": 3, "speed": 2, "interval": 30, "customText": "Set"},
            {"label": "Squats", "icon": "🦵", "maxCount": 25, "repeatCount": 4, "speed": 2, "interval": 45, "customText": "Round"},
            {"label": "Jumping Jacks", "icon": "🤸", "maxCount": 30, "repeatCount": 3, "speed": 3, "interval": 30, "customText": "Set"},
            {"label": "Plank", "icon": "🧘", "maxCount": 60, "repeatCount": 3, "speed": 5, "interval": 60, "customText": "Hold"},
            {"label": "Burpees", "icon": "🏃", "maxCount": 15, "repeatCount": 3, "speed": 2, "interval": 60, "customText": "Set"},
            {"label": "Sit-ups", "icon": "🔥", "maxCount": 30, "repeatCount": 3, "speed": 3, "interval": 45, "customText": "Set"}
        ]
        
        self.load_settings()
        self.create_widgets()
        
    def load_settings(self):
        """Load settings from file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    self.presets = data.get('presets', self.presets)
            except:
                pass
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump({'presets': self.presets}, f, indent=2)
        except:
            pass
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#667eea')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="Voice Counter", 
                              font=("Segoe UI", 28, "bold"), 
                              bg='#667eea', fg='white')
        title_label.pack(pady=(0, 20))
        
        # Container frame
        container = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=2)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Progress screen (initially hidden)
        self.progress_frame = tk.Frame(container, bg='white')
        
        # Timer display
        timer_frame = tk.Frame(self.progress_frame, bg='#f0f0f0')
        timer_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        self.timer_label = tk.Label(timer_frame, text="00:00", 
                                    font=("Segoe UI", 20, "bold"), 
                                    bg='#f0f0f0')
        self.timer_label.pack()
        
        # Current count display
        self.count_display = tk.Label(self.progress_frame, text="", 
                                     font=("Segoe UI", 72, "bold"), 
                                     bg='white', fg='#667eea')
        self.count_display.pack(pady=20)
        
        # Status and repeat indicator
        self.status_label = tk.Label(self.progress_frame, text="Ready", 
                                    font=("Segoe UI", 16), 
                                    bg='white', fg='#666')
        self.status_label.pack()
        
        self.repeat_label = tk.Label(self.progress_frame, text="", 
                                    font=("Segoe UI", 14), 
                                    bg='white', fg='#999')
        self.repeat_label.pack(pady=5)
        
        # Progress bar
        progress_container = tk.Frame(self.progress_frame, bg='white')
        progress_container.pack(fill=tk.X, padx=20, pady=20)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_container, 
                                           variable=self.progress_var, 
                                           maximum=100)
        self.progress_bar.pack(fill=tk.X)
        
        self.progress_text = tk.Label(progress_container, text="0%", 
                                     font=("Segoe UI", 12), 
                                     bg='white')
        self.progress_text.pack()
        
        # Control buttons
        button_frame = tk.Frame(self.progress_frame, bg='white')
        button_frame.pack(pady=20)
        
        self.stop_button = tk.Button(button_frame, text="⏹ Stop", 
                                    font=("Segoe UI", 14, "bold"),
                                    bg='#f44336', fg='white',
                                    width=15, height=2,
                                    command=self.handle_stop)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.back_button = tk.Button(button_frame, text="← Back", 
                                    font=("Segoe UI", 14),
                                    bg='#999', fg='white',
                                    width=15, height=2,
                                    command=self.show_main_screen)
        self.back_button.pack(side=tk.LEFT, padx=5)
        
        # Main screen with preset buttons
        self.main_frame = tk.Frame(container, bg='white')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Settings button
        settings_btn = tk.Button(self.main_frame, text="⚙", 
                                font=("Segoe UI", 16),
                                command=self.show_settings,
                                width=3, height=1)
        settings_btn.pack(anchor=tk.NE, pady=(0, 10))
        
        # Preset buttons grid
        presets_frame = tk.Frame(self.main_frame, bg='white')
        presets_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preset_buttons = []
        for i, preset in enumerate(self.presets):
            row = i // 3
            col = i % 3
            
            btn = tk.Button(presets_frame, 
                          text=f"{preset['icon']}\n{preset['label']}\n{preset['maxCount']}x{preset['repeatCount']}",
                          font=("Segoe UI", 10, "bold"),
                          bg='#667eea', fg='white',
                          width=12, height=6,
                          command=lambda idx=i: self.start_exercise(idx))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            self.preset_buttons.append(btn)
        
        # Configure grid weights
        for i in range(3):
            presets_frame.columnconfigure(i, weight=1)
        for i in range(2):
            presets_frame.rowconfigure(i, weight=1)
    
    def show_main_screen(self):
        """Show main screen with preset buttons"""
        self.progress_frame.pack_forget()
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    def show_progress_screen(self):
        """Show progress screen"""
        self.main_frame.pack_forget()
        self.progress_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    def show_settings(self):
        """Show settings dialog for editing presets"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x500")
        settings_window.configure(bg='white')
        
        # List of presets
        preset_list = tk.Listbox(settings_window, font=("Segoe UI", 12), height=10)
        preset_list.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        for i, preset in enumerate(self.presets):
            preset_list.insert(tk.END, f"{preset['icon']} {preset['label']} - {preset['maxCount']}x{preset['repeatCount']}")
        
        # Button frame
        btn_frame = tk.Frame(settings_window, bg='white')
        btn_frame.pack(pady=10)
        
        def edit_preset():
            selection = preset_list.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a preset to edit")
                return
            
            idx = selection[0]
            self.edit_preset_dialog(idx, settings_window)
        
        tk.Button(btn_frame, text="Edit", command=edit_preset, 
                 font=("Segoe UI", 12), width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Close", command=settings_window.destroy, 
                 font=("Segoe UI", 12), width=10).pack(side=tk.LEFT, padx=5)
    
    def edit_preset_dialog(self, idx, parent):
        """Edit a preset"""
        preset = self.presets[idx]
        
        edit_window = tk.Toplevel(parent)
        edit_window.title(f"Edit {preset['label']}")
        edit_window.geometry("350x400")
        edit_window.configure(bg='white')
        
        # Label
        tk.Label(edit_window, text="Label:", font=("Segoe UI", 12), 
                bg='white').pack(pady=(20, 5))
        label_entry = tk.Entry(edit_window, font=("Segoe UI", 12), width=30)
        label_entry.insert(0, preset['label'])
        label_entry.pack()
        
        # Max Count
        tk.Label(edit_window, text="Max Count:", font=("Segoe UI", 12), 
                bg='white').pack(pady=(10, 5))
        max_count_entry = tk.Entry(edit_window, font=("Segoe UI", 12), width=30)
        max_count_entry.insert(0, str(preset['maxCount']))
        max_count_entry.pack()
        
        # Repeat Count
        tk.Label(edit_window, text="Repeat Count:", font=("Segoe UI", 12), 
                bg='white').pack(pady=(10, 5))
        repeat_count_entry = tk.Entry(edit_window, font=("Segoe UI", 12), width=30)
        repeat_count_entry.insert(0, str(preset['repeatCount']))
        repeat_count_entry.pack()
        
        # Speed
        tk.Label(edit_window, text="Speed (1-10):", font=("Segoe UI", 12), 
                bg='white').pack(pady=(10, 5))
        speed_entry = tk.Entry(edit_window, font=("Segoe UI", 12), width=30)
        speed_entry.insert(0, str(preset['speed']))
        speed_entry.pack()
        
        # Interval
        tk.Label(edit_window, text="Interval (seconds):", font=("Segoe UI", 12), 
                bg='white').pack(pady=(10, 5))
        interval_entry = tk.Entry(edit_window, font=("Segoe UI", 12), width=30)
        interval_entry.insert(0, str(preset['interval']))
        interval_entry.pack()
        
        def save_changes():
            try:
                self.presets[idx]['label'] = label_entry.get()
                self.presets[idx]['maxCount'] = int(max_count_entry.get())
                self.presets[idx]['repeatCount'] = int(repeat_count_entry.get())
                self.presets[idx]['speed'] = int(speed_entry.get())
                self.presets[idx]['interval'] = int(interval_entry.get())
                
                self.save_settings()
                self.update_preset_buttons()
                edit_window.destroy()
                messagebox.showinfo("Success", "Preset updated successfully!")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers")
        
        tk.Button(edit_window, text="Save", command=save_changes, 
                 font=("Segoe UI", 12, "bold"), bg='#4CAF50', fg='white',
                 width=15).pack(pady=20)
    
    def update_preset_buttons(self):
        """Update preset button labels"""
        for i, (btn, preset) in enumerate(zip(self.preset_buttons, self.presets)):
            btn.config(text=f"{preset['icon']}\n{preset['label']}\n{preset['maxCount']}x{preset['repeatCount']}")
    
    def start_exercise(self, preset_idx):
        """Start exercise with selected preset"""
        if self.is_running:
            return
        
        self.running_preset_index = preset_idx
        self.current_repeat = 0
        self.current_number = 0
        self.is_running = True
        self.elapsed_time = 0
        self.start_time = time.time()
        
        # Update UI
        self.progress_var.set(0)
        self.progress_text.config(text="0%")
        self.count_display.config(text="")
        self.status_label.config(text="Starting...")
        
        preset = self.presets[preset_idx]
        self.repeat_label.config(text=f"{preset['customText']} 0 of {preset['repeatCount']}")
        
        # Show progress screen
        self.show_progress_screen()
        
        # Start timer
        self.start_timer()
        
        # Start counting in a separate thread
        count_thread = threading.Thread(target=self.count_loop, daemon=True)
        count_thread.start()
    
    def start_timer(self):
        """Start the timer"""
        self.timer_running = True
        self.update_timer()
    
    def update_timer(self):
        """Update timer display"""
        if self.timer_running:
            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_timer)
    
    def stop_timer(self):
        """Stop the timer"""
        self.timer_running = False
    
    def get_numbers_to_say(self, max_count, speed):
        """Determine which numbers to say based on speed"""
        if speed <= 2:
            return list(range(1, max_count + 1))
        elif speed <= 4:
            return list(range(2, max_count + 1, 2))
        elif speed <= 6:
            return list(range(3, max_count + 1, 3))
        else:
            return list(range(5, max_count + 1, 5))
    
    def speak(self, text):
        """Speak text using text-to-speech"""
        try:
            self.engine.say(str(text))
            self.engine.runAndWait()
        except:
            pass
    
    def count_loop(self):
        """Main counting loop"""
        preset = self.presets[self.running_preset_index]
        max_count = preset['maxCount']
        repeat_count = preset['repeatCount']
        speed = preset['speed']
        interval = preset['interval']
        delay = 1.0 / speed
        
        numbers_to_say = self.get_numbers_to_say(max_count, speed)
        
        for rep in range(repeat_count):
            if not self.is_running:
                return
            
            self.current_repeat = rep
            
            # Announce set
            self.root.after(0, lambda r=rep: self.repeat_label.config(
                text=f"{preset['customText']} {r + 1} of {repeat_count}"))
            self.speak(f"{preset['customText']} {rep + 1}")
            time.sleep(delay * 2)
            
            # Count
            for num in range(1, max_count + 1):
                if not self.is_running:
                    return
                
                self.current_number = num
                self.root.after(0, lambda n=num: self.count_display.config(text=str(n)))
                self.root.after(0, lambda r=rep, n=num: self.repeat_label.config(
                    text=f"{preset['customText']} {r + 1} of {repeat_count} - Count {n} of {max_count}"))
                self.root.after(0, lambda: self.status_label.config(text="Counting..."))
                
                if num in numbers_to_say:
                    self.speak(num)
                
                # Update progress
                total_counts = max_count * repeat_count
                completed_counts = (rep * max_count) + num
                percentage = int((completed_counts / total_counts) * 100)
                self.root.after(0, lambda p=percentage: self.progress_var.set(p))
                self.root.after(0, lambda p=percentage: self.progress_text.config(text=f"{p}%"))
                
                time.sleep(delay)
            
            # Pause between sets
            if rep < repeat_count - 1:
                self.root.after(0, lambda: self.status_label.config(text="Pausing..."))
                time.sleep(interval)
        
        # Finish
        self.finish()
    
    def finish(self):
        """Complete the exercise"""
        self.is_running = False
        self.running_preset_index = -1
        self.stop_timer()
        
        self.root.after(0, lambda: self.count_display.config(text="✓"))
        self.root.after(0, lambda: self.status_label.config(text="Completed!"))
        self.root.after(0, lambda: self.repeat_label.config(text="All steps complete!"))
        self.root.after(0, lambda: self.progress_var.set(100))
        self.root.after(0, lambda: self.progress_text.config(text="100%"))
        
        self.speak("All complete")
    
    def handle_stop(self):
        """Stop the current exercise"""
        self.is_running = False
        self.running_preset_index = -1
        self.stop_timer()
        
        self.count_display.config(text="■")
        self.status_label.config(text="Stopped")
        
        # Stop speech
        try:
            self.engine.stop()
        except:
            pass

def main():
    root = tk.Tk()
    app = VoiceCountingProgram(root)
    root.mainloop()

if __name__ == "__main__":
    main()
