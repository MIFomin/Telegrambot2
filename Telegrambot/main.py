import os
import random

import telebot
from dotenv import load_dotenv
from telebot import types

import db_control
from consts import Keys, Reply

load_dotenv()

bot = telebot.TeleBot(os.getenv("TOKEN"))

keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
random_task = types.InlineKeyboardButton(Keys.RANDOM_TASK.value)
history = types.InlineKeyboardButton(Keys.HISTORY.value)
statistics = types.InlineKeyboardButton(Keys.STATISTICS.value)
next_olymp = types.InlineKeyboardButton(Keys.NEXT_OLYMP.value)
search = types.InlineKeyboardButton(Keys.SEARCH.value)
keyboard.add(random_task, history, statistics, next_olymp, search)


@bot.message_handler(commands=["start"])
def start_message(message):
    name = message.chat.first_name
    bot.send_message(
        message.chat.id,
        f"Привет, {name}, меня зовут Problems23bot, я буду тебе помогать изучать олимпиадную математику",
    )

    # создание таблицы Users если не существует
    db_control.execute(
        """
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grade INTEGER,
                completedTaskIds TEXT NOT NULL,
                telegramChatId TEXT UNIQUE
            );
        """
    )

    users = db_control.select(
        f"""SELECT * FROM Users WHERE telegramChatId = {message.chat.id};"""
    )

    if len(users) != 0:
        bot.send_message(
            message.chat.id, Reply.Success.EXISTS_USER.value, reply_markup=keyboard
        )
        return

    sent_msg = bot.send_message(message.chat.id, Reply.Success.ASK_GRADE.value)
    bot.register_next_step_handler(sent_msg, grade)


def grade(message):
    try:
        grade_num = int(message.text)
        if grade_num < 1 or grade_num > 11:
            raise ValueError("Invalid grade")

        # Добавление нового человека в базу по id чата если такого нет
        db_control.execute(
            f"""
            INSERT INTO Users (grade, completedTaskIds, telegramChatId) VALUES ({grade_num}, '', {message.chat.id});
            """
        )

        bot.send_message(
            message.chat.id, Reply.Success.SAVE_USER.value, reply_markup=keyboard
        )
    except ValueError:
        sent_msg = bot.send_message(message.chat.id, Reply.Error.INVALID_GRADE.value)
        bot.register_next_step_handler(sent_msg, grade)
    except Exception as e:
        sent_msg = bot.send_message(message.chat.id, Reply.Error.UNHANDLED.value, e)
        bot.register_next_step_handler(sent_msg, grade)


def get_user_tasks(message):
    users = db_control.select(
        f"""SELECT * FROM Users WHERE telegramChatId = {message.chat.id};"""
    )
    if len(users) == 0:
        return

    # если нашлось больше одного пользователя
    if len(users) > 1:
        bot.send_message(
            message.chat.id,
            Reply.Error.SEVERAL_USERS_FOUND.value,
            reply_markup=keyboard,
        )
        return

    # получаем список задач пользователя
    return users[0][2]


@bot.message_handler(func=lambda message: message.text == Keys.HISTORY.value)
def history_callback(message):
    # находим все задачи пользователя из таблицы Tasks по id
    user_tasks = get_user_tasks(message)
    if len(user_tasks) == 0:
        bot.send_message(
            message.chat.id,
            Reply.Error.USER_TASKS_EMPTY.value,
            reply_markup=keyboard,
        )
        return ''

    for task in user_tasks.split():
        tasks = db_control.select(f"SELECT * FROM Tasks WHERE id = {task};")
        if len(tasks) == 0:
            bot.send_message(
                message.chat.id,
                Reply.Error.TASK_NOT_FOUND.value,
                reply_markup=keyboard,
            )
            return ''

        bot.send_message(message.chat.id, tasks[0][1], reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == Keys.SEARCH.value)
def search_callback(message):
    sent_msg = bot.send_message(
        message.chat.id,
        "Введите номер задачи:",
    )
    bot.register_next_step_handler(sent_msg, search_task)


