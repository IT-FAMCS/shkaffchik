## Install Windows
```
git clone https://github.com/essaon/tele.git
python -m venv venv ^
venv/Scripts/activate ^
python -m pip install -r requirements.txt
```
## Install Linux
```
git clone https://github.com/essaon/tele.git && sudo python -m venv venv && venv/bin/activate && python -m pip install -r requirements.txt
```
## Initialise
Put yours bots token in field named TOKEN in main.py 
```
bot = telebot.TeleBot('TOKEN', parse_mode=None)
```
## Run
cd to main.py derictory and run
```
python main.py
```
