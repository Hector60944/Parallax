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
        except SyntaxError as exception:
            print(f'Module {module} failed to load: {exception}')
            return await ctx.send(f'Module **{module}** failed to load. See console for more details.')

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, module: str):
        """ Load an extension """
        try:
            self.bot.load_extension(f'extensions.{module}')
            await ctx.send('Module reloaded!')
        except SyntaxError as exception:
            print(f'Module {module} failed to load: {exception}')
            return await ctx.send(f'Module {module} failed to load. See console for more details.')


def setup(bot):
    bot.add_cog(Core(bot))
