import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from rq import Queue
from rq.job import Job
from worker import conn
import yaml
import discord
import asyncio
from urllib.parse import urlparse
import re
import requests
import json



class DiscordScraper:
    def __init__(self, username, password, server, channel):
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.get('https://www.discordapp.com/login')
        time.sleep(2)

        try:
            email = self.driver.find_element_by_id('register-email')
            email.send_keys(username)
            passfield = self.driver.find_element_by_id('register-password')
            passfield.send_keys(password)
            passfield.submit()
            assert self.driver.current_url in ['https://discordapp.com/app', 'https://discordapp.com/channels/@me']
        except:
            print('[*] Failed login attempt. Relying on user to do it.')
            pass

        url = 'https://discordapp.com/channels/{}/{}'.format(server, channel)
        self.driver.get(url)
        wait = WebDriverWait(self.driver, 100)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'guilds-wrapper')))
        self.latest_parsed = None


    def scrape(self):
        blocks = self.driver.find_elements_by_class_name('comment')
        parsed = []
        author_name = 'NA'
        author_id = 'NA'

        for block in blocks:
            try:
                author_name = block.find_element_by_class_name('user-name').text
                messages = block.find_elements_by_xpath('div')
                for message in messages:
                    text = message.find_element_by_class_name('markup').text
                    item = {
                        'author_name': author_name,
                        'text' : text
                    }
                    parsed.append(item)
            except:
                pass

        latest_parsed_temp = [x for x in parsed]
        ret = []

        try:
            while True:
                if (self.latest_parsed == None):
                    ret = parsed[::-1]
                    break
                elif (parsed[-1]!=self.latest_parsed[-1]):
                    ret.append(parsed.pop())
                else:
                    breakdown = False
                    length = min(len(parsed), len(latest_parsed))
                    for i in range(length):
                        if (parsed[-i]!=self.latest_parsed[-i]):
                            breakdown = True
                            break
                    if (breakdown):
                        ret.append(parsed.pop())
                    else:
                        break
        except :
            pass

        self.latest_parsed = latest_parsed_temp
        return ret[::-1]



class DiscordTransporter:
    def __init__(self, config, message_flow, truncated_words):
        self.scrapers = []
        for channel in message_flow['in']:
            self.scrapers.append(DiscordScraper(username=config['INSERVER']['USERNAME'], password=config['INSERVER']['PASSWORD'],
                                 server=config['INSERVER']['ID'], channel=channel))
        
        self.q = Queue(connection=conn)
        self.dc = discord.Client()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.dc.login(config['OUTSERVER']['TOKEN']))
        self.message_flow = message_flow
        self.words = truncated_words

    @staticmethod
    def strip(message, word):
        message['text'] = re.sub(r'\@(\w+)', '', message['text'].replace(word, ''))
        return message

    def run(self):
        messages = [scraper.scrape() for scraper in self.scrapers]
        messages = [item for sublist in messages for item in sublist]
        for w in self.words:
            messages = [self.strip(message, w) for message in messages]

        for message in messages:
            post_message(message, self.message_flow['out'][0], self.message_flow['out'][1])


def post_message(message, WHID, WHToken):
    URL = 'https://discordapp.com/api/webhooks/{}/{}'.format(WHID, WHToken)
    r = requests.post(baseURL, data={'content': message})


def main():
    print('[*] Booting up...')
    with open('config.yaml') as f:
        config = yaml.load(f)

    with open('message-flow.yaml') as f:
        flow_yaml = yaml.load(f)
        flows = flow_yaml['message_flow']
        words = flow_yaml['truncated_words']

    transporters = []
    for flow in flows:
        transporters.append(DiscordTransporter(config, flow, words))
    print('[*] Running...')

    while True:
        result = [t.run() for t in transporters]



if __name__=='__main__':
    main()
