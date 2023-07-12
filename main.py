import imaplib
import email
import time
from email.header import decode_header
import re
import os
import json
import pystray
from pystray import MenuItem as item
from PIL import Image
import threading
from plyer import notification


running = True


def checkMail(icon):
    with open("settings/settings.json", "r") as read_file:
        settingsJSON = json.load(read_file)
    while running:
        time.sleep(10)
        mail_pass = f"{settingsJSON[0]['mail_pass']}"
        username = f"{settingsJSON[0]['username']}"
        imap_server = "imap.mail.ru"
        imap = imaplib.IMAP4_SSL(imap_server)
        imap.login(username, mail_pass)

        imap.select("INBOX")

        imap.uid('search', "UNSEEN", "ALL")
        response = imap.uid('search', "UNSEEN", "ALL")
        numbers = response[1][0].decode().split()
        variables = []
        for number in numbers:
            variables.append(number)

        for variable in variables:
            res, msg = imap.fetch(f'{variable}'.encode("utf-8"), '(RFC822)')
            res, msg = imap.uid('fetch', f'{variable}'.encode("utf-8"), '(RFC822)')

            msg = email.message_from_bytes(msg[0][1])

            letter_date = email.utils.parsedate_tz(msg["Date"])
            letter_id = msg["Message-ID"]
            letter_from = msg["Return-path"]
            payload = msg.get_payload()

            subject = decode_header(msg["Subject"])[0][0].encode().strip()
            subject_without_b = re.sub(r"b['\"](.*?)['\"]", r"\1", str(subject))

            notification.notify(
                title="Вам пришло уведомление от MailRu",
                message=f"У вас непрочитанное сообщение заголовок {subject_without_b}",
                timeout=10,
                app_icon="icon.ico"
            )

        icon.update_menu()


def on_quit_clicked(icon, item):
    icon.stop()
    global running
    running = False


def settingsEdit():
    mail_pass_input = input("Введите пароль почты для внешних подключений: ")
    username_input = input("Введите почту которую будем читать (пример qwerty@mail.ru): ")
    settings = [
        {
            "mail_pass": f"{mail_pass_input}",
            "username": f"{username_input}"
        }
    ]
    with open("settings/settings.json", "w") as write_file:
        json.dump(settings, write_file, indent=4)
    print("Выключите программу и включите")


def main():

    image = Image.open("icon.png")

    menu = (
        item("Настройки", settingsEdit),
        item("Выход", on_quit_clicked)
    )
    icon = pystray.Icon("name", image, "MailRu", menu)
    thread = threading.Thread(target=checkMail, args=(icon,))
    thread.start()

    icon.run()


def settings():
    if not os.path.exists("settings"):
        os.makedirs("settings")
        if os.path.exists("settings.json"):
            with open("settings/settings.json", "r") as read_file:
                settingsJSON = json.load(read_file)
            main()
        else:
            mail_pass_input = input("Введите пароль почты для внешних подключений: ")
            username_input = input("Введите почту которую будем читать (пример qwerty@mail.ru): ")
            settings = [
                {
                    "mail_pass": f"{mail_pass_input}",
                    "username": f"{username_input}"
                }
            ]
            with open("settings/settings.json", "w") as write_file:
                json.dump(settings, write_file, indent=4)
            with open("settings/settings.json", "r") as read_file:
                settingsJSON = json.load(read_file)
            main()
    else:
        with open("settings/settings.json", "r") as read_file:
            settingsJSON = json.load(read_file)
        main()


if __name__ == "__main__":
    settings()