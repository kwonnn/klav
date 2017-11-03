import discord
import json
import os
import requests
import sys
import util


class CupcakeBot(discord.Client):
    def __init__(self):
        super().__init__()
        self.usernames = {}
        self.bin = 'https://api.myjson.com/bins/{}'.format(os.environ['BIN_ID'])
        self.prefix = '.'

    async def on_ready(self):
        print('Logged in:', client.user.name)
        self.read_configs()

    async def on_message(self, message):
        # Ignore own messages
        if message.author.id == client.user.id: return

        # Message should start with a prefix
        if message.content[0] != self.prefix: return

        await util.command_help(self, message)
        await util.command_set_username(self, message)
        await util.command_show_username(self, message)
        await util.command_check_compat(self, message)
        await util.command_unset_username(self, message)

    def read_configs(self):
        r = requests.get(self.bin, verify=False)
        if r.status_code != 200:
            report = 'error: read_configs: could not GET {}'.format(self.bin)
            print(report, file=sys.stderr)
            return
        self.usernames = json.loads(r.text)


client = CupcakeBot()

client.run(os.environ['CUPCAKE_BOT_TOKEN'])