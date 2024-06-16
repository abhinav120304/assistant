import threading
from flask import Flask, render_template, request, jsonify
import pyttsx3
import webbrowser
import datetime
import cv2
import os
import requests
import wikipediaapi

app = Flask(__name__)

def say(text):
    # Function to convert text to speech
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def respond_to_command(command):
    if "take picture" in command.lower():
        say("Alright, let's capture a picture!")
        frame = take_picture()
        # Handle frame if needed, currently just captures and returns
    elif "your name" in command.lower():
        say("I Am Kevin And I Am Here To Assist You")
    elif "open google" in command.lower():
        say("Sure, opening Google.")
        webbrowser.open("https://www.google.com")
    elif "open youtube" in command.lower():
        say("Okay, opening YouTube.")
        webbrowser.open("https://www.youtube.com")
    elif "open instagram" in command.lower():
        say("Okey, opening Instagram")
        webbrowser.open("https://www.instagram.com")  
    elif "open spotify" in command.lower():
        say("Okey, opening spotify")
        webbrowser.open("https://www.spotify.com")      
    elif "the time" in command.lower():
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        say(f"The current time is {current_time}. Is there anything else you'd like to know?")
    elif "thank you" in command.lower():
        say("You're welcome! Do you need assistance with anything else?")
    elif "exit" in command.lower():
        say("Alright, exiting the application. Goodbye!")
        shutdown_server()
    elif "joke" in command.lower():
        say("Sure, let me tell you a joke.")
        joke = fetch_joke()
        say(joke)
        say("Would you like to hear another one?")
        if "yes" in command.lower():
            joke = fetch_joke()
            say(joke)
        elif "no" in command.lower():
            say("I hope you have enjoyed")
    elif "news" in command.lower():
        say("Sure, let me fetch the latest news for you.")
        news = fetch_news()
        say(news)
        say("How else may I assist you?")
    elif "tell me about" in command.lower():
        query = command.lower().replace("tell me about", "").strip()
        say(f"Let me search Wikipedia for information on {query}.")
        wiki_summary = get_wikipedia_summary(query)
        say(wiki_summary)
        say("Is there anything else you'd like to know?")
    else:
        say("Sorry, I didn't understand that command. Can you please repeat or ask something else?")

def take_picture():
    # Initialize the camera
    cap = cv2.VideoCapture(0)

    # Capture frame-by-frame
    ret, frame = cap.read()

    if ret:
        # Save the captured frame as an image
        image_path = os.path.join('user_images', 'user_image.jpg')
        cv2.imwrite(image_path, frame)
        say("Picture taken successfully!")

    # Release the camera
    cap.release()

    return frame if ret else None

def fetch_joke():
    try:
        response = requests.get("https://official-joke-api.appspot.com/random_joke")
        joke = response.json()
        return f"{joke['setup']} - {joke['punchline']}"
    except Exception as e:
        return "I'm sorry, I couldn't fetch a joke at the moment."

def fetch_news():
    api_key = '5748f886855840ae8c4f52380c608a7b'
    url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
        news_data = response.json()
        headlines = [article['title'] for article in news_data['articles'][:5]]
        return ' '.join(headlines)
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return "I'm sorry, I couldn't fetch the news at the moment."
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "I'm sorry, an unexpected error occurred."

def get_wikipedia_summary(query):
    # Specify a user agent as per Wikipedia's User-Agent policy
    wiki_wiki = wikipediaapi.Wikipedia(
        language='en',
        extract_format=wikipediaapi.ExtractFormat.WIKI,
        user_agent="YourApplicationName/1.0 (YourContactInformation)"
    )
    
    page = wiki_wiki.page(query)
    if page.exists():
        return page.summary[:300]  # Limit summary to first 500 characters
    else:
        return "I'm sorry, I couldn't find any information on that topic."

@app.route('/')
def index():
    return render_template('index.html')
    

@app.route('/command', methods=['POST'])
def execute_command():
    data = request.json
    command = data['command']
    threading.Thread(target=respond_to_command, args=(command,)).start()
    return '', 204

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

if __name__ == '__main__':
    app.run(debug=True)
