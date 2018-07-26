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
                'autoDehoist': False,
                'antiInvite': False,
                'antiadsIgnore': [],
                'mutedRole': None,
                'mutePersist': True,
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

    async def set_persist(self, member: int, guild: int):
        await self.bot.r.table('mutepersist') \
            .insert({'id': str(member), str(guild): True}, conflict='update') \
            .run(self.bot.connection)

    async def get_persist(self, member: int, guild: int):
        should_mute = (await self.bot.r.table('mutepersist')
                       .get(str(member))
                       .default({})
                       .run(self.bot.connection)).get(str(guild), False)

        if should_mute:
            await self.bot.r.table('mutepersist') \
                .get(str(member)) \
                .replace(self.bot.r.row.without(str(guild))) \
                .run(self.bot.connection)

        return should_mute

    async def enable_slow(self, channel_id: int, cd: int):
        await self.bot.r.table('slowmode') \
            .insert({'id': str(channel_id), 'every': cd}, conflict='update') \
            .run(self.bot.connection)

    async def disable_slow(self, channel_id: int):
        await self.bot.r.table('slowmode') \
            .get(str(channel_id)) \
            .delete() \
            .run(self.bot.connection)

    async def get_slow(self, channel_id: int):
        return await self.bot.r.table('slowmode') \
            .get(str(channel_id))['every'] \
            .default(None) \
            .run(self.bot.connection)

    async def set_slow(self, user_id: int, channel_id: int):
        t = time()

        await self.bot.r.table('slowmode') \
            .insert({'id': str(user_id), str(channel_id): t}, conflict='update') \
            .run(self.bot.connection)

    async def should_slow(self, user_id: int, channel_id: int):
        cd = await self.get_slow(channel_id)

        if not cd:
            return False

        c_time = time()

        last_message = await self.bot.r.table('slowmode') \
            .get(str(user_id))[str(channel_id)] \
            .default(None) \
            .run(self.bot.connection)

        if not last_message:
            await self.set_slow(user_id, channel_id)
            return False

        triggered = c_time - last_message < cd

        if not triggered:
            await self.set_slow(user_id, channel_id)

        return triggered

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
