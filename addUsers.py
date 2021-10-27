''' 
CLI based tool to add new users to the database.
Database - testing.db, sqlite3
table - users (username, hash)
'''

import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Connect to the database
conn = sqlite3.connect('testing.db')
c = conn.cursor()

#  check against the password has of user "admin"
def check_password(password):
    c.execute("SELECT hash FROM users WHERE username = 'admin'")
    hashed_password = c.fetchone()
    return check_password_hash(hashed_password[0], password)

admin = input("Enter admin password: ")
if not check_password(admin):
    print("Incorrect password. You are not authorised to add/change users")
    conn.close()
    exit()

username = input("Enter username (email address): ")
password = input("Enter password: ")

h = generate_password_hash(password)

try:
    c.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, h))
    conn.commit()
    print("User added successfully")
except sqlite3.IntegrityError:
    print("User already exists")
    change = input("Do you want to change the password of existing user? (y/n): ")
    if change == 'y':
        c.execute("UPDATE users SET hash = ? WHERE username = ?", (h, username))
        conn.commit()
        print("Password updated successfully")
    else:
        print("Password not updated")
    
conn.close()
    

