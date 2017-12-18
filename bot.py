import json
# import rethinkdb as r
import os

from discord.ext.commands import AutoShardedBot

with open('config.json') as f:
    config = json.load(f)

bot = AutoShardedBot(command_prefix=config.get('prefixes'))
bot.invites = {}
# bot.r = r


for f in os.listdir('extensions'):
    if f.endswith('.py'):
        try:
            bot.load_extension(f'extensions.{f[:-3]}')
        except SyntaxError as exception:
            print(f'Failed to load {f}: {exception}')

bot.run(config.get('token'))


@bot.event
async def on_message(self, message):
    if message.author.bot:
        return

    await self.process_commands(message)
