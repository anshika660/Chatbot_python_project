from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import warnings
import threading
import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import pyjokes
import wikipedia
import requests

warnings.filterwarnings('ignore')

listener = sr.Recognizer()
app = Flask("__name__")
socketio = SocketIO(app)

def engine_talk(text):
    socketio.emit('synthesia_status', {'isSpeaking': True, 'message': text})
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 180)
    engine.say(text)
    engine.runAndWait()
    socketio.emit('synthesia_status', {'isSpeaking': False, 'message': text})

def user_commands():
    print("Adjusting for ambient noise. Please be quiet...")
    with sr.Microphone() as source:
        listener.adjust_for_ambient_noise(source)
    print("Listening for 'Hey synthesia'...")

    while True:
        command = ""
        try:
            with sr.Microphone() as source:
                voice = listener.listen(source)
                command = listener.recognize_google(voice)
                command = command.lower()
                print("Command recognized:", command)
                return command
        except sr.UnknownValueError:
            continue
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
        except Exception as e:
            print(f"Error recognizing speech: {e}")

def weather(city):
    api_key = "9ae9af8e8248a70263b1d60a0cc7dbe4"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + api_key + "&q=" + city
    response = requests.get(complete_url)
    x = response.json()
    
    if x["cod"] != "404":
        y = x["main"]
        current_temperature = y["temp"]
        temp_in_celsius = current_temperature - 273.15
        return str(int(temp_in_celsius))
    else:
        return None

def run_assistant():
    listening = False
    while True:
        if not listening:
            command = user_commands()
            if 'hey synthesia' in command:  # Updated trigger
                listening = True
                engine_talk("I am listening now. How can I help you today?")
                print("synthesia started listening.")
        else:
            command = user_commands()
            if 'introduce your instructor' in command:
                intro_text = "Hey, my instructors are Anshika Sharma and Anshita Sood. they both are from Kangra Himachal Pradesh . An Undergraduate Btech student in CSE background specialisation in AI and DS currently in second year. studying at Jaypee University of Information Technology."
                engine_talk(intro_text)
                print("Introduction provided:", intro_text)
            elif 'about jp' in command:
                jaypee_info = (
                    "Jaypee University has over 15 thousand alumni. "
                    "It holds more than 15 patents, filed or granted, "
                    "over 100 global academic collaborations, and has published more than 400 research papers internationally and nationally. "
                    "Jaypee University of Information Technology is a NAAC A++ in April 2024 for five years .It is the accredited and the First Private University in Himachal Pradesh with this coveted accreditation."
                )
                print("Jaypee information provided:", jaypee_info)
                engine_talk(jaypee_info)
            elif 'play a song' in command:
                song = 'Arijit Singh'
                engine_talk('Playing some music')
                print("Playing....")
                pywhatkit.playonyt(song)
            elif 'play' in command:
                song = command.replace('play', '')
                engine_talk('Playing....' + song)
                print("Playing....")
                pywhatkit.playonyt(song)
            elif 'time' in command:
                time = datetime.datetime.now().strftime('%I:%M %p')
                print(time)
                engine_talk('Current Time is ' + time)
            elif 'joke' in command:
                get_j = pyjokes.get_joke()
                print(get_j)
                engine_talk(get_j)
            elif 'who is' in command:
                person = command.replace('who is', '')
                info = wikipedia.summary(person, 1)
                print(info)
                engine_talk(info)
            elif 'weather' in command:
                engine_talk("Please tell me the city name.")
                city = user_commands()
                if city:
                    temperature = weather(city)
                    if temperature is not None:
                        engine_talk('The temperature in ' + city + ' is ' + temperature + ' degrees Celsius.')
                    else:
                        engine_talk('Sorry, I could not find the weather for ' + city + '.')
                else:
                    engine_talk("I didn't hear the city name properly.")
            elif 'stop' in command:
                engine_talk("Alright! ")
                break
            else:
                engine_talk("I didn't hear you properly")
                print("I didn't hear you properly")

def start_assistant():
    run_assistant()

@app.route('/')
def hello():
    return render_template("alexa.html")

@app.route("/submit", methods=["POST"])
def submit():
    run_assistant()
    return render_template("alexa.html")

if __name__ == "__main__":
    assistant_thread = threading.Thread(target=start_assistant)
    assistant_thread.start()
    socketio.run(app, debug=True, use_reloader=False)
