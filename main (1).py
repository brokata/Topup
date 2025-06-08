import telebot
import requests
import sqlite3
import logging
import random
import string
import base64
import io
import time
from threading import Thread
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# Dictionary to store user balances
user_balances = {}

# Replace with your bot token
API_TOKEN = "7643490329:AAFDxe-SopZ_sBUXNLCEf-xrH-pXxtkIP4U"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7ImlkIjoiNmFmM2FlMWU3Yzg4NDQ3OCJ9LCJpYXQiOjE3NDM1MTE4MjUsImV4cCI6MTc1MTI4NzgyNX0.ShQ-iQ96VKcqktZZnigUgqaDuooeuPGpnduzdtNxBGA"
HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

# Get the current balance of a user
def get_balance(user_id):
    return user_balances.get(user_id, 0.0)

# List of admin user IDs
ADMIN_IDS = [6983955329]

# Item prices (key: item_id, value: price in $)
# Item prices (key: item_id, value: price in $)
ITEM_PRICES = {
    "11": {"normal": 0.25, "reseller": 0.20},
    "22": {"normal": 0.50, "reseller": 0.40},
    "56": {"normal": 0.96, "reseller": 0.90},
    "86": {"normal": 1.15, "reseller": 1.06},
    "112": {"normal": 1.90, "reseller": 12.78},
    "172": {"normal": 2.30, "reseller": 2.12},
    "257": {"normal": 3.30, "reseller": 3.08},
    "343": {"normal": 4.30, "reseller": 4.15},
    "429": {"normal": 5.30, "reseller": 5.07},
    "514": {"normal": 6.50, "reseller": 6.15},
    "600": {"normal": 7.50, "reseller": 7.06},
    "706": {"normal": 8.50, "reseller": 8.19},
    "792": {"normal": 9.50, "reseller": 9.19},
    "878": {"normal": 11.00, "reseller": 10.24},
    "963": {"normal": 12.00, "reseller": 11.38},
    "1050": {"normal": 13.00, "reseller": 12.35},
    "1135": {"normal": 14.00, "reseller": 13.35},
    "1220": {"normal": 15.00, "reseller": 14.35},
    "1412": {"normal": 18.00, "reseller": 16.35},
    "1584": {"normal": 19.00, "reseller": 18.35},
    "1755": {"normal": 22.00, "reseller": 20.35},
    "1926": {"normal": 24.00, "reseller": 22.35},
    "2195": {"normal": 26.00, "reseller": 24.35},
    "2538": {"normal": 29.00, "reseller": 26.60},
    "2901": {"normal": 35.00, "reseller": 32.80},
    "3688": {"normal": 45.50, "reseller": 41.30},
    "4394": {"normal": 52.00, "reseller": 49.70},
    "5532": {"normal": 65.00, "reseller": 62.60},
    "6238": {"normal": 75.00, "reseller": 72.00},
    "6944": {"normal": 80.00, "reseller": 77.00},
    "7727": {"normal": 90.00, "reseller": 87.00},
    "9288": {"normal": 112.00, "reseller": 119.00},
    "10700": {"normal": 135.00, "reseller": 135.00},
    "Weekly": {"normal": 1.35, "reseller": 1.30},
    "2Weekly": {"normal": 2.70, "reseller": 2.60},
    "3Weekly": {"normal": 4.05, "reseller": 3.90},
    "4Weekly": {"normal": 5.40, "reseller": 5.20},
    "5Weekly": {"normal": 6.75, "reseller": 6.50},
    "twilight": {"normal": 8.00, "reseller": 7.00},
    "50×2": {"normal": 0.80, "reseller": 0.66},
    "150×2": {"normal": 2.30, "reseller": 1.99},
    "250×2": {"normal": 3.80, "reseller": 3.19},
    "500×2": {"normal": 7.00, "reseller": 6.55},
    "Check": {"normal": 0, "reseller": 0},
} 

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Create the bot instance
bot = telebot.TeleBot(API_TOKEN)

# User states
user_states = {}

