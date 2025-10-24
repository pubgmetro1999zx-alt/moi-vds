import os
import sqlite3
import telebot
from telebot import types

bot = telebot.TeleBot("8241565803:AAE5W3cYAym0oG_EtNhL_w3sK9X0EfFXn7g")

# Увеличиваем лимиты для больших файлов
bot.max_file_size = 50 * 1024 * 1024  # 50MB
bot._server_cert = None  # Отключаем проверку сертификата для стабильности

# База данных
conn = sqlite3.connect('files.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users
             (user_id INTEGER PRIMARY KEY, 
              username TEXT,
              storage_used INTEGER DEFAULT 0,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS files
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              user_id INTEGER, 
              filename TEXT,
              file_path TEXT,
              file_size INTEGER,
              uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()

# Папка для файлов
if not os.path.exists("user_files"):
    os.makedirs("user_files")

def get_user_files(user_id, page=0, limit=5):
    offset = page * limit
    cursor.execute("SELECT filename, file_size FROM files WHERE user_id=? ORDER BY uploaded_at DESC LIMIT ? OFFSET ?", 
                   (user_id, limit, offset))
    files = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) FROM files WHERE user_id=?", (user_id,))
    total = cursor.fetchone()[0]
    
    return files, total

def get_user_storage(user_id):
    cursor.execute("SELECT storage_used FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0

def update_user_storage(user_id, size):
    current = get_user_storage(user_id)
    cursor.execute("INSERT OR REPLACE INTO users (user_id, storage_used) VALUES (?, ?)", 
                   (user_id, current + size))
    conn.commit()

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or f"user_{user_id}"
    
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", 
                   (user_id, username))
    conn.commit()
    
    show_main_menu(message.chat.id, user_id)

def show_main_menu(chat_id, user_id):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("📤 Загрузить", callback_data=f"upload_{user_id}")
    btn2 = types.InlineKeyboardButton("📥 Выгрузить", callback_data=f"download_{user_id}")
    btn3 = types.InlineKeyboardButton("📋 Список файлов", callback_data=f"list_{user_id}_0")
    btn4 = types.InlineKeyboardButton("👤 Профиль", callback_data=f"profile_{user_id}")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    
    bot.send_message(chat_id, 
                    "🤖 Бот для работы с файлами\n\n"
                    "Выберите действие:",
                    reply_markup=markup)

@bot.message_handler(commands=['upload'])
def upload_command(message):
    user_id = message.from_user.id
    msg = bot.send_message(message.chat.id, 
                          "📤 Отправьте ЛЮБОЙ файл для загрузки\n"
                          "❌ Для отмены отправьте /cancel",
                          reply_markup=get_cancel_markup(user_id))
    bot.register_next_step_handler(msg, process_upload)

def get_cancel_markup(user_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Отменить", callback_data=f"cancel_{user_id}"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('upload_'))
def upload_callback(call):
    user_id = int(call.data.split('_')[1])
    
    if call.from_user.id != user_id:
        bot.answer_callback_query(call.id, "❌ Это не твое меню!")
        return
        
    msg = bot.send_message(call.message.chat.id, 
                          "📤 Отправьте ЛЮБОЙ файл для загрузки\n"
                          "❌ Для отмены отправьте /cancel",
                          reply_markup=get_cancel_markup(user_id))
    bot.register_next_step_handler(msg, process_upload)

def process_upload(message):
    if message.text and message.text == '/cancel':
        bot.send_message(message.chat.id, "✅ Загрузка отменена")
        return
        
    user_id = message.from_user.id
    
    # Принимаем ЛЮБОЙ файл - документ, фото, видео, аудио
    file_id = None
    file_name = "unknown"
    
    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_name = f"photo_{file_id}.jpg"
    elif message.video:
        file_id = message.video.file_id
        file_name = message.video.file_name or f"video_{file_id}.mp4"
    elif message.audio:
        file_id = message.audio.file_id
        file_name = message.audio.file_name or f"audio_{file_id}.mp3"
    elif message.voice:
        file_id = message.voice.file_id
        file_name = f"voice_{file_id}.ogg"
    else:
        bot.send_message(message.chat.id, "❌ Отправьте файл (документ, фото, видео, аудио)")
        return
    
    try:
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_size = len(downloaded_file)
        
        # Сохраняем файл
        user_folder = f"user_files/{user_id}"
        os.makedirs(user_folder, exist_ok=True)
        
        file_path = f"{user_folder}/{file_name}"
        
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
        
        # Сохраняем в базу
        cursor.execute('''INSERT INTO files (user_id, filename, file_path, file_size)
                       VALUES (?, ?, ?, ?)''', (user_id, file_name, file_path, file_size))
        update_user_storage(user_id, file_size)
        conn.commit()
        
        bot.send_message(message.chat.id, f"✅ Файл {file_name} загружен! ({file_size/1024:.1f} KB)")
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка загрузки: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('list_'))
def list_files(call):
    try:
        data = call.data.split('_')
        user_id = int(data[1])
        page = int(data[2]) if len(data) > 2 else 0  # ФИКС: проверяем длину массива
        
        if call.from_user.id != user_id:
            bot.answer_callback_query(call.id, "❌ Это не твое меню!")
            return
            
        files, total = get_user_files(user_id, page)
        
        if not files:
            bot.edit_message_text("📁 У вас нет файлов", 
                                call.message.chat.id,
                                call.message.message_id,
                                reply_markup=get_back_markup(user_id))
            return
        
        file_list = "\n".join([f"📄 {name} ({size/1024:.1f} KB)" for name, size in files])
        
        text = f"📁 Ваши файлы (стр. {page+1}):\n\n{file_list}\n\nВсего файлов: {total}"
        
        markup = types.InlineKeyboardMarkup()
        
        # Кнопки файлов для скачивания
        for filename, size in files:
            # Обрезаем длинные имена файлов
            display_name = filename[:30] + "..." if len(filename) > 30 else filename
            callback_data = f"get_{user_id}_{filename.replace(' ', '_')}"  # Заменяем пробелы
            markup.add(types.InlineKeyboardButton(f"📥 {display_name}", callback_data=callback_data))
        
        # Навигация
        nav_buttons = []
        if page > 0:
            nav_buttons.append(types.InlineKeyboardButton("◀️ Назад", callback_data=f"list_{user_id}_{page-1}"))
        
        if (page + 1) * 5 < total:
            nav_buttons.append(types.InlineKeyboardButton("Вперед ▶️", callback_data=f"list_{user_id}_{page+1}"))
        
        if nav_buttons:
            markup.row(*nav_buttons)
        
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data=f"back_{user_id}"))
        
        bot.edit_message_text(text,
                             call.message.chat.id,
                             call.message.message_id,
                             reply_markup=markup)
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Ошибка: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('download_'))
def download_menu(call):
    user_id = int(call.data.split('_')[1])
    
    if call.from_user.id != user_id:
        bot.answer_callback_query(call.id, "❌ Это не твое меню!")
        return
        
    # Переходим на первую страницу списка файлов
    call.data = f"list_{user_id}_0"
    list_files(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith('get_'))
