from time import sleep

import openai
import telebot
import os
from dotenv import load_dotenv
from datetime import datetime

# Define OpenAI and telegram API keys
load_dotenv()
openai.api_key = os.environ.get("CHATGPT_API_KEY")
telegram_token = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(telegram_token)


@bot.message_handler(commands=['start'])
def main(message):
    msg = bot.send_message(message.chat.id, "Спроси что-нибудь у меня")
    bot.register_next_step_handler(msg, chatgpt)


@bot.message_handler(commands=['help'])
def send_help(message):
    msg = bot.send_message(message.chat.id, "/reset - обнулить диалог")
    bot.register_next_step_handler(msg, chatgpt)


messages = [
    {"role": "system", "content": "You’re a kind helpful assistant"}]


@bot.message_handler(commands=['reset'])
def reset(message):
    msg = bot.send_message(message.chat.id, "***Диалог с ChatGPT обнулён***")
    global messages
    messages = [{"role": "system", "content": "You’re a kind helpful assistant"}]
    bot.register_next_step_handler(msg, chatgpt)


@bot.message_handler(content_types=['text'])
def chatgpt(message):
    # Generate a response
    messages.append({"role": "user", "content": message.text})

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.7, )
        response = completion.choices[0].message.content
        try:
            bot.send_message(message.chat.id, response)
        except ConnectionError:
            print("***Сбой в работе интернет соединения.\n"
                  "Повторяю запрос через ~5 секунд.***")
            sleep(5)
            bot.send_message(message.chat.id, response)
        messages.append(
            {"role": "assistant", "content": response})
    except openai.error.InvalidRequestError as e:
        bot.send_message(message.chat.id, f"***{e}\nКонтекст модели переполнен. Обнулите его с помощью команды "
                                          f"\n/reset\n***")
    except openai.error.APIConnectionError as e:
        bot.send_message(message.chat.id, "***Сервер openai перегружен или не доступен в данный момент.\n"
                                          "Повторите свой запрос заново.***")


    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Successes at", current_time)


bot.infinity_polling()
