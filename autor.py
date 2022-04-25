import logging
from help_defs import is_float, search_adress

import requests
import telegram

from data import db_session
from data.user import User
from data.spots import Spot
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, Bot
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler, CallbackContext,
)

import asyncio
import datetime




reply_keyboard = [['/start', '/help']]
db_session.global_init("data/tg_bot.db")
db_sess = db_session.create_session()
TOKEN = '5158943754:AAHR2r7utRWAJORTSKqmI-p6sUq06cNoVQw'
URL = 'https://api.telegram.org/bot/'
bot = Bot(TOKEN)

START_KEYBOARD = ['/start']
STANDART_KEYBOARD_1 = ['/find_loc', '/add_spot', '/my_cords', '/timer', '/help']
KB_TIMER = [["/set_timer 30", "/set_timer 60", "/set_timer 300"],
                  ["/back"]]

CLOSE_TIMER = [["/close"]]

REG_COUNTER = 0


def cups(name, one_time=False):
    list_with_cups = []
    for i in name:
        list_with_cups.append([i])

    markup = ReplyKeyboardMarkup(list_with_cups, one_time_keyboard=one_time)
    return markup


def help(update, context):
    '''Обработка /help'''
    if REG_COUNTER == 0:
        markup = cups(START_KEYBOARD)
    else:
        markup = cups(STANDART_KEYBOARD_1)
    update.message.reply_text(
        "Воспользуйся кнопками. Если ещё не авторизовался то прожми /start", reply_markup=markup)


############################################# Autorize ############################################################
def start_aut(update, context):
    if REG_COUNTER == 1:
        update.message.reply_text('Зачем тебе сюда? Ты же уже авторизован')
        return ConversationHandler.END
    rep_keyboard = cups(['/stop'], one_time=True)
    update.message.reply_text(
        "Привет! Я бот, который расскажет тебе о спотах поблизости. Давай зарегистрируемся введи мне своё имя", reply_markup=rep_keyboard)
    return 1


def f_res(update, context):
    name = update.message.text
    context.user_data['name'] = name
    if name.lower == 'admin':
        pass

    else:
        try:
            user = db_sess.query(User).filter(User.id == update.message.from_user['id']).one()
            print('adasd')
            markup = cups(['Да', "Нет"], one_time=True)
            update.message.reply_text(
                f'Пользователь с вашим токеном уже зарегистрирован под именем: {user.name}\n Хотите изменить имя?',
                reply_markup=markup)
            return 2

        except:
            user_id = db_sess.query(User).filter(User.id == update.message.from_user['id'])
            print(user_id)
            if user_id:
                context.user_data['user_id'] = update.message.from_user['id']
                update.message.reply_text(
                    "Осталось немного, напиши нам свой возраст, можно и без него,"
                    " но тогда некоторые функции не будут доступны тебе",
                )
                return 3

            else:
                update.message.reply_text('Вы уже существуете в бд')
        yes_rename(update, context)
        return ConversationHandler.END


# Rename user in DB
def rename(update, context):
    global REG_COUNTER
    if update.message.text.lower() == 'нет':
        user = db_sess.query(User).filter(User.id == update.message.from_user['id']).one()
        context.user_data['name'] = user.name
        REG_COUNTER = 1
        markup = cups(STANDART_KEYBOARD_1)
        update.message.reply_text('Ой! А я вас помню!', reply_markup=markup)
        return ConversationHandler.END
    print('kjy')
    yes_rename(update, context)


def yes_rename(update, context):
    global REG_COUNTER
    REG_COUNTER = 1
    markup = cups(STANDART_KEYBOARD_1)
    update.message.reply_text(
        f"{context.user_data['name'].capitalize()}, добро пожаловать!", reply_markup=markup)
    try:
        db_sess.query(User).filter(User.id == update.message.from_user['id']).update(
            {User.name: context.user_data['name']}, synchronize_session=False
        )
        db_sess.commit()
        print(REG_COUNTER)

    except:
        db_sess.rollback()
        print('error')

    return ConversationHandler.END


# Add age in DB
def add_db_age(update, context):
    global REG_COUNTER
    age = update.message.text
    context.user_data['age'] = age
    if age.isdigit():
        if int(age) < 13:
            markup = cups(START_KEYBOARD)
            ost = 13 - int(age)
            if ost > 4:
                update.message.reply_text(f'Извиняй друг, но ты ещё маловат. Приходи через {ost} лет', reply_markup=markup)
                return ConversationHandler.END

            elif 1 < ost <= 4:
                update.message.reply_text(f'Извиняй друг, но ты ещё маловат. Приходи через {ost} года', reply_markup=markup)
                return ConversationHandler.END

            else:
                update.message.reply_text(f'Извиняй друг, но ты ещё маловат. Приходи через {ost} год',  reply_markup=markup)
                return ConversationHandler.END

        else:
            user = User()
            user.id = context.user_data['user_id']
            user.name = context.user_data['name']
            user.age = age
            db_sess.add(user)
            db_sess.commit()
            db_sess.rollback()
            REG_COUNTER = 1
            markup = cups(STANDART_KEYBOARD_1)
            update.message.reply_text('Мы добавили тебя в нашу Базу :)', markup=markup)
            return ConversationHandler.END

    else:
        update.message.reply_text('Упс... Что-то пошло не так! Попробуй снова')


