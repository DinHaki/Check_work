import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, InputMediaDocument, InputMediaVideo
from telegram import KeyboardButton, ReplyKeyboardMarkup
from datetime import timedelta, datetime


from database_handler import DataBase


bot = telebot.TeleBot('6365731257:AAH49Z8Mu14LX2YMVCGSWZwXdDe9mhxSN88')
group_link = 't.me/poloies'
chat_id_group = '@poloies'


db = DataBase(db_file='datebase.db')
support_chat_id = -4159845515
main_chat_id = -1001925020959
price_step = 50
history_limit = 10


#__________________________Кнопки пользователя___________________________#
markup_keyboard = InlineKeyboardMarkup()
btn1 = InlineKeyboardButton("Баланс", callback_data="balance")
markup_keyboard.row(btn1)  
btn2 = InlineKeyboardButton("История торгов с принятием участия", callback_data="history")
markup_keyboard.row(btn2) 
btn3 = InlineKeyboardButton("Жалоба на пользователя", callback_data="report")
markup_keyboard.row(btn3) 
btn4 = InlineKeyboardButton("Правила",callback_data="rules")
btn5 = InlineKeyboardButton("Помощь",callback_data="help")
markup_keyboard.row(btn4,btn5) 

#__________________________Кнопки администратора___________________________#  
markup_administrator = InlineKeyboardMarkup()
markup_administrator.add(InlineKeyboardButton("История размещенных лотов", callback_data = "lots_history"))
markup_administrator.add(InlineKeyboardButton("Пожаловаться на пользователя", callback_data = "report"))
markup_administrator.add(InlineKeyboardButton("Создать лот", callback_data = "create"))
markup_administrator.add(InlineKeyboardButton("Баланс", callback_data = "balance"))
markup_administrator.add(InlineKeyboardButton("История торгов с принятием участия", callback_data = "history"))
markup_administrator.add(InlineKeyboardButton("Удаление лота", callback_data = "lots_deleting"))

#__________________________Кнопки супер администратора___________________________#  
markup_seper_adm = InlineKeyboardMarkup()
markup_seper_adm.add(InlineKeyboardButton("Выдать полномочия", callback_data = "invate"))
markup_seper_adm.add(InlineKeyboardButton("Проверка баланса пользователя", callback_data = "check"))
markup_seper_adm.add(InlineKeyboardButton("Составление ДКП", callback_data = "create_document"))

#__________________________Клавиатура для торгов___________________________# 
markup_main_menu = InlineKeyboardMarkup()
markup_main_menu.add(InlineKeyboardButton("Главное Меню", callback_data = "back"))


#__________________________Проверка какой пользователь зашел к боту и отправки соот-ей клавиатуры___________________________# 
@bot.message_handler(commands=['start'])
def start(message):
    if message.text == '/start':
        if message.chat.id == support_chat_id:
            pass
        elif message.chat.id == main_chat_id:
            pass

        else:
            user_id = message.from_user.id
            user_name = message.from_user.username

            if not db.is_user_exists(user_id):
                db.add_user(user_id, user_name)
                user_type = 'user'
            else:
                user_type = db.get_user_type(user_id)
            
            if user_type == 'user':
                markup = markup_keyboard
            elif user_type == 'admin':
                markup = markup_administrator
            elif user_type == 's_admin':
                markup = markup_seper_adm
                
            if user_type == 'blocked':
                bot.send_message(message.chat.id, 'Вы заблокированы, свяжитесь @dinhaki', reply_markup=None)
            else:
                hello_text =  f"Привет, я бот аукционов @poloies Я помогу вам следить за выбранными лотами ,и регулировать ход аукциона.А так же буду следить за вашими накопленными балами. Удачных торгов 🤝"
                bot.send_message(message.chat.id, hello_text, reply_markup=markup)
    else:
        lot_id =  int(message.text.split()[-1])
        
        max_bet = db.get_max_bet(lot_id)
        _, lot_name, lot_desc, lot_start_price, lot_geolocations, lot_medias, id_seller, _, _, _, _, _ = db.get_lot_info(lot_id)
        
        max_bet = db.get_max_bet(lot_id)
        if lot_start_price > max_bet:
            next_price = lot_start_price
        else:
            next_price = max_bet + price_step

        text =  f'{lot_name}\n{lot_desc}\nПродавец: @{db.get_user_name(id_seller)}\nСледующая ставка: {next_price}\n{lot_geolocations}'
        media_group_documents = []
        media_group = []
        media_list = lot_medias.split()
        for i in range(0, len(media_list), 2):
            file_type = media_list[i]
            file_id = media_list[i+1]
            if file_type == 'd':
                media_group_documents.append(InputMediaDocument(file_id, caption=''))
            elif file_type == 'p':
                media_group.append(InputMediaPhoto(file_id))
            elif file_type == 'v':
                media_group.append(InputMediaVideo(file_id))

        #__________________________Лот для лички___________________________# 
        markup_lot = InlineKeyboardMarkup()
        btn1 = (InlineKeyboardButton("⏰", callback_data = "time_to_end"))
        btn2 = (InlineKeyboardButton("ℹ", callback_data = "info"))
        markup_lot.row(btn1,btn2) 
        markup_lot.add(InlineKeyboardButton("Сделать ставку", callback_data = f"pay_{lot_id}"))
        

        if media_group_documents:
            bot.send_media_group(message.from_user.id, media=media_group_documents)
        bot.send_media_group(message.from_user.id, media=media_group)
        bot.send_message(message.from_user.id, text, reply_markup=markup_lot)


