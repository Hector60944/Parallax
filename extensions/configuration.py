import discord
from discord.ext import commands


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


class Configuration:
    def __init__(self, bot):
        self.bot = bot
        self.helpers = Helpers(bot)

    @commands.command()
    @commands.is_owner()
    async def migrate(self, ctx):
        migrate_data = {
            'selfrole': []
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
    async def warnings(self, ctx, warn_threshold: int):
        """ Set the amount of warnings a user needs before they are banned

        Specify '0' to disable banning.
        """
        config = await self.bot.db.get_config(ctx.guild.id)
        config.update({'warnThreshold': warn_threshold})
        await self.helpers.set_config(ctx.guild.id, config)

        return await ctx.send(f'Warn threshold set to **{warn_threshold}**')

    @config.command()
    async def invitekiller(self, ctx, option: str):
        """ Toggles whether discord invite links are suppressed

        Valid options: on | off
        """
        if not option:
            current = await self.bot.db.get_config(ctx.guild.id)
            setting = 'enabled' if current['antiInvite'] else 'disabled'
            return await ctx.send(f'Invite Killer is currently **{setting}**')

        enabled = option.lower() == 'on'
        config = await self.bot.db.get_config(ctx.guild.id)
        config['antiInvite'] = enabled
        await self.helpers.set_config(ctx.guild.id, config)

        setting = 'enabled' if enabled else 'disabled'
        return await ctx.send(f'Invite Killer has been **{setting}**')

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

    @config.command(aliases=['overview'])
    async def show(self, ctx):
        """ Displays current server configuration """
        config = await self.bot.db.get_config(ctx.guild.id)
        _event = config['messages']

        mute_role = discord.utils.get(ctx.guild.roles, id=int(config['mutedRole'])) if config['mutedRole'] else None
        log_channel = self.bot.get_channel(int(config['logChannel'])) if config['logChannel'] else None
        welcome_channel = self.bot.get_channel(int(_event['joinMessage']['channel'])) if _event['joinMessage']['channel'] else None
        leave_channel = self.bot.get_channel(int(_event['leaveMessage']['channel'])) if _event['leaveMessage']['channel'] else None
        join_log = self.bot.get_channel(int(_event['joinLog'])) if _event['joinLog'] else None
        leave_log = self.bot.get_channel(int(_event['leaveLog'])) if _event['leaveLog'] else None

        # ugh, spaghetti code...

        await ctx.send(f'''**Server Configuration | {ctx.guild.name}**
```prolog
Anti-Invite   : {'on' if config['antiInvite'] else 'off'}
Muted Role    : {mute_role.name if mute_role else 'unknown'}
Warning Limit : {config['warnThreshold']}
Autorole
  ╚ Bots      : {" ".join(config["autorole"]["bots"])}
  ╚ Users     : {" ".join(config["autorole"]["users"])}
Announce
  ╚ Welcome   : {welcome_channel.name if welcome_channel else 'unknown'}
  ╚ Leave     : {leave_channel.name if leave_channel else 'unknown'}
Log Channels
  ╚ Join      : {join_log.name if join_log else 'unknown'}
  ╚ Leave     : {leave_log.name if leave_log else 'unknown'}
  ╚ Moderation: {log_channel.name if log_channel else 'unknown'}
```
        ''')

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