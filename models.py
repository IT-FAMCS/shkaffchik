import sqlite3
from tabulate import tabulate
import telebot

class SQLconnect():
    def __init__(self):
        self.connect = sqlite3.connect('db.sqlite', check_same_thread=False)
        self.cursor = self.connect.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, description TEXT, quantity INTEGER)')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS taken (id TEXT)')
        
    def AddUser(self, id):
        if self.cursor.execute("SELECT id FROM taken WHERE id =?", (id,)).fetchone() != []:
            pass           
        else:
            self.cursor.execute("INSERT INTO taken (id) VALUES (?)", (id,))
            self.connect.commit()
    def CreateButtons(self,):
        self.cursor.execute("SELECT name FROM items")
        names = [row[0] for row in self.cursor.fetchall()]
        markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
        for name in names:
            item = telebot.types.KeyboardButton(name)
            markup.add(item)

        return markup
    def ListOfItems(self,):
        self.cursor.execute("SELECT name, description, quantity FROM items")
        answer = f"<pre>{tabulate(self.cursor.fetchall(), headers=['NAME', 'DISCR', 'QUANT'], tablefmt='orgtbl', colalign=('center',))}</pre>"
        return answer

    def ListOfTaken(self,):
        result = ''
        self.cursor.execute("PRAGMA table_info(taken)")
        columns = [column[1] for column in self.cursor.fetchall()]
        self.cursor.execute("SELECT * FROM taken")
        rows = self.cursor.fetchall()
        for i in range(1, len(columns)):
            non_zero_entries = [f"@{row[0]} - {row[i]}" for row in rows if row[i] != 0]
            if non_zero_entries:
                result += f"{columns[i]} | "
                if len(non_zero_entries) > 2:
                    print(f"{non_zero_entries[0]}, {non_zero_entries[1]} и еще {len(non_zero_entries) - 2}...\n")
                else:
                    result += ", ".join(non_zero_entries)
                    result += "\n"
        if result:
            return result
        else:
            return "Все предметы на месте!"
        
    def ListOfTakenByName(self, name):
        try:
            self.cursor.execute(f"SELECT id, {name.upper()} FROM taken")
            data = self.cursor.fetchall()
            answer = f"<pre>{tabulate(data, headers = ['TAGS', f'{name.upper()}'],  tablefmt='orgtbl', colalign=('center',))}</pre>"
            return answer
        except sqlite3.Error as e:
            print(f'Error: {e}')
            return "Нету @, либо такого предмета нет"

    def ListOfTakenByTag(self, name):
        self.cursor.execute("SELECT * FROM taken WHERE id = ?", (name,))
        data = self.cursor.fetchall()
        self.cursor.execute("SELECT name FROM items")
        temp = []
        temp1 = []
        for row in self.cursor.fetchall():
            row = str(row)[2:-3:1]
            temp.append(row)
        for i in range(len(temp)):
            temp1.append([temp[i],data[0][i+1]])
        data = ['Items', data[0][0]]
        answer = f"<pre>{tabulate(temp1, headers=data, tablefmt='orgtbl', colalign=('center',))}</pre>"
        return answer

    def EditQuantity(self, name, quantity):
        self.cursor.execute("UPDATE items SET quantity = ? WHERE name = ?", (quantity, name.upper()))
        self.connect.commit()

    def DeleteItem(self, name):
        self.cursor.execute("DELETE FROM items WHERE name =?", (name.upper(),))
        self.cursor.execute(f"ALTER TABLE taken DROP COLUMN {name.upper()}")
        self.connect.commit()
        return "Успешно"
    
    def CreateItem(self, name, descr, quantity):
        if self.cursor.execute("SELECT name FROM items WHERE name = ?", (name.upper(),)).fetchall():
                answer = "Такой предмет уже есть"
        else:
                self.cursor.execute("INSERT INTO items (name, description, quantity) VALUES (?, ?, ?);", (name.upper(), descr, quantity))
                self.connect.commit()
                self.cursor.execute(f"ALTER TABLE taken ADD COLUMN {name.upper()} INTEGER NOT NULL DEFAULT(0)")
                self.connect.commit()
                answer = "Успешно"
        return answer

    def TakeItemDetail(self, name):
        self.cursor.execute("SELECT quantity FROM items WHERE name = ?", (name.upper(),))
        item = self.cursor.fetchone()
        if item:
            answer = f"Кол-во: {item[0]}\nСколько хотите взять?"
        else:
            answer = "Такого предмета нет"
        return answer

    def TakeItem(self, name, quantity, id):
        data = self.cursor.execute("SELECT quantity FROM items WHERE name=?", (name.upper(),)).fetchone()
        if int(quantity) > data[0]:
            return "Попытка взять больше, чем имеется"
        
        self.cursor.execute("UPDATE items SET quantity =? WHERE name=?", (data[0] - int(quantity), name.upper()))
        self.connect.commit()

        old = self.cursor.execute(f"SELECT {name.upper()} FROM taken WHERE id = ?", (id,)).fetchone()[0]
        self.cursor.execute("UPDATE taken SET {} = ? WHERE id = ?".format(name.upper(),), (old + quantity, id))
        self.connect.commit()
        return "Успешно"
    
    def ReturnItemDetail(self, id):
        answer = ""
        for i in self.cursor.execute("SELECT name FROM items").fetchall():
            answer += f"{i[0]} - {str(self.cursor.execute(f"SELECT {i[0]} FROM taken WHERE id = ?", (id,)).fetchall())[2:-3:1]}\n"
        return answer

    def ReturnItems(self, name, quantity, id):

            data = self.cursor.execute(f"SELECT {name.upper()} FROM taken WHERE id = ?", (id,)).fetchone()
            if (int(quantity) > data[0]):
                    pass
            else:
                self.cursor.execute(f"UPDATE taken SET {name.upper()} = ? WHERE id = ?", (data[0] - int(quantity), id))
                self.connect.commit()
                
                data = self.cursor.execute("SELECT quantity FROM items WHERE name = ?", (name.upper(),)).fetchone()
                self.cursor.execute("UPDATE items SET quantity =? WHERE name =?", (data[0] + int(quantity), name.upper()))
                self.connect.commit()

        
    