#__________________________Отправка бланков документов Д.К.П. отправка адм-ом___________________________# 
@bot.callback_query_handler(func=lambda call: call.data=="create_document")
def create_document(call):
    msg = bot.send_message(call.message.chat.id, "Введите ник пользователя-продавца")
    return bot.register_next_step_handler(msg, get_user_name_seller)

def get_user_name_seller(message):
    user_name_seller = message.text
    msg = bot.send_message(message.chat.id, "Введите ник пользователя-покупателя")
    return bot.register_next_step_handler(msg, get_user_name_customer, user_name_seller)

def get_user_name_customer(message, user_name_seller):
    user_name_customer = message.text

    user_id_seller = db.get_user_info(user_name_seller)[0]
    user_id_customer= db.get_user_info(user_name_customer)[0]

    bot.send_document(user_id_seller, open(r'C:\Users\admin\Desktop\Ekz\blank1_DKP.docx', 'rb'))
    bot.send_document(user_id_customer, open(r'C:\Users\admin\Desktop\Ekz\blank2_DKP.docx', 'rb'))
    bot.send_message(message.chat.id, f"Продавцу @{user_name_seller} и покупателю @{user_name_customer} отправлены документы")


#__________________________Проверка истории лотов в которых была сделана ставка___________________________# 
@bot.callback_query_handler(func=lambda call: call.data=="history")
def show_history(call):
    user_id = call.message.chat.id
    
    history = db.get_history(user_id)[:history_limit]

    markup_history = InlineKeyboardMarkup()
    for lot_id in history:
        _, lot_name, lot_desc, _, _, _, id_seller, _, _, _, _, _ = db.get_lot_info(lot_id)
        seller_name = db.get_user_name(id_seller)
        markup_history.add(InlineKeyboardButton(f"@{seller_name} {lot_name} {lot_desc}"[:50] + " ...", callback_data=f"show_lot_{lot_id}"))

    


    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Последние 10 лотов, в которых вы ставили ставку", reply_markup=markup_history)

