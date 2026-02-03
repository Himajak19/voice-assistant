import speech_recognition as sr
from gtts import gTTS
from IPython.display import Audio, display, Javascript
from google.colab import output
from base64 import b64decode
import io
from pydub import AudioSegment

# --- JavaScript for Microphone Access ---
RECORD_JS = """
const sleep = time => new Promise(resolve => setTimeout(resolve, time))
const b2text = blob => new Promise(resolve => {
  const reader = new FileReader()
  reader.onloadend = e => resolve(e.srcElement.result)
  reader.readAsDataURL(blob)
})
var record = time => new Promise(async resolve => {
  stream = await navigator.mediaDevices.getUserMedia({ audio: true })
  recorder = new MediaRecorder(stream)
  chunks = []
  recorder.ondataavailable = e => chunks.push(e.data)
  recorder.start()
  await sleep(time)
  recorder.onstop = async ()=>{
    blob = new Blob(chunks)
    text = await b2text(blob)
    resolve(text)
  }
  recorder.stop()
})
"""

def speak(text):
    """Assistant speaks using Google Text-to-Speech (Colab compatible)"""
    print(f"Assistant: {text}")
    tts = gTTS(text=text, lang='en')
    filename = "response.mp3"
    tts.save(filename)
    display(Audio(filename, autoplay=True))

def listen(timeout=5):
    """Captures audio from browser and converts to text"""
    display(Javascript(RECORD_JS))
    print("Listening...")
    s = output.eval_js('record(%d)' % (timeout * 1000))
    b = b64decode(s.split(',')[1])
    
    # Process audio for SpeechRecognition
    audio = AudioSegment.from_file(io.BytesIO(b))
    audio.export("temp.wav", format="wav")
    
    recognizer = sr.Recognizer()
    with sr.AudioFile("temp.wav") as source:
        audio_data = recognizer.record(source)
        try:
            query = recognizer.recognize_google(audio_data)
            print(f"You said: {query}")
            return query.lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that.")
            return ""
        except sr.RequestError:
            speak("Speech service is down.")
            return ""

# --- Main Assistant Loop ---
def run_assistant():
    speak("Hello! I am your Colab assistant. How can I help you?")
    
    while True:
        command = listen()
        
        if "time" in command:
            import datetime
            now = datetime.datetime.now().strftime("%H:%M")
            speak(f"The current time is {now}")
            
        elif "joke" in command:
            speak("Why did the programmer quit his job? Because he didn't get arrays!")
            
        elif "exit" in command or "stop" in command:
            speak("Goodbye!")
            break
            
        elif command != "":
            speak("I heard you, but I don't know that command yet.")

# Start the assistant
run_assistant()
