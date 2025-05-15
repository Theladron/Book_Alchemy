import os

import requests
from dotenv import load_dotenv

load_dotenv()
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

API_URL = "https://chatgpt-42.p.rapidapi.com/aitohuman"

HEADERS = {
    "Content-Type": "application/json",
    "X-RapidAPI-Host": "chatgpt-42.p.rapidapi.com",
    "X-RapidAPI-Key": RAPIDAPI_KEY
}


def get_book_recommendations(title, genre):
    if genre != "N/A":
        prompt = f"Suggest books similar to '{title}', which is in the {genre} genre."
    else:
        prompt = f"Suggest books similar to '{title}'."

    response = requests.post(API_URL, headers=HEADERS, json={"text": prompt})
    if response.status_code == 200:
        try:
            data = response.json()
            return data.get("result", ["No recommendations found."])[0]
        except Exception as e:
            return f"Error parsing response: {e}"
    else:
        return f"Error {response.status_code}: {response.text}"


def get_author_recommendations(author, genre):
    prompt = f"Suggest books by authors similar to {author}, whose works are in the {genre} genre."

    response = requests.post(API_URL, headers=HEADERS, json={"text": prompt})

    if response.status_code == 200:
        try:
            data = response.json()
            return data.get("result", ["No recommendations found."])[0]
        except Exception as e:
            return f"Error parsing response: {e}"
    else:
        return f"Error {response.status_code}: {response.text}"


def get_homepage_recommendations(user_books):
    prompt = "Suggest books based on the following rated books: " + ", ".join(
        [f"{book.title} ({book.rating})" for book in user_books])
    response = requests.post(API_URL, headers=HEADERS, json={"text": prompt})
    if response.status_code == 200:
        try:
            data = response.json()
            return data.get("result", ["No recommendations found."])[0]
        except Exception as e:
            return f"Error parsing response: {e}"
    else:
        return f"Error {response.status_code}: {response.text}"