#__________________________Открытие лота по нажатию на кнопку лота___________________________# 
@bot.callback_query_handler(func=lambda call: call.data[:8]=="show_lot")
def show_lot(call):
    user_id = call.message.chat.id
    lot_id = call.data[9:]
    max_bet = db.get_max_bet(lot_id)

    _, lot_name, lot_desc, lot_start_price, lot_geolocations, lot_medias, id_seller, _, _, _, _, _ = db.get_lot_info(lot_id)
        
    if lot_start_price > max_bet:
        next_price = lot_start_price
    else:
        next_price = max_bet + price_step

    text =  f'{lot_name}\n{lot_desc}\nПродавец: @{db.get_user_name(id_seller)}\nСледующая ставка: {next_price}\n{lot_geolocations}'
    media_group_documents = []
    media_group = []
    media_list = lot_medias.split()

    markup_lot = InlineKeyboardMarkup()
    btn1 = (InlineKeyboardButton("⏰", callback_data = "time_to_end"))
    btn2 = (InlineKeyboardButton("ℹ", callback_data = "info"))
    markup_lot.row(btn1,btn2) 
    markup_lot.add(InlineKeyboardButton("Сделать ставку", callback_data = f"pay_{lot_id}"))


    for i in range(0, len(media_list), 2):
        file_type = media_list[i]
        file_id = media_list[i+1]
        if file_type == 'd':
            media_group_documents.append(InputMediaDocument(file_id, caption=''))
        elif file_type == 'p':
            media_group.append(InputMediaPhoto(file_id))
        elif file_type == 'v':
            media_group.append(InputMediaVideo(file_id))
    
    if media_group_documents:
        bot.send_media_group(user_id, media=media_group_documents)
    bot.send_media_group(user_id, media=media_group)
    bot.send_message(user_id, text, reply_markup=markup_lot)

#__________________________Проверка истории лотов которые размещал адм-ор и удаление этого лота___________________________# 
@bot.callback_query_handler(func=lambda call: call.data in ["lots_history", "lots_deleting"])
def show_history(call):
    user_id = call.message.chat.id
    
    history = db.get_lots_history(user_id)[:history_limit]

    if call.data == "lots_history":
        markup_history = InlineKeyboardMarkup()
        for lot_id in history:
            _, lot_name, lot_desc, _, _, _, id_seller, _, _, _, _, _ = db.get_lot_info(lot_id)
            seller_name = db.get_user_name(id_seller)
            markup_history.add(InlineKeyboardButton(f"@{seller_name} {lot_name} {lot_desc}"[:50] + " ...", callback_data=f"show_lot_{lot_id}"))

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Последние 10 лотов, которые вы размещали", reply_markup=markup_history)
    
    elif call.data == "lots_deleting":
        markup_history = InlineKeyboardMarkup()
        for lot_id in history:
            _, lot_name, lot_desc, _, _, _, id_seller, _, _, _, _, _ = db.get_lot_info(lot_id)
            seller_name = db.get_user_name(id_seller)
            markup_history.add(InlineKeyboardButton(f"@{seller_name} {lot_name} {lot_desc}"[:50] + " ...", callback_data=f"del_lot_{lot_id}"))
        
        text = "Последние 10 лотов, которые вы размещали. Выберите лот для удаления"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup_history)

#__________________________Удаление этого лота___________________________# 
@bot.callback_query_handler(func=lambda call: call.data[:7]=="del_lot")
def del_lot(call):
    lot_id = int(call.data[8:])

    message_id = db.get_lot_info(lot_id)[10]
    bot.delete_message(main_chat_id, message_id)

    media_messages_ids = db.get_lot_info(lot_id)[11]
    for m_id in list(map(int, media_messages_ids.split())):
        bot.delete_message(main_chat_id, m_id)

#__________________________Открытие сообщения ввода суммы___________________________
@bot.callback_query_handler(func=lambda call: call.data[:3]=="pay")
def create_lot(call):
    lot_id = int(call.data[4:])
    #__________________________Клавиатура для торгов___________________________# 
    markup_keyboard_trade = InlineKeyboardMarkup()
    btn1 = (InlineKeyboardButton("10", callback_data = "add_10"))
    btn2 = (InlineKeyboardButton("50", callback_data = "add_50"))
    btn3 = (InlineKeyboardButton("100", callback_data = "add_100"))
    markup_keyboard_trade.row(btn1,btn2,btn3) 
    btn4 = (InlineKeyboardButton("500", callback_data = "add_500"))
    btn5 = (InlineKeyboardButton("1000", callback_data = "add_1000"))
    btn6 = (InlineKeyboardButton("5000", callback_data = "add_5000"))
    markup_keyboard_trade.row(btn4,btn5,btn6) 
    btn7 = (InlineKeyboardButton("Сбросить ставку", callback_data = "zero"))
    btn8 = (InlineKeyboardButton("Подтвердить ставку", callback_data = f"save_{lot_id}"))
    markup_keyboard_trade.row(btn7,btn8) 
    bot.send_message(call.message.chat.id, f"Введите сумму которую хотите добавить к текущей ставке\nСумма которую хотите добавить: 0", reply_markup=markup_keyboard_trade)

