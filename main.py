import time
import schedule
import telebot
from selenium import webdriver
from telebot import types
import os

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("window-size=1920,1080")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")



bot = telebot.TeleBot("1296277300:AAEzQ8XGMCInvrbqkZCu0B1EIqw0yIwNbjQ")


def get_new_ads(search, message):


    driver = webdriver.Chrome(executable_path='/usr/lib/chromium-browser/chromedriver', options=chrome_options)
    #driver = webdriver.Chrome(executable_path='chromedriver.exe', options=chrome_options)
    url = 'http://www.avito.ru/moskva?q='+search
    try:
        driver.get(url)
        ads = "Page title was '{}'".format(driver.title)
        print(ads)
        ads = driver.find_elements_by_css_selector('div[class="iva-item-content-UnQQ4"]')[:1]

        ads_list = []
        for ad in ads:
            title = ad.find_element_by_css_selector('div[class = "iva-item-titleStep-_CxvN"]').find_element_by_css_selector('a').get_attribute('title')
            href = ad.find_element_by_css_selector('div[class = "iva-item-titleStep-_CxvN"]').find_element_by_css_selector('a').get_attribute('href')
            price = ad.find_element_by_css_selector('div[class = "iva-item-priceStep-QN8Kl"]').find_element_by_css_selector('meta[itemprop="price"]').get_attribute('content')
            ads_list.append({'title':title,'href':href,'price':price})

    finally:
        driver.close()
        driver.quit()
    ads = str(ads_list)[2:-2].replace('}, {', '\n\n').replace('}', '').replace('{','').replace("'title':", '\nНазвание: ').replace("'href':", '\nСсылка: ').replace("'price':", '\nЦена: ')
    # time.sleep(100)
    send_new_ads(message, ads)

def url(message):
    markup = types.InlineKeyboardMarkup()
    btn_my_site= types.InlineKeyboardButton(text='Наш сайт', url='https://google.ru')
    markup.add(btn_my_site)
    bot.send_message(message.chat.id, "Нажми на кнопку и перейди на наш сайт.", reply_markup = markup)
    send_welcome(message)

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Получить объявления', 'Перейти на сайт') #Имена кнопок
    msg = bot.send_message(message.chat.id, 'Avito Bot 1.0', reply_markup=markup)
    bot.register_next_step_handler(msg, process_step)


def process_step(message):
    chat_id = message.chat.id
    if message.text=='Получить объявления':
        msg = bot.send_message(chat_id, "Введите запрос")
        bot.register_next_step_handler(msg, get_ads)
    elif message.text=='Перейти на сайт':
        url(message)

def get_ads(message):
    bot.send_message(message.chat.id,'Подождите, идет загрузка объявлений')
    schedule.every(5).minutes.do(get_new_ads, search = message.text, message = message)
    

def send_new_ads(message, ads):
    if len(ads) > 4096:
        for x in range(0, len(ads), 4096):
           bot.send_message(message.chat.id, ads[x:x+4096])
    else:
        bot.send_message(message.chat.id, ads)

    send_welcome(message)
    
bot.polling(none_stop=True)

