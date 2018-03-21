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



class DiscordScraper:
    def __init__(self, username, password, server, channel):
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.get('https://www.discordapp.com/login')
        time.sleep(2)

        email = self.driver.find_element_by_id('register-email')
        email.send_keys(username)
        self.driver.find_element_by_id('register-password').send_keys(password)
        email.submit()
        time.sleep(2)
        self.driver.get('https://discordapp.com/channels/{}/{}'.format(server, channel))

        wait = WebDriverWait(self.driver, 100)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'guilds-wrapper')))
        self.latest_parsed = None


    def scrape(self):
        blocks = self.driver.find_elements_by_class_name('comment')
        parsed = []
        author_name = 'NA'
        author_id = 'NA'
        print(len(blocks))

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
        print(len(parsed))

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
        print(len(ret))

        self.latest_parsed = latest_parsed_temp
        return ret[::-1]



class DiscordTransporter:
    def __init__(self, username, password, inserver, message_flow, truncated_words):
        self.scrapers = []
        for channel in message_flow['in']:
            self.scrapers.append(DiscordScraper(username=username, password=password, server=inserver, channel=channel))
        
        self.q = Queue(connection=conn)
        self.dc = discord.Client()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.dc.login(username, password))
        self.message_flow = message_flow
        self.words = truncated_words

    def run(self):
        messages = [scraper.scrape() for scraper in self.scrapers]
        messages = [item for sublist in messages for item in sublist]
        for w in self.words:
            messages = [message.replace(w, '') for message in messages]

        for message in messages:
            print('doing')
            task = self.q.enqueue_call(func='bot.post_message', args=(message, self.dc, self.message_flow['out']), result_ttl=5000, timeout=3600)
            print('done')


def post_message(message, client, channel):
    loop = asyncio.get_event_loop()
    channel = discord.Object(id=channel)
    loop.run_until_complete(client.send_message(channel, '{}: {}'.format(message['author_name'], message['text'])))


def main():
    print('[*] Booting up...')
    with open('config.yaml') as f:
        config = yaml.load(f)
        username = config['CREDS']['USERNAME']
        password = config['CREDS']['PASSWORD']
        inserver = config['INSERVER']

    with open('message-flow.yaml') as f:
        config = yaml.load(f)
        flows = config['message_flow']
        words = config['truncated_words']

    transporters = []
    for flow in flows:
        transporters.append(DiscordTransporter(username, password, inserver, flow, words))
    print('[*] Running...')

    while True:
        result = [t.run() for t in transporters]



if __name__=='__main__':
    main()
