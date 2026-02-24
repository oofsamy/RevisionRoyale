# RevisionRoyale

My A-Level NEA OCR Project Repository.

## Installation

Ensure **Python 3** (Preferably 3.11.6 as this program has been only extensively tested on this version) is installed.

This program relies on quite a few of external libraries which are not automatically packaged with Python 3.11.6, which are the following but not limited to:

- Flask

- Dotenv

- werkzeug

- FSRS

- arrow
  

For now, an automatic library installation process has not been yet implemented, but you can install each library by executing the following command into Command Prompt / Terminal.


`pip3 install LIBRARY_NAME_HERE`  

## Usage

Make sure to create a file called `.env` in your program and enter your own secret key (your own choice but you must not change it between runs for the password hashing functionality) in the following format:
`SECRET_KEY=SUCH_A_SECRET_KEY`

Open command prompt and execute the command: `python app.py` then open the link http://127.0.0.1:5000/ or the link http://localhost:5000/ in your browser

The username has the following requirements: 4-32 characters in length (inclusive) and must not contain any spaces.

The password has the following requirements: Minimum 8 characters in length (inclusive) and must contain a digit.
