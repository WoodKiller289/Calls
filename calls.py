import telebot
from telebot import types
import logging
import sys

# Константы
TOKEN = '7969743484:AAFICUHs0UDQEYIRG6vryaysj_k0J4smzHE'
WORKER_CHAT_ID = -1002490791470  # ID группы для работников
ADMIN_CHAT_ID = 6262188354  # ID админа
bot = telebot.TeleBot(TOKEN)

# Глобальные переменные
user_languages = {}
order_data = {}
worker_active_orders = {}  # Формат {worker_id: client_id}
active_chats = {}  # Формат {client_id: worker_id}

# Глобальный список пользователей
user_list = set()

# Настройка логирования ошибок
logging.basicConfig(filename='bot_errors.log', level=logging.ERROR)

# Команда /start для выбора языка
@bot.message_handler(commands=['start'])
def start(message):
    user_list.add(message.chat.id)  # Добавляем пользователя в список
    markup = types.InlineKeyboardMarkup()
    button_ru = types.InlineKeyboardButton("РУССКИЙ", callback_data="lang_ru")
    button_en = types.InlineKeyboardButton("ENGLISH", callback_data="lang_en")
    markup.add(button_ru, button_en)
    bot.send_message(message.chat.id, "Выберите язык / Choose your language:", reply_markup=markup)

# Обработчик выбора языка
@bot.callback_query_handler(func=lambda call: call.data in ["lang_ru", "lang_en"])
def callback_language(call):
    if call.data == "lang_ru":
        user_languages[call.message.chat.id] = 'ru'
        bot.send_message(call.message.chat.id, "Вы выбрали Русский язык.")
        send_terms(call.message.chat.id, 'ru')
    elif call.data == "lang_en":
        user_languages[call.message.chat.id] = 'en'
        bot.send_message(call.message.chat.id, "You have selected English.")
        send_terms(call.message.chat.id, 'en')

# Отправка правил и кнопки "Принять"
def send_terms(chat_id, language):
    markup = types.InlineKeyboardMarkup()
    button_accept = types.InlineKeyboardButton("ПРИНЯТЬ" if language == 'ru' else "ACCEPT", callback_data="accept_terms")
    markup.add(button_accept)

    if language == 'ru':
        terms_text = (
            "Правила конфиденциальности и оплаты:\n"
            "1. Вы соглашаетесь предоставлять максимально подробную информацию о вашем заказе для лучшего результата.\n"
            "2. Все платежи являются окончательными и невозвратными.\n"
            "3. Мы уважаем вашу конфиденциальность и гарантируем защиту ваших данных.\n"
            "4. Все заказы обрабатываются строго в соответствии с предоставленной информацией.\n"
            "5. Для любых вопросов свяжитесь с нашим администратором.\n"
            "\nНажимая 'ПРИНЯТЬ', вы соглашаетесь с условиями."
        )
    else:
        terms_text = (
            "Privacy and Payment Terms:\n"
            "1. You agree to provide accurate information about your order for proper processing.\n"
            "2. All payments are final and non-refundable.\n"
            "3. We respect your privacy and ensure the protection of your data.\n"
            "4. All orders are processed strictly according to the provided information.\n"
            "5. For any inquiries, please contact our administrator.\n"
            "\nBy pressing 'ACCEPT', you agree to these terms."
        )
    bot.send_message(chat_id, terms_text, reply_markup=markup)

# Обработчик нажатия "Принять"
@bot.callback_query_handler(func=lambda call: call.data == "accept_terms")
def accept_terms(call):
    language = user_languages.get(call.message.chat.id, 'ru')
    send_menu(call.message.chat.id, language)

# Отправка основного меню
def send_menu(chat_id, language):
    if language == 'ru':
        menu_text = "Вы в меню. Доступные команды:\n/order - Создать заказ\n/contact - Связаться с администратором"
    else:
        menu_text = "You are in the menu. Available commands:\n/order - Create an order\n/contact - Contact admin with admin ASAP"
    bot.send_message(chat_id, menu_text)

# Обработка команды /contact
@bot.message_handler(commands=['contact'])
def contact_admin(message):
    language = user_languages.get(message.chat.id, 'en')  # По умолчанию английский
    if language == 'ru':
        contact_info = f"Связаться с администратором: [Админ](tg://user?id={ADMIN_CHAT_ID})"
    else:
        contact_info = f"Contact the administrator: [Admin](tg://user?id={ADMIN_CHAT_ID})"
    bot.send_message(
        message.chat.id, 
        contact_info, 
        parse_mode="Markdown"
    )

