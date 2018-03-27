# discord-transporter

Transporting Discord messages from one server to another. 

## Installation

On a Ubuntu 16.04 LTS machine.

0. Configure `config.yaml` and `message-flow.yaml` correctly.

1. Execute the _setup.sh_ script as following.
    
```console
$ ./setup.sh
```

2. (If it is a VPS) Execute the following script to install _tightvnc_.

```console
$ ./vnc.sh
```

3. Open Discord and login manually to the INPUT server account once. Use VNC if it is a VPS.

## Running

```console
$ python3 bot.py
```
