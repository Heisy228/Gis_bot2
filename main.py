import telebot.types

from keyboards import *
from config import *
import re
from seatable_api import Base
from telebot import types

# БД

base = Base(api_token, server_url)
base.auth()

# БД

bot = telebot.TeleBot(TOKEN)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    print(call.data)

    if call.data == '1':

        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Спасибо за ответ!")
        base.query('update Table1 set User_vote = 1 where User_ID = %s' % call.message.chat.id)

    elif call.data == 'pool_yes':
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        raw_pool = base.query('select Placeholder from Voting')
        a = []
        for i in raw_pool:
            for value in i.values():
                a.append(value)
        pool_question = a[0]
        a.pop(0)
        print(a)

        ads = base.query('select User_ID from Table1')
        for i in ads:
            for value in i.values():
                print(value)
                bot.send_poll(chat_id=value, question="%s" % pool_question, options=a, is_anonymous=False)
        bot.send_message(call.message.chat.id, "Опрос отправлен! Для просмотра его результатов, напишите /result",
                         reply_markup=admin_keyboard())
        bot.delete_message(call.message.chat.id, call.message.message_id)

    elif call.data == 'pool_no':
        base.query('delete from Voting')
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Опрос удален", reply_markup=admin_keyboard())

    elif 'points_yes' in call.data:
        data = str(call.data).split("-")
        points_amount = int(data[1])
        points_receiver = data[2]
        previous_points = base.query('select User_points from Table1 where User_ID = %s' % points_receiver)
        true_points = int(get_cell(previous_points)) + points_amount
        base.query('update Table1 set User_points = {points} where User_ID = {ID}'.format(points=true_points,
                                                                                          ID=points_receiver))

        bot.edit_message_text("Баллы добавлены. Тепрь у пользователя %s баллов" % true_points,
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id)

        bot.send_message(points_receiver,
                         "Вам добавлено {points} баллов. "
                         "Тепрь у вас {total_points} баллов".format(points=points_amount, total_points=true_points))

    elif call.data == 'points_no':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Отказано в добавлении баллов!")

    elif call.data == 'reply_done':
        bot.edit_message_text('На сообщение ниже был дан ответ.', chat_id=call.message.chat.id,
                              message_id=call.message.message_id)

    elif call.data == 'help_ads':
        bot.edit_message_text(ads_help, chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=help_keyboard_inline())

    elif call.data == 'help_poll':
        bot.edit_message_text(poll_help, chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=help_keyboard_inline())

    elif call.data == 'help_questions':
        bot.edit_message_text(questions_help, chat_id=call.message.chat.id,
                              message_id=call.message.message_id, reply_markup=help_keyboard_inline())

    elif call.data == 'help_leave':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Назад к клавиатуре администратора", reply_markup=admin_keyboard())

    elif call.data == 'category_Acril':
        foto = get_cell(base.query('select Photo from Acril where Number = "1"'))
        name = get_cell(base.query(
            'select Name from Acril where Number = "1"'))
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_photo(call.message.chat.id, foto, name, reply_markup=pages_keyboard(1, "Acril"))

    elif call.data == 'category_PVH':
        foto = get_cell(base.query('select Photo from PVH where Number = "1"'))
        name = get_cell(base.query(
            'select Name from PVH where Number = "1"'))
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_photo(call.message.chat.id, foto, name, reply_markup=pages_keyboard(1, "PVH"))

    elif call.data == 'category_charm':
        foto = get_cell(base.query('select Photo from Charms where Number = "1"'))
        name = get_cell(base.query(
            'select Name from Charms where Number = "1"'))
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_photo(call.message.chat.id, foto, name, reply_markup=pages_keyboard(1, "Charms"))

    elif "next_page" in call.data:
        current_category = str(call.data).split(" ")[1]
        current_page = str(call.data).split(" ")[2]
        foto = get_cell(base.query(
            'select Photo from {category} where Number = "{page}"'.format(category=current_category, page=current_page)))
        name = get_cell(base.query(
            'select Name from {category} where Number = "{page}"'.format(category=current_category, page=current_page)))


        bot.edit_message_media(
            media=types.InputMediaPhoto(foto), chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.edit_message_caption(
            name, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=pages_keyboard(current_page, current_category))

    elif "point_purchase" in call.data:
        current_category = str(call.data).split(" ")[1]
        current_page = str(call.data).split(" ")[2]
        price = int(str(call.data).split(" ")[3])
        previous_points = base.query('select User_points from Table1 where User_ID = %s' % call.message.chat.id)
        name = get_cell(base.query(
            'select Name from {category} where Number = "{page}"'.format(category=current_category, page=current_page)))
        code  = get_cell(base.query(
            'select Code from {category} where Number = "{page}"'.format(category=current_category, page=current_page)))
        if int(get_cell(previous_points)) < price:
            bot.send_message(call.message.chat.id,
                             "У вас недостаточно баллов!")
        else:
            true_points = int(get_cell(previous_points)) - price
            base.query('update Table1 set User_points = {points} where User_ID = {ID}'.format(points=true_points,
                                                                                              ID=call.message.chat.id))
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, "Вы успешно купили {c_name} за GIS-баллы!".format(c_name=name))
            base.query('update Table1 set bought_product = "{c_code}-{girl}" where User_ID = {ID}'.format(c_code=code,girl=name, ID=call.message.chat.id))
            bot.send_message(call.message.chat.id,
                             "В следующем сообщении напишите пункт выдачи, в котором вам будет удобно забрать ваш заказ")
            base.query('update Table1 set User_state = "Points_spent" where User_ID = %s' % call.message.chat.id)
            bot.send_message(admin_id, "Покупатель купил {c_name} за GIS-баллы!".format(c_name=name))


    elif call.data == 'back_to_category_choice':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Выберите категорию", reply_markup=categoty_choise())

    elif call.data == 'ads_yes':
        base.query('update Table1 set Admin_status = "Chilling" where User_ID = %s' % call.message.chat.id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Рассылка успешно отправлена", reply_markup=admin_keyboard())
        ads_text = get_cell(base.query('select Text from Ads'))
        ads_users = base.query('select User_ID from Table1')
        for i in ads_users:
            for value in i.values():
                bot.send_message(value, ads_text)

    elif call.data == 'ads_no':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "Рассылка отменена", reply_markup=admin_keyboard())
        base.query('update Table1 set Admin_status = "Chilling" where User_ID = %s' % call.message.chat.id)