# Обработка команды /order
@bot.message_handler(commands=['order'])
def order(message):
    language = user_languages.get(message.chat.id, 'ru')
    
    if language == 'en':
        bot.send_message(message.chat.id, 
            "Please provide the details of your order in as much detail as possible.(In the first line, select the language for the call!) \n"
            "Language En, De \n"
            "Purpose of the call/task; \n"
            "Background/What led to the order; \n"
            "Cardholder's full name + Gender; \n"
            "SSN,DOB,MMN - optionally; \n"
            "Addresses; \n"
            "Cardholder's email + Is access available?; \n"
            "Cardholder's phone + Is access to the phone available?; \n"
            "Number to call from; \n"
            "Number to call; \n"
            "Website/Name of the organization we are calling; \n"
            "Details/AN RN Card number. \n"
            "Did u have a BG/CR? \n"
            "Please describe your case in one message for the bot to work correctly! confirm and wait for further communication."
        )
    else:
        bot.send_message(message.chat.id, 
            "Пожалуйста, опишите детали вашего заказа максимально подробно.(В первой строке укажите язык) \n"
            "Язык En, De \n"
            "Цель звонка/задача; \n"
            "предыстория/что предшествовало заказу; \n"
            "ФИО кардхолдера + пол; \n"
            "SSN,DOB,MMN - не всегда все; \n"
            "адреса; \n"
            "почта кх. + Есть ли доступ?; \n"
            "Телефон кх + Есть ли доступ к телефону?; \n"
            "Номер с которого звонить; \n"
            "номер куда звонить; \n"
            "сайт / название организации куда звоним; \n"
            "Детали/AN RN, номер карты. \n"
            "Есть наличие BG/CR? \n"
            "Пожалуйста, описывайте ваш кейс в одном сообщении для верной работы бота! подтвердите и ожидайте дальнейшего сообщения"
        )
    bot.register_next_step_handler(message, handle_order_details)

# Обработка данных заказа
def handle_order_details(message):
    order_data[message.chat.id] = {
        "text": message.text,
        "user_id": message.chat.id
    }

    language = user_languages.get(message.chat.id, 'ru')

    # Отправляем заказ в рабочую группу
    bot.send_message(WORKER_CHAT_ID, f"Новый заказ:\n{message.text}\nОтветьте на это сообщение, чтобы взять заказ в работу.")
    
    if language == 'en':
        bot.send_message(message.chat.id, "Your order is already in the queue. Once the worker is ready to start your order, you will immediately receive a notification")
    else:    
        bot.send_message(message.chat.id, "Ваш заказ уже в очереди. После того, как прозвон будет готов приступить к вашему заказу, вам сразу же придёт уведомление")

# Обработка ответов от работников
@bot.message_handler(func=lambda message: message.reply_to_message and message.chat.id == WORKER_CHAT_ID)
def worker_reply(message):
    try:
        # Проверяем, что это ответ на сообщение о заказе
        if message.reply_to_message.text.startswith("Новый заказ:"):
            client_id = next((user_id for user_id, order in order_data.items() if order['text'] in message.reply_to_message.text), None)

            if client_id:
                # Закрепляем работника за заказом
                worker_active_orders[message.from_user.id] = client_id
                active_chats[client_id] = message.from_user.id

                # Уведомляем клиента и админа
                
                bot.send_message(client_id, "Ваш заказ принят. Свяжитесь с @WoodAbel для оплаты.")
                bot.send_message(ADMIN_CHAT_ID, f"Клиент {client_id} должен связаться для оплаты.")

            else:
                bot.send_message(message.chat.id, "Не удалось найти заказ.")
    except Exception as e:
        logging.error(f"Ошибка при ответе на заказ: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при обработке заказа.")

# Команда /create_chat для создания чата после оплаты
@bot.message_handler(commands=['create_chat'])
def create_chat(message):
    try:
        _, worker_id, client_id = message.text.split()
        worker_id = int(worker_id)
        client_id = int(client_id)

        if active_chats.get(client_id) == worker_id:
            bot.send_message(worker_id, "Чат с клиентом открыт. Напишите сообщение.")
            bot.send_message(client_id, "Чат с работником открыт. Вы можете писать.")
        else:
            bot.send_message(message.chat.id, "Нет активного заказа для этого клиента и работника.")
    except ValueError:
        bot.send_message(message.chat.id, "Используйте формат команды: /create_chat <worker_id> <client_id>.")

# Обработка ответов от работников
@bot.message_handler(func=lambda message: message.reply_to_message and message.chat.id == WORKER_CHAT_ID)
def worker_reply(message):
    try:
        if message.reply_to_message.text.startswith("Новый заказ:"):
            client_id = next((user_id for user_id, order in order_data.items() if order['text'] in message.reply_to_message.text), None)

            if client_id:
                # Закрепляем работника за заказом
                worker_active_orders[message.from_user.id] = client_id
                active_chats[client_id] = message.from_user.id

                # Уведомляем клиента и админа
                bot.send_message(client_id, "Ваш заказ принят. Свяжитесь с админом для оплаты.")
                bot.send_message(ADMIN_CHAT_ID, f"Клиент {client_id} должен связаться для оплаты.")
            else:
                bot.send_message(message.chat.id, "Не удалось найти заказ.")
    except Exception as e:
        logging.error(f"Ошибка при ответе на заказ: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при обработке заказа.")

