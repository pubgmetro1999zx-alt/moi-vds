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