#__________________________Добавление суммы которую хочешь в текстовом окне___________________________# 
@bot.callback_query_handler(func=lambda call: call.data[:3]=="add")
def add_to_sum(call):
    lot_id = int(call.message.reply_markup.keyboard[-1][-1].callback_data.split('_')[-1])
    #__________________________Клавиатура для торгов___________________________# 
    markup_keyboard_trade = InlineKeyboardMarkup()
    btn1 = (InlineKeyboardButton("10", callback_data = "add_10"))
    btn2 = (InlineKeyboardButton("50", callback_data = "add_50"))
    btn3 = (InlineKeyboardButton("100", callback_data = "add_100"))
    markup_keyboard_trade.row(btn1,btn2,btn3) 
    btn4 = (InlineKeyboardButton("500", callback_data = "add_500"))
    btn5 = (InlineKeyboardButton("1000", callback_data = "add_1000"))
    btn6 = (InlineKeyboardButton("5000", callback_data = "add_5000"))
    markup_keyboard_trade.row(btn4,btn5,btn6) 
    btn7 = (InlineKeyboardButton("Сбросить ставку", callback_data = "zero"))
    btn8 = (InlineKeyboardButton("Поддвердить ставку", callback_data = f"save_{lot_id}"))
    markup_keyboard_trade.row(btn7,btn8)

    value_to_add = int(call.data[4:])
    current_sum = int(call.message.text.split()[-1])
    bot.edit_message_text(f"Введите сумму которую хотите добавить к текущей ставке\nСумма которую хотите добавить: {current_sum+value_to_add}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup_keyboard_trade)

#__________________________Сброс суммы которую хочешь добавить до 0___________________________# 
@bot.callback_query_handler(func=lambda call: call.data=="zero")
def clear_sum(call):
    lot_id = int(call.message.reply_markup.keyboard[-1][-1].callback_data.split('_')[-1])
    #__________________________Клавиатура для торгов вторая___________________________# 
    markup_keyboard_trade = InlineKeyboardMarkup()
    btn1 = (InlineKeyboardButton("10", callback_data = "add_10"))
    btn2 = (InlineKeyboardButton("50", callback_data = "add_50"))
    btn3 = (InlineKeyboardButton("100", callback_data = "add_100"))
    markup_keyboard_trade.row(btn1,btn2,btn3) 
    btn4 = (InlineKeyboardButton("500", callback_data = "add_500"))
    btn5 = (InlineKeyboardButton("1000", callback_data = "add_1000"))
    btn6 = (InlineKeyboardButton("5000", callback_data = "add_5000"))
    markup_keyboard_trade.row(btn4,btn5,btn6) 
    btn7 = (InlineKeyboardButton("Сбросить ставку", callback_data = "zero"))
    btn8 = (InlineKeyboardButton("Поддвердить ставку", callback_data = f"save_{lot_id}"))
    markup_keyboard_trade.row(btn7,btn8)

    bot.edit_message_text(f"Введите сумму которую хотите добавить к текущей ставке\nСумма которую хотите добавить: 0", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup_keyboard_trade)

#__________________________Добавление суммы к самоу лоту___________________________# 
@bot.callback_query_handler(func=lambda call: call.data[:4]=="save")
def save_sum(call):
    user_id = int(call.message.chat.id)
    lot_id = int(call.message.reply_markup.keyboard[-1][-1].callback_data.split('_')[-1])
    current_sum = int(call.message.text.split()[-1])

    max_bet = db.get_max_bet(lot_id)
    _, lot_name, lot_desc, lot_start_price, lot_geolocations, lot_medias, id_seller, _, _, _, message_id, _ = db.get_lot_info(lot_id)

    if lot_start_price > max_bet:
        next_price = lot_start_price
    else:
        next_price = max_bet + price_step
    
    if current_sum < next_price:
        bot.edit_message_text(f"Ваша ставка должна быть больше", chat_id=call.message.chat.id, message_id=call.message.message_id)
    else:
        bot.edit_message_text(f"Ваша ставка сделана на сумму: {current_sum}", chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup_main_menu)
        db.add_bet(user_id, lot_id, current_sum)

        text =  f'{lot_name}\n{lot_desc}\nПродавец: @{db.get_user_name(id_seller)}\nСледующая ставка: {current_sum+price_step}\n{lot_geolocations}'

        markup_lot_informations = InlineKeyboardMarkup()
        btn1 = (InlineKeyboardButton("⏰", callback_data = "time_to_end"))
        btn2 = (InlineKeyboardButton("ℹ", callback_data = "info"))
        markup_lot_informations.row(btn1,btn2) 
        markup_lot_informations.add(InlineKeyboardButton("Открыть лот", url=f"http://t.me/qqwwwerrrtyyyy_bot?start={lot_id}")) 

        bot.edit_message_text(text, main_chat_id, message_id, reply_markup=markup_lot_informations)

#__________________________Супер_админ чек баланса___________________________#
@bot.callback_query_handler(func=lambda call: call.data=="check")
def create_check_balance(call):    
    msg = bot.send_message(call.message.chat.id, "Введите ник пользователя для проверки баланса")
    return bot.register_next_step_handler(msg, check)

def check(message):
    name_user = message.text
    balance = db.check_balance(name_user)
    bot.send_message(message.chat.id, f"У пользователя @{name_user}, баланс: {balance}")

#__________________________чек баланса аккаунта___________________________#
@bot.callback_query_handler(func=lambda call: call.data=="balance")
def chek_user_balance(call):
    print(call.message.chat.username)
    name_user = call.message.chat.username
    balance = db.check_balance(name_user)
    bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = f"Ваш Баланс: {balance}", reply_markup=markup_main_menu)

