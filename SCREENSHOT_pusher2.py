import os
import time
import telebot
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Конфигурация
TELEGRAM_BOT_TOKEN = '7461307559:AAE_SUxxRMXibmN3fh-_ikl6tV6o52F3Abo'
TELEGRAM_CHAT_ID = '-1002570793758'  # Можно узнать у @userinfobot
FOLDER_TO_WATCH = 'C:/Jira_Attachments/PLAT-110405'  # Путь к папке, которую мониторим

# Инициализация бота
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Словарь для отслеживания последнего времени модификации файлов
file_modification_times = {}

class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            self.process_file(event.src_path, "Новый файл")

    def on_modified(self, event):
        if not event.is_directory:
            self.process_file(event.src_path, "Изменен файл")

    def process_file(self, file_path, action_prefix):
        time.sleep(1)  # Даем файлу полностью загрузиться/измениться
        
        try:
            current_mod_time = os.path.getmtime(file_path)
            
            # Если файл новый или время модификации изменилось
            if file_path not in file_modification_times or file_modification_times[file_path] != current_mod_time:
                self.send_file_to_telegram(file_path, action_prefix)
                file_modification_times[file_path] = current_mod_time
        except Exception as e:
            print(f"Ошибка при обработке файла {file_path}: {e}")

    def send_file_to_telegram(self, file_path, action_prefix):
        try:
            with open(file_path, 'rb') as file:
                file_name = os.path.basename(file_path)
                
                # Определяем тип файла для правильной отправки
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    bot.send_photo(TELEGRAM_CHAT_ID, file, caption=f"{action_prefix}: {file_name}")
                elif file_name.lower().endswith(('.mp4', '.mov', '.avi')):
                    bot.send_video(TELEGRAM_CHAT_ID, file, caption=f"{action_prefix}: {file_name}")
                elif file_name.lower().endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx')):
                    bot.send_document(TELEGRAM_CHAT_ID, file, caption=f"{action_prefix}: {file_name}")
                else:
                    bot.send_document(TELEGRAM_CHAT_ID, file, caption=f"{action_prefix}: {file_name}")
                
                print(f"Файл {file_name} отправлен в Telegram ({action_prefix})")
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
    # Сначала запоминаем время модификации существующих файлов
    for root, dirs, files in os.walk(FOLDER_TO_WATCH):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                file_modification_times[file_path] = os.path.getmtime(file_path)
            except:
                continue
    
    # Запускаем мониторинг
    start_monitoring()