#Stop dialog
def stop(update, context):
    if REG_COUNTER == 1:
        murkup = cups(STANDART_KEYBOARD_1)
    else:
        murkup = cups(START_KEYBOARD)
    print('stop')
    update.message.reply_text('Остановка системы входа!', reply_markup=murkup)
    return ConversationHandler.END


############################################# Add location ############################################################
def start_locating(update, context):
    if REG_COUNTER == 0:
        markup = cups(START_KEYBOARD)
        update.message.reply_text('ТЫ КАК ВООБЩЕ СЮДА ПОПАЛ?! Сходи и зарегистрируйся'
                                  ' сначала, для этого нажми на кнопку /start', reply_markup=markup)
        return ConversationHandler.END
    markup = cups(['/stop_loc'], one_time=True)
    print('hui1')
    update.message.reply_text(
        "Отлично, давай определим твоё мостоположение. Напиши мне свой адресс"
        " (можешь найти в яндекс картах, например)", reply_markup=markup)
    return 1


def add_adress(update, context):
    adress = update.message.text
    print(adress)
    try:
        search = search_adress(adress)
        lat = search[0]
        lon = search[1]
        db_sess.query(User).filter(User.id == update.message.from_user['id']).update(
            {User.lat: float(lat),
             User.lon: float(lon)
             }
        )
        db_sess.commit()
        markup = cups(STANDART_KEYBOARD_1)
        db_sess.rollback()
        update.message.reply_text('Мы обновили твои координаты', reply_markup=markup)
        return ConversationHandler.END

    except FileNotFoundError:
        update.message.reply_text('Похоже, что ты ввёл не коректный адресс')


def stop_loc(update, context):
    murkup = cups(STANDART_KEYBOARD_1)
    update.message.reply_text('Остановка всех систем по приказу главнокомандуещего!', reply_markup=murkup)
    return ConversationHandler.END


############################################# Add new spot ############################################################


def start_add_spot(update, context):
    print('her1')
    if REG_COUNTER == 0:
        markup = cups(START_KEYBOARD)
        update.message.reply_text('ТЫ КАК ВООБЩЕ СЮДА ПОПАЛ?! Сходи и зарегистрируйся'
                                  ' сначала, для этого нажми на кнопку /start', reply_markup=markup)
        return ConversationHandler.END

    print('her2')
    db_sess = db_session.create_session()
    data_user = db_sess.query(User).filter(User.id == update.message.from_user['id'])
    if data_user:
        markup = cups(['/stop_spot'], one_time=True)
        update.message.reply_text('Давай же добавим новый спот. Введи его название', reply_markup=markup)
        return 1

    else:
        update.message.reply_text("Похоже, что ты ещё не зарегистрирован у нас.")
        return ConversationHandler.END


def spot_name(update, context):
    spot_mess = update.message.text
    db = db_sess.query(Spot).filter(Spot.name == spot_mess)
    if db_sess.query(db.exists()).scalar():
        update.message.reply_text('Похоже, что такой спот уже существует!')

    else:
        context.user_data['spot_name'] = spot_mess
        update.message.reply_text('Теперь его его адрес,'
                                  ' взять его можно всё в тех же яндекс картах')
        return 2


def spot_cords(update, context):
    adress = update.message.text
    print(adress)
    try:
        search = search_adress(adress)
        lat = search[0]
        lon = search[1]

        db = db_sess.query(Spot).filter((Spot.lat == float(lat)) and (Spot.lon == lon))
        if db_sess.query(db.exists()).scalar():
            update.message.reply_text('Похоже, что такой спот уже существует! Попробуй по новой')
            return ConversationHandler.END

        else:
            update.message.reply_text('Великолепно, а теперь отправь его фото, для наглядности')
            context.user_data['spot_lat'] = lat
            context.user_data['spot_lon'] = lon
            return 3

    except FileNotFoundError:
        update.message.reply_text('Похоже, что ты ввёл не коректный адресс')


def spot_photo(update, context):
    photo_mess = update.message.photo[-1]
    # bot.send_photo(chat_id=update.message.chat_id, photo=)
    spot = Spot()
    spot.photo = photo_mess['file_id']
    spot.name = context.user_data['spot_name']
    spot.lat = context.user_data['spot_lat']
    spot.lon = context.user_data['spot_lon']
    spot.user_id = update.message.from_user['id']
    db_sess.add(spot)
    db_sess.commit()
    markup = cups(STANDART_KEYBOARD_1)
    print('отработал')
    update.message.reply_text('Мы добавили новый спот в свою коллекцию!', reply_markup=markup)
    return ConversationHandler.END


