import json
import torch
from .my_nltk_script import bag_of_words, tokenize
from .model import NeuralNet
import random
from googletrans import Translator
import requests
import os
from dotenv import load_dotenv
import wikipedia
import re
import logging

class ChatBot:
    load_dotenv()
    api_key = os.getenv("API_KEY")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    translator = Translator()

    with open(r'static/intents.json', 'r') as f:
        intents = json.load(f)

    FILE = r"static/data.pth"
    data = torch.load(FILE)
    input_size = data["input_size"]
    hidden_size = data["hidden_size"]
    output_size = data["output_size"]
    all_words = data["all_words"]
    tags = data["tags"]
    model_state = data["model_state"]

    model = NeuralNet(input_size, hidden_size, output_size).to(device)
    model.load_state_dict(model_state)
    model.eval()

    translation_cache = {}

    @staticmethod
    def translate_text(text, dest_language='en'):
        if not text:
            return text
        if (text, dest_language) in ChatBot.translation_cache:
            return ChatBot.translation_cache[(text, dest_language)]

        try:
            translation = ChatBot.translator.translate(text, dest=dest_language)
            if translation is None:
                raise Exception("Translation returned None")
            translated_text = translation.text
            ChatBot.translation_cache[(text, dest_language)] = translated_text
            return translated_text
        except Exception as e:
            logging.error(f"Translation error: {e}")
            return text

    @staticmethod
    def generate_audio(text, lang='ENG'):
        if not text:
            return None
        try:
            response = requests.post(
                'https://api.bland.ai/v1/voices/e1289219-0ea2-4f22-a994-c542c2a48a0f/sample',
                headers={
                    'Content-Type': 'application/json',
                    'authorization': ChatBot.api_key
                },
                json={
                    'text': text,
                    'voice_settings': {},
                    'language': lang
                }
            )
            if response.status_code == 200:
                return response.content
            else:
                logging.error(f"Failed to generate audio for: {text}. Status code: {response.status_code}")
                return None
        except requests.RequestException as e:
            logging.error(f"Request error: {e}")
            return None

def get_response(sentence):
    bot_name = "Greeta:\n"
    if not sentence:
        return bot_name + "Sorry, I didn't get it. Can you please rephrase?"
    
    try:
        lang_detection = ChatBot.translator.detect(sentence)
        lang = lang_detection.lang if lang_detection is not None else 'en'
    except Exception as e:
        logging.error(f"Language detection error: {e}")
        lang = 'en'  # Default to English if detection fails

    translated_sentence = ChatBot.translate_text(sentence, dest_language=lang)

    sentence_tokens = tokenize(translated_sentence)
    X = bag_of_words(sentence_tokens, ChatBot.all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(ChatBot.device)

    output = ChatBot.model(X)
    _, predicted = torch.max(output, dim=1)
    tag = ChatBot.tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.75:
        response_text = next(intent['responses'][random.choice(range(len(intent['responses'])))]
                             for intent in ChatBot.intents["intents"] if tag == intent["tag"])
    else:
        try:
            summary = wikipedia.summary(translated_sentence, sentences=1)
            response_text = re.sub(r',(?![a-zA-Z0-9])', '', summary)
        except wikipedia.exceptions.PageError:
            response_text = "Sorry, the response for the given topic was not found."
        except wikipedia.exceptions.DisambiguationError:
            response_text = "Ambiguous topic! Please provide more specific details."
        except Exception as e:
            logging.error(f"Wikipedia fetch error: {e}")
            response_text = "Sorry, I didn't get it. Can you please rephrase?"

    translated_response = ChatBot.translate_text(response_text, dest_language=lang)

    audio_data = ChatBot.generate_audio(translated_response)
    if audio_data:
        try:
            # Implement your logic to play audio here, based on the format returned by your API
            # For example:
            # play_audio(audio_data)
            pass
        except Exception as e:
            logging.error(f"Audio playback error: {e}")
    else:
        logging.error("Audio generation failed")

    return bot_name + translated_response
