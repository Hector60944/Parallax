import re
from datetime import datetime

import discord

from utils import interaction

invite_rx = re.compile(r'discord(?:app\.com\/invite|\.gg)\/([a-z0-9]{1,16})', re.IGNORECASE)
dehoist_rx = re.compile(r'^[^a-z0-9]', re.IGNORECASE)


class Helpers:
    def __init__(self, bot):
        self.bot = bot

    async def get_log_channel(self, guild_id: int):
        channel = (await self.bot.r.table('settings').get(str(guild_id)).default({}).run(self.bot.connection)).get('logChannel', None)
        return interaction.get_channel(self.bot, channel)

    async def anti_invite_enabled(self, guild_id: int, channel_id: int):
        config = await self.bot.db.get_config(guild_id)
        return config['antiInvite'] and str(channel_id) not in config['antiadsIgnore']

    async def ams_enabled(self, guild_id: int):
        config = await self.bot.db.get_config(guild_id)
        return config['consecutiveMentions'] > 0

    async def auto_dehoist_enabled(self, guild_id: int):
        config = await self.bot.db.get_config(guild_id)
        return config['autoDehoist']

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
        if isinstance(message.channel, discord.DMChannel) or message.author.bot or message.guild.unavailable:
            return

        if await self.helpers.anti_invite_enabled(message.guild.id, message.channel.id):
            await self.anti_invite(message)

        if await self.helpers.ams_enabled(message.guild.id):
            await self.anti_mention_spam(message)

        await self.slow_mode(message)

    async def on_member_update(self, old, new):
        if await self.helpers.auto_dehoist_enabled(new.guild.id):
            await self.auto_dehoist(old, new)

    async def auto_dehoist(self, old, new):
        if not dehoist_rx.match(new.display_name):
            return

        try:
            await new.edit(nick='boobs', reason='[ AutoMod ] Auto-Dehoist')
        except (discord.Forbidden, discord.HTTPException, discord.NotFound):
            pass

    async def slow_mode(self, message):
        if await self.bot.db.should_slow(message.author.id, message.channel.id):
            try:
                await message.delete()
            except (discord.Forbidden, discord.HTTPException):
                pass

    async def anti_mention_spam(self, ctx):
        if not interaction.check_bot_has(ctx, ban_members=True) or \
                not interaction._check_hierarchy(ctx.guild.me, ctx.author, True, True) or \
                interaction.check_user_has(ctx, manage_messages=True):
            return

        if not ctx.mentions:
            return await self.bot.db.update_mentions(ctx.author.id, ctx.guild.id, 0)

        threshold = (await self.bot.db.get_config(ctx.guild.id))['consecutiveMentions']
        consec_mentions = await self.bot.db.get_mentions(ctx.author.id, ctx.guild.id) + 1
        await self.bot.db.update_mentions(ctx.author.id, ctx.guild.id, consec_mentions)

        if consec_mentions % threshold == 0:
            await ctx.author.ban(reason='[ AutoMod ] Mention spamming', delete_message_days=7)
            await ctx.channel.send(f'Auto-Banned {ctx.author} for mention spamming')
            await self.post_modlog_entry(ctx.guild.id, ctx.author, 'Mention spam')
        elif consec_mentions % threshold > 1:
            await ctx.channel.send(f'{ctx.author.mention} Stop spamming mentions ({consec_mentions % threshold}/{threshold})')

    async def anti_invite(self, ctx):
        invite = invite_rx.search(ctx.content)
        if isinstance(ctx.author, discord.User):
            print(f'Encountered a user on anti_invite:\n\tAuthor Type: {type(ctx.author)}\n\tChannel Type: {type(ctx.channel)}\n\tUser: {str(ctx.author)}\n\tIs Bot: {ctx.author.bot}')
            return

        if not invite or \
                not interaction.check_bot_has(ctx, manage_messages=True) or \
                not interaction._check_hierarchy(ctx.guild.me, ctx.author, True, True) or interaction.check_user_has(ctx, kick_members=True) or \
                not await self.helpers.is_valid_advert(invite.group(), ctx.guild.id):
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
                await self.post_modlog_entry(ctx.guild.id, ctx.author, 'Advertising')
        else:
            await ctx.channel.send(f'{ctx.author.mention} Do not advertise here ({attempts % 3}/3)')

    async def post_modlog_entry(self, guild_id: int, target: discord.User, reason: str):
        channel = await self.helpers.get_log_channel(guild_id)

        if not channel:
            return

        permissions = channel.permissions_for(channel.guild.me)

        if permissions.send_messages and permissions.embed_links:
            embed = discord.Embed(color=0xbe2f2f,
                                  title=f'**User Banned**',
                                  description=f'**Target:** {str(target)} ({target.id})\n'
                                              f'**Reason:** [ AutoMod ] {reason}',
                                  timestamp=datetime.utcnow())
            embed.set_footer(text=f'Performed by {str(self.bot.user)}', icon_url=self.bot.user.avatar_url_as(format='png'))
            await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Modules(bot))
