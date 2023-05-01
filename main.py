import pyttsx3
import speech_recognition as sr
import datetime
import wolframalpha
import sympy
import requests
import spacy


engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Set the desired voice

# Load the spaCy English model
nlp = spacy.load('en_core_web_sm')

# Set up OpenFDA API URL and parameters
api_url = 'https://api.fda.gov/drug/label.json'
search_param = 'indications_and_usage:'
limit = 10

def speak(audio):
    engine.say(audio)
    print(audio)
    engine.runAndWait()

def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening.......")
        r.pause_threshold = 1
        audio = r.listen(source,timeout=10,phrase_time_limit=10)

    try:
        print("Recognizing.....")
        query = r.recognize_google(audio, language='en-in')
        print(f"user said: {query}")
        if query.lower() == "exit" or "quit" in query.lower():
            speak("Goodbye Sir!")
            return False
        elif "doctor" in query.lower():
            recommend_medicine()
        else:
            WolframeAlpha(query)
    except Exception as e:
        speak("Say That Again Sir!")
        return True
    return True

def wish_me():
    hour = datetime.datetime.now().hour
    if hour >= 0 and hour < 12:
        speak("Good Morning Sir!")

    elif hour >= 12 and hour < 18:
        speak("Good Afternoon Sir!")

    else:
        speak("Good Evening Sir!")

    speak("I am your AI assistant. How can I assist you?")

def WolframeAlpha(query):
    api_key = "T9KXP5-W996EKAUX7"
    requester = wolframalpha.Client(api_key)
    requested = requester.query(query)
    
    try:
        # Check if the query has a direct answer
        Answer = next(requested.results).text
        speak(Answer)

    except StopIteration:
        try:
            # Check if the query has a result that can be computed
            pods = requested.pods
            result = next(pod for pod in pods if pod["@id"] == "Result")
            Answer = result.subpod.plaintext
            speak(Answer)

        except StopIteration:
            try:
                # Check if the query has an image result
                pods = requested.pods
                image = next(pod for pod in pods if pod["@id"] == "Image")
                url = image["subpod"]["img"]["@src"]
                speak(f"You can see the result at this url: {url}")

            except StopIteration:
                # No answer found, try to solve math problems
                try:
                    Answer = sympy.simplify(query)
                    speak(str(Answer))
                except:
                    speak('Not Found Sir!')

def get_medicines_for_disease(disease):
    # Set up API query parameters
    query_params = {
        'search': f'{search_param}"{disease}"',
        'limit': limit
    }

    # Call OpenFDA API and retrieve results
    response = requests.get(api_url, params=query_params)
    results = response.json()

    # Extract medicine names from results
    medicines = []
    for result in results['results']:
        if 'openfda' in result:
            if 'generic_name' in result['openfda']:
                medicines.append(result['openfda']['generic_name'][0])

    return medicines

def recommend_medicine():
    # Greet the patient and ask about their symptoms
    speak("Hello! I'm Dr. AI. How can I help you today?")
    symptoms = input("Please describe your symptoms: ")
    speak(symptoms)

    # Use spaCy to analyze the user's symptoms
    doc = nlp(symptoms)

    # Extract the nouns and adjectives from the analyzed text
    keywords = [token.lemma_.lower() for token in doc if token.pos_ in ['NOUN', 'ADJ']]

    # Get a list of recommended medicines for the user's symptoms
    recommended_medicines = []
    for keyword in keywords:
        medicines = get_medicines_for_disease(keyword)
        recommended_medicines.extend(medicines)

    # Remove duplicates from the list of recommended medicines
    recommended_medicines = list(set(recommended_medicines))

    # Ask follow-up questions to gather more information about the patient's condition
    while True:
        severity = input("On a scale of 1 to 10, how severe are your symptoms? ")
        speak(severity)
        if severity.isdigit() and 1 <= int(severity) <= 10:
            break
        else:
            speak("Please enter a number between 1 and 10.")

    while True:
        duration = input("How long have you been experiencing these symptoms (in days)? ")
        if duration.isdigit() and int(duration) >= 0:
            break
        else:
            speak("Please enter a non-negative number.")

    # Analyze the user's sickness time and severity and provide a personalized recommendation
    if int(severity) >= 8:
        recommended_medicine = recommended_medicines[0]
        speak(f"Based on the severity of your symptoms, we recommend taking {recommended_medicine} as soon as possible.")
    elif int(severity) >= 5:
        recommended_medicine = recommended_medicines[1]
        speak(f"Based on the severity of your symptoms, we recommend taking {recommended_medicine}.")
    else:
        recommended_medicine = recommended_medicines[2]
        speak(f"Based on your symptoms and sickness time, we recommend taking {recommended_medicine}.")

    # Provide additional advice and tips for managing the patient's symptoms
    if int(duration) >= 7:
        speak("If your symptoms do not improve after 7 days, please consult a medical professional.")
    else:
        speak("Make sure to rest and drink plenty of fluids to help your body fight off the infection.")
        


if __name__ == "__main__":
    wish_me()
    while takecommand():
        
        pass