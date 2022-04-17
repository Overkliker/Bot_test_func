import logging
from help_defs import is_float

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
        "Привет! Я бот, который расскажет тебе о спотах поблизости. Давай зарегистрируемся введи мне своё имя")
    return 1


def f_res(update, context):
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
            print(user_id)
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


def rename(update, context):
    if update.message.text.lower() == 'нет':


def stop(update, context):
    murkup = user_keyboard(context)
    update.message.reply_text('reg stop', reply_markup=murkup)
    return ConversationHandler.END

############################################# Add location ############################################################

def start_locating(update, context):
    db_sess = db_session.create_session()
    update.message.reply_text(
        "Отлично, давай определим твоё мостоположение. Напиши мне свою широту и долготу"
        " (можешь найти в яндекс картах, например). Сначала широта")
    return 1


def add_lat(update, context):
    lat = update.message.text
    if is_float(lat):
        context.user_data['lat'] = int(lat)
        update.message.reply_text('Хорошо, а теперь долготу')
        return 2

    else:
        update.message.reply_text('Похоже, что ты написал не широту')

def add_lon(update, context):
    lon = update.message.text
    if is_float(lon):
        context.user_data['lon'] = lon
        db_sess.query(User).filter_by(id=update.message.from_user['id']).update(
            {'lat': context.user_data['lat'],
             'lon': lon
             }
        )
        db_sess.commit()
        db_sess.rollback()
        return ConversationHandler.END

    else:
        update.message.reply_text('Похоже, что ты ввёл не долготу')

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
        update.message.reply_text('Теперь его координаты в виде широты и долготы,'
                                  ' взять их можно всё в тех же яндекс картах. Отправь сначала широту')
        return 2


def spot_lat(update, context):
    lat = update.message.text
    if not is_float(lat):
        update.message.reply_text('Похоже, что ты ввёл не широту')

    else:
        context.user_data['spot_lat'] = lat
        update.message.reply_text('Теперь мне нужна его долгота')
        return 3


def spot_lon(update, context):
    lon = update.message.text
    if is_float(lon):
        db = db_sess.query(Spot).filter((Spot.lat == float(context.user_data['spot_lat'])) and (Spot.lon == lon))
        print(db)
        if db_sess.query(db.exists()).scalar():
            update.message.reply_text('Похоже, что такой спот уже существует! Попробуй по новой')
            return ConversationHandler.END

        else:
            update.message.reply_text('Великолепно, а теперь отправь его фото, для наглядности')
            context.user_data['spot_lon'] = lon
            return 4

    else:
        update.message.reply_text('Похоже, что ты ввёл не долготу')


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
        states={1: [MessageHandler(Filters.text, add_lat)],
                2: [MessageHandler(Filters.text, add_lon)]},
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
                2: [MessageHandler(Filters.text, spot_lat)],
                3: [MessageHandler(Filters.text, spot_lon)],
                4: [MessageHandler(Filters.photo, spot_photo)]},
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
