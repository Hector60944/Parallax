import json
import os

import rethinkdb as r
from discord.ext.commands import AutoShardedBot


if __name__ == '__main__':
    r.set_loop_type('asyncio')

    with open('config.json') as f:
        config = json.load(f)

    bot = AutoShardedBot(command_prefix=config.get('prefixes'))
    bot.connection = bot.loop.run_until_complete(r.connect(db='parallax'))
    bot.r = r

    for f in os.listdir('extensions'):
        if f.endswith('.py'):
            try:
                bot.load_extension(f'extensions.{f[:-3]}')
            except SyntaxError as exception:
                print(f'Failed to load {f}: {exception}')

    @bot.event
    async def on_message(message):
        if message.author.bot:
            return

        await bot.process_commands(message)

    bot.run(config.get('token'))
