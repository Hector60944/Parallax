import json
import os
from datetime import datetime

import rethinkdb as r
from discord.ext.commands import AutoShardedBot, when_mentioned_or


class Database:
    def __init__(self, bot):
        self.bot = bot

    async def get_config(self, guild_id: int):
        return await self.bot.r.table('settings') \
            .get(str(guild_id)) \
            .default({
                'warnThreshold': 0,
                'antiInvite': False,
                'mutedRole': None,
                'logChannel': None,
                'autorole': {
                    'bots': [],
                    'users': []
                },
                'messages': {
                    'joinLog': None,
                    'leaveLog': None,
                    'joinMessage': {
                        'message': '',
                        'channel': None
                    },
                    'leaveMessage': {
                        'message': '',
                        'channel': None
                    }
                }
            }).run(self.bot.connection)


if __name__ == '__main__':
    r.set_loop_type('asyncio')

    with open('config.json') as f:
        config = json.load(f)

    bot = AutoShardedBot(command_prefix=when_mentioned_or(*config.get('prefixes')), help_attrs=dict(hidden=True))
    bot.startup = datetime.now()
    bot.version = config['version']
    bot.messages_seen = 0
    bot.db = Database(bot)
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
        bot.messages_seen += 1
        if not bot.is_ready() or message.author.bot:
            return

        await bot.process_commands(message)

    bot.run(config.get('token'))
