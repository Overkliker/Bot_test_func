import logging

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
    ConversationHandler,
)



reply_keyboard = [['/start', '/help']]
db_session.global_init("data/tg_bot.db")
db_sess = db_session.create_session()
TOKEN = '5158943754:AAHR2r7utRWAJORTSKqmI-p6sUq06cNoVQw'
URL = 'https://api.telegram.org/bot/'
bot = Bot(TOKEN)

def user_keyboard(context):
    '''Кнопки по-умолчанию для админа и пользователя. ВОзвращает ReplyKeyboardMarkup'''
    try:
        markup = ReplyKeyboardMarkup(context.user_data['reply_keyboard'], one_time_keyboard=False)
    except:
        context.user_data['reply_keyboard'] = [['/start', '/stop'], ['Мероприятия']]
        markup = ReplyKeyboardMarkup(context.user_data['reply_keyboard'], one_time_keyboard=False)
    return markup


def help(update, context):
    '''Обработка /help'''
    update.message.reply_text(
        "Воспользуйся кнопками. Если что-то пошло не так, начни сначала /start")

############################################# Autorize ############################################################
def start_aut(update, context):
    db_sess = db_session.create_session()
    update.message.reply_text(
        "Привет! Я бот, который расскажет тебе о спотах поблизости. Давай зарегистрируемся:")
    return 1


def f_res(update, context):
    global user
    name = update.message.text
    context.user_data['name'] = name
    if name.lower == 'admin':
        update.message.reply_text('Чтобы отправить сообщение всем участникам чата, наберите /start ваше сообщение')
        context.user_data['reply_keyboard'] = [['Разместить информацию', 'Мероприятия'],
                                               ['/events прошедшие', '/events будущие']]

    else:
        context.user_data['reply_keyboard'] = [['/Регистрация', '/Споты'], ['/Мои споты']]
        try:
            user = db_sess.query(User).filter(User.id == update.message.from_user['id']).one()
            markup = ReplyKeyboardMarkup([['Да', 'Нет']], one_time_keyboard=True)
            update.message.reply_text(
                f'Пользователь с вашим токеном уже зарегистрирован под именем: {user.name}\n Хотите изменить имя?')
            return 2

        except:
            user_id = db_sess.query(User).filter(User.id == update.message.from_user['id']).one()
            if user_id:
                user = User()
                user.name = name
                user.id = update.message.from_user['id']
                db_sess.add(user)
                db_sess.commit()
                db_sess.rollback()

            else:
                update.message.reply_text('Вы уже существуете в бд')

        return ConversationHandler.END


def stop(update, context):
    murkup = user_keyboard(context)
    update.message.reply_text('reg stop', reply_markup=murkup)
    return ConversationHandler.END

############################################# Add location ############################################################

def start_locating(update, context):
    db_sess = db_session.create_session()
    update.message.reply_text(
        "Давай ты напишешь нам своё местопнахождения, что бы мы могли найти ближайшие споты для тебя:")
    return 1


def add_loc(update, context):
    loc = update.message.text
    print('sdffasafd')
    context.user_data['location'] = loc
    db_sess.query(User).filter_by(id=update.message.from_user['id']).update(
        {'location': loc}
    )
    db_sess.commit()
    db_sess.rollback()
    return ConversationHandler.END

def stop_loc(update, context):
    murkup = user_keyboard(context)
    update.message.reply_text('Loc stop', reply_markup=murkup)
    return ConversationHandler.END


############################################# Add age ############################################################


def start_age(update, context):
    db_sess = db_session.create_session()
    murkup = [['/stop_age']]
    update.message.reply_text(
        "Осталось немного, напиши нам свой возраст, можно и без него, но тогда некоторые функции не будут доступны тебе:",
)
    return 1