#__________________________Выдача полномочий ад-ора__________________________#
@bot.callback_query_handler(func=lambda call: call.data=="invate")
def create_new_status(call):
    msg = bot.send_message(call.message.chat.id, "Введите ник пользователя кому ходите выдать полномочия") 
    return bot.register_next_step_handler(msg, get_nick_user)

def get_nick_user(message):
    nickname_user = message.text                                                                                     
    msg = bot.send_message(message.chat.id, "Введите статус который хотите выдать (admin, blocked, user, support)")
    return bot.register_next_step_handler(msg, get_new_status, nickname_user)

def get_new_status(message, nickname_user):
    new_status = message.text
    bot.send_message(message.chat.id, f"Пользователю @{nickname_user} выдан статус: {new_status}")
    db.change_user_type(nickname_user, new_status)

#__________________________Создание жалобы администратором__________________________# 
@bot.callback_query_handler(func=lambda call: call.data=="report")
def create_report(call):
    user_id = call.message.chat.id
    msg = bot.send_message(call.message.chat.id, "Введите ник пользователя")
    return bot.register_next_step_handler(msg, get_nickname_user, user_id)

def get_nickname_user(message, user_id):
    name_suspect = message.text
    msg = bot.send_message(message.chat.id, "Введите описание жалобы")
    return bot.register_next_step_handler(msg, get_comment_report, user_id, name_suspect)

def get_comment_report(message, user_id, name_suspect):
    comment_report = message.text
    bot.send_message(message.chat.id, "Ваша жалоба отправлена поддержке")

    user_name = db.get_user_name(user_id)
    user_id_suspect = db.get_user_info(name_suspect)[0]
    reports_count = db.get_approved_reports_count(user_id_suspect)
    report_id = db.get_new_report_id()

    markup_support = InlineKeyboardMarkup()
    markup_support.add(InlineKeyboardButton("Подтвердить", callback_data=f"report_accept_{report_id}"))
    markup_support.add(InlineKeyboardButton("Отклонить", callback_data=f"report_delete_{report_id}"))

    text =  f"""Проверьте жалобу: От пользователя @{user_name} на пользователя @{name_suspect}\nЖалоба: {comment_report}\nДанный пользователь имеет {reports_count} жалоб"""
    message_id = bot.send_message(support_chat_id, text, reply_markup=markup_support).message_id

    db.create_report(user_id, user_id_suspect, comment_report, message_id)

