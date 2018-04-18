import asyncio
import textwrap
import time
from asyncio.subprocess import PIPE

import discord
from discord.ext import commands
from utils import pagination


class Admin:
    def __init__(self, bot):
        self.bot = bot
        self._eval = {
            'env': {},
            'count': 0
        }

    @commands.command()
    @commands.is_owner()
    async def reboot(self, ctx):
        await self.bot.logout()

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
        self._eval['env'].update({
            'self': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'channel': ctx.message.channel,
            'guild': ctx.message.guild,
            'author': ctx.message.author,
        })

        silent = code.startswith('--silent')
        code = code.replace('```py\n', '').replace('```', '').replace('`', '').replace('--silent', '')

        _code = 'async def func(self):\n  try:\n{}\n  finally:\n    self._eval[\'env\'].update(locals())'\
            .format(textwrap.indent(code, '    '))

        before = time.monotonic()
        try:
            exec(_code, self._eval['env'])

            func = self._eval['env']['func']
            output = await func(self)

            if output:
                output = repr(output)
        except Exception as e:
            output = '{}: {}'.format(type(e).__name__, e)
        after = time.monotonic()
        self._eval['count'] += 1
        count = self._eval['count']

        code = code.split('\n')
        if len(code) == 1:
            _in = 'In [{}]: {}'.format(count, code[0])
        else:
            _first_line = code[0]
            _rest = code[1:]
            _rest = '\n'.join(_rest)
            _countlen = len(str(count)) + 2
            _rest = textwrap.indent(_rest, '...: ')
            _rest = textwrap.indent(_rest, ' ' * _countlen)
            _in = 'In [{}]: {}\n{}'.format(count, _first_line, _rest)

        message = '```py\n{}'.format(_in)
        if output:
            message += '\nOut[{}]: {}'.format(count, output)
        ms = int(round((after - before) * 1000))
        message += '\n# {} ms\n```'.format(ms)

        if not silent:
            try:
                await ctx.send(message)
            except discord.HTTPException:
                await ctx.send("Output was too big to be printed.")

    @commands.command()
    @commands.is_owner()
    async def setgame(self, ctx, *, game: str):
        """ Changes the current game """
        await self.bot.change_presence(game=discord.Game(name=game))
        await ctx.send('Game set :thumbsup:')


def setup(bot):
    bot.add_cog(Admin(bot))
