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
    """
    Gets suggested books based on the books title and genre,
    handles exceptions
    :param title: name of the book as string
    :param genre: genre of the book as string
    :return: response as string if found, esle error message
    """
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
    """
    Gets suggested books by authors similar to the author and the author's main genre,
    handles exceptions
    :param author: author name as string
    :param genre: author's main genre as string
    :return: response as string if found, esle error message
    """
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
    """
    Gets suggested books from the api based on rated books from the library, handles exceptions
    :param user_books: rated books used for the prompt as list
    :return: response as string if found, else error message
    """
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