#__________________________Подтверждение или отмена жалобы и добавления пользоваетял в Ч.С.__________________________# 
@bot.callback_query_handler(func=lambda call: call.data[:13] in ["report_accept", "report_delete"])
def process_report(call):
    report_id = int(call.data.split('_')[-1])
    _, _, user_id_suspect, _, _, message_id = db.get_report_info(report_id)

    if call.data[:13] == "report_accept":
        db.approve_report(report_id)
        user_name_suspect = db.get_user_name(user_id_suspect)
        reports_count = db.get_approved_reports_count(user_id_suspect)
        if reports_count >= 3:
            db.change_user_type(user_name_suspect, "blocked")
    bot.delete_message(support_chat_id, message_id)


#__________________________Создание лота администратором___________________________# 
@bot.callback_query_handler(func=lambda call: call.data=="create")
def create_lot(call):
    user_id = call.message.chat.id
    msg = bot.send_message(call.message.chat.id, "Введите название лота")
    return bot.register_next_step_handler(msg, get_lot_name, user_id)

def get_lot_name(message, user_id):
    lot_name = message.text
    if not lot_name:
        msg = bot.send_message(message.chat.id, "Необходимо ввести название лота")
        return bot.register_next_step_handler(msg, get_lot_name, user_id)

    msg = bot.send_message(message.chat.id, "Введите описание лота")
    return bot.register_next_step_handler(msg, get_lot_desc, user_id, lot_name)

def get_lot_desc(message, user_id, lot_name):
    lot_desc = message.text
    if not lot_desc:
        msg = bot.send_message(message.chat.id, "Введино некорректное описание лота")
        return bot.register_next_step_handler(msg, get_lot_desc, user_id, lot_name)
    
    msg = bot.send_message(message.chat.id, "Введите начальную стоимость лота")
    return bot.register_next_step_handler(msg, get_lot_starp_price, user_id, lot_name, lot_desc) 

def get_lot_starp_price(message, user_id, lot_name, lot_desc):
    lot_starp_price = message.text
    if not lot_starp_price.isnumeric():
        msg = bot.send_message(message.chat.id, "Введина некорректная стоимость лота")
        return bot.register_next_step_handler(msg, get_lot_starp_price, user_id, lot_name, lot_desc) 
    
    msg = bot.send_message(message.chat.id, "Введите адресс нахождения лота")
    return bot.register_next_step_handler(msg, get_lot_geolocations, user_id, lot_name, lot_desc, lot_starp_price) 

def get_lot_geolocations(message, user_id, lot_name, lot_desc, lot_starp_price):
    lot_geolocations = message.text
    if not lot_geolocations:
        msg = bot.send_message(message.chat.id, "Введина некоректный адресс лота")
        return bot.register_next_step_handler(msg, get_lot_geolocations, user_id, lot_name, lot_desc, lot_starp_price) 
    
    msg = bot.send_message(message.chat.id, "Перетащите в чат фото/видео для лота")
    return bot.register_next_step_handler(msg, get_lot_medias, user_id, lot_name, lot_desc, lot_starp_price, lot_geolocations) 

def get_lot_medias(message, user_id, lot_name, lot_desc, lot_starp_price, lot_geolocations):
    lot_medias = ' '

    if message.document:
        lot_medias += f'd {message.document.file_id} '
    elif message.photo:
        lot_medias += f'p {message.photo[-1].file_id} '
    elif message.video:
        lot_medias += f'v {message.video.file_id} '
    
    if ' v ' in lot_medias or ' p ' in lot_medias:
        msg = bot.send_message(message.chat.id, "Перетащите в чат еще фото/видео для лота или напишите 'стоп', чтобы закончить создание лота")
    else:
        msg = bot.send_message(message.chat.id, "Необходимо добавить хотябы одно фото или видео")
    return bot.register_next_step_handler(msg, get_lot_medias_next, user_id, lot_name, lot_desc, lot_starp_price, lot_geolocations, lot_medias) 