@bot.message_handler(commands=['resetpoll'])
def admin_check(message):
    base.query('delete from Voting')
    bot.send_message(message.chat.id, "Предыдущий опрос удален", reply_markup=admin_keyboard())
    base.query('update Table1 set User_vote = NULL')


@bot.message_handler(commands=['test'])
def admin_check(message):

    bot.send_message(message.chat.id,
                     "Выберите категорию", reply_markup=categoty_choise())


@bot.message_handler(commands=['result'])
def resetpoll(message):
    try:
        length = len(base.query('select Number from Voting')) - 1
        a = []
        b = [[]] * length
        c = [0] * length
        print("c = ===", c)
        print("b=    ", b)
        print("Окончательное количество опций = %s" % length)
        for i in range(length):
            a.append(base.query('select User_vote from Table1 where User_vote = %s' % i))
        print("a=", a)
        print("           ")
        for i in range(length):
            for j in range(len(a[i])):
                for value in a[i][j].values():
                    b[value].append(value)

        for i in range(len(b)):
            for j in range(len(b[i])):
                if b[i][j] == i:
                    c[i] = c[i] + 1

        raw_pool = base.query('select Placeholder from Voting')
        a = []
        for i in raw_pool:
            for value in i.values():
                a.append(value)
        pool_question = a[0]
        a.pop(0)
        bot.send_message(message.chat.id, "Вот результы опроса '%s' " % pool_question)
        for i in range(len(c)):
            bot.send_message(message.chat.id,
                             "За вариант '{option}' проголосовало {count} человека".format(option=a[i], count=c[i]))
    except:
        bot.send_message(message.chat.id, "Сейчас никакого опроса не проводится!")


@bot.message_handler(commands=['admin'])
def admin_check(message):
    user_state = base.query('select User_state from Table1 where User_ID = %s' % message.chat.id)
    if user_state == [{'User_state': 'Admin'}]:
        bot.send_message(message.chat.id, "Клавиатура администратора", reply_markup=admin_keyboard())
    else:
        bot.send_message(message.chat.id, 'Троян успешно загружен на ваше устройство')


@bot.message_handler(commands=['start'])
def start_message(message):
    request = ('select User_ID from Table1 where User_ID = %s' % message.chat.id)
    check = base.query(request)
    if len(check) > 0:
        print("Это старый пользователь!")

    else:
        print("Пользователь НЕ найден")
        row_data = {
            "User_ID": "%s" % message.chat.id,
            "User_state": "Starting",
            "User_FirstName": "%s" % message.from_user.first_name,
            "User_LastName": "%s" % message.from_user.last_name,
            "User_Username": "%s" % message.from_user.username,
            "User_points": "%s" % 0,
        }
        base.append_row('Table1', row_data)

    bot.send_message(message.chat.id,
                     f"Здравствуйте, если у вас есть вопросы или предложения по продукции GIS, напишите сюда!",
                     reply_markup=user_keyboard())


