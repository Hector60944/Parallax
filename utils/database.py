class Database:
    def __init__(self, bot):
        self.bot = bot

    async def get_config(self, guild_id: int):
        return await self.bot.r.table('settings') \
            .get(str(guild_id)) \
            .default({
                'modOnly': False,
                'accountAge': None,
                'verificationRole': None,
                'warnThreshold': 0,
                'antiInvite': False,
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

    async def remove_timed_entry(self, guild_id: int, user_id: int, table: str):
        await self.bot.r.table(table) \
            .filter({'user_id': str(user_id), 'guild_id': str(guild_id)}) \
            .delete() \
            .run(self.bot.connection)