def get_lot_medias_next(message, user_id, lot_name, lot_desc, lot_starp_price, lot_geolocations, lot_medias):
    if message.text == 'стоп':
        user_name = db.get_user_name(user_id)

        text =  f'{lot_name}\n{lot_desc}\nПродавец: @{user_name}\nСледующая ставка: {lot_starp_price}\n{lot_geolocations}'
        media_group_documents = []
        media_group = []
        media_list = lot_medias.split()
        for i in range(0, len(media_list), 2):
            file_type = media_list[i]
            file_id = media_list[i+1]
            if file_type == 'd':
                media_group_documents.append(InputMediaDocument(file_id, caption=''))
            elif file_type == 'p':
                media_group.append(InputMediaPhoto(file_id, caption=text if not media_group else ''))
            elif file_type == 'v':
                media_group.append(InputMediaVideo(file_id, caption=text if not media_group else ''))
        
        if not media_group:
            msg = bot.send_message(message.chat.id, "Необходимо отправить хотябы одно фото или видео")
            return bot.register_next_step_handler(msg, get_lot_medias_next, user_id, lot_name, lot_desc, lot_starp_price, lot_geolocations, lot_medias) 

        
        lot_id = db.create_lot(lot_name, lot_desc, lot_starp_price, lot_geolocations, lot_medias, user_id)

        #__________________________Кнопки поддержки___________________________# 
        markup_support = InlineKeyboardMarkup()
        markup_support.add(InlineKeyboardButton("Подтвердить", callback_data=f"accept_{lot_id}"))
        markup_support.add(InlineKeyboardButton("Отклонить", callback_data=f"delete_{lot_id}"))
        
        messages_ids = [support_chat_id]
        if media_group_documents:
            messages_ids.append(bot.send_media_group(support_chat_id, media=media_group_documents)[0].message_id)
        messages_ids.append(bot.send_media_group(support_chat_id, media=media_group)[0].message_id)
        messages_ids.append(bot.send_message(support_chat_id, "Проверьте данный лот на наличие дефектов", reply_markup=markup_support).message_id)

        db.fill_lot_messages_ids(lot_id, messages_ids)

    else:
        if message.document:
            lot_medias += f'd {message.document.file_id} '
        elif message.photo:
            lot_medias += f'p {message.photo[-1].file_id} '
        elif message.video:
            lot_medias += f'v {message.video.file_id} '

        if ' v ' in lot_medias or ' p ' in lot_medias:
            msg = bot.send_message(message.chat.id, "Перетащите в чат еще фото/видео для лота или напишите 'стоп', чтобы закончить создание лота")
        else:
            msg = bot.send_message(message.chat.id, "Необходимо добавить хотябы одно фото или видео")
        return bot.register_next_step_handler(msg, get_lot_medias_next, user_id, lot_name, lot_desc, lot_starp_price, lot_geolocations, lot_medias) 

#__________________________Создание лота администратором___________________________# 
@bot.callback_query_handler(func=lambda call: call.data[:6] in ["accept", "delete"])
def process_lot(call):
    lot_id = int(call.data[7:])

    messages_ids = db.get_messages_ids(lot_id)
    chat_id, messages_ids = messages_ids[0], messages_ids[1:]
    max_bet = db.get_max_bet(lot_id)

    if call.data[:6] == "accept":
        db.set_lot_is_approved(lot_id, True)
        
        _, lot_name, lot_desc, lot_start_price, lot_geolocations, lot_medias, id_seller, _, _, _, _, _ = db.get_lot_info(lot_id)
        
        if lot_start_price > max_bet:
            next_price = lot_start_price
        else:
            next_price = max_bet + price_step

        text =  f'{lot_name}\n{lot_desc}\nПродавец: @{db.get_user_name(id_seller)}\nСледующая ставка: {next_price}\n{lot_geolocations}'
        media_group_documents = []
        media_group = []
        media_list = lot_medias.split()
        for i in range(0, len(media_list), 2):
            file_type = media_list[i]
            file_id = media_list[i+1]
            if file_type == 'd':
                media_group_documents.append(InputMediaDocument(file_id, caption=''))
            elif file_type == 'p':
                media_group.append(InputMediaPhoto(file_id))
            elif file_type == 'v':
                media_group.append(InputMediaVideo(file_id))

        markup_lot_informations = InlineKeyboardMarkup()
        btn1 = (InlineKeyboardButton("⏰", callback_data = "time_to_end"))
        btn2 = (InlineKeyboardButton("ℹ", callback_data = "info"))
        markup_lot_informations.row(btn1,btn2)
        markup_lot_informations.add(InlineKeyboardButton("Открыть лот", url=f"http://t.me/qqwwwerrrtyyyy_bot?start={lot_id}")) 
        
        main_group_media_messages_ids = []
        if media_group_documents:
            main_group_media_messages_ids.append(bot.send_media_group(main_chat_id, media=media_group_documents)[0].message_id)
        main_group_media_messages_ids.append(bot.send_media_group(main_chat_id, media=media_group)[0].message_id)
        main_chat_message_id = bot.send_message(main_chat_id, text, reply_markup=markup_lot_informations).message_id

        db.fill_lot_main_group_message_id(lot_id, main_chat_message_id)
        db.fill_lot_main_group_media_messages_ids(lot_id, " ".join(list(map(str, main_group_media_messages_ids))))

    else:
        db.set_lot_is_approved(lot_id, False)
    
    for message_id in messages_ids:
        bot.delete_message(chat_id, message_id)