@bot.message_handler(content_types=['text'])
def complaint_question(message):
    banned_check = base.query('select User_banned from Table1 where User_ID = %s' % message.chat.id)
    user_state = base.query('select User_state from Table1 where User_ID = %s' % message.chat.id)
    print(user_state)

    if banned_check != [{'User_banned': 'YES'}]:

        if message.text == "Узнать количество GIS-баллов":
            true_points = get_cell(base.query('select User_points from Table1 where User_ID = %s' % message.chat.id))
            bot.send_message(message.chat.id, "Количество ваших баллов: %s" % true_points)

        elif message.text == "Задать вопрос":
            bot.send_message(message.chat.id,
                             "В следующем сообщении(или сообщениях) напишите свой вопрос. "
                             "Его получит наша служба поддержки и вскоре ответит на него в этом диалоге.")
            base.query('update Table1 set User_state = "Question" where User_ID = %s' % message.chat.id)

        elif message.text == "Отправить жалобу":
            bot.send_message(message.chat.id,
                             "В следующем сообщении(или сообщениях) как можно подробнее опишите свою проблему. "
                             "Вы можете прикладывать фото. "
                             "Это сообщение получит наша служба поддержки и вскоре ответит на него в этом диалоге.")
            base.query('update Table1 set User_state = "Complaint" where User_ID = %s' % message.chat.id)

        elif message.text == "Запросить добавление баллов":
            bot.send_message(message.chat.id, "В следующем сообщении напишите артикул купленного вами товара. "
                                              "Вскоре, баллы будут начисленны")
            base.query('update Table1 set User_state = "Points" where User_ID = %s' % message.chat.id)

        elif message.text == "Потратить баллы":
            bot.send_message(message.chat.id,
                             "Выберите категорию", reply_markup=categoty_choise())

        elif user_state == [{'User_state': 'Question'}] and 'Задать вопрос' not in message.text:
            bot.send_message(admin_id, 'Сообщение от покупателя! #вопрос ❓❓❓ :', reply_markup=reply_keyboard())
            bot.send_message(message.chat.id, 'Ваш вопрос отправлен в службу поддержки!')
            bot.forward_message(admin_id, message.chat.id, message.message_id)

        elif user_state == [{'User_state': 'Complaint'}] and 'Отправить жалобу' not in message.text:
            bot.send_message(admin_id, 'Сообщение от покупателя! #жалоба 🔴🔴🔴 :', reply_markup=reply_keyboard())
            bot.send_message(message.chat.id, 'Ваша жалоба отправлена в службу поддержки!')
            bot.forward_message(admin_id, message.chat.id, message.message_id)

        elif user_state == [{'User_state': 'Points'}] and 'Запросить добавление баллов' not in message.text:

            try:
                base.query('select User_Username from Table1 where User_ID = %s' % message.chat.id)
                points = get_cell(base.query('select points_amount from Table_points where Code = %s' % message.text))
                bot.send_message(admin_id, 'Сообщение от покупателя! #баллы :',
                                 reply_markup=points_keyboard(points, message.chat.id))
                bot.send_message(message.chat.id, 'Артикул получен, баллы скоро придут!')
                bot.forward_message(admin_id, message.chat.id, message.message_id)

            except:
                bot.send_message(message.chat.id, 'Неверный артикул!')

        elif user_state == [{'User_state': 'Points_spent'}]:
            girl = get_cell(base.query('select bought_product from Table1 where User_ID = %s' % message.chat.id))
            girl = girl.split("-")
            girl_code = girl[0]
            girl_name = girl[1]
            bot.send_message(admin_id, 'Покупатель отправил адрес для отправки заказа "{name}" Артикул этого товара = {code}  #покупка :'.format(name = girl_name,code=girl_code), reply_markup=reply_keyboard())
            bot.send_message(message.chat.id, 'Информация получена. Администратор может связаться с вами для уточнения деталей')
            base.query('update Table1 set User_state = "Nothing" where User_ID = %s' % message.chat.id)
            bot.forward_message(admin_id, message.chat.id, message.message_id)


    else:
        bot.send_message(message.chat.id, 'Ты в бане, пошел нахууууууууууй')

    if user_state == [{'User_state': 'Admin'}]:
        status_check = base.query('select Admin_status from Table1 where User_ID = %s' % message.chat.id)
        print(status_check)
        print(message.text)
        if status_check == [{'Admin_status': 'Banning'}] and message.text != "Выйти из режима бана":
            about_to_be_banned = message.reply_to_message.forward_from.id
            base.query('update Table1 set User_banned = "YES" where User_ID = %s' % about_to_be_banned)
            bot.send_message(message.chat.id, "Пользователь забанен!")

        elif status_check == [{'Admin_status': 'Unbanning'}] and message.text != "Выйти из режима разбана":
            about_to_be_unbanned = message.text
            base.query('update Table1 set User_banned = "No" where User_Username = "%s"' % about_to_be_unbanned)
            bot.send_message(message.chat.id, "Пользователь разбанен!")

        elif status_check == [{'Admin_status': 'Ads'}] and message.text != "Отмена рассылки":
            base.query('update Ads set Text = "%s"' % message.text)
            bot.send_message(message.chat.id, "Сообщение будет вылядить так:")
            bot.send_message(message.chat.id, message.text)
            bot.send_message(message.chat.id, "Отправить его?",reply_markup=ads_yes_no())



        elif status_check == [{'Admin_status': 'Pool_starting'}] and message.text != "Отмена опроса":
            base.query('update Table1 set Admin_status = "Pool_pending" where User_ID = %s' % message.chat.id)
            raw_pool = message.text.split("-")
            pool_question = raw_pool[0]
            raw_pool.pop(0)
            print(raw_pool)
            row_data = {"Placeholder": "%s" % pool_question, }
            base.append_row('Voting', row_data)

            for i in range(len(raw_pool)):
                row_data = {
                    "Placeholder": "%s" % raw_pool[i],
                    "Value": "%s" % 0,
                    "Number": "%s" % i,
                }
                base.append_row('Voting', row_data)

            bot.send_message(message.chat.id, "Опрос будет выглядеть вот так: ")
            bot.send_poll(chat_id=message.chat.id, question="%s" % pool_question, options=raw_pool, is_anonymous=False)
            bot.send_message(message.chat.id, "Отправлять его?", reply_markup=yesno_keyboard())

        elif message.text == "Забанить кого нибудь нахуй":
            ban_cancel = telebot.types.ReplyKeyboardMarkup()
            ban_cancel.row("Выйти из режима бана")
            bot.send_message(message.chat.id, "Ответь на сообщение того,кого надо забанить", reply_markup=ban_cancel)
            base.query('update Table1 set Admin_status = "Banning" where User_ID = %s' % message.chat.id)

        elif message.text == "Выйти из режима бана":
            base.query('update Table1 set Admin_status = "Chilling" where User_ID = %s' % message.chat.id)
            bot.send_message(message.chat.id, "Отмена режима бана", reply_markup=admin_keyboard())

        elif message.text == "Выйти из режима разбана":
            base.query('update Table1 set Admin_status = "Chilling" where User_ID = %s' % message.chat.id)
            bot.send_message(message.chat.id, "Отмена режима разбана", reply_markup=admin_keyboard())

        elif message.text == "Выйти из режима добавления баллов":
            base.query('update Table1 set Admin_status = "Chilling" where User_ID = %s' % message.chat.id)
            bot.send_message(message.chat.id, "Отмена добавления баллов", reply_markup=admin_keyboard())

        elif message.text == "Разбанить кого-нибудь":
            unban_cancel = telebot.types.ReplyKeyboardMarkup()
            unban_cancel.row("Выйти из режима разбана")
            bot.send_message(message.chat.id, "Напиши username чела, и его разбанят(это который через @)",
                             reply_markup=unban_cancel)
            base.query('update Table1 set Admin_status = "Unbanning" where User_ID = %s' % message.chat.id)

        elif message.text == "Сделать рассылку":
            base.query('update Table1 set Admin_status = "Ads" where User_ID = %s' % message.chat.id)
            ads_cancel = telebot.types.ReplyKeyboardMarkup()
            ads_cancel.row("Отмена рассылки")
            bot.send_message(message.chat.id,
                             'Следующее сообщение которое ты отправишь, будет направлено всем пользователям бота! '
                             'Можешь отменить рассылку кнопкой.', reply_markup=ads_cancel)

        elif message.text == "Отмена рассылки":
            base.query('update Table1 set Admin_status = "Chilling" where User_ID = %s' % message.chat.id)
            bot.send_message(message.chat.id, "Выход из режима рассылки", reply_markup=admin_keyboard())

        elif message.text == "Отмена опроса":
            base.query('update Table1 set Admin_status = "Chilling" where User_ID = %s' % message.chat.id)
            base.query('delete from Voting')
            bot.send_message(message.chat.id, "Опрос отменен", reply_markup=admin_keyboard())

        elif message.text == "Cписок команд":
            bot.send_message(message.chat.id, "Клавиатура команд", reply_markup=admin_commands())

        elif message.text == "Баны":
            bot.send_message(message.chat.id, "Меню банов", reply_markup=ban_keyboard())

        elif message.text == "Помощь":
            bot.send_message(message.chat.id, "Меню помощи", reply_markup=help_keyboard_inline())

        elif status_check == [{'Admin_status': 'Chilling'}]:
            try:
                bot.send_message(message.reply_to_message.forward_from.id, message.text)
            except:
                bot.send_message(message.chat.id,
                                 "Ты че то не так сделал или бот работает неправильно. "
                                 "Для ответа пользователям нажимай на сообщениях reply/ответить")


