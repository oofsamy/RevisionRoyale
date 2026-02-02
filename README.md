# RevisionRoyale

My A-Level NEA OCR Project Repository.

  

## Installation

Ensure **Python 3** (Preferably 3.11.6 as this program has been only extensively tested on this version) is installed.

  

This program relies on quite a few of external libraries which are not automatically packaged with Python 3.11.6, which are the following but not limited to:

- Flask

- Dotenv

- werkzeug

  

For now, an automatic library installation process has not been yet implemented, but you can install each library by executing the following command into Command Prompt / Terminal.

  

`pip3 install LIBRARY_NAME_HERE`

  

## Usage

Open command prompt and execute the command: `python app.py` then open the link http://127.0.0.1:5000/ in your browser

  

# GET Requests

These are the following GET endpoints (used for web-browsing not API requests):

  

⋅⋅⋅⋅* `/` returns the startup.html page

....* `/login` returns the login.html page

....* `/register` returns the register.html page

....* `/setup-subjects` returns the setup_subjects.html page

....* `/dashboard` returns an empty page consisting of a success message for now

  

# POST Requests
These are the following POST endpoints (used for API requests on the servers' behalf)

  
|Parameter Key|Parameter Value|
|--|--|
| username  | User's username |
| password  | User's password |  

  

## For Developer Purposes

The .env file contains the following variable used in the program

`SECRET_KEY=SUCH_A_SECRET_KEY_HAHAHA`