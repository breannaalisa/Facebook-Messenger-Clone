import sqlite3
import bcrypt
import datetime

# Database setup
def create_db():
    conn = sqlite3.connect('messenger.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, timestamp TEXT, message TEXT)''')
    conn.commit()
    conn.close()

create_db()

# Functions
def valid_username(username):
    return len(username) >= 5 and username.isalnum() and username[0].isalpha()

def valid_password(password):
    return (len(password) >= 5 and
            any(char.islower() for char in password) and
            any(char.isupper() for char in password) and
            any(char.isdigit() for char in password))

def username_exists(username):
    conn = sqlite3.connect('messenger.db')
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    return result is not None

def add_user(username, password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = sqlite3.connect('messenger.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
    conn.commit()
    conn.close()

def check_password(username, password):
    conn = sqlite3.connect('messenger.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()
    if result:
        return bcrypt.checkpw(password.encode('utf-8'), result[0])
    return False

def send_message(sender, receiver, message):
    current_time = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    conn = sqlite3.connect('messenger.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (sender, receiver, timestamp, message) VALUES (?, ?, ?, ?)",
              (sender, receiver, current_time, message))
    conn.commit()
    conn.close()

def print_messages(username):
    conn = sqlite3.connect('messenger.db')
    c = conn.cursor()
    c.execute("SELECT sender, timestamp, message FROM messages WHERE receiver=?", (username,))
    messages = c.fetchall()
    conn.close()
    if not messages:
        print("No messages in your inbox!")
        return
    for i, (sender, timestamp, content) in enumerate(messages, start=1):
        print(f"Message #{i} received from {sender}")
        print(f"Time: {timestamp}")
        print(content)
        print()

def delete_messages(username):
    conn = sqlite3.connect('messenger.db')
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE receiver=?", (username,))
    conn.commit()
    conn.close()

# Main Program Code
print("Welcome to Facebook Messenger 2.0!")

while True:
    action = input("Would you like to (l)ogin, (r)egister or (q)uit? ")
    if action == "r":
        register_name = input("Username (case sensitive): ")
        register_pass = input("Password (case sensitive): ")
        if not username_exists(register_name):
            add_user(register_name, register_pass)
            print(f"Registration successful! Welcome {register_name}!")
            send_message("admin", register_name, "Welcome to Facebook Messenger!")
        else:
            print("Duplicate username, user registration has been cancelled.")
    elif action == "l":
        login_name = input("Username (case sensitive): ")
        login_pass = input("Password (case sensitive): ")
        if check_password(login_name, login_pass):
            while True:
                print(f"You are logged in successfully as {login_name}.")
                action2 = input("Would you like to (r)ead messages, (s)end a message, (d)elete messages or (l)ogout? ")
                if action2 == "r":
                    print_messages(login_name)
                elif action2 == "s":
                    recipient = input("Username of recipient: ")
                    message = input("Your message: ")
                    if username_exists(recipient):
                        send_message(login_name, recipient, message)
                        print("Message sent!")
                    else:
                        print("This recipient does not exist.")
                elif action2 == "d":
                    delete_messages(login_name)
                    print("Your messages have been deleted.")
                elif action2 == "l":
                    print(f"Logging out as {login_name}.")
                    break
        else:
            print("Login failed, user login has been cancelled.")
    elif action == "q":
        print("Goodbye! Thanks for using Facebook Messenger 2.0!")
        break


