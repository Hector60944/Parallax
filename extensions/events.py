import discord
from discord import utils as dutils
from discord.ext.commands import errors


class Events:
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        await self.bot.change_presence(game=discord.Game(name='-help'))
        app_info = await self.bot.application_info()
        self.invite_url = dutils.oauth_url(app_info.id)
        print(f'Logged in as {self.bot.user.name}\nBot invite link: {self.invite_url}')

    async def on_command_error(self, ctx, error):
        if isinstance(error, errors.MissingRequiredArgument):
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
            permissions = "\n".join([f"- {p.upper()}" for p in error.missing_perms])
            await ctx.send(f"**You're missing permissions:**\n{permissions}")

        elif isinstance(error, errors.BotMissingPermissions):
            permissions = "\n".join([f"- {p.upper()}" for p in error.missing_perms])
            await ctx.send(f"**Parallax is missing permissions:**\n{permissions}")

        else:
            pass


def setup(bot):
    bot.add_cog(Events(bot))
