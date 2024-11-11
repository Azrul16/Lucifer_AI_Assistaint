import os
import re
import pygame
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
from gpt4all import GPT4All
import speech_recognition as sr
from datetime import date
from gtts import gTTS
from io import BytesIO
from pygame import mixer
import time


pygame.init()
pygame.mixer.init()


# Define the model path and type
model_path = "D:/Github/Lucifer_AI_Assistaint/lucifer/model/"
model_type = "llama"
model_no=1
model_no =int(input("Which Data Model you want?\n1. LLama 3.2 1B(Take less time to generate short answer)\n2. Custom Dataset 7B(Take more time for efficient answer)"))


#Generating cleen text
def clean_text_regex(text):
    # Remove '*' and '#' using regex
    cleaned_text = re.sub(r'[*#?,]', '', text)
    return cleaned_text

# Load the GPT4All model
print("Loading the model, please wait...")
try:
    # Here we pass a dummy model name ('local_model') since GPT4All expects it
    model_name = "Llama-3.2-1B-Instruct-Q4_K_M" if model_no == 1 else "local_model"

    model = GPT4All(model_name=model_name, model_path=model_path, model_type=model_type, allow_download=False)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Failed to load the model: {e}")
    exit(1)

# Function to generate a response from the chatbot (faster and shorter)
def chatbot_response(prompt):
    if any(word in prompt for word in ("quit", "bye", "exit", "terminate")):
         speak_text("Goodbye!")
         exit()

    prompt = prompt + ". give one line answer"
    try:
        # Increase the max_tokens to prevent incomplete answers
        response = model.generate(
            prompt, 
            max_tokens=150,   # Increased tokens to allow for a complete response
            temp=0.5,         # Set temperature to moderate to keep a good balance between randomness and coherence
            top_p=0.9,        # Set top_p to a moderate value for diversity
        )
        text= clean_text_regex(response.strip())
        
        print(text)
        #speak_text(text)
        return text
    except Exception as e:
        return f"Error generating response: {str(e)}"
def speak_text(text):
    mp3file = BytesIO()
    tts = gTTS(text, lang="en", tld='us')
    tts.write_to_fp(mp3file)
    mp3file.seek(0)
    mixer.music.load(mp3file)
    mixer.music.play()
    while mixer.music.get_busy():
        time.sleep(0.1)

# Main function
def main():
    global today, numtext, numtts, numaudio, messages
    rec = sr.Recognizer()
    mic = sr.Microphone()
    while True:
        with mic as source:
            rec.adjust_for_ambient_noise(source, duration=1)
            print("Listening ...")
            speak_text('Listening')
            
            try:
                # Capture audio input
                audio = rec.listen(source, timeout=40, phrase_time_limit=30)
                # Recognize speech using Google Web Speech API
                text = rec.recognize_google(audio, language="en-EN")

                # Print recognized text in terminal
                print(f"Recognized Text: {text}")

                # Read out the recognized text using Text-to-Speech
                #speak_text(f"{text}")
                #Generate the response from the Llama
                #generate_response(text=text)
                chatbot_response(text)


            except sr.UnknownValueError:
                print("Could not understand audio.")
            except sr.RequestError as e:
                print(f"Speech Recognition error: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
        mixer.music.stop()
