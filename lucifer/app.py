import tkinter as tk
from tkinter import scrolledtext
import threading
import speech_recognition as sr
from main import chatbot_response, speak_text
import os

class LuciferVoiceAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lucifer, The Morningstar")
        self.root.geometry("800x700")
        self.root.config(bg="#1e1e1e")  # Dark background

        # Main container with padding and dark background
        self.main_container = tk.Frame(root, bg="#2a2a2a", bd=2, relief="groove")
        self.main_container.pack(expand=True, fill="both", padx=20, pady=20)

        # Title label with a stylish font
        self.title_label = tk.Label(
            self.main_container,
            text="Lucifer, The Morningstar",
            font=("Segoe UI", 26, "bold"),
            fg="#ffcc00",
            bg="#2a2a2a"
        )
        self.title_label.pack(pady=10)

        # Chat display area with a dark theme
        self.chat_frame = tk.Frame(self.main_container, bg="#1e1e1e")
        self.chat_frame.pack(expand=True, fill="both", pady=10)

        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 12),
            bg="#1e1e1e",
            fg="#d4d4d4",
            height=15,
            borderwidth=0,
            insertbackground="white",
            state='normal'  # Initially allow editing to insert history
        )
        self.chat_display.pack(expand=True, fill="both", padx=5, pady=5)
        self.chat_display.config(state='disabled')

        # Status bar with indicator
        self.status_label = tk.Label(
            self.main_container,
            text="Ready to listen for your commands.",
            font=("Segoe UI", 12),
            fg="#00ff00",
            bg="#2a2a2a"
        )
        self.status_label.pack(pady=5)

        # Buttons container with rounded buttons
        self.buttons_frame = tk.Frame(self.main_container, bg="#2a2a2a")
        self.buttons_frame.pack(pady=5)

        # Rounded Start button
        self.start_button = tk.Button(
            self.buttons_frame,
            text="Start Listening",
            command=self.start_listening,
            font=("Segoe UI", 12),
            bg="#ff8c00",
            fg="white",
            activebackground="#d2691e",
            width=20,
            height=2,
            relief="flat",
            bd=0
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        # Rounded Stop button
        self.stop_button = tk.Button(
            self.buttons_frame,
            text="Stop",
            command=self.stop_listening,
            font=("Segoe UI", 12),
            bg="#e94560",
            fg="white",
            activebackground="#c72d45",
            width=20,
            height=2,
            relief="flat",
            bd=0
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Text input area for typed commands with a rounded entry box
        self.text_input_frame = tk.Frame(self.main_container, bg="#2a2a2a")
        self.text_input_frame.pack(fill="x", pady=10)

        self.text_entry = tk.Entry(
            self.text_input_frame,
            font=("Segoe UI", 12),
            bg="#333333",
            fg="white",
            insertbackground="white",
            borderwidth=2,
            relief="flat"
        )
        self.text_entry.pack(side=tk.LEFT, padx=10, pady=10, expand=True, fill="x")

        # Send button with a rounded appearance
        self.send_button = tk.Button(
            self.text_input_frame,
            text="Send",
            command=self.send_text_command,
            font=("Segoe UI", 12),
            bg="#ff8c00",
            fg="white",
            activebackground="#d2691e",
            width=10,
            relief="flat",
            bd=0
        )
        self.send_button.pack(side=tk.RIGHT, padx=10)

        # Initialize recognizer and listening state
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.listen_thread = None

        # Load conversation history
        self.load_history()

    def add_to_chat(self, speaker, message, color="#d4d4d4"):
        """Add a message to the chat display and update it properly."""
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{speaker}: ", "bold")
        self.chat_display.insert(tk.END, f"{message}\n\n", f"speaker_{color}")
        self.chat_display.tag_config("bold", font=("Segoe UI", 12, "bold"))
        self.chat_display.tag_config(f"speaker_{color}", foreground=color)
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')

    def clear_chat(self):
        """Clear the chat display"""
        self.chat_display.config(state='normal')
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state='disabled')

    def start_listening(self):
        speak_text("Listening")
        if not self.is_listening:
            self.is_listening = True
            self.status_label.config(text="Listening for commands...", fg="#00ff00")
            self.listen_thread = threading.Thread(target=self.listen_for_command, daemon=True)
            self.listen_thread.start()

    def stop_listening(self):
        self.is_listening = False
        self.status_label.config(text="Stopped listening.", fg="red")

    def get_chatbot_response(self, command):
        try:
            response = chatbot_response(command)
            self.root.after(0, lambda: self.add_to_chat("Lucifer", response, "#00ff00"))
            self.root.after(0, lambda: speak_text(response))
        except Exception as e:
            error_message = "Sorry, I couldn't process that. Please try again."
            self.root.after(0, lambda: self.add_to_chat("Lucifer", error_message, "#e94560"))
            self.root.after(0, lambda: speak_text(error_message))

    def listen_for_command(self):
        while self.is_listening:
            try:
                with sr.Microphone() as source:
                    self.status_label.config(text="Listening for your command...", fg="#00ff00")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    if not self.is_listening:
                        break
                    command = self.recognizer.recognize_google(audio)
                    self.custom_process_command(command)
            except sr.UnknownValueError:
                self.add_to_chat("Lucifer", "I didn't catch that. Could you please repeat?", "#e94560")
            except sr.RequestError:
                self.add_to_chat("Lucifer", "Network error. Please check your connection.", "#e94560")
            except Exception as e:
                self.status_label.config(text="Error encountered. Try again.", fg="red")

    def send_text_command(self):
        command = self.text_entry.get().strip()
        if command:
            self.text_entry.delete(0, tk.END)
            self.custom_process_command(command)

    def custom_process_command(self, command):
        self.add_to_chat("You", command, "#ffcc66")
        threading.Thread(target=self.get_chatbot_response, args=(command,), daemon=True).start()

    def load_history(self):
        """Load chat history from a file if it exists"""
        if os.path.exists("chat_history.txt"):
            with open("chat_history.txt", "r") as file:
                history = file.read()
                self.chat_display.config(state='normal')
                self.chat_display.insert(tk.END, history)
                self.chat_display.config(state='disabled')

    def save_history(self):
        """Save chat history to a file"""
        with open("chat_history.txt", "w") as file:
            file.write(self.chat_display.get(1.0, tk.END))

    def on_close(self):
        """Override the window close event to save history"""
        self.save_history()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = LuciferVoiceAssistantApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)  # Save history on window close
    root.mainloop()
