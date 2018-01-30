import asyncio
from datetime import datetime

import discord
from discord.ext import commands
from utils import interaction, timeparser


class Helpers:
    def __init__(self, bot):
        self.bot = bot

    async def create_timed_ban(self, guild_id: int, user: int, due: int):
        await self.bot.r.table('bans') \
            .insert({'user_id': str(user), 'guild_id': str(guild_id), 'due': str(due)}) \
            .run(self.bot.connection)

    async def create_timed_mute(self, guild_id: int, user: int, due: int, role: int):
        await self.bot.r.table('mutes') \
            .insert({'user_id': str(user), 'guild_id': str(guild_id), 'due': str(due), 'role_id': str(role)}) \
            .run(self.bot.connection)

    async def get_warns(self, user: int, guild_id: int):
        warns = await self.bot.r.table('warns').get(str(user)).default({}).run(self.bot.connection)

        return warns.get(str(guild_id), 0)

    async def set_warns(self, user: int, guild_id: int, warns: int):
        await self.bot.r.table('warns') \
            .insert({'id': str(user), str(guild_id): warns}, conflict='update') \
            .run(self.bot.connection)

    async def post_modlog_entry(self, guild_id: int, action: str, target: discord.User, moderator: discord.User, reason: str, time: str=''):
        config = await self.bot.db.get_config(guild_id)

        if config['logChannel']:
            channel = self.bot.get_channel(int(config['logChannel']))
            if channel:
                permissions = channel.permissions_for(channel.guild.me)
                if permissions.send_messages and permissions.embed_links:
                    embed = discord.Embed(color=0xbe2f2f,
                                          title=f'**User {action}**',
                                          description=f'**Target:** {target} ({target.id})\n'
                                                      f'**Reason:** {reason}',
                                          timestamp=datetime.utcnow())
                    embed.set_footer(text=f'Performed by {moderator}', icon_url=moderator.avatar_url_as(format='png'))

                    if time:
                        embed.description += f'\n**Duration:** {time}'

                    await channel.send(embed=embed)