def spot_stopping(update, context):
    print('saddsf')
    murkup = cups(STANDART_KEYBOARD_1)
    update.message.reply_text('Раз на то ваша воля...', markup=murkup)
    return ConversationHandler.END


######################### Get user cords #####################
def user_cords(update, context):
    print(REG_COUNTER)
    if REG_COUNTER == 0:
        markup = cups(START_KEYBOARD)
        update.message.reply_text('ТЫ КАК ВООБЩЕ СЮДА ПОПАЛ?! Сходи и зарегистрируйся'
                                  ' сначала, для этого нажми на кнопку /start', reply_markup=markup)
        return ConversationHandler.END
    us_id = update.message.from_user['id']
    db_sess = db_session.create_session()
    loc = db_sess.query(User.lat, User.lon).filter(User.id == update.message.from_user['id']).all()
    print(loc)

    if loc[0][0] != None and loc[0][1] != None:
        cords = requests.get(f'http://127.0.0.1:5000/users/select/{us_id}/cords').json()
        # print(cords)
        lat = cords['user'][0]['lat']
        lon = cords['user'][0]['lon']
        update.message.reply_text(f'Вот ваши координаты: {lat, lon}')

    else:
        update.message.reply_text('Мне кажется, что ты не добавил свои координаты')
        return ConversationHandler.END


###################### Get nearest spots #####################
def nearest_spots(update, context):
    spots = requests.get('Здесь будет сделан запрос в базу данных через rest-api').json()
    l_spots = []
    for i in spots:
        l_spots.append(i['name'])

    for i in l_spots:
        bot.send_photo(chat_id=update.message.chat_id, photo=l_spots[0], caption=spots[1])


########################## Add timer #########################
def set_timer(update, context):
    chat_id = update.message.chat_id
    try:
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text('Извините, не умеем возвращаться в прошлое')
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(task, due, context=chat_id, name=str(chat_id))

        text = f"Засек {due} секунд!"
        context.bot_data.update({"timer": due})
        if job_removed:
            text += ' Старая задача удалена.'

        close_timer_markup = cups(CLOSE_TIMER)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=str(text),
                                 reply_markup=close_timer_markup)

    except (IndexError, ValueError):
        update.message.reply_text('Использование: /set_timer <секунд>')

    except telegram.error.BadRequest:
        pass


def remove_job_if_exists(name, context):
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def unset(update, context):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = 'Таймер отменен!' if job_removed else 'У вас нет активных таймеров'
    timer_markup = cups(STANDART_KEYBOARD_1)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text,
                             reply_markup=timer_markup)


def timer(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Здесь ты можешь завести таймер")


def task(context):
    timer_markup = cups(KB_TIMER)
    job = context.job
    time_duration = context.bot_data["timer"]
    text = f"{time_duration} сек истекло"
    context.bot.send_message(job.context, text=text)


def back(update: Update, context: CallbackContext):
    start_markup = cups(STANDART_KEYBOARD_1)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Выберите функцию",
                             reply_markup=start_markup)


###################### main func ##################
def main():
    updater = Updater('5158943754:AAHR2r7utRWAJORTSKqmI-p6sUq06cNoVQw', use_context=True)
    dp = updater.dispatcher

    start_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_aut, pass_chat_data=True)],
        states={1: [MessageHandler(~ Filters.command, f_res)],
                2: [MessageHandler(~ Filters.command, rename)],
                3: [MessageHandler(~ Filters.command, add_db_age)]},
        fallbacks=[CommandHandler('stop', stop)]
    )

    location = ConversationHandler(
        entry_points=[CommandHandler('find_loc', start_locating, pass_chat_data=True)],
        states={1: [MessageHandler(~ Filters.command, add_adress)]},
        fallbacks=[CommandHandler('stop_loc', stop_loc)]
    )
    get_cords = CommandHandler('my_cords', user_cords)
    get_list_spots = CommandHandler('nearest_spots', nearest_spots)

    new_spot = ConversationHandler(
        entry_points=[CommandHandler('add_spot', start_add_spot, pass_chat_data=True)],
        states={1: [MessageHandler(~ Filters.command, spot_name)],
                2: [MessageHandler(~ Filters.command, spot_cords)],
                3: [MessageHandler(~ Filters.command, spot_photo)]},
        fallbacks=[CommandHandler('stop_spot', spot_stopping)]
    )

    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(start_handler)
    dp.add_handler(location)
    dp.add_handler(new_spot)
    dp.add_handler(get_list_spots)
    dp.add_handler(get_cords)

    dp.add_handler(CommandHandler("timer", timer))
    dp.add_handler(CommandHandler("set_timer", set_timer))
    dp.add_handler(CommandHandler("close", unset))
    dp.add_handler(CommandHandler("back", back))

    updater.start_polling()


if __name__ == '__main__':
    main()
