import re
from datetime import datetime

import discord
from discord.ext.commands import errors

from utils.interaction import HierarchicalError, get_channel

invite_rx = re.compile(r'discord(?:app\.com\/invite|\.gg)\/([a-z0-9]{1,16})', re.IGNORECASE)


class Events:
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Game(name='-help'))
        app_info = await self.bot.application_info()
        self.bot.invite_url = discord.utils.oauth_url(app_info.id, discord.Permissions(8))
        print(f'Logged in as {self.bot.user.name}\nBot invite link: {self.bot.invite_url}')

    async def on_message_delete(self, message):
        if not message.guild or not message.content:
            return

        cleaned = invite_rx.sub('[INVITE]', message.content).replace('[', '\[')
        store = {
            'id': str(message.channel.id),
            'content': cleaned,
            'author': f'{str(message.author)} ({message.author.id})',
            'timestamp': str(message.created_at)
        }

        await self.bot.r.table('snipes').insert(store, conflict='replace').run(self.bot.connection)

        config = await self.bot.db.get_config(message.guild.id)
        channel = get_channel(self.bot, config['messages']['deleteLog'])

        if channel:
            embed = discord.Embed(color=0xbe2f2f, description=message.content)
            embed.set_author(name=str(message.author), icon_url=message.author.avatar_url_as(format='png'))
            embed.set_footer(text=f'Message ID: {message.id}')
            try:
                await channel.send(embed=embed)
            except (discord.HTTPException, discord.Forbidden):
                pass

    async def on_member_join(self, member):
        config = await self.bot.db.get_config(member.guild.id)
        account_age = config['accountAge']
        verification = config['verificationRole']

        log = get_channel(self.bot, config['messages']['joinLog'])
        join = config['messages']['joinMessage']

        category = 'bots' if member.bot else 'users'
        assigned = config['autorole'][category]

        if log:
            embed = discord.Embed(color=0x3f94e8, description='Member Joined', timestamp=datetime.utcnow())
            embed.set_author(name=f'{str(member)} ({member.id})', icon_url=member.avatar_url)
            try:
                await log.send(embed=embed)
            except (discord.Forbidden, discord.HTTPException):
                pass

        if account_age and verification and member.guild.me.guild_permissions.manage_roles:
            now = datetime.utcnow()

            if (now - member.created_at).total_seconds() < int(account_age):
                role = [discord.utils.get(member.guild.roles, id=int(verification))]

                if role:
                    try:
                        await member.add_roles(*role, reason='[ Parallax Anti-Alt ] New account requires verification')
                    except (discord.Forbidden, discord.HTTPException):
                        pass

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

    async def on_member_remove(self, member):
        config = await self.bot.db.get_config(member.guild.id)
        log = get_channel(self.bot, config['messages']['leaveLog'])
        leave = config['messages']['leaveMessage']

        if log:
            embed = discord.Embed(color=0x3f94e8, description='Member Left', timestamp=datetime.utcnow())
            embed.set_author(name=f'{str(member)} ({member.id})', icon_url=member.avatar_url)
            try:
                await log.send(embed=embed)
            except (discord.Forbidden, discord.HTTPException):
                pass

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

    async def on_command_error(self, ctx, error):
        try:
            if isinstance(error, (errors.MissingRequiredArgument, errors.BadArgument)):
                if isinstance(error, errors.MissingRequiredArgument):
                    msg = f'You need to specify `{error.param.name}`'
                elif isinstance(error, errors.BadArgument):
                    msg = error.args[0].replace('"', '`')

                msg += f'\n\nUse `{ctx.prefix}help {ctx.command}` to view the syntax of the command'

                await ctx.send(msg)

            elif hasattr(error, 'original') and isinstance(error.original, HierarchicalError):
                await ctx.send(error.original)

            elif isinstance(error, errors.CommandInvokeError):
                print(f'Command {ctx.command.name.upper()} encountered an error:\n\t{error}')
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
        except (discord.Forbidden, discord.HTTPException):
            pass


def setup(bot):
    bot.add_cog(Events(bot))
