import telebot
import time
import config
from bs4 import BeautifulSoup
import requests
import re

id_channel = '@vc1234567889'
bot = telebot.TeleBot(config.TOKEN)  # токен импортируется из специального файла


@bot.message_handler(content_types=['text'])
def commands(message):
    # Телеграм-бот в бесконечном цикле выкладывает ссылку на пост в телеграм-канал,
    # если id поста отличается от id предыдущего поста.
    if message.text == 'Start':
        back_post_id = None
        while True:
            time.sleep(10)  # паузы между запросами по 10 сек
            post_text = parser(back_post_id)
            back_post_id = post_text[1]

            if post_text[0] is not None:
                bot.send_message(id_channel, post_text[0])
                time.sleep(300)  # бот проверяет наличие свежего поста на сайте vc.ru раз в 5 минут, но только если
                # успешно выслал на канал свежий пост
    else:
        bot.send_message(message.from_user.id, 'Human, I understand only "Start" command. Please write it')


def parser(back_post_id):
    # Парсер, достает из кода страницы id поста и ссылку на пост.
    URL = 'https://vc.ru/new'
    # Намеренно использован https://vc.ru/new, а не https://vc.ru, новости с первого адреса проще парсить.

    page = requests.get(URL)
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, 'lxml')
    else:
        return None, back_post_id

    post = soup.find('div', class_=re.compile('l-mb'))
    post_id = post['data-content-id']

    if post_id != back_post_id:
        url = post.find('a', class_='content-link', href=True)['href']
        return f'{url}', post_id
    else:
        return None, post_id


bot.polling()