# Команда /create_chat для создания чата после оплаты
@bot.message_handler(commands=['create_chat'])
def create_chat(message):
    try:
        _, worker_id, client_id = message.text.split()
        worker_id = int(worker_id)
        client_id = int(client_id)

        if active_chats.get(client_id) == worker_id:
            bot.send_message(worker_id, "Чат с клиентом открыт. Напишите сообщение.")
            bot.send_message(client_id, "Чат с работником открыт. Вы можете писать.")
        else:
            bot.send_message(message.chat.id, "Нет активного заказа для этого клиента и работника.")
    except ValueError:
        bot.send_message(message.chat.id, "Используйте формат команды: /create_chat <worker_id> <client_id>.")

# Обработка сообщений от клиента и работника
@bot.message_handler(func=lambda message: message.chat.id in active_chats or message.chat.id in worker_active_orders)
def route_message(message):
    if message.chat.id in active_chats:  # Сообщение от клиента
        worker_id = active_chats[message.chat.id]
        # Пересылаем сообщение работнику
        bot.send_message(worker_id, f"Сообщение от клиента: {message.text}")
        # Уведомляем админа
        bot.send_message(ADMIN_CHAT_ID, f"Сообщение от клиента {message.chat.id} к работнику {worker_id}: {message.text}")
    elif message.chat.id in worker_active_orders:  # Сообщение от работника
        client_id = worker_active_orders[message.chat.id]
        # Пересылаем сообщение клиенту
        bot.send_message(client_id, f"Сообщение от работника: {message.text}")
        # Уведомляем админа
        bot.send_message(ADMIN_CHAT_ID, f"Сообщение от работника {message.chat.id} к клиенту {client_id}: {message.text}")

# Завершение заказа клиентом
@bot.message_handler(commands=['complete_order'])
def complete_order(message):
    user_id = message.chat.id
    language = user_languages.get(user_id, 'ru')

    # Уведомление о завершении
    if language == 'en':
        bot.send_message(user_id, "Your order has been successfully completed. Returning to main menu.")
    else:
        bot.send_message(user_id, "Ваш заказ успешно завершён. Возвращаем вас в главное меню.")

    # Возвращаем клиента в главное меню
    send_menu(user_id, language)

# Завершение заказа администратором и удаление чата
@bot.message_handler(commands=['delete_chat'])
def delete_chat(message):
    try:
        _, worker_id, client_id = message.text.split()
        worker_id = int(worker_id)
        client_id = int(client_id)

        # Удаляем чат из активных заказов
        if worker_active_orders.get(worker_id) == client_id:
            del worker_active_orders[worker_id]
            del active_chats[client_id]

            bot.send_message(ADMIN_CHAT_ID, f"Чат между работником {worker_id} и клиентом {client_id} удалён.")
            bot.send_message(worker_id, "Ваш чат с клиентом завершён.")
            bot.send_message(client_id, "Ваш чат с работником завершён. Спасибо за использование сервиса!")
        else:
            bot.send_message(ADMIN_CHAT_ID, "Ошибка: этот чат не найден в активных.")
    except ValueError:
        bot.send_message(message.chat.id, "Используйте формат команды: /delete_chat <worker_id> <client_id>.")

# Обработка команды /broadcast
@bot.message_handler(commands=['broadcast'])
def broadcast(message):
    if message.chat.id == ADMIN_CHAT_ID:  # Проверка, что команду выполняет админ
        try:
            # Получаем текст сообщения после команды /broadcast
            _, broadcast_message = message.text.split(' ', 1)
            
            # Рассылка сообщения всем пользователям
            for user_id in user_list:
                try:
                    bot.send_message(user_id, f"📢 Broadcast message:\n\n{broadcast_message}")
                except Exception as e:
                    logging.error(f"Failed to send message to {user_id}: {e}")
                    bot.send_message(ADMIN_CHAT_ID, f"Не удалось отправить сообщение пользователю {user_id}. Ошибка: {e}")

            bot.send_message(ADMIN_CHAT_ID, "📢 Broadcast завершён. Сообщение отправлено всем пользователям.")
        except ValueError:
            bot.send_message(ADMIN_CHAT_ID, "⚠️ Используйте формат команды: /broadcast <текст сообщения>")
    else:
        bot.send_message(message.chat.id, "⚠️ У вас нет прав для выполнения этой команды.")

# Команда для остановки бота и очистки данных
@bot.message_handler(commands=['stop'])
def stop_and_cleanup(message):
    # Проверка на права администратора
    if message.chat.id == ADMIN_CHAT_ID:
        # Очистка всех данных
        order_data.clear()
        worker_active_orders.clear()
        user_languages.clear()

        # Логируем успешное завершение
        logging.info("Все данные очищены, бот останавливается.")
        bot.send_message(message.chat.id, "Бот останавливается, все данные очищены.")

        # Остановка бота
        bot.stop_polling()  # Останавливаем работу бота
        sys.exit(0)  # Завершаем программу
    else:
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")

# Запуск бота
if __name__ == "__main__":
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(f"Error occurred: {e}")