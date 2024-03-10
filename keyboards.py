import telebot
from seatable_api import Base
from telebot import types
from telebot.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from config import *
base = Base(api_token, server_url)
base.auth()


def admin_keyboard():
    admin_keyboard = telebot.types.ReplyKeyboardMarkup()
    admin_keyboard.row("Сделать рассылку", "Cписок команд")
    admin_keyboard.row("Помощь","Баны")
    return admin_keyboard

def ban_keyboard():
    admin_keyboard = telebot.types.ReplyKeyboardMarkup()
    admin_keyboard.row("Забанить кого нибудь нахуй","Разбанить кого-нибудь")
    admin_keyboard.row("/admin")

    return admin_keyboard


def user_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup()
    keyboard.row("Задать вопрос", "Отправить жалобу")
    #keyboard.row("Узнать количество GIS-баллов", "Потратить баллы")
    #keyboard.row("Запросить добавление баллов")
    return keyboard

def help_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup()
    keyboard.row("Помощь по рассылке", "Помощь по опросам")
    keyboard.row("Помощь по жалобам и вопросам","Помощь по банам")
    keyboard.row("/admin")
    return keyboard

def help_keyboard_inline():
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(InlineKeyboardButton("Помощь по рассылке", callback_data="help_ads"),
                 InlineKeyboardButton("Помощь по опросам", callback_data="help_poll"))
    keyboard.add(InlineKeyboardButton("Помощь по жалобам и вопросам", callback_data="help_questions"))
    keyboard.add(InlineKeyboardButton("Выход из меню помощи", callback_data="help_leave"))
    return keyboard


def points_keyboard(amount,user_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 5
    data = "points_yes-" + str(amount) + "-" +str(user_id)
    keyboard.add(InlineKeyboardButton("Добавить %s баллов" % amount, callback_data=data),
                       InlineKeyboardButton("Отказать", callback_data="points_no"))
    return keyboard


def yesno_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(InlineKeyboardButton("Да", callback_data="pool_yes"),
                       InlineKeyboardButton("Нет", callback_data="pool_no"))
    return keyboard

def reply_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(InlineKeyboardButton("Решено", callback_data="reply_done"))
    return keyboard

def admin_commands():
    keyboard = telebot.types.ReplyKeyboardMarkup()
    keyboard.row("/resetpoll", "Команда удаляет ВСЮ информацию о предыдущем опросе")
    keyboard.row("/result", "Команда показывает результаты предыдушего опроса")
    keyboard.row("/admin", "Вызов клавиатуры администратора")
    return keyboard

def categoty_choise():
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 5
    keyboard.add(InlineKeyboardButton("Акриловые фигурки", callback_data='category_Acril'))
    keyboard.add(InlineKeyboardButton("ПВХ фигурки", callback_data="category_PVH"))
    keyboard.add(InlineKeyboardButton("Брелки", callback_data="category_charm"))
    return keyboard

def ads_yes_no():
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 5
    keyboard.add(InlineKeyboardButton("Отправить", callback_data='ads_yes'))
    keyboard.add(InlineKeyboardButton("Отмена рассылки", callback_data="ads_no"))
    return keyboard



def pages_keyboard(current_page,category):
    name = get_cell(base.query(
        'select Name from {c_category} where Number = "{page}"'.format(c_category=category, page=current_page)))
    price = get_cell(base.query(
        'select Price from {c_category} where Number = "{page}"'.format(c_category=category, page=current_page)))
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 5
    prv_page = int(current_page) - 1

    last_page = len(base.query('select Number from {c_category} '.format(c_category=category)))

    if prv_page < 1:
        prv_page =1

    nxt_page = int(current_page) + 1
    if nxt_page >last_page:
        nxt_page = 3

    keyboard.add(InlineKeyboardButton("<=", callback_data='next_page {cat} {np}'.format(cat=category, np=prv_page)),
                 InlineKeyboardButton("Страница {c_page}/{max_page}".format(c_page=current_page,max_page=last_page), callback_data = "nothing"),
                 InlineKeyboardButton("=>", callback_data='next_page {cat} {np}'.format(cat=category, np=nxt_page)))
    keyboard.add(InlineKeyboardButton("Заказать {Name} за {c_price} GIS баллов".format(Name=name, c_price = price), callback_data='point_purchase {c_category} {page} {c_price}'.format(c_category=category,page=current_page,c_price=price)))
    keyboard.add(InlineKeyboardButton("Вернуться к выбору категории", callback_data="back_to_category_choice"))
    return keyboard