@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    banned_check = base.query('select User_banned from Table1 where User_ID = %s' % message.chat.id)
    user_state = base.query('select User_state from Table1 where User_ID = %s' % message.chat.id)
    if banned_check != [{'User_banned': 'YES'}]:

        if user_state == [{'User_state': 'Question'}]:
            bot.send_message(admin_id, 'Сообщение от покупателя! #вопрос ❓❓❓ :')
            bot.send_message(message.chat.id, 'Ваш вопрос отправлен в службу поддержки!')
            bot.forward_message(admin_id, message.chat.id, message.message_id)

        if user_state == [{'User_state': 'Complaint'}]:
            bot.send_message(admin_id, 'Сообщение от покупателя! #жалоба 🔴🔴🔴 :')
            bot.send_message(message.chat.id, 'Ваша жалоба отпрвавлена в службу поддержки!')
            bot.forward_message(admin_id, message.chat.id, message.message_id)
    else:
        bot.send_message(message.chat.id, 'Ты в бане, пошел нахууууууууууй')


@bot.message_handler(content_types=['document'])
def handle_docs_photo(message):
    banned_check = base.query('select User_banned from Table1 where User_ID = %s' % message.chat.id)
    user_state = base.query('select User_state from Table1 where User_ID = %s' % message.chat.id)
    if banned_check != [{'User_banned': 'YES'}]:

        if user_state == [{'User_state': 'Question'}]:
            bot.send_message(admin_id, 'Сообщение от покупателя! #вопрос ❓❓❓ :')
            bot.send_message(message.chat.id, 'Ваш вопрос отправлен в службу поддержки!')
            bot.forward_message(admin_id, message.chat.id, message.message_id)

        if user_state == [{'User_state': 'Complaint'}]:
            bot.send_message(admin_id, 'Сообщение от покупателя! #жалоба 🔴🔴🔴 :')
            bot.send_message(message.chat.id, 'Ваша жалоба отпрвавлена в службу поддержки!')
            bot.forward_message(admin_id, message.chat.id, message.message_id)
    else:
        bot.send_message(message.chat.id, 'Ты в бане, пошел нахууууууууууй')


