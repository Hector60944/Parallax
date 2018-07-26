import discord
from discord.ext import commands

from utils import timeparser, pagination
from utils.interaction import get_channel


class Helpers:
    def __init__(self, bot):
        self.bot = bot

    async def set_config(self, guild_id: int, config: dict):
        config.update({'id': str(guild_id)})
        await self.bot.r.table('settings') \
            .insert(config, conflict='replace') \
            .run(self.bot.connection)

    async def delete_config(self, guild_id: int):
        await self.bot.r.table('settings').get(str(guild_id)).delete().run(self.bot.connection)

    async def set_prefix(self, guild_id: int, prefix: str):
        await self.bot.r.table('prefixes') \
            .insert({'id': str(guild_id), 'prefix': prefix}, conflict='replace') \
            .run(self.bot.connection)

    async def get_prefix(self, guild_id: int):
        return (await self.bot.r.table('prefixes')
                .get(str(guild_id))
                .default({})
                .run(self.bot.connection)) \
                .get('prefix', None)

    def get_channel_names(self, channel_ids: list):
        names = []

        for c in channel_ids:
            chan = self.bot.get_channel(int(c))
            if chan:
                names.append(chan.name)

        return names


class Configuration:
    def __init__(self, bot):
        self.bot = bot
        self.helpers = Helpers(bot)

    @commands.command()
    @commands.is_owner()
    async def migrate(self, ctx):
        migrate_data = {
            'autoDehoist': False
        }
        m = await ctx.send('Migrating all server settings...')
        await self.bot.r.table('settings').update(migrate_data).run(self.bot.connection)
        await m.edit(content='Done.')

    @commands.group(aliases=['configure'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def config(self, ctx):
        """ Configure server-specific settings """
        if not ctx.invoked_subcommand:
            _help = await self.bot.formatter.format_help_for(ctx, ctx.command)

            for page in _help:
                await ctx.send(page)

    @config.command()
    async def prefix(self, ctx, *, prefix: str=None):
        """ Sets a custom prefix for this guild. Omit to reset """
        if prefix is not None and len(prefix) > 30:
            return await ctx.send('Prefix cannot exceed 30 characters')

        if prefix:
            prefix = prefix.strip('"')

        await self.helpers.set_prefix(ctx.guild.id, prefix)

        if not prefix:
            await ctx.send('Prefix reset')
        else:
            await ctx.send(f'Prefix changed to **`{prefix}`**')

    @config.command()
    async def modonly(self, ctx, setting: bool):
        """ Toggles whether non-mods are ignored """
        config = await self.bot.db.get_config(ctx.guild.id)
        config.update({'modOnly': setting})
        await self.helpers.set_config(ctx.guild.id, config)

        return await ctx.send(f'Mod-Only **{"enabled" if setting else "disabled"}**')

    @config.command()
    async def warnings(self, ctx, warn_threshold: int):
        """ Sets the warning ban threshold

        Specify '0' to disable banning.
        """
        config = await self.bot.db.get_config(ctx.guild.id)
        config.update({'warnThreshold': warn_threshold})
        await self.helpers.set_config(ctx.guild.id, config)

        return await ctx.send(f'Warn threshold set to **{warn_threshold}**')

    @config.command(name='accountage', aliases=['account'])
    async def account_age(self, ctx, *, minimum_age: str=None):
        """ Sets the minimum account age needed to join the server """
        config = await self.bot.db.get_config(ctx.guild.id)

        if not minimum_age:
            config.update({'accountAge': None})
            await self.helpers.set_config(ctx.guild.id, config)
            return await ctx.send('Alt account identifying disabled.')

        time = timeparser.parse(minimum_age)

        if not time:
            return await ctx.send('Invalid time specified. Example format: `1d`, `1 d`, `1 day`')

        config.update({'accountAge': str(time.relative)})
        await self.helpers.set_config(ctx.guild.id, config)

        await ctx.send(f'Minimum account age set to `{time.amount}{time.unit}`')

    @config.command()
    async def verificationrole(self, ctx, *, role: discord.Role=None):
        """ Sets the role assigned to new accounts """
        config = await self.bot.db.get_config(ctx.guild.id)

        if not role:
            config.update({'verificationRole': None})
            await self.helpers.set_config(ctx.guild.id, config)
            return await ctx.send('Verification role reset.')

        config.update({'verificationRole': str(role.id)})
        await self.helpers.set_config(ctx.guild.id, config)

        await ctx.send(f'Verification role set to `{role.name}`')

    @config.command()
    async def antiinvite(self, ctx, setting: bool):
        """ Toggles whether discord invite links are suppressed """
        config = await self.bot.db.get_config(ctx.guild.id)
        config.update({'antiInvite': setting})
        await self.helpers.set_config(ctx.guild.id, config)

        await ctx.send(f'Anti-Invite **{"enabled" if setting else "disabled"}**')

    @config.command()
    async def ignoreads(self, ctx, method: str, *, channel: discord.TextChannel):
        """ Adds/Removes a channel to the anti-ads whitelist

        method must be either add or remove"""
        if method != 'add' and method != 'remove':
            return await ctx.send('Invalid method! Method must be `add` or `remove`')

        config = await self.bot.db.get_config(ctx.guild.id)

        if method == 'add':
            if str(channel.id) in config['antiadsIgnore']:
                return await ctx.send(f'{channel.mention} is already whitelisted.')

            config['antiadsIgnore'].append(str(channel.id))
            await ctx.send(f'{channel.mention} is now whitelisted!')
        elif method == 'remove':
            if str(channel.id) not in config['antiadsIgnore']:
                return await ctx.send(f'{channel.mention} is not whitelisted.')

            config['antiadsIgnore'].pop(config['antiadsIgnore'].index(str(channel.id)))
            await ctx.send(f'{channel.mention} is no longer whitelisted.')

        await self.helpers.set_config(ctx.guild.id, config)

    @config.command(name='ams')
    async def ams_threshold(self, ctx, threshold: int):
        """ Sets anti-mention spam threshold.

        Each message that contains at least one mention will count towards the threshold.

        Set threshold to 0 to disable this feature."""
        if threshold < 0:
            return await ctx.send('Threshold must be 0 or higher.')

        config = await self.bot.db.get_config(ctx.guild.id)
        config['consecutiveMentions'] = threshold
        await self.helpers.set_config(ctx.guild.id, config)
        await ctx.send(f'Set AMS threshold to **{threshold}**')

    @config.command()
    async def autodehoist(self, ctx, setting: bool):
        """ Sets whether auto-dehoist is enabled or not """
        config = await self.bot.db.get_config(ctx.guild.id)
        config['autoDehoist'] = setting
        await self.helpers.set_config(ctx.guild.id, config)
        await ctx.send(f'Auto-Dehoist is now **{"enabled" if setting else "disabled"}**')

    @config.command()
    async def muterole(self, ctx, *, role: discord.Role=None):
        """ Sets the Muted role to the target role """
        config = await self.bot.db.get_config(ctx.guild.id)
        if not role:
            config['mutedRole'] = None
            await self.helpers.set_config(ctx.guild.id, config)
            await ctx.send(f'Setting cleared.')
        else:
            if role.position > ctx.me.top_role.position:
                await ctx.send('The specified role is above my highest role, and therefore is unassignable. '
                               'Move my highest role above the target role, or choose a lower role.')
            else:
                config['mutedRole'] = str(role.id)
                await self.helpers.set_config(ctx.guild.id, config)
                await ctx.send(f'Muted role set to **{role.name}**')

    @config.command()
    async def mutepersist(self, ctx, setting: bool):
        """ Toggles mute-role persistence

        If a user leaves and rejoins while muted, Parallax can reapply the muted role (if set)"""
        config = await self.bot.db.get_config(ctx.guild.id)
        config.update({'mutePersist': setting})
        await self.helpers.set_config(ctx.guild.id, config)

        await ctx.send(f'Mute-Persistence **{"enabled" if setting else "disabled"}**')

    @config.command()
    async def logs(self, ctx, channel: discord.TextChannel=None):
        """ Sets the channel to post bans/kicks/mutes etc to """
        config = await self.bot.db.get_config(ctx.guild.id)
        if not channel:
            config['logChannel'] = None
            await ctx.send(f'Setting cleared.')
        else:
            config['logChannel'] = str(channel.id)
            await ctx.send(f'Log channel set to **{channel.name}**')

        await self.helpers.set_config(ctx.guild.id, config)

    @config.command()
    async def autorole(self, ctx, category: str, method: str, *, role: discord.Role):
        """ Setup autorole for members that join your server

        category: users | bots
        method  : add   | remove
        role    : id or name of a role in your server
        """
        if method.lower() not in ['add', 'remove']:
            return await ctx.send('Method must be either `add` or `remove`')

        if category.lower() not in ['users', 'bots']:
            return await ctx.send('Category must be either `users` or `bots`')

        config = await self.bot.db.get_config(ctx.guild.id)
        current_roles = config['autorole'][category.lower()]

        if method.lower() == 'add':
            if str(role.id) in current_roles:
                return await ctx.send('That role is already being assigned')

            current_roles.append(str(role.id))
            await self.helpers.set_config(ctx.guild.id, config)
            await ctx.send(f'**{role.name}** will now be automatically assigned to new {category.lower()}')
        else:
            if str(role.id) not in current_roles:
                return await ctx.send('That role is not currently being assigned')

            current_roles.pop(current_roles.index(str(role.id)))
            await self.helpers.set_config(ctx.guild.id, config)
            await ctx.send(f'**{role.name}** will no longer be automatically assigned')

    @config.command()
    async def joinlog(self, ctx, *, channel: discord.TextChannel=None):
        """ Log when a user joins the server """
        config = await self.bot.db.get_config(ctx.guild.id)
        if not channel:
            config['messages']['joinLog'] = None
            await ctx.send(f'Setting cleared.')
        else:
            config['messages']['joinLog'] = str(channel.id)
            await ctx.send(f'Join log channel set to **{channel.name}**')

        await self.helpers.set_config(ctx.guild.id, config)

    @config.command()
    async def leavelog(self, ctx, *, channel: discord.TextChannel=None):
        """ Log when a user leaves the server """
        config = await self.bot.db.get_config(ctx.guild.id)
        if not channel:
            config['messages']['leaveLog'] = None
            await ctx.send(f'Setting cleared.')
        else:
            config['messages']['leaveLog'] = str(channel.id)
            await ctx.send(f'Leave log channel set to **{channel.name}**')

        await self.helpers.set_config(ctx.guild.id, config)

    @config.command()
    async def deletelog(self, ctx, *, channel: discord.TextChannel=None):
        """ Log when a message is deleted """
        config = await self.bot.db.get_config(ctx.guild.id)
        if not channel:
            config['messages']['deleteLog'] = None
            await ctx.send(f'Setting cleared.')
        else:
            config['messages']['deleteLog'] = str(channel.id)
            await ctx.send(f'Delete log channel set to **{channel.name}**')

        await self.helpers.set_config(ctx.guild.id, config)

    @config.command()
    async def welcomechannel(self, ctx, channel: discord.TextChannel=None):
        """ Sets the welcome message channel """
        config = await self.bot.db.get_config(ctx.guild.id)
        join = config['messages']['joinMessage']

        if not channel:
            join['channel'] = None
            await ctx.send('Welcome channel reset')
        else:
            join['channel'] = str(channel.id)
            await ctx.send(f'Set welcome channel to **{channel.name}**')

        await self.helpers.set_config(ctx.guild.id, config)

    @config.command()
    async def welcomemsg(self, ctx, *, message: str=''):
        """ Sets the welcome message when a user joins the server

        special formatting keywords:
        {user}      - Mentions the user that joined
        {user:tag}  - The user's name and discriminator
        {server}    - The server's name
        {count}     - The amount of members in the server
        {owner}     - The server owner's name and discriminator
        """
        config = await self.bot.db.get_config(ctx.guild.id)
        join = config['messages']['joinMessage']

        if not message:
            join['message'] = None
            await ctx.send('Welcome message reset')
        else:
            join['message'] = message
            await ctx.send(f'Updated welcome message')

        await self.helpers.set_config(ctx.guild.id, config)

    @config.command()
    async def leavechannel(self, ctx, channel: discord.TextChannel=None):
        """ Sets the leave message channel """
        config = await self.bot.db.get_config(ctx.guild.id)
        leave = config['messages']['leaveMessage']

        if not channel:
            leave['channel'] = None
            await ctx.send('Leave channel reset')
        else:
            leave['channel'] = str(channel.id)
            await ctx.send(f'Set leave channel to **{channel.name}**')

        await self.helpers.set_config(ctx.guild.id, config)

    @config.command()
    async def leavemsg(self, ctx, *, message: str=''):
        """ Sets the leave message when a user leaves the server

        special formatting keywords:
        {user}      - Mentions the user that joined
        {user:tag}  - The user's name and discriminator
        {server}    - The server's name
        {count}     - The amount of members in the server
        """
        config = await self.bot.db.get_config(ctx.guild.id)
        leave = config['messages']['leaveMessage']

        if not message:
            leave['message'] = None
            await ctx.send('Leave message reset')
        else:
            leave['message'] = message
            await ctx.send(f'Updated leave message')

        await self.helpers.set_config(ctx.guild.id, config)

    @config.command(name='addcd', aliases=['slow'])
    async def add_cd(self, ctx, cooldown: int, *, channel: discord.TextChannel):
        """ Enables slowmode for the specified channel

        Cooldown: The time before a user can send a message in seconds (1 message per X seconds)
        Channel : The channel to apply the cooldown to"""
        if cooldown <= 0:
            return await ctx.send(f'Cooldown must be 1 second or higher. To disable slowmode for the channel, use `{ctx.prefix}config remcd <channel>`')

        await self.bot.db.enable_slow(channel.id, cooldown)
        await ctx.send(f'Enabled slowmode for **{channel.name}**. Users will be limited to **1 message/{cooldown}s**')

    @config.command(name='remcd', aliases=['nocd'])
    async def rem_cd(self, ctx, *, channel: discord.TextChannel):
        """ Disables slowmode for the specified channel

        Channel: The channel to disable the cooldown for"""
        await self.bot.db.disable_slow(channel.id)
        await ctx.send(f'Slowmode is no longer active for **{channel.name}**')

    @config.command(aliases=['overview'])
    async def show(self, ctx):
        """ Displays current server configuration """
        config = await self.bot.db.get_config(ctx.guild.id)
        _event = config['messages']

        prefix = await self.helpers.get_prefix(ctx.guild.id) or self.bot.config.get('prefixes')[0]
        verification = discord.utils.get(ctx.guild.roles, id=int(config['verificationRole'])) if config['verificationRole'] else None
        mute_role = discord.utils.get(ctx.guild.roles, id=int(config['mutedRole'])) if config['mutedRole'] else None
        log_channel = get_channel(self.bot, config['logChannel'])
        welcome_channel = get_channel(self.bot, _event['joinMessage']['channel'])
        leave_channel = get_channel(self.bot, _event['leaveMessage']['channel'])
        join_log = get_channel(self.bot, _event['joinLog'])
        leave_log = get_channel(self.bot, _event['leaveLog'])
        delete_log = get_channel(self.bot, _event['deleteLog'])
        ignored_channels = ' '.join(self.helpers.get_channel_names(config['antiadsIgnore']))

        settings = f'''
Prefix       : {prefix}
Mod-Only     : {'on' if config['modOnly'] else 'off'}
Muting
  Role       : {mute_role.name if mute_role else ''}
  Persist    : {'on' if config['mutePersist'] else 'off'}
Warning Limit: {config['warnThreshold']}
AMS Thres.   : {config['consecutiveMentions']}
Auto-Dehoist : {'on' if config['autoDehoist'] else 'off'}
Min Acc. Age : {config['accountAge'] or 'off'}
Verif. Role  : {verification.name if verification else 'None'}
Anti-Invite
  Status     : {'on' if config['antiInvite'] else 'off'}
  Ignored    : {ignored_channels or 'None'}
Autorole
  Bots       : {" ".join(config["autorole"]["bots"])}
  Users      : {" ".join(config["autorole"]["users"])}
Announce
  Welcome    : {welcome_channel.name if welcome_channel else ''}
  Leave      : {leave_channel.name if leave_channel else ''}
Log Channels
  Join       : {join_log.name if join_log else ''}
  Leave      : {leave_log.name if leave_log else ''}
  Deletes    : {delete_log.name if delete_log else ''}
  Moderation : {log_channel.name if log_channel else ''}
        '''

        pages = pagination.paginate(settings, 1950)

        for page in pages:
            await ctx.send(f'```prolog\n{page.strip()}```')

    @config.command()
    async def selfrole(self, ctx, method: str, *, role: discord.Role):
        """ Setup self-assignable roles

        method  : add   | remove
        role    : id or name of a role in your server
        """
        if method.lower() not in ['add', 'remove']:
            return await ctx.send('Method must be either `add` or `remove`')

        config = await self.bot.db.get_config(ctx.guild.id)
        current_roles = config['selfrole']

        if method.lower() == 'add':
            if str(role.id) in current_roles:
                return await ctx.send('That role is already assignable')

            if role.position > ctx.author.top_role.position:
                return await ctx.send('You can\'t make higher roles assignable')

            current_roles.append(str(role.id))
            await self.helpers.set_config(ctx.guild.id, config)
            await ctx.send(f'**{role.name}** is now self-assignable')
        else:
            if str(role.id) not in current_roles:
                return await ctx.send('That role is not currently assignable')

            current_roles.pop(current_roles.index(str(role.id)))
            await self.helpers.set_config(ctx.guild.id, config)
            await ctx.send(f'**{role.name}** is no longer self-assignable')


def setup(bot):
    bot.add_cog(Configuration(bot))
