import logging
from data import db_session
from data.user import User
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
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
user = User()

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
    update.message.reply_text(
        "Осталось немного, напиши нам свой возраст, можно и без него, но тогда некоторые функции не будут доступны тебе:")
    return 1


def add_age(update, context):
    age = update.message.text
    context.user_data['age'] = age
    try:
        if int(age) < 13:
            ost = 13 - int(age)
            if ost > 4:
                update.message.reply_text(f'Извиняй друг, но ты ещё маловат. Приходи через {ost} лет')

            elif 1 < ost <= 4:
                update.message.reply_text(f'Извиняй друг, но ты ещё маловат. Приходи через {ost} года')

            else:
                update.message.reply_text(f'Извиняй друг, но ты ещё маловат. Приходи через {ost} год')

        else:
            db_sess.query(User).filter_by(id=update.message.from_user['id']).update(
                {'age': age}
            )
            db_sess.commit()
            db_sess.rollback()
            return ConversationHandler.END

    except:
        update.message.reply_text('Упс... Что-то пошло не так! Попробуй снова')


def stop_age(update, context):
    murkup = user_keyboard(context)
    update.message.reply_text('Ну как хочешь! Значит будешь демо ботом пользоваться', reply_markup=murkup)
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
        fallbacks=[CommandHandler('stop_loc', stop_age)]
    )

    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(start_handler)
    dp.add_handler(location)
    dp.add_handler(add_age_scen)
    updater.start_polling()


if __name__ == '__main__':
    main()
