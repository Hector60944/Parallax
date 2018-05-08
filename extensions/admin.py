import asyncio
import textwrap
from asyncio.subprocess import PIPE

import discord
from discord.ext import commands

from utils import hastepaste, pagination


class Admin:
    def __init__(self, bot):
        self.bot = bot
        self.env = {}

    @commands.command()
    @commands.is_owner()
    async def reboot(self, ctx):
        await self.bot.logout()

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, *modules: str):
        """ Reload an extension """
        failed = []
        for module in modules:
            try:
                self.bot.unload_extension(f'extensions.{module}')
                self.bot.load_extension(f'extensions.{module}')
            except (ImportError, SyntaxError, ModuleNotFoundError) as exception:
                failed.append((module, str(exception)))

        if failed:
            formatted = '\n'.join([f'{f[0]:15} - {f[1]}' for f in failed])
            await ctx.send(f'**{len(failed)}** extensions failed to reload\n```\n{formatted}```')
        else:
            await ctx.send('All modules reloaded successfully.')

    @commands.command()
    @commands.is_owner()
    async def cleanup(self, ctx, amount: int):
        """ Cleans up messages sent by the bot """
        if amount <= 0 or amount > 100:
            return await ctx.send('Invalid amount.')

        await ctx.channel.purge(limit=amount, check=lambda m: m.author.id == self.bot.user.id, bulk=False)

    @commands.command()
    @commands.is_owner()
    async def bash(self, ctx, *, command: str):
        """ Execute bash commands """

        proc = await asyncio.create_subprocess_shell(command, stdin=None, stderr=PIPE, stdout=PIPE)
        out = (await proc.stdout.read()).decode('utf-8')
        err = (await proc.stderr.read()).decode('utf-8')

        if not out and not err:
            return await ctx.message.add_reaction('👌')

        if out:
            pages = pagination.paginate(out, 1950)
            for page in pages:
                await ctx.send(f"```bash\n{page}\n```")

        if err:
            pages = pagination.paginate(err, 1950)
            for page in pages:
                await ctx.send(f"```bash\n{page}\n```")

    @commands.command()
    @commands.is_owner()
    async def eval(self, ctx, *, code: str):
        """ Evaluate Python code """
        if code == 'exit()':
            self.env.clear()
            return await ctx.send('Environment cleared')

        self.env.update({
            'self': self,
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'channel': ctx.message.channel,
            'guild': ctx.message.guild,
            'author': ctx.message.author,
        })

        code = code.replace('```py\n', '').replace('```', '').replace('`', '').strip()

        _code = 'async def func():\n  try:\n{}\n  finally:\n    self.env.update(locals())'\
            .format(textwrap.indent(code, '    '))

        try:
            exec(_code, self.env)

            func = self.env['func']
            output = await func()

            output = repr(output) if output else str(output)
        except Exception as e:
            output = '{}: {}'.format(type(e).__name__, e)

        code = code.split('\n')
        s = ''
        for i, line in enumerate(code):
            s += '>>> ' if i == 0 else '... '
            s += line + '\n'

        message = f'```py\n{s}\n{output}\n```'

        try:
            await ctx.send(message)
        except discord.HTTPException:
            paste = await hastepaste.create(message)
            await ctx.send(f'Output too big: <{paste}>')

    @commands.command()
    @commands.is_owner()
    async def setgame(self, ctx, *, game: str):
        """ Changes the current game """
        await self.bot.change_presence(game=discord.Game(name=game))
        await ctx.send('Game set :thumbsup:')


def setup(bot):
    bot.add_cog(Admin(bot))