# Database setup
conn = sqlite3.connect("bot_data.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    chat_id INTEGER PRIMARY KEY,
    balance REAL DEFAULT 0.0
)
""")
conn.commit()

# Database initialization
def init_db():
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 0.0,
            is_reseller INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
    logging.info("Database initialized successfully.")

def check_transaction_status(chat_id, md5, message_id, amount):
    start_time = time.time()
    while time.time() - start_time < 180:  # Check for 3 minutes
        try:
            check_response = requests.post(
                "https://khqr.sanawin.icu/khqr/check-transaction",
                json={"md5": md5, "bakongToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7ImlkIjoiNmFmM2FlMWU3Yzg4NDQ3OCJ9LCJpYXQiOjE3NDM1MTE4MjUsImV4cCI6MTc1MTI4NzgyNX0.ShQ-iQ96VKcqktZZnigUgqaDuooeuPGpnduzdtNxBGA"},
                headers=HEADERS
            ).json()

            if check_response.get("status") == "success":
                # Send the success message after the payment
                bot.send_message(chat_id, f"Automated Deposit System ⚙️\n\nCurrency: USD 💵\n\nBalance Added: ${amount} ✅\n\nPayment: KHQR PAYMENT SCAN")
                
                # Send a thank you message for the payment
                bot.send_message(chat_id, f"Thank you for your payment of ${amount}. We appreciate your support! 🙏")

                # Update the user's balance after successful payment
                update_balance(chat_id, amount)
                
                # Delete the payment request message
                bot.delete_message(chat_id, message_id)
                return

            time.sleep(5)
        except Exception as e:
            print(f"Error checking transaction: {e}")

    # If transaction takes too long, notify about the timeout
    bot.send_message(chat_id, "Transaction Timeout, Please create new Deposit")
    bot.delete_message(chat_id, message_id)

# Generate QR Code
def generate_qr(message, amount):
    try:
        create_payload = {
            "type": "personal",
            "data": {
                "bakongAccountID": "tang_baksea@aclb",
                "accName": "Dotana",
                "accountInformation": "122070508110833",
                "currency": "USD",
                "amount": float(amount),
                "address": "PhnomPenh"
            }
        }

        response = requests.post(
            "https://khqr.sanawin.icu/khqr/create",
            json=create_payload,
            headers=HEADERS
        ).json()

        if response["success"]:
            qr_code_base64 = response["data"]["qrCodeImage"].split("base64,")[1]
            qr_image_bytes = base64.b64decode(qr_code_base64)
            qr_image_io = io.BytesIO(qr_image_bytes)
            qr_image_io.name = 'qr_code.png'

            sent_message = bot.send_photo(
                message.chat.id,
                qr_image_io,
                caption=f"Here is your payment 𝐐𝐑 code\nNote: Expires in 3 minutes."
            )

            Thread(
                target=check_transaction_status,
                args=(message.chat.id, response["data"]["md5"], sent_message.message_id, amount)
            ).start()
        else:
            bot.send_message(message.chat.id, "Wow, too fast. Please wait for 1 seconds...")

    except Exception as e:
        print(f"Error generating QR code: {e}")
        bot.send_message(message.chat.id, "Wow, too fast. Please wait for 1 seconds...")

# Update user balance
def update_balance(chat_id, amount):
    cursor.execute("INSERT OR IGNORE INTO users (chat_id) VALUES (?)", (chat_id,))
    cursor.execute("UPDATE users SET balance = balance + ? WHERE chat_id = ?", (amount, chat_id))
    conn.commit()

# Get user balance
def get_balance(chat_id):
    cursor.execute("INSERT OR IGNORE INTO users (chat_id) VALUES (?)", (chat_id,))
    conn.commit()
    cursor.execute("SELECT balance FROM users WHERE chat_id = ?", (chat_id,))
    return cursor.fetchone()[0]

# Get a user's balance
def get_balance(user_id):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0.0

# Update a user's balance
def update_balance(user_id, amount):
    try:
        conn = sqlite3.connect("bot_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()

        if result:
            new_balance = result[0] + amount
            cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
            logging.info(f"Updated balance for User ID {user_id}: {new_balance}")
        else:
            cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, amount))
            logging.info(f"Added new User ID {user_id} with balance: {amount}")

        conn.commit()
    except Exception as e:
        logging.error(f"Error updating balance: {e}")
        conn.rollback()
    finally:
        conn.close() 

# Check if a user is a reseller
def is_reseller(user_id):
    """
    Check if the user is a reseller.
    
    Args:
        user_id (int): The ID of the user.
    
    Returns:
        bool: True if the user is a reseller, False otherwise.
    """
    try:
        conn = sqlite3.connect("bot_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT is_reseller FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] == 1 if result else False
    except Exception as e:
        logging.error(f"Error checking reseller status for user {user_id}: {e}")
        return False       

# Set a user as a reseller
def addre(user_id):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    cursor.execute("UPDATE users SET is_reseller = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

# Unset a user as a reseller
def delre(user_id):
    conn = sqlite3.connect("bot_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    cursor.execute("UPDATE users SET is_reseller = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()        

# Command to set a user as a reseller
@bot.message_handler(commands=['addre'])
def addre_handler(message):
    admin_id = message.from_user.id
    if admin_id not in ADMIN_IDS:
        bot.reply_to(message, "You are not authorized to use this command.")
        return

    try:
        target_user_id = int(message.text.split()[1])
        addre(target_user_id)
        bot.reply_to(message, f"✅ User {target_user_id} is now a reseller.")
    except (IndexError, ValueError):
        bot.reply_to(message, "Usage: /addre <user_id>")

# Command to unset a user as a reseller
@bot.message_handler(commands=['delre'])
def delre_handler(message):
    admin_id = message.from_user.id
    if admin_id not in ADMIN_IDS:
        bot.reply_to(message, "You are not authorized to use this command.")
        return

    try:
        target_user_id = int(message.text.split()[1])
        delre(target_user_id)
        bot.reply_to(message, f"✅ User {target_user_id} is no longer a reseller.")
    except (IndexError, ValueError):
        bot.reply_to(message, "Usage: /delre <user_id>")

# Command for admins to add balance
@bot.message_handler(commands=['cbal'])
def cbal_handler(message):
    try:
        # Check if the sender is an admin
        admin_id = message.from_user.id
        if admin_id not in ADMIN_IDS:
            bot.reply_to(message, "You are not authorized to use this command.")
            return

        # Parse the command arguments
        args = message.text.split()
        if len(args) != 3:
            bot.reply_to(message, "Invalid format. Use: /cbal <user_id> <amount>")
            return

        # Extract user_id and amount
        user_id = int(args[1])
        amount = float(args[2])

        # Update the user's balance
        update_balance(user_id, amount)

        # Notify the admin
        bot.reply_to(message, f"Successfully added ${amount:.2f} to User ID {user_id}.")

        # Notify the user
        try:
            bot.send_message(
                user_id,
                f"🎉 Your balance has been updated! ${amount:.2f} has been added to your account."
            )
        except Exception as e:
            logging.error(f"Error notifying user {user_id}: {e}")

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")

# Command for admins to check all user balances
@bot.message_handler(commands=['allbal'])
def allbal_handler(message):
    try:
        # Check if the sender is an admin
        admin_id = message.from_user.id
        if admin_id not in ADMIN_IDS:
            bot.reply_to(message, "You are not authorized to use this command.")
            return

        # Fetch all users and their balances from the database
        conn = sqlite3.connect("bot_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, balance FROM users")
        users = cursor.fetchall()
        conn.close()

        if not users:
            bot.reply_to(message, "No users found in the database.")
            return

        # Format the balances into a readable string
        balances = "\n".join([f"User ID: {user[0]}, Balance: ${user[1]:.2f}" for user in users])
        bot.reply_to(message, f"📊 **All User Balances:**\n\n{balances}")

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")      

# Function to handle the /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    button1 = KeyboardButton('👤 Account')
    button2 = KeyboardButton('🎮 Game')
    button3 = KeyboardButton('💰 Deposit')
    markup.add(button1, button2, button3)
    bot.send_message(message.chat.id, "How can i help you?", reply_markup=markup)

# Function to handle the 'Hello' button press (Show balance)
@bot.message_handler(func=lambda message: message.text == '👤 Account')
def handle_hello(message):
    user_balance = get_balance(message.chat.id)
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    bot.send_message(message.chat.id, f"Name: {username}\nID: {user_id}\nBalance: ${user_balance} USD")

# Function to handle the 'Game' button press
@bot.message_handler(func=lambda message: message.text == '🎮 Game')
def handle_game(message):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button1 = KeyboardButton('Mobile Legends')
    button2 = KeyboardButton('Free Fire')
    button_back = KeyboardButton('Back')
    markup.add(button1, button2, button_back)
    bot.send_message(message.chat.id, "Select product category", reply_markup=markup)

# Function to handle the 'Back' button press
@bot.message_handler(func=lambda message: message.text == 'Back')
def handle_back(message):
    send_welcome(message)

# Function to handle 'Free Fire' and 'Mobile Legends' game choice
@bot.message_handler(func=lambda message: message.text == 'Mobile Legends')
def handle_game_choice(message):
    user_id = message.from_user.id
    if is_reseller(user_id):
        bot.reply_to(message, """Products List Mobile Legend 
        Reselller

