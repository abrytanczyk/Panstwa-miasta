import tkinter as tk
from client import Client
import argparse
import select


ROOM_NUMBER = -1
letter = ""
game_started = False


def send_answer(client, categories, scoreText):
    message = ""
    for c in categories:
        message += c.get() + ';'
    client.send(message)
    get_score(client, scoreText)


def set_room(nr, window):
    global ROOM_NUMBER
    ROOM_NUMBER = nr
    window.destroy()


def get_score(client, scoreText):
    data_as_bytes = client.s.recv(1024)
    data = data_as_bytes.decode()
    scoreText.set(data)


def startGame(client, letterText):
    global game_started
    game_started = True
    msg = str(ROOM_NUMBER) + ";Start Game"
    client.s.send(str.encode(msg))
    letter_as_bytes = client.s.recv(1024)
    global letter
    letter = letter_as_bytes.decode()
    letterText.set(letter)
    time_refresher()


def check_letter():
    global client
    global letter
    global game_started
    global window
    global letterText
    global startButton
    if not game_started:
        to_read,to_write,in_error = select.select([client.s],[],[],0)
        for s in to_read:
            letter_as_bytes = s.recv(1024)
            letter = letter_as_bytes.decode()
            letterText.set(letter)
            game_started = True
            startButton.config(state=tk.DISABLED)
            time_refresher()
        window.after(1000, check_letter)


def show_welcome_window():
    welcomeWindow = tk.Tk()
    welcomeWindow.title("Państwa-miasta - Wybierz pokój")

    room1Button = tk.Button(welcomeWindow,text='Pokój 1',command=lambda number=0:set_room(number, welcomeWindow)).pack(padx=10,pady=10)
    room2Button = tk.Button(welcomeWindow,text='Pokój 2',command=lambda number=1:set_room(number, welcomeWindow)).pack(padx=10,pady=10)
    room3Button = tk.Button(welcomeWindow,text='Pokój 3',command=lambda number=2:set_room(number, welcomeWindow)).pack(padx=10,pady=10)
    room4Button = tk.Button(welcomeWindow,text='Pokój 4',command=lambda number=3:set_room(number, welcomeWindow)).pack(padx=10,pady=10)
    room5Button = tk.Button(welcomeWindow,text='Pokój 5',command=lambda number=4:set_room(number, welcomeWindow)).pack(padx=10,pady=10)

    welcomeWindow.mainloop()


def show_window(client):
    global timeText
    global window
    global game_started
    global cat
    global score
    global timeNow
    global letterText
    global startButton
    window = tk.Tk()
    window.title("Państwa-miasta")

    cat = []
    for i in range(len(client.categories)):
        cat.append(tk.StringVar())

    informationFrame = tk.Frame(master=window)
    informationFrame.pack(padx=10,pady=10)

    letterFrame = tk.Frame(master=informationFrame)
    letterFrame.grid(row=0,padx=40)

    # to display letter letter.set(value)
    letterText = tk.StringVar()

    letterLabel = tk.Label(letterFrame,text='Litera').grid(row=0)
    letterEntry = tk.Entry(letterFrame,state='disabled',textvariable=letterText).grid(row=0,column=1)

    timeFrame = tk.Frame(master=informationFrame)
    timeFrame.grid(row=0,column=1,padx=40)

    # to display time timeText.set(value)
    timeText = tk.StringVar()
    
    timeLabel = tk.Label(timeFrame,text="Pozostały czas: ").grid(row=0)
    timeEntry = tk.Entry(timeFrame,state='disabled',textvariable=timeText).grid(row=0,column=1)

    categoriesFrame = tk.Frame(master=window)
    categoriesFrame.pack(padx=10,pady=10)

    category1Label = tk.Label(categoriesFrame,text=client.categories[0]).grid(row=1,column=0)
    category2Label = tk.Label(categoriesFrame,text=client.categories[1]).grid(row=1,column=1)
    category3Label = tk.Label(categoriesFrame,text=client.categories[2]).grid(row=1,column=2)
    category4Label = tk.Label(categoriesFrame,text=client.categories[3]).grid(row=1,column=3)
    category5Label = tk.Label(categoriesFrame,text=client.categories[4]).grid(row=1,column=4)

    category1Entry = tk.Entry(categoriesFrame,textvariable=cat[0]).grid(row=2)
    category2Entry = tk.Entry(categoriesFrame,textvariable=cat[1]).grid(row=2,column=1)
    category3Entry = tk.Entry(categoriesFrame,textvariable=cat[2]).grid(row=2,column=2)
    category4Entry = tk.Entry(categoriesFrame,textvariable=cat[3]).grid(row=2,column=3)
    category5Entry = tk.Entry(categoriesFrame,textvariable=cat[4]).grid(row=2,column=4)

    startButton = tk.Button(window,text='Rozpocznij',command=lambda:[startGame(client, letterText), startButton.config(state=tk.DISABLED)])
    startButton.pack(padx=10,pady=10)

    scoreInGameFrame = tk.Frame(master=window)
    scoreInGameFrame.pack(padx=10,pady=10)

    # to display score score.set(value)
    score = tk.StringVar()

    scoreInGameLabel = tk.Label(scoreInGameFrame,text='Wynik w grze').grid(row=0)
    scoreInGameEntry = tk.Entry(scoreInGameFrame,state='disabled',textvariable=score).grid(row=0,column=1)
    
    
    timeNow = 60
    timeText.set(str(timeNow))

    window.after(1000, check_letter)
    window.mainloop()


def time_refresher():
    global timeNow
    global timeText
    global game_started
    global window
    global client 
    global cat
    global score
    if game_started:
        if timeNow > 1:
            timeNow = client.get_time()
            timeText.set(str(timeNow))
            window.after(1000, time_refresher) # every second...
        else:
            timeText.set(str(0))
            send_answer(client, cat, score)
            game_started = False


parser = argparse.ArgumentParser()
parser.add_argument("ip_add",help="Server's ip address")
parser.add_argument("port_number",help="Server's port number")
args = parser.parse_args()

HOST = args.ip_add
PORT = int(args.port_number)

show_welcome_window()

if ROOM_NUMBER != -1:
    client = Client(HOST, PORT, ROOM_NUMBER)
    show_window(client)
    client.disconnect()
