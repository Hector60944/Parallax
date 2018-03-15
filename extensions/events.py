from datetime import datetime

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
        log = config['messages']['joinLog']
        join = config['messages']['joinMessage']

        category = 'bots' if member.bot else 'users'
        assigned = config['autorole'][category]

        if assigned and member.guild.me.guild_permissions.manage_roles:

            roles = [discord.utils.get(member.guild.roles, id=int(r)) for r in assigned if discord.utils.get(member.guild.roles, id=int(r))]
            try:
                await member.add_roles(*roles, reason='[ Parallax AutoRole ]')
            except (discord.Forbidden, discord.HTTPException):
                pass

        if join['message'] and join['channel'] and not member.bot:
            channel = self.bot.get_channel(int(join['channel']))

            if channel:
                m = join['message'] \
                    .replace('{user}', member.mention) \
                    .replace('{user:tag}', str(member)) \
                    .replace('{server}', member.guild.name) \
                    .replace('{owner}', str(member.guild.owner))

                try:
                    await channel.send(m)
                except (discord.Forbidden, discord.HTTPException):
                    pass

        if log:
            channel = self.bot.get_channel(int(log))

            if channel:
                embed = discord.Embed(color=0x3f94e8, description='Member Joined', timestamp=datetime.utcnow())
                embed.set_author(name=f'{str(member)} ({member.id})', icon_url=member.avatar_url)
                try:
                    await channel.send(embed=embed)
                except (discord.Forbidden, discord.HTTPException):
                    pass

    async def on_member_remove(self, member):
        config = await self.bot.db.get_config(member.guild.id)
        log = config['messages']['leaveLog']
        leave = config['messages']['leaveMessage']

        if leave['message'] and leave['channel'] and not member.bot:
            channel = self.bot.get_channel(int(leave['channel']))

            if channel:
                m = leave['message'] \
                    .replace('{user}', member.mention) \
                    .replace('{user:tag}', str(member)) \
                    .replace('{server}', member.guild.name)

                try:
                    await channel.send(m)
                except (discord.Forbidden, discord.HTTPException):
                    pass

        if log:
            channel = self.bot.get_channel(int(log))

            if channel:
                embed = discord.Embed(color=0x3f94e8, description='Member Left', timestamp=datetime.utcnow())
                embed.set_author(name=f'{str(member)} ({member.id})', icon_url=member.avatar_url)
                try:
                    await channel.send(embed=embed)
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
                await ctx.send(f'**Error:**\n```py\n{str(error)}\n```')

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
