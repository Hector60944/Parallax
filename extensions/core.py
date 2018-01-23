from discord.ext import commands


class Core:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, module: str):
        """ Reload an extension """
        try:
            self.bot.unload_extension(f'extensions.{module}')
            self.bot.load_extension(f'extensions.{module}')
            await ctx.send('Module reloaded!')
        except (SyntaxError, ModuleNotFoundError) as exception:
            await ctx.send(f'Module **{module}** failed to load: `{exception}`')

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, module: str):
        """ Load an extension """
        try:
            self.bot.load_extension(f'extensions.{module}')
            await ctx.send('Module reloaded!')
        except (SyntaxError, ModuleNotFoundError) as exception:
            await ctx.send(f'Module **{module}** failed to load: `{exception}`')


def setup(bot):
    bot.add_cog(Core(bot))
