import tkinter as tk
from client import Client
import argparse


def send_answer(client, categories):
    # send
    message = ""
    for c in categories:
        message += c.get() + ';'
    client.send(message)


def show_window(client):
    window = tk.Tk()
    window.title("Państwa-miasta")

    cat = []
    for i in range(len(client.categories)):
        cat.append(tk.StringVar())

    informationFrame = tk.Frame(master=window)
    informationFrame.pack(padx=10, pady=10)

    letterFrame = tk.Frame(master=informationFrame)
    letterFrame.grid(row=0, padx=40)

    # to display letter letter.set(value)
    letter = tk.StringVar()

    letterLabel = tk.Label(letterFrame, text='Litera').grid(row=0)
    letterEntry = tk.Entry(letterFrame, state='disabled', textvariable=letter).grid(row=0, column=1)

    timeFrame = tk.Frame(master=informationFrame)
    timeFrame.grid(row=0, column=1, padx=40)

    # to display time timeText.set(value)
    timeText = tk.StringVar()

    timeLabel = tk.Label(timeFrame, text="Pozostały czas: ").grid(row=0)
    timeEntry = tk.Entry(timeFrame, state='disabled', textvariable=timeText).grid(row=0, column=1)

    categoriesFrame = tk.Frame(master=window)
    categoriesFrame.pack(padx=10, pady=10)

    category1Label = tk.Label(categoriesFrame, text=client.categories[0]).grid(row=1, column=0)
    category2Label = tk.Label(categoriesFrame, text=client.categories[1]).grid(row=1, column=1)
    category3Label = tk.Label(categoriesFrame, text=client.categories[2]).grid(row=1, column=2)
    category4Label = tk.Label(categoriesFrame, text=client.categories[3]).grid(row=1, column=3)
    category5Label = tk.Label(categoriesFrame, text=client.categories[4]).grid(row=1, column=4)

    category1Entry = tk.Entry(categoriesFrame, textvariable=cat[0]).grid(row=2)
    category2Entry = tk.Entry(categoriesFrame, textvariable=cat[1]).grid(row=2, column=1)
    category3Entry = tk.Entry(categoriesFrame, textvariable=cat[2]).grid(row=2, column=2)
    category4Entry = tk.Entry(categoriesFrame, textvariable=cat[3]).grid(row=2, column=3)
    category5Entry = tk.Entry(categoriesFrame, textvariable=cat[4]).grid(row=2, column=4)

    sendButton = tk.Button(window, text='Wyślij', command=lambda
        catToSend=cat : send_answer(client, catToSend)).pack(padx=10, pady=10)

    scoreInGameFrame = tk.Frame(master=window)
    scoreInGameFrame.pack(padx=10, pady=10)

    # to display score score.set(value)
    score = tk.StringVar()

    scoreInGameLabel = tk.Label(scoreInGameFrame, text='Wynik w grze').grid(row=0)
    scoreInGameEntry = tk.Entry(scoreInGameFrame, state='disabled', textvariable=score).grid(row=0, column=1)

    window.mainloop()


def update_window():
    window.mainloop()

    #while True:
    #    window.update_idletasks()
    #    window.update()


#window = tk.Tk()
#window.title("Państwa-miasta")

parser = argparse.ArgumentParser()
parser.add_argument("ip_add", help="Server's ip address")
parser.add_argument("port_number", help="Server's port number")
args = parser.parse_args()

HOST = args.ip_add
PORT = int(args.port_number)

client = Client(HOST, PORT)
show_window(client)
