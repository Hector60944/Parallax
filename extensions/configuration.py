import discord
from discord.ext import commands


class Helpers:
    def __init__(self, bot):
        self.bot = bot

        self.default_config = {
            'warnThreshold': 0,
            'antiInvite': False,
            'mutedRole': None,
            'logChannel': None
        }

    async def get_config(self, guild_id: int):
        return await self.bot.r.table('settings') \
            .get(str(guild_id)) \
            .default(self.default_config) \
            .run(self.bot.connection)

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

    @commands.group(aliases=['configure'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def config(self, ctx):
        if not ctx.invoked_subcommand:
            _help = await self.bot.formatter.format_help_for(ctx, ctx.command)

            for page in _help:
                await ctx.send(page)

    @config.command()
    async def reset(self, ctx):
        """ Resets the specified setting in the config, or the entire config if no setting specified """
        await self.helpers.set_config(ctx.guild.id, self.helpers.default_config)
        await ctx.send(f'Successfully reset server settings.')

    @config.command()
    async def warnings(self, ctx, warn_threshold: int):
        """ Set the amount of warnings a user needs before they are banned

        Specify '0' to disable banning.
        """
        config = await self.helpers.get_config(ctx.guild.id)
        config.update({'warnThreshold': warn_threshold})
        await self.helpers.set_config(ctx.guild.id, config)

        return await ctx.send(f'Warn threshold set to **{warn_threshold}**')

    @config.command()
    async def invitekiller(self, ctx, option: str):
        """ Toggles whether discord invite links are suppressed

        Valid options: on | off
        """
        if not option:
            current = await self.helpers.get_config(ctx.guild.id)
            setting = 'enabled' if current['antiInvite'] else 'disabled'
            return await ctx.send(f'Invite Killer is currently **{setting}**')

        enabled = option.lower() == 'on'
        config = await self.helpers.get_config(ctx.guild.id)
        config['antiInvite'] = enabled
        await self.helpers.set_config(ctx.guild.id, config)

        setting = 'enabled' if enabled else 'disabled'
        return await ctx.send(f'Invite Killer has been **{setting}**')

    @config.command()
    async def muterole(self, ctx, role: discord.Role=None):
        """ Sets the Muted role to the target role """
        config = await self.helpers.get_config(ctx.guild.id)
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
        config = await self.helpers.get_config(ctx.guild.id)
        if not channel:
            config['logChannel'] = None
            await self.helpers.set_config(ctx.guild.id, config)
            await ctx.send(f'Setting cleared.')
        else:
            config['logChannel'] = str(channel.id)
            await self.helpers.set_config(ctx.guild.id, config)
            await ctx.send(f'Log channel set to **{channel.name}**')

    @config.command(aliases=['overview'])
    async def show(self, ctx):
        """ Displays current server configuration """
        config = await self.helpers.get_config(ctx.guild.id)

        mute_role = discord.utils.get(ctx.guild.roles, id=int(config['mutedRole'])) if config['mutedRole'] else None
        log_channel = self.bot.get_channel(int(config['logChannel'])) if config['logChannel'] else None

        t = f'''**Server Configuration | {ctx.guild.name}**
```prolog
Anti-Invite  : {'on' if config['antiInvite'] else 'off'}
Muted Role   : {mute_role.name if mute_role else 'unknown'}
Log Channel  : {log_channel.name if log_channel else 'unknown'}
Warning Limit: {config['warnThreshold']}
```
        '''

        await ctx.send(t)


def setup(bot):
    bot.add_cog(Configuration(bot))
