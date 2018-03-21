import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from rq import Queue
from rq.job import Job
from worker import conn
import yaml
from slackclient import SlackClient
from urllib.parse import urlparse



class DiscordScraper:
    def __init__(self, username, password, server, channel):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
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
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'comment')))
        self.latest_parsed = None


    def scrape(self):
        blocks = self.driver.find_elements_by_class_name('comment')
        parsed = []
        author_name = 'NA'
        author_id = 'NA'

        for block in blocks[1:]:
            author_name = block.find_element_by_class_name('user-name').text
            messages = block.find_elements_by_xpath('div')
            for message in messages:
                text = message.find_element_by_class_name('markup').text
                item = {
                    'author_name': author_name,
                    'text' : text
                }
                parsed.append(item)

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
                    for i in range(len(parsed)):
                        if (parsed[i]!=self.latest_parsed[i]):
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
    def __init__(self, username, password, slack_token, message_flow, truncated_words):
        self.scrapers = []
        for channel in message_flow['in']:
            self.scrapers.append(SlackScraper(username=username, password=password, channel=channel))
        
        self.q = Queue(connection=conn)
        self.sc = SlackClient(slack_token)
        self.message_flow = message_flow
        self.words = truncated_words

    def run(self):
        messages = [scraper.scrape() for scraper in self.scrapers]
        messages = [item for sublist in messages for item in sublist]
        for w in self.words:
            messages = [message.replace(w, '') for message in messages]

        for message in messages:
            task = self.q.enqueue_call(func='bot.post_message', args=(message, self.sc, self.message_flow['out']), result_ttl=5000, timeout=3600)



def post_message(message, sc, channel):
    sc.api_call('chat.postMessage', channel=channel,
                        text='{} [{}]: {}'.format(message['author_name'], message['timestamp'], message['text']))


def main():
    print('[*] Booting up...')
    with open('config.yaml') as f:
        config = yaml.load(f)
        username = config['CREDS']['USERNAME']
        password = config['CREDS']['PASSWORD']
        slack_token = config['SLACKAPI']['TOKEN']

    with open('message-flow.yaml') as f:
        config = yaml.load(f)
        flows = config['message_flow']
        words = config['truncated_words']

    transporters = []
    for flow in flows:
        transporters.append(SlackTransporter(username, password, slack_token, flow, words))
    print('[*] Running...')

    while True:
        result = [t.run() for t in transporters]



if __name__=='__main__':
    main()