def search_task(message):
    try:
        mes = int(message.text)
        task = db_control.select(f"SELECT * FROM Tasks WHERE id = {mes}")
        show_task(message, task)
    except:
        bot.send_message(
            message.chat.id, Reply.Error.UNHANDLED.value, reply_markup=keyboard
        )


@bot.message_handler(func=lambda message: message.text == Keys.RANDOM_TASK.value)
def random_task_callback(message):
    user_tasks = list(map(int, get_user_tasks(message).split()))
    unfinished_tasks = set()

    if len(user_tasks) == 0:
        tasks = db_control.select("SELECT * FROM Tasks;")
        unfinished_tasks.update(tasks)
    else:
        all_tasks = db_control.select(f"SELECT * FROM Tasks ;")
        tasks = []
        for i in range(len(all_tasks)):
            if i + 1 not in user_tasks:
                tasks.append(all_tasks[i])
        if not tasks:
            bot.send_message(message.chat.id, Reply.Success.ALL_SOLVED.value, reply_markup=keyboard)
            return
        unfinished_tasks.update(tasks)
    if len(unfinished_tasks) > 1:
        task = [list(unfinished_tasks)[random.randint(0, len(unfinished_tasks) - 1)]]
    else:
        task = list(unfinished_tasks)
    show_task(message, task)


def show_task(message, task):
    callback_str = f"yes_{task[0][0]}"
    bot.send_message(message.chat.id, task[0][1])
    keyboard1 = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton(Keys.YES.value, callback_data=callback_str)
    no = types.InlineKeyboardButton(Keys.NO.value, callback_data=Keys.NO.value)
    keyboard1.add(yes, no)
    bot.send_message(message.chat.id, 'Готовы предоставить ответ?', reply_markup=keyboard1)


@bot.callback_query_handler(func=lambda call: True)
def read_answer(call):
    if call.data == Keys.NO.value:
        bot.send_message(call.message.chat.id, 'Оставим эту задачу на потом', reply_markup=keyboard)
        return

    _, id = call.data.split('_')
    task = db_control.select(
        f"""SELECT * FROM Tasks WHERE id = {id};"""
    )
    answer = bot.send_message(call.message.chat.id, "Ваш ответ:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(answer, check_if_correct, task[0])


def check_if_correct(answer, task):
    tasks = get_user_tasks(answer)
    if answer.text != task[2]:
        bot.send_message(answer.chat.id, 'К сожалению, ответ неправильный', reply_markup=keyboard)
        return

    if tasks == '':
        updated_tasks = str(task[0])
    else:
        updated_tasks = " ".join(list(set(f"{tasks} {task[0]}".split())))

    db_control.execute(f"UPDATE Users SET completedTaskIds='{updated_tasks}' WHERE telegramChatId={answer.chat.id};")
    bot.send_message(answer.chat.id, 'Задача решена правильно!', reply_markup=keyboard)
@bot.message_handler(func=lambda message: message.text == Keys.STATISTICS.value)
def send_statisitics(message):
    tasks = get_user_tasks(message).split()
    # 11 lvls of difficulty
    levels = db_control.select(f"SELECT level FROM Tasks WHERE id IN ({', '.join(tasks)})")
    levels = [levels[i][0] for i in range(len(levels))]
    levels = list(map(int, levels))
    count = [0] * 11
    for lvl in levels:
        count[lvl - 1] += 1
    msg = [f'Уровень {i + 1}: {count[i]}' for i in range(len(count))]
    msg = '\n'.join(msg)
    bot.send_message(message.chat.id, 'Решены задачи следующей сложности:')
    bot.send_message(message.chat.id, msg, reply_markup = keyboard)
@bot.message_handler(func=lambda message: message.text == Keys.NEXT_OLYMP.value)
def send_timetable(message):
    with open('C:\\Users\\jugof\\Desktop\\Telegrambot\\Календарь математических олимпиад.txt', 'r', encoding='utf-8') as file:
        txt = file.read()
    bot.send_message(message.chat.id, txt, reply_markup=keyboard)
if __name__ == "__main__":
    print("Bot is running")
    bot.infinity_polling()
