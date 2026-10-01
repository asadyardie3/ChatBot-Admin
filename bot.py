import db
from command_parser import parse

HELP = """I can manage users. Try:
- add the user "john.smith@xyz.com" with phone number "+92332"
- remove the user "john.smith@xyz.com"
- update samanthas city to Cordoba
- update john.smith@xyz.com phone to +92 300 1234567
- list users"""


def process(message, current_email):
    cmd = parse(message)
    action = cmd["action"]

    if action == "add":
        if not cmd["email"]:
            return 'Please include an email, e.g. add the user "john@xyz.com" with phone number "+92332".'
        return db.add_user(cmd["email"], cmd["phone"])
    if action == "delete":
        return db.delete_user(cmd["who"], current_email)
    if action == "update":
        return db.update_user(cmd["who"], cmd["field"], cmd["value"], current_email)
    if action == "list":
        return db.list_users()
    if action == "help":
        return HELP
    return "Sorry, I didn't understand that. Type 'help' to see examples."