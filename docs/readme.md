# Book Alchemy
is designed for showcasing the combination of litesql database handling, 
flask routing and frontend integration via Html and JS, combined with api requests and ai prompting. <br>
Used apis: <br>

| Author/Book infos | Recommendations | 
|-------------------|-----------------|
| [open library](https://openlibrary.org)             | [chatgpt 4](https://rapidapi.com/rphrp1985/api/chatgpt-42/playground/)         |



## Key Features 🚀
* Create, update and delete authors and books
  * The Api fetches additional author/book information and provides a book cover
  * Search for books/authors, sort entries
* Click on any book or author to get additional information
  * In addition to the information, get recommendations for books similar to the current book or authors work
* Rate your books on a scale from 1-10
* Get Ai recommendations for books you might like based on your rated books
* Work with the flask routes or directly on the HTML pages

## Prerequisites 📋
Before you install the program, make sure you have the following prerequisites installed
* Python 3.x
* Pip (Python's package manager)

## Installation ⚙️

1. Clone the repository and install the dependencies via 
```bash
  pip install -r requirements.txt 📋
```
2. Create a [rapidapi](https://rapidapi.com/) account or log in on a google account
3. go to the [chatgpt 4](https://rapidapi.com/rphrp1985/api/chatgpt-42/playground) page 
and subscribe to the free, basic plan
4. Create a **.env** file in the root folder of the project and add
```bash
  API_KEY="your key" 📋
```
5. Run the **db_setup.py** once to create the database folder and file
```bash
      Windows                   Mac
python db_setup.py 📋   python3 db_setup.py 📋
```
6. Run flask
```bash
  flask run 📋
```
Visit http://localhost:5000 in your browser to view the app

## Usage 💻

### Home Page 🏠
* View the current books added
* Rate the books from 1-10
* Search for Books/Authors and Sort by Books/Authors
* Get recommendations based on the rated books of your current filter selection
### Add an Author 🧑‍💻
* Create an Author with Name, Birthdate and ***(optional)*** Date of Death
### Add a Book 📖
* Create your books manually
* Search for a book via ISBN
### Delete Books or Authors 🗑️
* When you delete the last Book from an Author, decide if the Author should be deleted aswell
* When you delete an Author, all Books by the Author will be deleted aswell

## Project Libraries used 🗂️
* flask~=3.1.0
* sqlalchemy~=2.0.40
* flask_sqlalchemy
* jinja2
* requests~=2.32.3
* python-dotenv~=1.1.0
## Contributions 🤝
If you'd like to contribute to this project, feel free to submit a pull request. 
Contributions are welcome in the form of bug fixes, new features, or general improvements. 
Please ensure that your code is properly tested and follows the style guidelines before submitting.
Since this is a Masterschool exercise, I might not be able to view new contributions on a regular basis.
