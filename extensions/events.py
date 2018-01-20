import discord
from discord.ext.commands import errors


class Events:
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        await self.bot.change_presence(game=discord.Game(name='-help'))
        app_info = await self.bot.application_info()
        self.invite_url = discord.utils.oauth_url(app_info.id)
        print(f'Logged in as {self.bot.user.name}\nBot invite link: {self.invite_url}')

    async def on_command_error(self, ctx, error):
        try:
            if isinstance(error, (errors.MissingRequiredArgument, errors.BadArgument)):
                command = ctx.invoked_subcommand or ctx.command
                _help = await ctx.bot.formatter.format_help_for(ctx, command)

                for page in _help:
                    await ctx.send(page)

            elif isinstance(error, errors.CommandInvokeError):
                print(error)
                await ctx.send('An error has occurred in this command and has been logged.')

            elif isinstance(error, errors.CommandOnCooldown):
                await ctx.send('You can use this command in {0:.0f} seconds.'.format(error.retry_after))

            elif isinstance(error, errors.MissingPermissions):
                embed = discord.Embed(title='You need the following permissions:',
                                      description='\n'.join(p.title().replace('_', ' ') for p in error.missing_perms),
                                      color=0xbe2f2f)
                await ctx.send(embed=embed)

            elif isinstance(error, errors.BotMissingPermissions):
                embed = discord.Embed(title='Missing required permissions:',
                                      description='\n'.join(p.title().replace('_', ' ') for p in error.missing_perms),
                                      color=0xbe2f2f)
                await ctx.send(embed=embed)

            else:
                pass
        except: # noqa: bare-except
            pass  # lol


def setup(bot):
    bot.add_cog(Events(bot))
