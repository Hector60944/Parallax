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

    async def get_warns(self, user: int):
        return (await self.bot.r.table('warns')
                .get(str(user))
                .default({'warns': 0})
                .run(self.bot.connection))['warns']

    async def set_warns(self, user: int, warns: int):
        await self.bot.r.table('warns') \
            .insert({'id': str(user), 'warns': warns}, conflict='replace') \
            .run(self.bot.connection)


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
    async def reset(self, ctx, setting: str=None):
        """ Resets the specified setting in the config, or the entire config if no setting specified """
        if not setting:
            await self.helpers.delete_config(ctx.guild.id)
            await ctx.send('All settings reset')
        else:
            config = await self.helpers.get_config(ctx.guild.id)
            if setting in config:
                config[setting] = self.helpers.default_config[setting]
                await self.helpers.set_config(ctx.guild.id, config)
                await ctx.send(f'Successfully reset `{setting}`')
            else:
                await ctx.send(f'Invalid setting provided. View available settings with `{ctx.prefix}config`')

    @config.command()
    async def warnings(self, ctx, warn_threshold: int=None):
        """ Set the amount of warnings a user needs before they are banned

        Specify '0' to disable banning.
        """
        if not warn_threshold:
            current = await self.helpers.get_config(ctx.guild.id)
            return await ctx.send(f'Current threshold: **{current["warnThreshold"]}**')

        config = await self.helpers.get_config(ctx.guild.id)
        config.update({'warnThreshold': warn_threshold})
        await self.helpers.set_config(ctx.guild.id, config)

        return await ctx.send(f'Warn threshold set to **{warn_threshold}**')

    @config.command()
    async def invitekiller(self, ctx, option: str=None):
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
            if not config['mutedRole']:
                await ctx.send('A muted role hasn\'t been configured for this server')
            else:
                role = discord.utils.get(ctx.guild.roles, id=int(config['mutedRole']))
                if not role:
                    await ctx.send('A muted role was configured for this server but no longer exists.')
                else:
                    await ctx.send(f'The currently configured muted role is **{role.name}**')
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
            if not config['logChannel']:
                return await ctx.send('A log channel hasn\'t been configured for this server')
            else:
                channel = self.bot.get_channel(int(config['logChannel']))
                if channel:
                    await ctx.send(f'The current log channel is **{channel.name}**')
                else:
                    await ctx.send('A log channel was configured for this server but no longer exists.')
        else:
            config['logChannel'] = str(channel.id)
            await self.helpers.set_config(ctx.guild.id, config)
            await ctx.send(f'Log channel set to **{channel.name}**')


def setup(bot):
    bot.add_cog(Configuration(bot))
