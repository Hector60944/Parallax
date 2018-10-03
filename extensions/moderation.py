import asyncio
import regex
from datetime import datetime

import discord
from discord.ext import commands

from utils import hastepaste, interaction, timeparser
from utils.idconverter import IDConverter

no_cancer_regex = regex.compile(r'^[^\p{L}\p{M}\s+0-9]')
no_symbols_regex = regex.compile(r'^[^a-zA-Z0-9]')
no_numbers_regex = regex.compile(r'^[0-9]')


class Helpers:
    def __init__(self, bot):
        self.bot = bot

    async def resolve_user(self, u_id: int):
        try:
            return self.bot.get_user(u_id) or await self.bot.get_user_info(u_id)
        except discord.NotFound:
            return None

    async def create_timed_ban(self, guild_id: int, user: int, due: int):
        await self.bot.r.table('bans') \
            .insert({'user_id': str(user), 'guild_id': str(guild_id), 'due': str(due)}) \
            .run(self.bot.connection)

    async def create_timed_mute(self, guild_id: int, user: int, due: int, role: int):
        await self.bot.r.table('mutes') \
            .insert({'user_id': str(user), 'guild_id': str(guild_id), 'due': str(due), 'role_id': str(role)}) \
            .run(self.bot.connection)

    async def get_warns(self, user: int, guild_id: int):
        return (await self.bot.r.table('warns').get(str(user)).default({}).run(self.bot.connection)).get(str(guild_id), 0)

    async def set_warns(self, user: int, guild_id: int, warns: int):
        await self.bot.r.table('warns') \
            .insert({'id': str(user), str(guild_id): warns}, conflict='update') \
            .run(self.bot.connection)

    async def post_modlog_entry(self, guild_id: int, action: str, target: discord.User, moderator: discord.User,
                                reason: str, time: str='', color=0xbe2f2f):
        config = await self.bot.db.get_config(guild_id)
        log = interaction.get_channel(self.bot, config['logChannel'])

        if log:
            permissions = log.permissions_for(log.guild.me)
            if permissions.send_messages and permissions.embed_links:
                embed = discord.Embed(color=color,
                                      title=f'**User {action}**',
                                      description=f'**Target:** {target} ({target.id})\n'
                                                  f'**Reason:** {reason}',
                                      timestamp=datetime.utcnow())
                embed.set_footer(text=f'Performed by {moderator}', icon_url=moderator.avatar_url_as(format='png'))

                if time:
                    embed.description += f'\n**Duration:** {time}'

                await log.send(embed=embed)