@bot.poll_answer_handler()
def handle_poll(answer):
    a = answer.option_ids[0]

    base.query('update Table1 set User_vote = {option} where User_ID = {ID}'.format(option=a, ID=answer.user.id))


@bot.message_handler(content_types=['poll'])
def testttt(message):
    message_str = str(message)
    b = message_str.rpartition('poll')[-1]
    question_id = [_.start() for _ in re.finditer('question', b)]
    question_id_end = [_.start() for _ in re.finditer('options', b)]
    option_ids = [_.start() for _ in re.finditer('text', b)]
    option_ids_end = [_.start() for _ in re.finditer('voter_count', b)]

    options = []
    question = b[question_id[0] + 12:question_id_end[0] - 4]
    for i in range(len(option_ids)):
        options.append(b[option_ids[i] + 8:option_ids_end[i] - 4])

    ads = base.query('select User_ID from Table1')
    for i in ads:
        for value in i.values():
            bot.send_poll(chat_id=value, question="%s" % question, options=options, is_anonymous=False)
    bot.send_message(message.chat.id, "Опрос отправлен пользователям! Для просмотра его результатов, напишите /result",
                     reply_markup=admin_keyboard())

    row_data = {"Placeholder": "%s" % question}
    base.append_row('Voting', row_data)
    for i in range(len(options)):
        row_data = {
            "Placeholder": "%s" % options[i],
            "Value": "%s" % 0,
            "Number": "%s" % i,
        }
        base.append_row('Voting', row_data)

    print(options)
    print(question)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
