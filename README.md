# discord-transporter

Transporting Discord messages from one server to another. 

## Installation

__DISCLAIMER.__ The following instructions are for a _Ubuntu 16.04 LTS_ machine. The program can run on other distros, but you may have to make slight modifications to the installation procedure to make that happen. Personally I would recommend going with _Ubuntu 16.04 LTS_, as that is the OS the program was built and tested upon.

__STEP 1.__ Execute the `setup.sh` script. All this script does is install the required software packages and download the _chromedriver_ and _geckodriver_ executables.


__STEP 2.__ _Only if the machine is a server_. Execute the `vnc.sh` script to install _tightvnc_ and _xfce_ desktop environment.


__STEP 3.__ Open Discord using a browser and login manually to the `INSERVER` Discord server account, i.e. the Discord server from where the messages need to be scraped. You need to do this only once from the machine where this program will be run, to whitelist the machine's IP in Discord. Use VNC to do this step if you're installing the program on a VPS.


## Configuring Credentials and Message Flow

You need to edit and configure two _YAML_ files, one containing login credentials, another containing the message flow. Before that, you'll also need to do some groundwork as described below.


### Understanding Discord URLs  
From the URL of any Discord channel, we can get the server ID and channel ID. The format of the URL is,

    https://discordapp.com/channels/SERVER_ID/CHANNEL_ID

For example, we can take a look at the "introduction" channel of the "r/creativethoughts" Discord server. The URL of the channel is 

    https://discordapp.com/channels/293286532851433473/428819612239659010

So, for this channel, 
```
SERVER_ID=293286532851433473
CHANNEL_ID=428819612239659010
```

### Creating Webhooks

The program uses webhooks to post messages to your discord channels. For every discord channel you want to post message to, you have to create a webhook for that. Check out [this article](https://support.discordapp.com/hc/en-us/articles/228383668-Intro-to-Webhooks) for understaning how to create a webhook for your channel.

The program will be needing the URLs of the webhooks, so note them down while you're creating them.

### Configuring the Credentials YAML

The format of the file should be like the following.

```yaml
INSERVER:
  USERNAME: DISCORD_USERNAME
  PASSWORD: DISCORD_PASSWORD
  ID: SERVER_ID
```

Here the credentials and server ID should be of the `INSERVER`, i.e. the Discord server from where the messages need to be scraped. 

### Configuring the Message Flow YAML

```yaml
message_flow:
  - in: [CHANNEL1_ID, CHANNEL2_ID, CHANNEL3_ID]
    out: WEBHOOK1_URL
  - in: [CHANNEL4_ID]
    out: WEBHOOK2_URL

truncated_words:
  - secretive phrase
  - something offensive
```

According the above sample YAML, the program will copy messages from channels with IDs `CHANNEL1_ID`, `CHANNEL2_ID` and `CHANNEL3_ID`, and then paste them into the channel with webhook URL `WEBHOOK1_URL`. It will also copy messages from `CHANNEL4_ID` channel and paste them into channel with `WEBHOOK2_URL` webhook.

While transporting the messages, it will censor and omit the phrases "_secretive phrase_" and "_something offensive_".

## Running

```console
$ python3 bot.py -h
usage: bot.py [-h] [-c CREDS] [-f FLOW] [-b {firefox,chrome}]

optional arguments:
  -h, --help            show this help message and exit
  -c CREDS, --creds CREDS
                        Credentials YAML file. Check README for details.
  -f FLOW, --flow FLOW  Message Flow YAML file. Check README for details.
  -b {firefox,chrome}, --browser {firefox,chrome}
                        Whether to use Firefox or Chrome for scraping.
```

So considering the credentials and message flow YAML files are saved as `creds.yaml` and `message-flow.yaml` respectively, and that we want to use firefox as the scraper, the command we'd use to run the program is the following.

```console
$ python3 bot.py -c creds.yaml -f message-flow.yaml -b firefox
```