11 = $0.20
22 = $0.40
56 = $0.90
86 = $1.06
172 = $2.12
257 = $3.08
343 = $4.15
429 = $5.07
514 = $6.15
600 = $7.06
706 = $8.19
878 = $10.24
963 = $11.38
1050 = $12.35
1135 = $13.35
1220 = $14.35
1412 = $16.35
1584 = $18.35
1755 = $20.35
2195 = $24.35
2901 = $32.80
3688 = $41.30
4394 = $49.70
5532 = $62.60
6238 = $72.00
7727 = $87.00
9288 = $119.00
Weekly = $1.30
2Weekly = $2.60
3Weekly = $3.90
4Weekly = $5.20
5Weekly = $6.50
Twilight  = $7.00
50×2 = $0.66
150×2 = $1.99
250×2 = $3.19
500×2 = $6.55
Check = $0.00

Example format order:
123456789 12345 Weekly
userid serverid item""")
    else:
        bot.reply_to(message, """Products List Mobile Legend

11 = $0.25
22 = $0.50
56 = $0.95
86 = $1.15
172 = $2.20
257 = $3.30
343 = $4.30
429 = $5.30
514 = $6.50
600 = $7.50
706 = $8.50
792 = $9.50
878 = $11.00
963 = $12.00
1050 = $13.00
1135 = $14.00
1220 = $15.00
1412 = $18.00
1584 = $19.00
1756 = $22.00
1926 = $24.00
2195 = $26.00
2538 = $29.00
2901 = $35.00
3688 = $45.00
4394 = $52.00
5532 = $65.00
6238 = $75.00
6944 = $80.00
7727 = $90.00
9288 = $110.00
10700 = $135.00
Weekly = $1.35
2Weekly = $2.70
3Weekly = $4.05
4Weekly = $5.40
5Weekly = $6.75
Twilight = $8.00
50×2 = $0.80
150×2 = $2.30
250×2 = $3.80
500×2 = 7.00
Check = $0.00

