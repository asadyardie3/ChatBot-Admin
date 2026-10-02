# Chatbot Admin

A simple web chatbot that lets an admin add, delete and update user records using natural chat commands.

## Features
- Simple login: a user is admitted if their email already exists in the system
- Chat interface available after login
- Add, remove and update users by typing plain-English commands
- Data stored in a local SQLite database

## Setup
1. Clone the repo and open the folder
2. Create and activate a virtual environment:
   python -m venv venv
   venv\Scripts\activate
3. Install dependencies:
   pip install -r requirements.txt
4. Run the app:
   python app.py
5. Open the address shown in the terminal in your browser

## Example commands
- add user "john.smith@xyz.com" with phone number "+92332"
- remove user "john.smith@xyz.com"
- update samantha's city to Cordoba

## Project structure
- app.py: web server and routes
- bot.py: chat command handling
- command_parser.py: turns chat messages into actions
- db.py: database functions
- templates/ and static/: front-end files