#__________________________Время до 23___________________________# 
@bot.callback_query_handler(func=lambda call: call.data=="time_to_end") 
def check_time_last_lot(call):
    datetime_now = datetime.now()
    if datetime_now.hour == 23:
        datetime_finish = datetime_now + timedelta(days=1)
    else:
        datetime_finish = datetime_now
    datetime_finish = datetime(datetime_finish.year, datetime_finish.month, datetime_finish.day, 23, 0, 0, 0)

    diff = (datetime_finish - datetime_now).seconds
    diff_hours = diff // 3600
    diff -= diff_hours * 3600
    diff_minutes = diff // 60
    diff -= diff_minutes * 60
    diff_seconds = diff

    bot.answer_callback_query(call.id, f"Осталось {diff_hours} Часа {diff_minutes} Минут {diff_seconds} Секунд") 

#__________________________Всплывающее окно инфо___________________________# 
@bot.callback_query_handler(func=lambda call: call.data=="info") 
def check_button_info(call):
    bot.answer_callback_query(call.id, """После окончания торгов, победитель должен выйти на связь с продавцом самостоятельно в течении суток. Победитель обязан выкупить лот в ТЕЧЕНИИ ТРЁХ СУТОК""")       

#__________________________Внутри пользователя___________________________#   
@bot.callback_query_handler(func=lambda call: True)
def lk_keyboard(call):
    if call.data == "rules":
        bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = '''После окончания торгов,победитель должен выйти на связь с продавцом самостоятельно в течении суток‼️
Победитель обязан выкупить лот в течении ТРЁХ дней,после окончания аукциона🔥
                         
НЕ ВЫКУП ЛОТА - ПЕРМАНЕНТНЫЙ БАН ВО ВСЕХ НУМИЗМАТИЧЕСКИХ СООБЩЕСТВАХ И АУКЦИОНАХ🤬
                         
Что бы узнать время окончания аукциона,нажмите на ⏰
Антиснайпер - Ставка сделанная за 10 минут до конца,автоматически переносит
Аукцион на 10 минут вперёд ‼️
Работают только проверенные продавцы,их Отзывы сумарно достигают 10000+ на различных площадках.
Дополнительные Фото можно запросить у продавца.
                         
Случайно сделал ставку?🤔
Напиши продавцу‼️
                         
Отправка почтой,стоимость пересылки указана под фото.
Лоты можно копить, экономя при этом на почте.
Отправка в течении трёх дней после оплаты‼️''', reply_markup = markup_main_menu)
        
    elif call.data == "back":
        user_id = call.message.chat.id
        user_type = db.get_user_type(user_id)

        if user_type == 'user':
            markup = markup_keyboard
        elif user_type == 'admin':
            markup = markup_administrator

        bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "Привет, я бот аукционов @poloies Я помогу вам следить за выбранными лотами ,и регулировать ход аукциона. Удачных торгов 🤝", reply_markup=markup)
  
    elif call.data == "help":
        bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "Свяжитесь с нами, если у вас возникли вопросы @poloies облемах или нахождении ошибок пишите @dinhaki", reply_markup=markup_main_menu)
      

print("Ready")
bot.infinity_polling()