Example format order:
123456789 12345 Weekly
userid serverid item""")

# Function to handle 'Free Fire' and 'Mobile Legends' game choice
@bot.message_handler(func=lambda message: message.text == 'Free Fire')
def handle_game_choice(message):
    bot.send_message(message.chat.id, f"Comming soon.")
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_back = KeyboardButton('Back')
    markup.add(button_back)
    bot.send_message(message.chat.id, "Would you like to go back?", reply_markup=markup)

# Command to set a user as a reseller
@bot.message_handler(commands=['rel'])
def addre_handler(message):
    user_id = message.from_user.id
    if is_reseller(user_id):
        bot.reply_to(message, "HI SIS CUTE\nMobile Legends Product List \n\n86 Diamond - $61.5\n172 Diamond - $122\n257 Diamond  - $177.5\n343 Diamond  - $239\n429 Diamond  - $299.5\n514 Diamond  - $355\n600 Diamond  - $416.5\n706 Diamond  - $480\n792 Diamond  - $541.5 \n878 Diamond  - $602\n963 Diamond  - $657.5\n1050 Diamond  - $724\n1135 Diamond  - $779.5 \n1412 Diamond  - $960\n1584 Diamond  - $1082\n1755 Diamond  - $1199\n1926 Diamond  - $1315\n2195 Diamond  - $1453 \n2538 Diamond (2538) - $1692\n2901 Diamond (2901) - $1933\n3688 Diamond (3688) - $2424 \n4394 Diamond (4394) - $2904\n5532 Diamond (5532) - $3660\n6238 Diamond (6238) - $4140\n6944 Diamond (6944) - $4620\n7727 Diamond (7727) - $5113 \n8433 Diamond (8433) - $5593\n9288 Diamond (9288) - $6079\n10700 Diamond (10700) - $7039\nTwilight Pass (twilight) - $402.5\nWeekly Pass (Weekly) - $76 \n2 x Weekly Pass (2Weekly) - $152\n3 x Weekly Pass (3Weekly) - $228\n4 x Weekly Pass (4Weekly) - $304 \n5 x Weekly Pass (5Weekly) - $380\n\nExample format order:\n123456789 12345 86\nuserid serverid code")
    else:
        bot.reply_to(message, "You're not rel.")

# Function to send the code order id  
def generate_redeem_code():
    # Generate a random number (0-99999999999999) to ensure a total length of 20 characters 
    number = random.randint(0, 99999999999999) 
     
    # Generate four random uppercase letters 
    letters = ''.join(random.choices(string.ascii_uppercase, k=4)) 
     
    # Construct the redeem code 
    redeem_code = f"S2{number:014d}{letters}"  # The number is zero-padded to 19 digits 
     
    return redeem_code

# Handler for Button 3 ("💰 ដាក់ប្រាក់")
@bot.message_handler(func=lambda message: message.text == "💰 Deposit")
def button_3_handler(message):
    bot.send_message(message.chat.id, "Please enter the amount in USD:")
    user_states[message.chat.id] = "waiting_for_amount"

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "waiting_for_amount")
def handle_amount(message):
    try:
        amount = float(message.text)
        if amount <= 0:
            bot.send_message(message.chat.id, "Please enter an amount greater than $0")
            return

        # Clear user state
        user_states.pop(message.chat.id, None)

        # Generate QR code
        generate_qr(message, amount)

    except ValueError:
        bot.send_message(message.chat.id, "Please send 0.01")

# Automatically handles purchase messages in the format "server_id zone_id item_id"
@bot.message_handler(func=lambda message: len(message.text.split()) == 3)
def buy_item_handler(message):
    try:
        user_id = message.from_user.id
        args = message.text.split()

        # Extract server ID, zone ID, and item ID from the message
        server_id = args[0]
        zone_id = args[1]
        item_id = args[2]

        # Check if the item ID is valid and if the price is available
        # Determine the price
        if item_id in ITEM_PRICES:
            price = ITEM_PRICES[item_id]["reseller"] if is_reseller(user_id) else ITEM_PRICES[item_id]["normal"]
        else:
            bot.reply_to(message, f"Sorry, we do not support buying {item_id} items.")
            return

        # Check user balance
        balance = get_balance(user_id)
        if balance < price:
            bot.reply_to(message, f"Insufficient balance. The item costs ${price:.2f}. Please add funds.")
            return

        #  Validate Mobile Legends ID with API
        api_url = f"https://api.isan.eu.org/nickname/ml?id={server_id}&zone={zone_id}"
        response =requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                nickname = data.get("name", "Unknown")
            else:
                bot.reply_to(message, "ID Game is wrong.")
                return
        else:
            bot.reply_to(message, "ID Game is wrong")
            return

        # Deduct price from balance
        # Deduct the balance and process the purchase
        update_balance(user_id, -price)
        # Code
        code = generate_redeem_code()

        # Notify the user
        bot.reply_to(message, f"New Order Sucessfully ❇️\nPlayer ID: {server_id}\nServer ID: {zone_id}\nNickname: {nickname}\nProduct: {item_id}\nStatus: Success ✅")

        # Forward purchase details to groups
        # Forward purchase details to Group 1
        group_1_id = -1002224584287 # Replace with your Group 1 ID
        purchase_details = f"{server_id} {zone_id} {item_id}"
        bot.send_message(group_1_id, purchase_details)

        # Forward buyer information to Group 2
        group_2_id = -1002172568129  # Replace with your Group 2
        buyer_info = f"New Order Sucessfully ❇️\nPlayer ID: {server_id}\nServer ID: {zone_id}\nNickname: {nickname}\nProduct: {item_id}\nOrder ID: {code}\nStatus: Success ✅"
        bot.send_message(group_2_id, buyer_info)

    except Exception as e:
        bot.reply_to(message, f"An error occurred: {e}")                   

# Run the bot
if __name__ == "__main__":
    init_db()
    logging.info("Bot is running...")
    bot.infinity_polling()