class Moderation:
    def __init__(self, bot):
        self.bot = bot
        self.helpers = Helpers(bot)

    @commands.command(aliases=['ub'])
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx, member: int, *, reason: str='None specified'):
        """ Unbans a member from the server by their Discord ID

        To get a user's ID: https://support.discordapp.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID"""
        bans = await ctx.guild.bans()
        ban = discord.utils.get(bans, user__id=member)

        if not ban:
            return await ctx.send('No banned users found with that ID')

        prompt = await ctx.send(f'The user **{str(ban.user)}** was banned for **{ban.reason}**.\n\nAre you sure you want to revoke this ban? (`y`/`n`)')

        try:
            m = await self.bot.wait_for('message', check=lambda m: m.content == 'y' or m.content == 'n', timeout=20)
        except asyncio.TimeoutError:
            await prompt.edit(content='Prompt cancelled; no response.')
        else:
            if m.content == 'n':
                return await ctx.send(f'Ban revocation for **{str(ban.user)}** cancelled.')

            await ctx.guild.unban(ban.user, reason=f'[ {ctx.author} ] {reason}')
            await m.add_reaction('🛠')
            await self.helpers.post_modlog_entry(ctx.guild.id, 'Unbanned', ban.user, ctx.author, reason)

    @commands.command(aliases=['b'])
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member, *, reason: commands.clean_content(fix_channel_mentions=True)='None specified'):
        """ Bans a user from the server

        Timed bans: For the reason parameter, specify a time, unit and then your reason. E.g:
        5s Looked at me wrong

        Where 5s means 5 seconds. Supported units: seconds, minutes, hours, days, weeks.
        When using a unit, specify the first letter (seconds -> s, minutes -> m etc...)
        """
        if not interaction.check_hierarchy(ctx.me, member):
            return await ctx.send("Role hierarchy prevents me from doing that.")

        if not interaction.check_hierarchy(ctx.author, member, owner_check=True):
            return await ctx.send("Role hierarchy prevents you from doing that.")

        time, reason = timeparser.convert(reason)

        await member.ban(reason=f'[ {ctx.author} ] {reason}', delete_message_days=7)
        await ctx.message.add_reaction('🔨')

        if time:
            await self.helpers.post_modlog_entry(ctx.guild.id, 'Banned', member, ctx.author, reason, f'{time.amount} {time.unit}')
            await self.helpers.create_timed_ban(ctx.guild.id, member.id, time.absolute)
        else:
            await self.helpers.post_modlog_entry(ctx.guild.id, 'Banned', member, ctx.author, reason)

    @commands.command(aliases=['k'])
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member, *, reason: commands.clean_content(fix_channel_mentions=True)='None specified'):
        """ Kicks a user from the server """
        if not interaction.check_hierarchy(ctx.me, member):
            return await ctx.send("Role hierarchy prevents me from doing that.")

        if not interaction.check_hierarchy(ctx.author, member, owner_check=True):
            return await ctx.send("Role hierarchy prevents you from doing that.")

        await member.kick(reason=f'[ {ctx.author} ] {reason}')
        await ctx.message.add_reaction('👢')
        await self.helpers.post_modlog_entry(ctx.guild.id, 'Kicked', member, ctx.author, reason)

    @commands.command(aliases=['d', 'purge', 'prune', 'clear', 'delete', 'remove'])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.guild_only()
    async def clean(self, ctx, amount: int, options: str=None, *users: discord.Member):
        """ Deletes messages in a channel

        You can remove messages sent by bots by specifying 'bot' as the filter.
        You can remove messages by users by specifying 'user' as the filter.
        You can remove messages by specific users by mentioning them after specifying 'user' as the filter.
        """
        pred = None

        if options:
            if 'bot' in options:
                pred = lambda m: m.author.bot  # noqa: E731
            if 'user' in options:
                if users:
                    pred = lambda m: any(m.author.id == u.id for u in users)  # noqa: E731
                else:
                    pred = lambda m: not m.author.bot  # noqa: E731

        if amount <= 0:
            return await ctx.send("Specify an amount above 0")

        if amount > 1000:
            amount = 1000

        try:
            await ctx.channel.purge(limit=amount, check=pred)
            await ctx.message.add_reaction('♻')
        except discord.HTTPException:
            await ctx.send("An unknown error occurred while cleaning the channel.")
        except discord.NotFound:
            pass

    @commands.command(aliases=['w'])
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def warn(self, ctx, member: discord.Member, *, reason: commands.clean_content(fix_channel_mentions=True)='None specified'):
        """ Issues a warning to the given user """
        if not interaction.check_hierarchy(ctx.me, member):
            return await ctx.send("Role hierarchy prevents me from doing that.")

        if not interaction.check_hierarchy(ctx.author, member, owner_check=True):
            return await ctx.send("Role hierarchy prevents you from doing that.")

        threshold = (await self.bot.db.get_config(ctx.guild.id))['warnThreshold']
        current_warns = await self.helpers.get_warns(member.id, ctx.guild.id) + 1

        if threshold != 0:
            amount = current_warns % threshold

            if amount == 0:
                await member.ban(reason=f'[ {ctx.author} ] Too many warnings', delete_message_days=7)
                await ctx.send(f'Banned **{member.name}** for hitting the warning limit ({threshold}/{threshold})')
            else:
                await ctx.send(f'Warned **{member}** for **{reason}** (Warnings: {amount}/{threshold})')
        else:
            await ctx.send(f'Warned **{member}** for **{reason}** (Warnings: {current_warns})')

        await self.helpers.set_warns(member.id, ctx.guild.id, current_warns)
        await self.helpers.post_modlog_entry(ctx.guild.id, 'Warned', member, ctx.author, reason)

    @commands.command(aliases=['m'])
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    async def mute(self, ctx, member: discord.Member, *, reason: commands.clean_content(fix_channel_mentions=True)='None specified'):
        """ Mutes the specified user

        Timed mutes: For the reason parameter, specify a time, unit and then your reason. E.g:
        5s Looked at me wrong

        Where 5s means 5 seconds. Supported units: seconds, minutes, hours, days, weeks.
        When using a unit, specify the first letter (seconds -> s, minutes -> m etc...)
        """
        if not interaction.check_hierarchy(ctx.me, member):
            return await ctx.send("Role hierarchy prevents me from doing that.")

        if not interaction.check_hierarchy(ctx.author, member, owner_check=True):
            return await ctx.send("Role hierarchy prevents you from doing that.")

        config = await self.bot.db.get_config(ctx.guild.id)
        if not config['mutedRole']:
            return await ctx.send('A muted role hasn\'t been configured for this server. '
                                  'You can change the role by using the `config` command.')

        role = discord.utils.get(ctx.guild.roles, id=int(config['mutedRole']))

        if not role:
            return await ctx.send('A muted role was configured for this server but no longer exists. '
                                  'You can change the role by using the `config` command.')

        if role.position > ctx.me.top_role.position:
            return await ctx.send('The muted role\'s position is higher than my top role. Unable to assign the role')

        time, reason = timeparser.convert(reason)

        await member.add_roles(role, reason=f'[ {ctx.author} ] {reason}')
        await ctx.message.add_reaction('🔇')

        if time:
            await self.helpers.post_modlog_entry(ctx.guild.id, 'Muted', member, ctx.author, reason, f'{time.amount} {time.unit}')
            await self.helpers.create_timed_mute(ctx.guild.id, member.id, time.absolute, role.id)
        else:
            await self.helpers.post_modlog_entry(ctx.guild.id, 'Muted', member, ctx.author, reason)

    @commands.command(aliases=['um'])
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    async def unmute(self, ctx, member: discord.Member, *, reason: commands.clean_content(fix_channel_mentions=True)='None specified'):
        """ Unmutes the specified user """
        if not interaction.check_hierarchy(ctx.me, member):
            return await ctx.send("Role hierarchy prevents me from doing that.")

        if not interaction.check_hierarchy(ctx.author, member, owner_check=True):
            return await ctx.send("Role hierarchy prevents you from doing that.")

        config = await self.bot.db.get_config(ctx.guild.id)
        if not config['mutedRole']:
            return await ctx.send('A muted role hasn\'t been configured for this server. '
                                  'You can change the role by using the `config` command.')

        role = discord.utils.get(ctx.guild.roles, id=int(config['mutedRole']))

        if not role:
            return await ctx.send('A muted role was configured for this server but no longer exists. '
                                  'You can change the role by using the `config` command.')

        if role.position > ctx.me.top_role.position:
            return await ctx.send('The muted role\'s position is higher than my top role. Unable to unassign the role')

        await member.remove_roles(role, reason=f'[ {ctx.author} ] {reason}')
        await ctx.message.add_reaction('🔈')
        await self.helpers.post_modlog_entry(ctx.guild.id, 'Unmuted', member, ctx.author, reason)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    async def lock(self, ctx):
        """ Locks the current channel """
        ow = ctx.channel.overwrites_for(ctx.guild.default_role)
        ow.send_messages = False
        await ctx.channel.set_permissions(target=ctx.guild.default_role, overwrite=ow, reason=f'[ {ctx.author} ] Lockdown')
        await ctx.message.add_reaction('🔒')

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    async def unlock(self, ctx):
        """ Unlocks the current channel """
        ow = ctx.channel.overwrites_for(ctx.guild.default_role)
        ow.send_messages = None
        await ctx.channel.set_permissions(target=ctx.guild.default_role, overwrite=ow, reason=f'[ {ctx.author} ] Removed lockdown')
        await ctx.message.add_reaction('🔓')

    @commands.command(aliases=['vk', 'vckick'])
    @commands.bot_has_permissions(manage_channels=True)
    @commands.guild_only()
    async def voicekick(self, ctx, *users: discord.Member):
        """ Kicks the target users from their voicechannels """
        if not ctx.author.guild_permissions.move_members:
            return await ctx.send('**You need the following permissions:**\n-Move Members')

        if not ctx.me.guild_permissions.move_members:
            return await ctx.send('**Missing required permissions:**\n-Move Members')

        dest = await ctx.guild.create_voice_channel(name='voicekick', reason=f'[ {ctx.author} ] Voicekick')
        in_voice = list(filter(lambda m: m.voice is not None and m.voice.channel is not None and m.voice.channel.permissions_for(ctx.me).move_members,
                               users))
        for m in in_voice:
            await m.move_to(dest, f'[ {ctx.author} ] Voicekick')

        await dest.delete(f'[ {ctx.author} ] Voicekick')
        await ctx.message.add_reaction('👢')


def setup(bot):
    bot.add_cog(Moderation(bot))
