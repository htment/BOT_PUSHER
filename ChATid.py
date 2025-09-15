import requests

TOKEN = "_____________________________"

def get_chat_id():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    response = requests.get(url).json()
    
    if not response["result"]:
        print("Сначала напишите боту любое сообщение в Telegram!")
    else:
        chat_id = response["result"][0]["message"]["chat"]["id"]
        print(f"Ваш TELEGRAM_CHAT_ID: {chat_id}")

get_chat_id()