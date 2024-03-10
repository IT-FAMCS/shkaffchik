import telebot
from functools import partial
from models import SQLconnect
import textwrap


sql = SQLconnect()

bot = telebot.TeleBot('6914373217:AAE3Ed21LFpqo1ykAcpOup2vmFcOIrnnWug', parse_mode='HTML')
retur = telebot.types.ReplyKeyboardMarkup()
retur.add(telebot.types.KeyboardButton('Назад'))

markup = telebot.types.ReplyKeyboardMarkup()
item1 = telebot.types.KeyboardButton('Список')
item2 = telebot.types.KeyboardButton('Взять предмет')
item3 = telebot.types.KeyboardButton('Вернуть предметы')
item4 = telebot.types.KeyboardButton('Создать предмет')
item5 = telebot.types.KeyboardButton('Взятые')
item6 = telebot.types.KeyboardButton('Изменить кол-во предмета')
item7 = telebot.types.KeyboardButton('Удалить предмет')
markup.add(item1, item2, item3, item4, item5, item6, item7)

@bot.message_handler(commands=['start'])
def answer(message):
    sql.AddUser(message.from_user.username)
    bot.send_message(message.chat.id, 'Это Шкаф-бот!',reply_markup=markup)
    
@bot.message_handler(content_types='text')
def Ans(message):
    if message.text == "Список":
        bot.send_message(message.chat.id, sql.ListOfItems())
    if message.text == "Создать предмет":
        bot.send_message(message.chat.id, "Введите название \n(Название должно быть в одно слово, например НазваниеПредмета)", reply_markup=retur)
        bot.register_next_step_handler(message, NameOfItem)
    if message.text == "Взять предмет":
        buttons = sql.CreateButtons()
        bot.send_message(message.chat.id, "Введите название предмета", reply_markup=buttons)
        bot.register_next_step_handler(message, TakeItemDetailBot)
    if message.text == "Вернуть предметы":
        bot.send_message(message.chat.id, sql.ReturnItemDetail(message.from_user.username), reply_markup=retur)
        bot.register_next_step_handler(message, ReturnItemNameBot)
    if message.text == "Взятые":
        bot.send_message(message.chat.id, "Введите название предмета или тег пользователя", reply_markup=retur)
        bot.register_next_step_handler(message, NameOrTagListBot)
    if message.text == "Изменить кол-во предмета":
        bot.send_message(message.chat.id, "Введите название предмета", reply_markup=retur)
        bot.register_next_step_handler(message, NameOfEditBot)
    if message.text == "Удалить предмет":
        bot.send_message(message.chat.id, "Введите название предмета", reply_markup=retur)
        bot.register_next_step_handler(message, DeleteItemBot)



def NameOrTagListBot(message):
    Name = message.text
    try:
        if "@" in Name:
            bot.send_message(message.chat.id, sql.ListOfTakenByTag(Name[1::1]))
        elif Name == "Все":
            bot.send_message(message.chat.id, sql.ListOfTaken())
        else:
            bot.send_message(message.chat.id, sql.ListOfTakenByName(Name))
    except Exception as e:
        bot.send_message(message, text="Такого тега или предмета не найдено")

#Создание предмета в шкафу
def NameOfItem(message):
    Name = message.text
    if " " in Name:
        bot.send_message(message.chat_id, "Присутствуют пробелы")
    else:
        if Name == 'Назад':
            bot.send_message(message.chat_id, 'ок', reply_markup=markup)
            bot.register_next_step_handler(message, Ans)
        if len(Name) >=15 :
            bot.send_message(message.chat.id, "Длинновато")
        else:
            bot.send_message(message.chat.id, "Введите описание (опционально)")
            bot.register_next_step_handler(message,partial(discr, Name))
def discr(Name, message):
    Discription = message.text
    if Discription == 'Назад':
        bot.send_message(reply_markup=markup)
        bot.register_next_step_handler(message, Ans)
    Discription = textwrap.fill(Discription, 20)
    if len(Discription) >=200:
        bot.send_message(message.chat.id, "Длинновато")
    else:
        bot.send_message(message.chat.id, "Введите кол-во предмета")
        bot.register_next_step_handler(message, partial(FinalCreate, Name, Discription))
def FinalCreate(Name, Discription,  message):
    try:
        Quantity = int(message.text)
    except ValueError:
        if message.text == 'Назад':
            bot.send_message(message.chat_id,'ок', reply_markup=markup) 
            bot.register_next_step_handler(message, Ans)
        Quantity = 0
        bot.send_message(message.chat.id, "Неправильное значение\nКол-во будет 0")
    if Quantity < 0:
        bot.send_message(message.chat.id, "Неверное значение")
    else:
        bot.send_message(message.chat.id, sql.CreateItem(Name, Discription, Quantity))



#Взятие предмета из шкафа
def TakeItemDetailBot(message):
    Name = message.text
    bot.send_message(message.chat.id, sql.TakeItemDetail(Name), reply_markup=markup)
    if sql.TakeItemDetail(Name) == "Такого предмета нет":
        pass
    else:
        bot.register_next_step_handler(message, partial(TakeItemBot, Name))
def TakeItemBot(Name, message):
    try:
        Quantity = int(message.text)
    except ValueError:
        Quantity = 0
        bot.send_message(message.chat.id, "Неправильное значение\nКол-во будет 0", reply_markup=markup)
    if Quantity < 0:
        bot.send_message(message.chat.id, "Неверное значение", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, sql.TakeItem(Name, Quantity, message.from_user.username), reply_markup=markup)


#Возврат предмета в шкаф 
def ReturnItemNameBot(message):
    Name = message.text
    if message.text == 'Назад':
            bot.send_message(message.chat_id,'ок', reply_markup=markup)      
            bot.register_next_step_handler(message, Ans)
    bot.send_message(message.chat.id, "Введите кол-во предмета, которое хотите вернуть")
    bot.register_next_step_handler(message, partial(ReturnItemBot, Name))
def ReturnItemBot(Name, message):
    try:
        Quantity = int(message.text)
    except ValueError:
        if message.text == 'Назад':
            bot.send_message(message.chat_id,'ок', reply_markup=markup)    
            bot.register_next_step_handler(message, Ans)
        Quantity = 0
        bot.send_message(message.chat.id, "Неправильное значение\nКол-во будет 0")
    if Quantity < 0:
        bot.send_message(message.chat.id, "Неверное значение")
    else:
        sql.ReturnItems(Name, Quantity, message.from_user.username)
        bot.send_message(message.chat.id, "Успешно")


#
def NameOfEditBot(message):
    if message.text == 'Назад':
            bot.send_message(message.chat_id,'ок', reply_markup=markup)
            bot.register_next_step_handler(message, Ans)
    Name = message.text
    bot.send_message(message.chat.id, "Введите новое кол-во")
    bot.register_next_step_handler(message, partial(EditBot, Name))
def EditBot(Name, message):
    if message.text == 'Назад':
            bot.send_message(message.chat_id,'ок', reply_markup=markup)       
            bot.register_next_step_handler(message, Ans)
    Quantity = int(message.text)
    if Quantity < 0:
        bot.send_message(message.chat.id, "Неверное значение")
    else:
        sql.EditQuantity(Name, Quantity)
        bot.send_message(message.chat.id, "Успешно")

#
def DeleteItemBot(message):
    if message.text == 'Назад':
            bot.send_message(message.chat_id,'ок', reply_markup=markup)      
            bot.register_next_step_handler(message, Ans)
    Name = message.text
    bot.send_message(message.chat.id, sql.DeleteItem(Name))
bot.infinity_polling()
