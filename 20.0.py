import telebot
from telebot import types
import requests
import random
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import flask

appname="telebot-stone"
server = flask.Flask(__name__)
apikey="d99ab3f1-55a5-4122-9246-893d20ce57c0"

#подключение к боту
token = "841031434:AAEAh_aajJKNTuNchDBT7cfr1_KmRyCwQNI"
bot = telebot.TeleBot(token)

#подключение к база данных
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred, {"databaseURL":"https://winx-b4050.firebaseio.com/"})

database = []
season = "Сезон 1-2"
qNum = 0

@bot.message_handler(commands=["start"])
def StartHandler(msg):
    global database
    
    name = msg.from_user.first_name
    bot.send_message(msg.chat.id,"Привет, " + name + "!")
    bot.send_message(msg.chat.id,"Я подготовил для тебя 3 вапроса по вселенной Винкс!") 
    database = db.reference('').get()
    AskSeason(msg)

def AskSeason(msg):
    keyboard = types.ReplyKeyboardMarkup()

    btn1 = types.KeyboardButton("Сезон 1-2")
    btn2 = types.KeyboardButton("Сезон 3-4")
    btn3 = types.KeyboardButton("Сезон 5-6")
    btn4 = types.KeyboardButton("Сезон 7-8")

    keyboard.add(btn1)
    keyboard.add(btn2)
    keyboard.add(btn3)
    keyboard.add(btn4)

    s = bot.send_message(msg.chat.id,"Выбери сезон:", reply_markup = keyboard)
    bot.register_next_step_handler(s,StartQuiz)

def StartQuiz(msg):
    global season
    global database
    season = msg.text
    random.shuffle(database[season])
    AskQuestion(msg)

def AskQuestion(msg):
    global database
    global qNum
    global season
    
    question = database[season][qNum]["question"]

    answers = []
    answers.append(database[season][qNum]["correct"])
    answers.append(database[season][qNum]["incorrect1"])
    answers.append(database[season][qNum]["incorrect2"])
    answers.append(database[season][qNum]["incorrect3"])
    random.shuffle(answers)

    keyboard = types.ReplyKeyboardMarkup()

    btn1 = types.KeyboardButton(answers[0])
    btn2 = types.KeyboardButton(answers[1])
    btn3 = types.KeyboardButton(answers[2])
    btn4 = types.KeyboardButton(answers[3])

    keyboard.add(btn1)
    keyboard.add(btn2)
    keyboard.add(btn3)
    keyboard.add(btn4)

    W = bot.send_message(msg.chat.id,question,reply_markup = keyboard)
    bot.register_next_step_handler(W,Answer)

    tip = database[season][qNum]["tip"]
    bot.send_message(msg.chat.id,tip)

    

def  Answer(msg):
    global qNum

    if msg.text == str(database[season][qNum]["correct"]):
        bot.send_message(msg.chat.id,"Правильно!")
    else:
        bot.send_message(msg.chat.id,"Ты ошибся!")

    qNum = qNum + 1

    if qNum == 3:
        keyboard = types.ReplyKeyboardRemove(selective = False)
        bot.send_message(msg.chat.id, "Ты молодец,игра окончена!",reply_markup = keyboard)
    else:
        AskQuestion(msg)
    
@server.route('/' + token, methods=['POST'])
def get_message():
     bot.process_new_updates([types.Update.de_json(flask.request.stream.read().decode("utf-8"))])
     return "!", 200

@server.route('/', methods=["GET"])
def index():
     bot.remove_webhook()
     bot.set_webhook(url=f"https://{appname}.herokuapp.com/{token}")
     return "Hello from Heroku!", 200
     

if __name__ == "_main_":
     server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
#bot.polling()
    
