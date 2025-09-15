import os
import time
import telebot
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Конфигурация
TELEGRAM_BOT_TOKEN = '___________________________'
TELEGRAM_CHAT_ID = '-4883529011'  # Можно узнать у @userinfobot
FOLDER_TO_WATCH = 'C:/Jira_Attachments/PLAT-95123'  # Путь к папке, которую мониторим

# Инициализация бота
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Словарь для отслеживания уже обработанных файлов
processed_files = {}

class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            time.sleep(1)  # Даем файлу полностью загрузиться
            
            if file_path not in processed_files:
                self.send_file_to_telegram(file_path)
                processed_files[file_path] = True

    def send_file_to_telegram(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                file_name = os.path.basename(file_path)
                
                # Определяем тип файла для правильной отправки
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    bot.send_photo(TELEGRAM_CHAT_ID, file, caption=f"Новый файл: {file_name}")
                elif file_name.lower().endswith(('.mp4', '.mov', '.avi')):
                    bot.send_video(TELEGRAM_CHAT_ID, file, caption=f"Новый файл: {file_name}")
                elif file_name.lower().endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx')):
                    bot.send_document(TELEGRAM_CHAT_ID, file, caption=f"Новый файл: {file_name}")
                else:
                    bot.send_document(TELEGRAM_CHAT_ID, file, caption=f"Новый файл: {file_name}")
                
                print(f"Файл {file_name} отправлен в Telegram")
        except Exception as e:
            print(f"Ошибка при отправке файла: {e}")

def start_monitoring():
    # Инициализация наблюдателя
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, FOLDER_TO_WATCH, recursive=True)
    observer.start()
    
    print(f"Бот запущен и мониторит папку {FOLDER_TO_WATCH}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    # Сначала добавляем уже существующие файлы в processed_files
    for root, dirs, files in os.walk(FOLDER_TO_WATCH):
        for file in files:
            file_path = os.path.join(root, file)
            processed_files[file_path] = True
    
    # Запускаем мониторинг
    start_monitoring()