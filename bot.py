import json
import os
from datetime import datetime

import rethinkdb as r
from discord.ext.commands import AutoShardedBot

from utils import database


async def get_prefix(bot, message):  # literal shit code send help
    valid = []

    if hasattr(bot, 'user'):
        valid.append(f'<@{bot.user.id}> ')
        valid.append(f'<@!{bot.user.id}> ')

    if message.guild is not None:
        custom = (await bot.r.table('prefixes')
                  .get(str(message.guild.id))
                  .default({})
                  .run(bot.connection)) \
                  .get('prefix', None)

        if custom:
            valid.append(custom)
        else:
            valid.append(*bot.config.get('prefixes'))

    return valid


if __name__ == '__main__':
    r.set_loop_type('asyncio')

    with open('config.json') as f:
        config = json.load(f)

    bot = AutoShardedBot(command_prefix=get_prefix, help_attrs=dict(hidden=True))
    bot.startup = datetime.now()
    bot.messages_seen = 0
    bot.db = database.Database(bot)
    bot.connection = bot.loop.run_until_complete(r.connect(db='parallax'))
    bot.r = r
    bot.config = config

    for f in os.listdir('extensions'):
        if f.endswith('.py'):
            try:
                bot.load_extension(f'extensions.{f[:-3]}')
            except SyntaxError as exception:
                print(f'Failed to load {f}: {exception}')

    @bot.event
    async def on_message(message):
        bot.messages_seen += 1
        if not bot.is_ready() or message.author.bot:
            return

        if message.guild and not message.guild.unavailable:
            config = await bot.db.get_config(message.guild.id)
            if config.get('modOnly', False) and not message.author.guild_permissions.kick_members:
                return

        await bot.process_commands(message)

    bot.run(config.get('token'))
