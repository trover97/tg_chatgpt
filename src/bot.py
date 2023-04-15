import openai
import telebot
import os
from dotenv import load_dotenv

# Define OpenAI and telegram API keys
load_dotenv()
openai.api_key = os.environ.get("CHATGPT_API_KEY")
telegram_token = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(telegram_token)


@bot.message_handler(commands=['start'])
def main(message):
    msg = bot.send_message(message.chat.id, "Спроси что-нибудь у меня")
    bot.register_next_step_handler(msg, chatgpt)


@bot.message_handler(content_types=['text'])
def chatgpt(message):
    # Generate a response
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message.text}],
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7, )

    response = completion.choices[0].message.content
    bot.send_message(message.chat.id, response)


bot.polling(none_stop=True)
