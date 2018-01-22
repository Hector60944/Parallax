import discord
from discord.ext.commands import errors


class Events:
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        await self.bot.change_presence(game=discord.Game(name='-help'))
        app_info = await self.bot.application_info()
        self.bot.invite_url = discord.utils.oauth_url(app_info.id, discord.Permissions(8))
        print(f'Logged in as {self.bot.user.name}\nBot invite link: {self.bot.invite_url}')

    async def on_member_join(self, member):
        config = await self.bot.db.get_config(member.guild.id)
        category = 'bots' if member.bot else 'users'

        assigned = config['autorole'][category]

        if assigned:
            if not member.guild.me.guild_permissions.manage_roles:
                return

            roles = [discord.utils.get(member.guild.roles, id=int(r)) for r in assigned if discord.utils.get(member.guild.roles, id=int(r))]
            try:
                await member.add_roles(*roles, reason='[ Parallax AutoRole ]')
            except (discord.Forbidden, discord.HTTPException):
                pass

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
                permissions = '\n'.join(f'- {p.title().replace("_", " ")}' for p in error.missing_perms)
                await ctx.send(f'**You need the following permissions:**\n{permissions}')

            elif isinstance(error, errors.BotMissingPermissions):
                permissions = '\n'.join(f'- {p.title().replace("_", " ")}' for p in error.missing_perms)
                await ctx.send(f'**Missing required permissions:**\n{permissions}')

            else:
                pass
        except: # noqa: bare-except
            pass  # lol


def setup(bot):
    bot.add_cog(Events(bot))
