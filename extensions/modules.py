import re

import discord
from .utils import interaction

invite_rx = re.compile("discord(?:app)?\.(?:gg|com\/invite)\/([a-z0-9]{3,16})", re.IGNORECASE)


class Modules:
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        # if check for anti_invite module
        await self.anti_invite(message)

    async def anti_invite(self, ctx):
        if not interaction.check_bot_has(ctx, manage_messages=True, ban_members=True) or \
                not interaction.check_hierarchy(ctx.guild.me, ctx.author) or interaction.check_user_has(ctx, manage_messages=True) or \
                not invite_rx.search(ctx.content):
            return

        try:
            await ctx.delete()
        except discord.NotFound:
            pass

        attempts = self.bot.invites.get(ctx.author.id, 0) + 1
        self.bot.invites.update({ctx.author.id: attempts})
        
        if attempts % 3 == 0:
            await ctx.author.ban(reason='[ Parallax AutoBan ] Advertising', days=7)
            await ctx.channel.send(f'AutoBanned {ctx.author} for advertising')
        else:
            await ctx.channel.send(f'{ctx.author.mention} Do not advertise here ({attempts % 3}/3)')


def setup(bot):
    bot.add_cog(Modules(bot))
