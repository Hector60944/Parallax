import asyncio
from time import time

import discord


class Database:
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self._watch_reminders())

    async def get_config(self, guild_id: int):
        return await self.bot.r.table('settings') \
            .get(str(guild_id)) \
            .default({
                'modOnly': False,
                'accountAge': None,
                'verificationRole': None,
                'warnThreshold': 0,
                'consecutiveMentions': 0,
                'antiInvite': False,
                'antiadsIgnore': [],
                'mutedRole': None,
                'logChannel': None,
                'autorole': {
                    'bots': [],
                    'users': []
                },
                'selfrole': [],
                'messages': {
                    'joinLog': None,
                    'leaveLog': None,
                    'deleteLog': None,
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

    async def get_mentions(self, user_id: int, guild_id: int):
        return (await self.bot.r.table('mentions')
                .get(str(user_id))
                .default({})
                .run(self.bot.connection)).get(str(guild_id), 0)

    async def update_mentions(self, user_id: int, guild_id: int, count: int):
        await self.bot.r.table('mentions') \
            .insert({'id': str(user_id), str(guild_id): count}, conflict='update') \
            .run(self.bot.connection)

    async def remove_timed_entry(self, guild_id: int, user_id: int, table: str):
        await self.bot.r.table(table) \
            .filter({'user_id': str(user_id), 'guild_id': str(guild_id)}) \
            .delete() \
            .run(self.bot.connection)

    async def add_reminder(self, author: int, due: int, content: str):
        await self.bot.r.table('reminders') \
            .insert({'author': str(author), 'due': due, 'content': content}) \
            .run(self.bot.connection)

    async def get_expired_reminders(self):
        t = time()

        return await self.bot.r.table('reminders') \
            .filter(self.bot.r.row['due'] <= t) \
            .coerce_to('array') \
            .run(self.bot.connection)

    async def delete_expired_reminders(self):
        t = time()

        await self.bot.r.table('reminders') \
            .filter(self.bot.r.row['due'] <= t) \
            .delete() \
            .run(self.bot.connection)

    async def _watch_reminders(self):
        while True:
            expired = await self.get_expired_reminders()
            await self.delete_expired_reminders()

            for reminder in expired:
                u = self.bot.get_user(int(reminder['author']))

                if not u:
                    continue

                try:
                    await u.send(reminder['content'])
                except (discord.HTTPException, discord.Forbidden):
                    pass

            await asyncio.sleep(10)
