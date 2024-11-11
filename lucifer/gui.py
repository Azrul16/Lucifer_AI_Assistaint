import tkinter as tk
from tkinter import scrolledtext
import threading
import speech_recognition as sr
from main import chatbot_response, speak_text  # Assuming these functions are defined in main.py

class LuciferVoiceAssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lucifer Voice Assistant")
        self.root.geometry("800x700")
        self.root.config(bg="#4a3f35")  # Dark orange background

        # Main container
        self.main_container = tk.Frame(root, bg="#4a3f35")
        self.main_container.pack(expand=True, fill="both", padx=10, pady=5)

        # Title label
        self.title_label = tk.Label(
            self.main_container, text="Lucifer Voice Assistant",
            font=("Helvetica", 24, "bold"),
            fg="#ffcc00", bg="#4a3f35"
        )
        self.title_label.pack(pady=10)

        # Chat display area
        self.chat_frame = tk.Frame(self.main_container, bg="#ff8c00")
        self.chat_frame.pack(expand=True, fill="both", pady=10)

        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            font=("Helvetica", 11),
            bg="#ff8c00",
            fg="white",
            height=15
        )
        self.chat_display.pack(expand=True, fill="both", padx=5, pady=5)
        self.chat_display.config(state='disabled')

        # Status and controls container
        self.controls_frame = tk.Frame(self.main_container, bg="#4a3f35")
        self.controls_frame.pack(fill="x", pady=10)

        # Status label
        self.status_label = tk.Label(
            self.controls_frame,
            text="Say 'Lucifer' to start listening for commands.",
            font=("Helvetica", 12),
            fg="#ffcc00",
            bg="#4a3f35",
            wraplength=400,
            justify="center"
        )
        self.status_label.pack(pady=5)

        # Text input area for typed commands
        self.text_input_frame = tk.Frame(self.main_container, bg="#4a3f35")
        self.text_input_frame.pack(fill="x", pady=10)

        self.text_entry = tk.Entry(
            self.text_input_frame,
            font=("Helvetica", 12),
            bg="#ffcc66",
            fg="black",
            width=50
        )
        self.text_entry.pack(side=tk.LEFT, padx=5, pady=5)

        # Send button for text input
        self.send_button = tk.Button(
            self.text_input_frame,
            text="Send",
            command=self.send_text_command,
            font=("Helvetica", 12),
            bg="#ff8c00",
            fg="white",
            activebackground="#d2691e",
            width=10
        )
        self.send_button.pack(side=tk.LEFT, padx=5)

        # Initialize recognizer and listening state
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.listen_thread = None
        self.wake_word = "lucifer"
        self.exit_commands = ["bye", "exit"]

        # Start the listening process as soon as the app runs
        self.start_listening()

    def add_to_chat(self, speaker, message, color="#ffffff"):
        """Add a message to the chat display and update it properly."""
        self.chat_display.config(state='normal')  # Enable editing

        # Add the speaker's message
        self.chat_display.insert(tk.END, f"{speaker}: ", "bold")
        self.chat_display.insert(tk.END, f"{message}\n\n", f"speaker_{color}")

        # Set up styles for speaker and message
        self.chat_display.tag_config("bold", font=("Helvetica", 11, "bold"))
        self.chat_display.tag_config(f"speaker_{color}", foreground=color)

        self.chat_display.see(tk.END)  # Scroll to the end of the chat
        self.chat_display.config(state='disabled')  # Disable editing again to prevent manual changes

    def start_listening(self):
        """Start listening for the wake word"""
        speak_text("Listening")
        if not self.is_listening:
            self.is_listening = True
            self.status_label.config(text="Listening for 'Lucifer'...", fg="#ffcc00")
            self.listen_thread = threading.Thread(target=self.listen_for_wake_word, daemon=True)
            self.listen_thread.start()

    def stop_listening(self):
        """Stop the listening process"""
        self.is_listening = False
        self.status_label.config(text="Stopped listening.", fg="white")

    def listen_for_wake_word(self):
        """Continuously listen for the wake word"""
        while self.is_listening:
            try:
                with sr.Microphone() as source:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    command = self.recognizer.recognize_google(audio).lower()

                    if self.wake_word in command:
                        self.status_label.config(text="Listening for commands...", fg="#ffcc00")
                        self.listen_for_command()  # After wake word, listen for commands
                        break  # Break out of this loop to avoid repeated wake word detection

            except sr.UnknownValueError:
                pass  # Ignore if nothing is heard
            except sr.RequestError:
                self.add_to_chat("Lucifer", "Network error. Please check your connection.", "#e94560")
            except Exception as e:
                print("Error while listening for wake word: ", e)

    def listen_for_command(self):
        """Listen for commands once the wake word is detected"""
        while self.is_listening:
            try:
                with sr.Microphone() as source:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    command = self.recognizer.recognize_google(audio).lower()

                    if any(exit_word in command for exit_word in self.exit_commands):
                        self.stop_listening()
                        self.add_to_chat("Lucifer", "Goodbye! Exiting listening mode.", "#e94560")
                        break  # Exit listening loop

                    print(f"You said: {command}")
                    self.custom_process_command(command)

            except sr.UnknownValueError:
                pass  # Ignore if nothing is heard
            except sr.RequestError:
                self.add_to_chat("Lucifer", "Network error. Please check your connection.", "#e94560")
            except Exception as e:
                print("Error while listening: ", e)
                self.status_label.config(text="Error encountered. Try again.", fg="#e94560")

    def custom_process_command(self, command):
        """Wrapper for processCommand to capture the response"""
        self.add_to_chat("You", command, "#ffcc66")
        # Use threading to avoid blocking the main thread
        threading.Thread(target=self.get_chatbot_response, args=(command,), daemon=True).start()

    def get_chatbot_response(self, command):
        """Get the response from the chatbot and update the UI"""
        try:
            response = chatbot_response(command)  # Assuming this function is blocking
            self.add_to_chat("Lucifer", response, "#ff8c00")
        except Exception as e:
            print(f"Error while getting chatbot response: {e}")
            self.add_to_chat("Lucifer", "Sorry, I couldn't process that. Please try again.", "#e94560")

    def send_text_command(self):
        """Process the command entered in the text input field"""
        command = self.text_entry.get().strip()
        if command:
            self.text_entry.delete(0, tk.END)
            self.custom_process_command(command)

if __name__ == "__main__":
    root = tk.Tk()
    app = LuciferVoiceAssistantApp(root)
    root.mainloop()
