import discord
from discord.ext import commands
from utils import interaction


class Helpers:
    def __init__(self, bot):
        self.bot = bot

    async def get_config(self, guild_id: int):
        return await self.bot.r.table('settings').get(str(guild_id)).default({'warnThreshold': 0, 'antiInvite': False}).run(self.bot.connection)

    async def set_config(self, guild_id: int, config: dict):
        config.update({'id': str(guild_id)})
        await self.bot.r.table('settings').insert(config, conflict='replace').run(self.bot.connection)

    async def get_warns(self, user: int):
        warns = await self.bot.r.table('warns').get(str(user)).default({'warns': 0}).run(self.bot.connection)
        return warns['warns']

    async def set_warns(self, user: int, warns: int):
        await self.bot.r.table('warns').insert({'id': str(user), 'warns': warns}, conflict='replace').run(self.bot.connection)


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
    async def warnings(self, ctx, warn_threshold: int=None):
        """ Set the amount of warnings a user needs before they are banned
        
        Specify '0' to disable banning.
        """
        if not warn_threshold:
            current = await self.helpers.get_config(ctx.guild.id)
            return await ctx.send(f'Current threshold: {current["warnThreshold"]}')

        config = await self.helpers.get_config(ctx.guild.id)
        config.update({'warnThreshold': warn_threshold})
        await self.helpers.set_config(ctx.guild.id, config)

        return await ctx.send('Guild settings updated.')

    @config.command()
    async def invitekiller(self, ctx, option: str=None):
        """ Toggles whether discord invite links are suppressed """
        if not option:
            current = await self.helpers.get_config(ctx.guild.id)
            setting = 'enabled' if current['antiInvite'] else 'disabled'
            return await ctx.send(f'Invite Killer is currently {setting}')

        enabled = option in ['1', 'yes', 'y', 'true', 'on', 'enable', 'enabled']
        config = await self.helpers.get_config(ctx.guild.id)
        config['antiInvite'] = enabled
        await self.helpers.set_config(ctx.guild.id, config)

        setting = 'enabled' if enabled else 'disabled'
        return await ctx.send(f'Invite Killer has been {setting}')


def setup(bot):
    bot.add_cog(Configuration(bot))
