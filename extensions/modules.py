import re
from datetime import datetime

import discord
from utils import interaction

invite_rx = re.compile("discord(?:app)?\.(?:gg|com\/invite)\/([a-z0-9]{1,16})", re.IGNORECASE)


class Helpers:
    def __init__(self, bot):
        self.bot = bot

    async def get_log_channel(self, guild_id: int):
        return (await self.bot.r.table('settings').get(str(guild_id)).default({}).run(self.bot.connection)).get('logChannel', None)

    async def anti_invite(self, guild_id: int):
        return (await self.bot.r.table('settings').get(str(guild_id)).default({}).run(self.bot.connection)).get('antiInvite', False)

    async def get_invites(self, user: int):
        return (await self.bot.r.table('invites').get(str(user)).default({}).run(self.bot.connection)).get('invites', 0)

    async def set_invites(self, user: int, invites: int):
        await self.bot.r.table('invites').insert({'id': str(user), 'invites': invites}, conflict='replace').run(self.bot.connection)


class Modules:
    def __init__(self, bot):
        self.bot = bot
        self.helpers = Helpers(bot)

    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel):
            return

        if await self.helpers.anti_invite(message.guild.id):
            await self.anti_invite(message)

    async def anti_invite(self, ctx):
        if not interaction.check_bot_has(ctx, manage_messages=True) or \
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
            if interaction.check_bot_has(ctx, ban_members=True):
                await ctx.author.ban(reason='[ Parallax AutoBan ] Advertising', delete_message_days=7)
                await ctx.channel.send(f'Auto-Banned {ctx.author} for advertising')
                channel = await self.helpers.get_log_channel(ctx.guild.id)
                if not channel:
                    return

                channel = self.bot.get_channel(int(channel))
                if channel:
                    permissions = channel.permissions_for(channel.guild.me)
                    if permissions.send_messages and permissions.embed_links:
                        embed = discord.Embed(color=0xbe2f2f,
                                              title=f'**User Banned**',
                                              description=f'**Target:** {str(ctx.author)} ({ctx.author.id})\n'
                                                          f'**Reason:** Advertising',
                                              timestamp=datetime.utcnow())
                        embed.set_footer(text=f'Performed by {str(self.bot.user)}', icon_url=self.bot.user.avatar_url_as(format='png'))
                        await channel.send(embed=embed)
        else:
            await ctx.channel.send(f'{ctx.author.mention} Do not advertise here ({attempts % 3}/3)')


def setup(bot):
    bot.add_cog(Modules(bot))