def add_age(update, context):
    age = update.message.text
    context.user_data['age'] = age
    if age.isdigit():
        if int(age) < 13:
            ost = 13 - int(age)
            if ost > 4:
                update.message.reply_text(f'Извиняй друг, но ты ещё маловат. Приходи через {ost} лет')
                return ConversationHandler.END

            elif 1 < ost <= 4:
                update.message.reply_text(f'Извиняй друг, но ты ещё маловат. Приходи через {ost} года')
                return ConversationHandler.END

            else:
                update.message.reply_text(f'Извиняй друг, но ты ещё маловат. Приходи через {ost} год')
                return ConversationHandler.END

        else:
            db_sess.query(User).filter_by(id=update.message.from_user['id']).update(
                {'age': age}
            )
            db_sess.commit()
            db_sess.rollback()
            return ConversationHandler.END

    else:
        update.message.reply_text('Упс... Что-то пошло не так! Попробуй снова')


def stop_age(update, context):
    murkup = user_keyboard(context)
    update.message.reply_text('Ну как хочешь! Значит будешь демо ботом пользоваться', reply_markup=murkup)
    return ConversationHandler.END




############################################# Add new spot ############################################################

def send_photo_file_id(chat_id, file_id):
    requests.get(f'{URL}{TOKEN}/sendPhoto?chat_id={chat_id}&photo={file_id}')


def start_add_spot(update, context):
    db_sess = db_session.create_session()
    murkup = [['/stop_spot']]
    update.message.reply_text('Давай же добавим новый спот. Введи его название:')
    return 1


def spot_name(update, context):
    spot_mess = update.message.text
    db = db_sess.query(Spot).filter(Spot.name == spot_mess)
    if db_sess.query(db.exists()).scalar():
        update.message.reply_text('Похоже, что такой спот уже существует!')

    else:
        context.user_data['spot_name'] = spot_mess
        update.message.reply_text('Теперь его координаты в формате: 39.2423, 71.23212')
        return 2


def spot_cords(update, context):
    cords = update.message.text
    db = db_sess.query(Spot).filter(Spot.coords == cords)
    if db_sess.query(db.exists()).scalar():
        update.message.reply_text('Похоже, что такой спот уже существует!')

    else:
        context.user_data['spot_cords'] = cords
        update.message.reply_text('Теперь надо бы прикрепить фото нового спота, пришли мне её')
        return 3

def spot_photo(update, context):
    photo_mess = update.message.photo[-1]
    # bot.send_photo(chat_id=update.message.chat_id, photo=)
    spot = Spot()
    spot.photo = photo_mess['file_id']
    spot.name = context.user_data['spot_name']
    spot.coords = context.user_data['spot_cords']
    spot.user_id = update.message.from_user['id']
    db_sess.add(spot)
    db_sess.commit()
    db_sess.rollback()
    print('отработал')
    return ConversationHandler.END


def spot_stopping(update, context):
    murkup = user_keyboard(context)
    update.message.reply_text('Раз на то ваша воля...', reply_markup=murkup)
    return ConversationHandler.END



def main():
    updater = Updater('5158943754:AAHR2r7utRWAJORTSKqmI-p6sUq06cNoVQw', use_context=True)
    dp = updater.dispatcher

    start_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_aut, pass_chat_data=True)],
        states={1: [MessageHandler(Filters.text, f_res)]},
        fallbacks=[CommandHandler('stop', stop)]
    )

    location = ConversationHandler(
        entry_points=[CommandHandler('find_loc', start_locating, pass_chat_data=True)],
        states={1: [MessageHandler(Filters.text, add_loc)]},
        fallbacks=[CommandHandler('stop_loc', stop_loc)]
    )
    add_age_scen = ConversationHandler(
        entry_points=[CommandHandler('add_age', start_age, pass_chat_data=True)],
        states={1: [MessageHandler(Filters.text, add_age)]},
        fallbacks=[CommandHandler('stop_age', stop_age)]
    )
    new_spot = ConversationHandler(
        entry_points=[CommandHandler('add_spot', start_add_spot, pass_chat_data=True)],
        states={1: [MessageHandler(Filters.text, spot_name, pass_chat_data=True)],
                2: [MessageHandler(Filters.text, spot_cords)],
                3: [MessageHandler(Filters.photo, spot_photo)]},
        fallbacks=[CommandHandler('stop_spot', spot_stopping)]
    )

    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(start_handler)
    dp.add_handler(location)
    dp.add_handler(add_age_scen)
    dp.add_handler(new_spot)
    updater.start_polling()


if __name__ == '__main__':
    main()
