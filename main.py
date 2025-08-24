import speech_recognition as sr
import webbrowser
import requests
from gtts import gTTS
import pygame
import os
from spotipy.oauth2 import SpotifyOAuth
import google.generativeai as genai
import musicLibrary
from datetime import datetime
# === API KEYS & CONFIGURATION ===
GEMINI_API_KEY = #API key here
genai.configure(api_key=GEMINI_API_KEY)
newsapi = #API key here
OPENWEATHERMAP_API_KEY = #API key here
scope = "user-read-playback-state,user-modify-playback-state,user-read-currently-playing"

# === INITIALIZATION ===
recognizer = sr.Recognizer()

# Speak function to be used by the command line interface
def speak_and_play(text):
    tts = gTTS(text)
    tts.save('temp.mp3')
    
    pygame.mixer.init()
    pygame.mixer.music.load('temp.mp3')
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.music.unload()
    os.remove("temp.mp3")

# This is the function the API will call. It returns a string.
def aiProcess(command):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(command)
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return "Sorry, I am unable to process that request right now."

def get_weather(city):
    try:
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        complete_url = f"{base_url}q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
        response = requests.get(complete_url)
        data = response.json()
        if data.get("cod") == 200:
            main = data['main']
            weather = data['weather'][0]
            temperature = main['temp']
            humidity = main['humidity']
            description = weather['description']
            return (
                f"The temperature in {city} is {temperature:.1f} degrees Celsius, "
                f"with {description}. The humidity is {humidity} percent."
            )
        else:
            return "Sorry, I could not find the weather for that city."
    except Exception as e:
        print(f"Weather API error: {e}")
        return "Sorry, there was an error fetching the weather."


def processCommand(c):
    c = c.lower()
    if "weather in" in c:
        city = c.split("weather in")[-1].strip()
        return get_weather(city)
    elif "open google" in c:
        webbrowser.open("https://google.com")
        return "Opening Google."
    elif "open facebook" in c:
        webbrowser.open("https://facebook.com")
        return "Opening Facebook."
    elif "open youtube" in c:
        webbrowser.open("https://youtube.com")
        return "Opening YouTube."
    elif "open linkedin" in c:
        webbrowser.open("https://linkedin.com")
        return "Opening LinkedIn."
    elif "open instagram" in c:
        webbrowser.open("https://instagram.com")
        return "Opening Instagram."
    elif c.startswith("play"):
        return "This command is not supported on the web interface."
    elif "news" in c:
        try:
            r = requests.get(f"https://newsapi.org/v2/top-headlines?country=in&apiKey={newsapi}")
            if r.status_code == 200:
                data = r.json()
                articles = data.get('articles', [])
                if articles:
                    titles = [article['title'] for article in articles]
                    return "Here are the top headlines: " + " ".join(titles)
                else:
                    return "Sorry, I couldn't find any news headlines."
            else:
                return "An error occurred while fetching news."
        except Exception as e:
            return f"An error occurred with the news API: {e}"
    elif "date" in c:
        today = datetime.now()
        return f"Today's date is {today.strftime('%A, %B %d, %Y')}."
    else:
        return aiProcess(c)

# This block is for the command line interface
if __name__ == "__main__":
    speak_and_play("Initializing Elena....")
    while True:
        try:
            with sr.Microphone() as source:
                print("Listening for wake word 'Elena'...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=2)
            word = recognizer.recognize_google(audio)
            if word.lower() == "elena":
                speak_and_play("Yes, my lady?")
                with sr.Microphone() as source:
                    print("Elena Active...")
                    recognizer.adjust_for_ambient_noise(source) 
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    command = recognizer.recognize_google(audio)
                    response_text = processCommand(command)
                    speak_and_play(response_text)
        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.WaitTimeoutError:
            print("Listening timed out, waiting for wake word again...")
        except Exception as e:

            print("Error; {0}".format(e))
