from discord.ext import commands


class Core:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, *modules: str):
        """ Reload an extension """
        failed = []
        for module in modules:
            try:
                self.bot.unload_extension(f'extensions.{module}')
                self.bot.load_extension(f'extensions.{module}')
            except (SyntaxError, ModuleNotFoundError) as exception:
                failed.append((module, str(exception)))

        if failed:
            formatted = '\n'.join([f'{f[0]:15} - {f[1]}' for f in failed])
            await ctx.send(f'**{len(failed)}** extensions failed to reload\n```\n{formatted}```')
        else:
            await ctx.send('All modules reloaded successfully.')

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
