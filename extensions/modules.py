import re
from datetime import datetime

import discord

from utils import interaction


invite_rx = re.compile(r'(?:https?:\/\/)?discord(?:app\.com\/invite|\.gg)\/([a-z0-9]{1,16})', re.IGNORECASE)


class Helpers:
    def __init__(self, bot):
        self.bot = bot

    async def get_log_channel(self, guild_id: int):
        channel = (await self.bot.r.table('settings').get(str(guild_id)).default({}).run(self.bot.connection)).get('logChannel', None)
        return interaction.get_channel(self.bot, channel)

    async def anti_invite(self, guild_id: int):
        return (await self.bot.r.table('settings').get(str(guild_id)).default({}).run(self.bot.connection)).get('antiInvite', False)

    async def get_invites(self, user: int, guild_id: int):
        return (await self.bot.r.table('invites').get(str(user)).default({}).run(self.bot.connection)).get(str(guild_id), 0)

    async def set_invites(self, user: int, guild_id: int, invites: int):
        await self.bot.r.table('invites').insert({'id': str(user), str(guild_id): invites}, conflict='update').run(self.bot.connection)

    async def is_valid_advert(self, invite: str, guild_id: int):
        try:
            resolved = await self.bot.get_invite(invite)
        except discord.NotFound as e:
            return True
        else:
            return resolved.guild.id != guild_id


class Modules:
    def __init__(self, bot):
        self.bot = bot
        self.helpers = Helpers(bot)

    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel) or message.author.bot:
            return

        if await self.helpers.anti_invite(message.guild.id):
            await self.anti_invite(message)

    async def anti_invite(self, ctx):
        invite = invite_rx.search(ctx.content)
        if isinstance(ctx.author, discord.User):
            print(f'Encountered a user on anti_invite:\n\tAuthor Type: {type(ctx.author)}\n\tChannel Type: {type(ctx.channel)}\n\tUser: {str(ctx.author)}\n\tIs Bot: {ctx.author.bot}')
            return

        if not invite or \
                not interaction.check_bot_has(ctx, manage_messages=True) or \
                not interaction._check_hierarchy(ctx.guild.me, ctx.author, True, True) or interaction.check_user_has(ctx, kick_members=True):
            return

        if not await self.helpers.is_valid_advert(invite.group(), ctx.guild.id):
            return

        try:
            await ctx.delete()
        except (discord.HTTPException, discord.NotFound):
            pass

        attempts = await self.helpers.get_invites(ctx.author.id, ctx.guild.id) + 1
        await self.helpers.set_invites(ctx.author.id, ctx.guild.id, attempts)

        if attempts % 3 == 0:
            if interaction.check_bot_has(ctx, ban_members=True):
                await ctx.author.ban(reason='[ AutoMod ] Advertising', delete_message_days=7)
                await ctx.channel.send(f'Auto-Banned {ctx.author} for advertising')

                channel = await self.helpers.get_log_channel(ctx.guild.id)

                if not channel:
                    return

                permissions = channel.permissions_for(channel.guild.me)
                if permissions.send_messages and permissions.embed_links:
                    embed = discord.Embed(color=0xbe2f2f,
                                          title=f'**User Banned**',
                                          description=f'**Target:** {str(ctx.author)} ({ctx.author.id})\n'
                                                      f'**Reason:** [ AutoMod ] Advertising',
                                          timestamp=datetime.utcnow())
                    embed.set_footer(text=f'Performed by {str(self.bot.user)}', icon_url=self.bot.user.avatar_url_as(format='png'))
                    await channel.send(embed=embed)
        else:
            await ctx.channel.send(f'{ctx.author.mention} Do not advertise here ({attempts % 3}/3)')


def setup(bot):
    bot.add_cog(Modules(bot))