class Moderation:
    def __init__(self, bot):
        self.bot = bot
        self.helpers = Helpers(bot)

    async def safe_react(self, message, emoji):
        try:
            await message.add_reaction(emoji)
        except (discord.HTTPException, discord.Forbidden):
            pass

    @commands.command()
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.guild)
    async def decancer(self, ctx):
        msg = await ctx.send('Please wait...')
        failed = 0

        members = [m for m in ctx.guild.members if no_cancer_regex.search(m.display_name)][:200]
        for m in members:
            try:
                await m.edit(nick='！ Dehoisted')
            except (discord.HTTPException, discord.Forbidden):
                failed += 1

        await msg.edit(content=f'**__Decancer Results__**\n**{len(members) - failed}** succeeded\n**{failed}** failed')

    @commands.group()
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.guild)
    async def dehoist(self, ctx):
        """ Renames users who hoist themselves to the top of the member list """
        if not ctx.invoked_subcommand:
            _help = await self.bot.formatter.format_help_for(ctx, ctx.command)

            for page in _help:
                await ctx.send(page)

    @dehoist.command()
    async def symbols(self, ctx):
        """ Dehoists names starting with symbols """
        msg = await ctx.send('Please wait...')
        failed = 0

        members = [m for m in ctx.guild.members if no_symbols_regex.match(m.display_name)][:200]
        for m in members:
            try:
                await m.edit(nick='！ Dehoisted')
            except (discord.HTTPException, discord.Forbidden):
                failed += 1

        await msg.edit(content=f'**__Dehoist Results__**\n**{len(members) - failed}** succeeded\n**{failed}** failed')

    @dehoist.command()
    async def numbers(self, ctx):
        """ Dehoists names starting with numbers """
        msg = await ctx.send('Please wait...')
        failed = 0

        members = [m for m in ctx.guild.members if no_numbers_regex.match(m.display_name)][:200]
        for m in members:
            try:
                await m.edit(nick='！ Dehoisted')
            except (discord.HTTPException, discord.Forbidden):
                failed += 1

        await msg.edit(content=f'**__Dehoist Results__**\n**{len(members) - failed}** succeeded\n**{failed}** failed')

    @dehoist.command()
    async def custom(self, ctx, *, prefix: str):
        """ Dehoists names starting with the given prefix """
        msg = await ctx.send('Please wait...')
        failed = 0

        members = [m for m in ctx.guild.members if m.display_name.startswith(prefix)][:200]
        for m in members:
            try:
                await m.edit(nick='！ Dehoisted')
            except (discord.HTTPException, discord.Forbidden):
                failed += 1

        await msg.edit(content=f'**__Dehoist Results__**\n**{len(members) - failed}** succeeded\n**{failed}** failed')

    @dehoist.command(name='all')
    async def _all(self, ctx):
        """ Dehoists names using a combination of all available presets """
        msg = await ctx.send('Please wait...')
        failed = 0

        members = [m for m in ctx.guild.members if no_numbers_regex.match(m.display_name) or no_symbols_regex.match(m.display_name)][:200]
        for m in members:
            try:
                await m.edit(nick='！ Dehoisted')
            except discord.NotFound:
                pass
            except (discord.HTTPException, discord.Forbidden):
                failed += 1

        await msg.edit(content=f'**__Dehoist Results__**\n**{len(members) - failed}** succeeded\n**{failed}** failed')

    @commands.command()
    @commands.guild_only()
    async def snipe(self, ctx):
        """ View the last deleted message in the channel """
        m = await self.bot.r.table('snipes').get(str(ctx.channel.id)).run(self.bot.connection)

        if not m:
            return await ctx.send('No snipes available.')

        await self.bot.r.table('snipes').get(str(ctx.channel.id)).delete().run(self.bot.connection)

        time = m.get('timestamp', None)
        if not time:
            time = discord.Embed.Empty
        else:
            try:
                time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')

        if len(m['content']) > 2048:
            url = await hastepaste.create(m['content'])
            content = f'[Snipe too long, view on HastePaste]({url})'
        else:
            content = m['content']

        em = discord.Embed(color=0xbe2f2f, description=content, timestamp=time)
        em.set_author(name=m['author'])
        em.set_footer(text=f'Sniped by {ctx.author} | Message sent ')
        await ctx.send(embed=em)

    @commands.command(aliases=['ub'])
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx, member: IDConverter, *, reason: str='None specified'):
        """ Unbans a member from the server """
        if not member:
            raise commands.BadArgument('invalid user/id specified')

        if not isinstance(member, int):
            member = member.id

        try:
            ban = await ctx.guild.get_ban(discord.Object(id=member))
        except discord.NotFound:
            return await ctx.send('No banned users found with that ID')
        except discord.HTTPException:
            return await ctx.send('An error occurred while fetching the ban information')
        else:
            prompt = await ctx.send(f'The user **{str(ban.user)}** was banned for **{ban.reason or "no reason specified"}**.\n\n'
                                    'Are you sure you want to revoke this ban? (`y`/`n`)')

            try:
                m = await self.bot.wait_for('message', check=lambda m: m.author.id == ctx.author.id and m.content.lower() in ['y', 'n'], timeout=15)
            except asyncio.TimeoutError:
                await prompt.edit(content='Prompt cancelled; no response.')
            else:
                if m.content == 'n':
                    return await ctx.send(f'Ban revocation for **{str(ban.user)}** cancelled.')

                await ctx.guild.unban(ban.user, reason=f'[ {ctx.author} ] {reason}')
                # TODO: Revoke any timed bans in rethinkdb
                await self.safe_react(m, '🛠')
                await self.helpers.post_modlog_entry(ctx.guild.id, 'Unbanned', ban.user, ctx.author, reason, '', 0x53dc39)

    @commands.command(aliases=['b'])
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, member: IDConverter, *, reason: commands.clean_content(fix_channel_mentions=True)='None specified'):
        """ Bans a user from the server

        Timed bans: For the reason parameter, specify a time, unit and then your reason. E.g:
        5s Spamming

        Where 5s means 5 seconds. Supported units: seconds, minutes, hours, days, weeks.
        When using a unit, specify the first letter (seconds -> s, minutes -> m etc...)
        """
        user = await self.helpers.resolve_user(member)

        if not user:
            raise commands.BadArgument('member is not a valid user/id')

        member = ctx.guild.get_member(user.id)

        if member:
            interaction.check_hierarchy(ctx, member)
        else:
            member = user

        time, reason = timeparser.convert(reason)

        await ctx.guild.ban(member, reason=f'[ {ctx.author} ] {reason}', delete_message_days=7)
        await self.safe_react(ctx.message, '🔨')
        await self.bot.db.remove_timed_entry(ctx.guild.id, member.id, 'mutes')  # Delete any timed mutes this user has

        if time:
            await self.helpers.post_modlog_entry(ctx.guild.id, 'Banned', member, ctx.author, reason, str(time))
            await self.helpers.create_timed_ban(ctx.guild.id, member.id, time.absolute)
        else:
            await self.helpers.post_modlog_entry(ctx.guild.id, 'Banned', member, ctx.author, reason)

    @commands.command(aliases=['k'])
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member, *, reason: commands.clean_content(fix_channel_mentions=True)='None specified'):
        """ Kicks a user from the server """
        interaction.check_hierarchy(ctx, member)

        await member.kick(reason=f'[ {ctx.author} ] {reason}')
        await self.safe_react(ctx.message, '👢')
        await self.helpers.post_modlog_entry(ctx.guild.id, 'Kicked', member, ctx.author, reason)

    @commands.group(aliases=['d', 'purge', 'prune', 'clear', 'delete', 'remove'])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.guild_only()
    async def clean(self, ctx):
        """ Deletes messages in a channel

        e.g. -clean all 50

        When pruning users, syntax must be formatted like so:
        -clean users <amount> [users...]"""
        if not ctx.invoked_subcommand:
            _help = await self.bot.formatter.format_help_for(ctx, ctx.command)

            for page in _help:
                await ctx.send(page)

    @clean.command()
    async def attachments(self, ctx, amount: int=100):
        """ Removes messages with any kind of attachments """
        await self.remove(ctx, amount, lambda m: len(m.attachments) > 0)  # noqa: E731

    @clean.command()
    async def images(self, ctx, amount: int=100):
        """ Removes messages with image attachments """
        await self.remove(ctx, amount, lambda m: len(m.attachments) > 0 and
                                                 any(a for a in m.attachments if a.url[-3:].lower() in ['jpg', 'gif', 'png', 'webp']))  # noqa: E731

    @clean.command()
    async def textonly(self, ctx, amount: int=100):
        """ Removes messages with no attachments """
        await self.remove(ctx, amount, lambda m: len(m.attachments) == 0)

    @clean.command()
    async def users(self, ctx, amount: int=100, *users: discord.Member):
        """ Removes messages sent by users """
        if users:
            await self.remove(ctx, amount, lambda m: any(m.author.id == u.id for u in users))  # noqa: E731
        else:
            await self.remove(ctx, amount, lambda m: not m.author.bot)  # noqa: E731

    @clean.command()
    async def bots(self, ctx, amount: int=100):
        """ Removes all messages sent by bots """
        await self.remove(ctx, amount, lambda m: m.author.bot)  # noqa: E731

    @clean.command(name='all')
    async def all_(self, ctx, amount: int=100):
        """ Removes all messages """
        await self.remove(ctx, amount, None)

    @clean.command()
    async def contains(self, ctx, word: str, amount: int=100):
        """ Removes messages that contain the given word (case-sensitive) """
        await self.remove(ctx, amount, lambda m: word in m.content)

    async def remove(self, ctx, amount, predicate):
        if amount <= 0:
            return await ctx.send('Amount cannot be 0 or less.')

        amount = max(min(amount, 1000), 1)

        try:
            await ctx.channel.purge(limit=amount, check=predicate)
        except discord.HTTPException:
            await ctx.send('An error occurred while cleaning the channel.'
                           'Note that due to API limitations, messages older than 2 weeks *cannot* be deleted.')
        except discord.NotFound:
            pass
        else:
            await self.safe_react(ctx.message, '♻')

    @commands.command(aliases=['w'])
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def warn(self, ctx, member: discord.Member, *, reason: commands.clean_content(fix_channel_mentions=True)='None specified'):
        """ Issues a warning to the given user """
        interaction._check_hierarchy(ctx.author, member, False)

        threshold = (await self.bot.db.get_config(ctx.guild.id))['warnThreshold']
        current_warns = await self.helpers.get_warns(member.id, ctx.guild.id) + 1
        append_reason = '' if reason == 'None specified' else f'for **{reason}**'

        if threshold == 0:
            await ctx.send(f'Warned **{member}** {append_reason} (Warnings: {current_warns})')
        else:
            amount = current_warns % threshold

            if amount == 0:
                try:
                    await member.ban(reason=f'[ {ctx.author} ] Too many warnings', delete_message_days=7)
                except discord.Forbidden:
                    await ctx.send(f'Unable to ban **{member.name}** for hitting the warning limit')
                else:
                    await ctx.send(f'Banned **{member.name}** for hitting the warning limit ({threshold}/{threshold})')
            else:
                await ctx.send(f'Warned **{member}** {append_reason} (Warnings: {amount}/{threshold})')

        await self.helpers.set_warns(member.id, ctx.guild.id, current_warns)
        await self.helpers.post_modlog_entry(ctx.guild.id, 'Warned', member, ctx.author, reason, '', 0xEFD344)

    @commands.command(aliases=['cw'])
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def clearwarns(self, ctx, member: discord.Member, *, reason: commands.clean_content(fix_channel_mentions=True)='None specified'):
        """ Clears a user's warnings """
        await self.helpers.set_warns(member.id, ctx.guild.id, 0)
        await self.helpers.post_modlog_entry(ctx.guild.id, 'Warns Cleared', member, ctx.author, reason, '', 0x53dc39)
        await self.safe_react(ctx.message, '👌')

    @commands.command(aliases=['m'])
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    async def mute(self, ctx, member: discord.Member, *, reason: commands.clean_content(fix_channel_mentions=True)='None specified'):
        """ Mutes the specified user

        Timed mutes: For the reason parameter, specify a time, unit and then your reason. E.g:
        5s Spamming

        Where 5s means 5 seconds. Supported units: seconds, minutes, hours, days, weeks.
        When using a unit, specify the first letter (seconds -> s, minutes -> m etc...)
        """
        interaction._check_hierarchy(ctx.author, member, False)

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

        if role in member.roles:
            return await ctx.send('That user is already muted.')

        time, reason = timeparser.convert(reason)

        await member.add_roles(role, reason=f'[ {ctx.author} ] {reason}')
        await self.safe_react(ctx.message, '🔇')

        if time:
            await self.helpers.post_modlog_entry(ctx.guild.id, 'Muted', member, ctx.author, reason, str(time))
            await self.helpers.create_timed_mute(ctx.guild.id, member.id, time.absolute, role.id)
        else:
            await self.helpers.post_modlog_entry(ctx.guild.id, 'Muted', member, ctx.author, reason)

    @commands.command(aliases=['um'])
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    async def unmute(self, ctx, member: discord.Member, *, reason: commands.clean_content(fix_channel_mentions=True)='None specified'):
        """ Unmutes the specified user """
        interaction._check_hierarchy(ctx.author, member, False)

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

        if role not in member.roles:
            return await ctx.send('That user is not currently muted.')

        await member.remove_roles(role, reason=f'[ {ctx.author} ] {reason}')
        await self.safe_react(ctx.message, '🔈')
        await self.helpers.post_modlog_entry(ctx.guild.id, 'Unmuted', member, ctx.author, reason, '', 0x53dc39)
        await self.bot.db.remove_timed_entry(ctx.guild.id, member.id, 'mutes')

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    async def lock(self, ctx):
        """ Locks the current channel """
        ow = ctx.channel.overwrites_for(ctx.guild.default_role)
        ow.send_messages = False
        await ctx.channel.set_permissions(target=ctx.guild.default_role, overwrite=ow, reason=f'[ {ctx.author} ] Lockdown')
        await self.safe_react(ctx.message, '🔒')

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    async def unlock(self, ctx):
        """ Unlocks the current channel """
        ow = ctx.channel.overwrites_for(ctx.guild.default_role)
        ow.send_messages = None
        await ctx.channel.set_permissions(target=ctx.guild.default_role, overwrite=ow, reason=f'[ {ctx.author} ] Removed lockdown')
        await self.safe_react(ctx.message, '🔓')

    @commands.command(aliases=['vk', 'vckick'])
    @commands.bot_has_permissions(manage_channels=True)
    @commands.guild_only()
    async def voicekick(self, ctx, *users: discord.Member):
        """ Kicks the target users from their voicechannels """
        if not ctx.author.guild_permissions.move_members:
            return await ctx.send('**You need the following permissions:**\n-Move Members')

        if not ctx.me.guild_permissions.move_members:
            return await ctx.send('**Missing required permissions:**\n-Move Members')

        if not users:
            raise commands.errors.BadArgument('users to voicekick must be specified')

        dest = await ctx.guild.create_voice_channel(name='voicekick', reason=f'[ {ctx.author} ] Voicekick')
        in_voice = [m for m in users if m.voice and m.voice.channel and m.voice.channel.permissions_for(ctx.me).move_members]

        for m in in_voice:
            await m.move_to(channel=dest, reason=f'[ {ctx.author} ] Voicekick')

        await dest.delete(reason=f'[ {ctx.author} ] Voicekick')
        await self.safe_react(ctx.message, '👢')

    @commands.command(aliases=['unassign'])
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    async def assign(self, ctx, *, role: discord.Role=None):
        """ Assign yourself a (public) role

        Use the same command to unassign a role
        """
        config = await self.bot.db.get_config(ctx.guild.id)

        if not config['selfrole']:
            return await ctx.send('There are no self-assignable roles')

        if not role:
            roles = [discord.utils.get(ctx.guild.roles, id=int(role_id)) for role_id in config['selfrole']]
            roles = sorted(filter(None, roles), key=lambda r: r.name)
            public_roles = ''

            for role in roles:
                r_name = role.name[:21] + '...' if len(role.name) > 21 else role.name
                public_roles += f'{r_name:25}({role.id})\n'

            await ctx.send(f'```\n{public_roles.strip() or "No roles available"}\n```')
        else:
            if str(role.id) not in config['selfrole']:
                return await ctx.send('That role isn\'t self-assignable')

            if role.position > ctx.me.top_role.position:
                return await ctx.send('Unable to assign; the target role\'s position is higher than my top role')

            if discord.utils.get(ctx.author.roles, id=role.id):
                await ctx.author.remove_roles(role, reason=f'Selfrole')
            else:
                await ctx.author.add_roles(role, reason=f'Selfrole')

            await self.safe_react(ctx.message, '👌')

    @commands.command(aliases=['slow', 'delay', 'ratelimit'])
    @commands.bot_has_permissions(manage_channels=True)
    @commands.guild_only()
    async def slowmode(self, ctx, delay: int, *, reason: commands.clean_content(fix_channel_mentions=True)='None specified'):
        """ Sets channel slowmode (delay is the time between messages)

        The delay can be 0-120 seconds, where `0` is off/disabled.
        E.g. if delay is 5 seconds, then users can send 1 message every 5 seconds"""
        if delay > 120:
            return await ctx.send('Delay cannot be higher than 120 seconds.')

        if delay < 0:
            return await ctx.send('Delay cannot be lower than 0 seconds.')

        await ctx.channel.edit(slowmode_delay=delay, reason=f'[ {ctx.author} ] {reason}')

        msg = 'disabled' if delay == 0 else f'set to {delay} seconds'
        await ctx.send(f'Slowmode {msg}')


def setup(bot):
    bot.add_cog(Moderation(bot))
