import telebot
from functools import partial
from models import SQLconnect
import textwrap


sql = SQLconnect()
bot = telebot.TeleBot('6629791393:AAF9w6GZZmIBK9h7zcfOGmiII65QJkXvLFc', parse_mode='HTML')
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
item8 = telebot.types.KeyboardButton('Изменить описание')
markup.add(item1, item2, item3, item4, item5, item6, item7, item8)

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
    if message.text == "Изменить описание":
        bot.send_message(message.chat.id, "Введите название предмета", reply_markup=retur)
        bot.register_next_step_handler(message, ChangeDescription)



def NameOrTagListBot(message):
    Name = message.text
    if Name == "Назад":
        bot.send_message(message.chat.id, "Ок", reply_markup=markup)
        bot.register_next_step_handler(message, Ans)
    else:
        try:
            if "@" in Name:
                bot.send_message(message.chat.id, sql.ListOfTakenByTag(Name[1::1]), reply_markup=markup)
            elif Name == "Все":
                bot.send_message(message.chat.id, sql.ListOfTaken(), reply_markup=markup)
            else:
                bot.send_message(message.chat.id, sql.ListOfTakenByName(Name), reply_markup=markup)
        except Exception as e:  
            bot.send_message(message.chat.id, "Такого тега или предмета не найдено", reply_markup=markup)

#Создание предмета в шкафу
def NameOfItem(message):
    print('name ok')
    Name = message.text
    if " " in Name:
            bot.send_message(message.chat.id, "Присутствуют пробелы", reply_markup=markup)
    else:
        if Name == 'Назад':
                bot.send_message(message.chat.id, 'ок', reply_markup=markup)
                bot.register_next_step_handler(message, Ans)
        else:
            if len(Name) >=15 :
                bot.send_message(message.chat.id, "Длинновато", reply_markup=markup)
            else:
                bot.send_message(message.chat.id, "Введите описание (опционально)")
                bot.register_next_step_handler(message,partial(discr, Name))
def discr(Name, message):
    print('discr ok')
    Discription = message.text
    if Discription == 'Назад':
        bot.send_message(reply_markup=markup)
        bot.register_next_step_handler(message, Ans)
    else:
        Discription = textwrap.fill(Discription, 20)
        if len(Discription) >=200:
            bot.send_message(message.chat.id, "Длинновато", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Введите кол-во предмета")
            bot.register_next_step_handler(message, partial(FinalCreate, Name, Discription))
def FinalCreate(Name, Discription,  message):
    try:
        Quantity = int(message.text)
        if Quantity < 0:
            bot.send_message(message.chat.id, "Неверное значение", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, sql.CreateItem(Name, Discription, Quantity), reply_markup=markup)
    except ValueError:
        if message.text == 'Назад':
            bot.send_message(message.chat.id,'ок', reply_markup=markup) 
            bot.register_next_step_handler(message, Ans)
        else:
            Quantity = 0
            bot.send_message(message.chat.id, "Неправильное значение\nКол-во будет 0", reply_markup=markup)
    

        
       


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
            bot.send_message(message.chat.id,'ок', reply_markup=markup)      
            bot.register_next_step_handler(message, Ans)
    else:
        bot.send_message(message.chat.id, "Введите кол-во предмета, которое хотите вернуть")
        bot.register_next_step_handler(message, partial(ReturnItemBot, Name))
def ReturnItemBot(Name, message):
    try:
        Quantity = int(message.text)
    except ValueError:
        if message.text == 'Назад':
            bot.send_message(message.chat.id,'ок', reply_markup=markup)    
            bot.register_next_step_handler(message, Ans)
        Quantity = 0
        bot.send_message(message.chat.id, "Неправильное значение\nКол-во будет 0", reply_markup=markup)
    if Quantity < 0:
        bot.send_message(message.chat.id, "Неверное значение", reply_markup=markup)
    else:
        sql.ReturnItems(Name, Quantity, message.from_user.username)
        bot.send_message(message.chat.id, "Успешно", reply_markup=markup)


#Изменение кол-ва предмета в шкафу
def NameOfEditBot(message):
    if message.text == 'Назад':
            bot.send_message(message.chat.id,'ок', reply_markup=markup)
            bot.register_next_step_handler(message, Ans)
    Name = message.text
    bot.send_message(message.chat.id, "Введите новое кол-во")
    bot.register_next_step_handler(message, partial(EditBot, Name))
def EditBot(Name, message):
    if message.text == 'Назад':
            bot.send_message(message.chat.id,'ок', reply_markup=markup)       
            bot.register_next_step_handler(message, Ans)
    Quantity = int(message.text)
    if Quantity < 0:
        bot.send_message(message.chat.id, "Неверное значение", reply_markup=markup)
    else:
        sql.EditQuantity(Name, Quantity)
        bot.send_message(message.chat.id, "Успешно", reply_markup=markup)

#Удаление предмета из шкафа
def DeleteItemBot(message):
    if message.text == 'Назад':
            bot.send_message(message.chat.id,'ок', reply_markup=markup)      
            bot.register_next_step_handler(message, Ans)
    Name = message.text
    bot.send_message(message.chat.id, sql.DeleteItem(Name), reply_markup=markup)

#Изменение описания предмета
def ChangeDescription(message):
    if message.text == 'Назад':
        bot.send_message(message.chat.id,'ок', reply_markup=markup)      
        bot.register_next_step_handler(message, Ans)
    else:
        Name = message.text
        bot.send_message(message.chat.id, "Введите новое описание")
        bot.register_next_step_handler(message, partial(FinalNewDescription, Name))
def FinalNewDescription(Name, message):
    NewDescription = message.text
    sql.ChangeDescription(Name, NewDescription)
    bot.send_message(message.chat.id, "Описание успешно изменено", reply_markup=markup)



bot.infinity_polling()