def download_file(call):
    try:
        data = call.data.split('_')
        user_id = int(data[1])
        filename = '_'.join(data[2:]).replace('_', ' ')  # Возвращаем пробелы обратно
        
        if call.from_user.id != user_id:
            bot.answer_callback_query(call.id, "❌ Это не твое меню!")
            return
            
        file_path = f"user_files/{user_id}/{filename}"
        
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            
            # Проверяем размер файла
            if file_size > 50 * 1024 * 1024:  # 50MB лимит
                bot.answer_callback_query(call.id, "❌ Файл слишком большой (>50MB)")
                return
                
            with open(file_path, 'rb') as file:
                bot.send_document(call.message.chat.id, file, visible_file_name=filename)
            bot.answer_callback_query(call.id, "✅ Файл отправлен")
        else:
            bot.answer_callback_query(call.id, "❌ Файл не найден")
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Ошибка: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('profile_'))
def show_profile(call):
    user_id = int(call.data.split('_')[1])
    
    if call.from_user.id != user_id:
        bot.answer_callback_query(call.id, "❌ Это не твое меню!")
        return
        
    cursor.execute("SELECT username, storage_used FROM users WHERE user_id=?", (user_id,))
    user_data = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) FROM files WHERE user_id=?", (user_id,))
    file_count = cursor.fetchone()[0]
    
    if user_data:
        username, storage_used = user_data
        profile_text = (f"👤 Профиль:\n\n"
                       f"🆔 ID: {user_id}\n"
                       f"📛 Username: @{username}\n"
                       f"📁 Файлов: {file_count}\n"
                       f"💾 Использовано: {storage_used/1024/1024:.2f} MB")
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data=f"back_{user_id}"))
        
        bot.edit_message_text(profile_text,
                            call.message.chat.id,
                            call.message.message_id,
                            reply_markup=markup)

def get_back_markup(user_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data=f"back_{user_id}"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('back_'))
def back_to_main(call):
    user_id = int(call.data.split('_')[1])
    
    if call.from_user.id != user_id:
        bot.answer_callback_query(call.id, "❌ Это не твое меню!")
        return
        
    show_main_menu(call.message.chat.id, user_id)
    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('cancel_'))
def cancel_action(call):
    user_id = int(call.data.split('_')[1])
    
    if call.from_user.id != user_id:
        bot.answer_callback_query(call.id, "❌ Это не твое меню!")
        return
        
    bot.send_message(call.message.chat.id, "✅ Действие отменено")
    show_main_menu(call.message.chat.id, user_id)

@bot.message_handler(commands=['cancel'])
def cancel_command(message):
    bot.send_message(message.chat.id, "✅ Действие отменено")
    show_main_menu(message.chat.id, message.from_user.id)

print("🚀 Бот запущен!")
bot.polling(none_stop=True)
