import tkinter as tk
from tkinter import scrolledtext
import threading
import speech_recognition as sr
from main import processCommand, speak  # Assuming these functions are defined in main.py

class FridayVoiceAssistantApp:
    def __init__(self, root):  # Correct constructor
        self.root = root
        self.root.title("Lucifer Voice Assistant")
        self.root.geometry("800x600")
        self.root.config(bg="#1a1a2e")

        # Main container with background color
        self.main_container = tk.Frame(root, bg="#1a1a2e")
        self.main_container.pack(expand=True, fill="both", padx=10, pady=5)

        # Title label with gradient-style color
        self.title_label = tk.Label(
            self.main_container, text="Friday Voice Assistant",
            font=("Helvetica", 24, "bold"),
            fg="#00d4ff", bg="#1a1a2e"
        )
        self.title_label.pack(pady=10)

        # Chat display area with contrasting background
        self.chat_frame = tk.Frame(self.main_container, bg="#0f3460")
        self.chat_frame.pack(expand=True, fill="both", pady=10)

        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            font=("Helvetica", 11),
            bg="#0f3460",
            fg="white",
            height=15
        )
        self.chat_display.pack(expand=True, fill="both", padx=5, pady=5)
        self.chat_display.config(state='disabled')

        # Status and controls container with lighter background
        self.controls_frame = tk.Frame(self.main_container, bg="#1a1a2e")
        self.controls_frame.pack(fill="x", pady=10)

        # Status label with vibrant color to indicate action
        self.status_label = tk.Label(
            self.controls_frame,
            text="Click 'Start Listening' to activate Friday.",
            font=("Helvetica", 12),
            fg="#e94560",
            bg="#1a1a2e",
            wraplength=400,
            justify="center"
        )
        self.status_label.pack(pady=5)

        # Buttons container
        self.buttons_frame = tk.Frame(self.controls_frame, bg="#1a1a2e")
        self.buttons_frame.pack(pady=5)

        # Start button with green theme
        self.start_button = tk.Button(
            self.buttons_frame,
            text="Start Listening",
            command=self.start_listening,
            font=("Helvetica", 12),
            bg="#22b573",
            fg="white",
            activebackground="#1f8e5d",
            width=15,
            height=1
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        # Stop button with red theme
        self.stop_button = tk.Button(
            self.buttons_frame,
            text="Stop",
            command=self.stop_listening,
            font=("Helvetica", 12),
            bg="#e94560",
            fg="white",
            activebackground="#c72d45",
            width=15,
            height=1
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Clear button with gray theme
        self.clear_button = tk.Button(
            self.buttons_frame,
            text="Clear Chat",
            command=self.clear_chat,
            font=("Helvetica", 12),
            bg="#525252",
            fg="white",
            activebackground="#3d3d3d",
            width=15,
            height=1
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Initialize recognizer and listening state
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.listen_thread = None

    def add_to_chat(self, speaker, message, color="#ffffff"):
        """Add a message to the chat display and print it to the terminal"""
        print(f"{speaker}: {message}")  # Print to terminal
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{speaker}: ", f"speaker_{color}")
        self.chat_display.insert(tk.END, f"{message}\n\n")
        self.chat_display.tag_config(f"speaker_{color}", foreground=color)
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')

    def clear_chat(self):
        """Clear the chat display"""
        self.chat_display.config(state='normal')
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state='disabled')

    def start_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.status_label.config(text="Listening for the wake word...", fg="#00d4ff")
            self.listen_thread = threading.Thread(target=self.listen_for_command, daemon=True)
            self.listen_thread.start()

    def stop_listening(self):
        self.is_listening = False
        self.status_label.config(text="Stopped listening.", fg="white")

    def custom_process_command(self, command):
        """Wrapper for processCommand to capture the response"""
        # Add user command to chat and print to terminal
        self.add_to_chat("You", command, "#00d4ff")
        
        # Store the original speak function
        original_speak = speak
        
        # Create a wrapper for the speak function
        def speak_wrapper(text):
            # Add Friday's response to chat and print to terminal
            self.root.after(0, lambda: self.add_to_chat("Friday", text, "#e94560"))
            print(f"Friday: {text}")  # Print to terminal
            # Call the original speak function
            original_speak(text)
        
        # Temporarily replace the speak function
        import main
        main.speak = speak_wrapper
        
        # Process the command
        try:
            processCommand(command)
        finally:
            # Restore the original speak function
            main.speak = original_speak

    def listen_for_command(self):
        while self.is_listening:
            try:
                with sr.Microphone() as source:
                    self.status_label.config(text="Listening for wake word...", fg="#00d4ff")
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)

                    if not self.is_listening:
                        break

                    word = self.recognizer.recognize_google(audio)
                    print(f"You said (wake word): {word}")  # Print to terminal

                    if word.lower() == "friday" and self.is_listening:
                        wake_response = "Yes! How may I help you?"
                        speak(wake_response)
                        self.add_to_chat("Friday", wake_response, "#e94560")
                        
                        self.status_label.config(text="Listening for command...", fg="#00d4ff")
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                        command = self.recognizer.recognize_google(audio)
                        print(f"You said: {command}")  # Print to terminal
                        
                        self.custom_process_command(command)
                        self.status_label.config(text="Command processed. Say 'Friday' to give another command.", fg="white")

            except Exception as e:
                print("Error while listening: ", e)  # Print error to terminal
                self.status_label.config(text="Error encountered. Try again.", fg="red")
                if not self.is_listening:
                    break

if __name__ == "__main__":  # Corrected if statement
    root = tk.Tk()
    app = FridayVoiceAssistantApp(root)
    root.mainloop()
