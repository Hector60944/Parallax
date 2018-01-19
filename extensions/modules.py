import re

import discord
from utils import interaction

invite_rx = re.compile("discord(?:app)?\.(?:gg|com\/invite)\/([a-z0-9]{1,16})", re.IGNORECASE)


class Helpers:
    def __init__(self, bot):
        self.bot = bot

    async def anti_invite(self, guild_id: int):
        return (await self.bot.r.table('settings').get(str(guild_id)).default({'antiInvite': False}).run(self.bot.connection))['antiInvite']

    async def get_invites(self, user: int):
        invites = await self.bot.r.table('invites').get(str(user)).default({'invites': 0}).run(self.bot.connection)
        return invites['invites']

    async def set_invites(self, user: int, invites: int):
        await self.bot.r.table('invites').insert({'id': str(user), 'invites': invites}, conflict='replace').run(self.bot.connection)


class Modules:
    def __init__(self, bot):
        self.bot = bot
        self.helpers = Helpers(bot)

    async def on_message(self, message):
        if await self.helpers.anti_invite(message.guild.id):
            await self.anti_invite(message)

    async def anti_invite(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel) or \
                not interaction.check_bot_has(ctx, manage_messages=True) or \
                not interaction.check_hierarchy(ctx.guild.me, ctx.author) or interaction.check_user_has(ctx, manage_messages=True) or \
                not invite_rx.search(ctx.content):
            return

        try:
            await ctx.delete()
        except (discord.HTTPException, discord.NotFound):
            pass

        attempts = await self.helpers.get_invites(ctx.author.id) + 1
        await self.helpers.set_invites(ctx.author.id, attempts)

        if attempts % 3 == 0:
            if interation.check_bot_has(ctx, ban_members=True):
                await ctx.author.ban(reason='[ Parallax AutoBan ] Advertising', delete_message_days=7)
                await ctx.channel.send(f'AutoBanned {ctx.author} for advertising')
        else:
            await ctx.channel.send(f'{ctx.author.mention} Do not advertise here ({attempts % 3}/3)')


def setup(bot):
    bot.add_cog(Modules(bot))
