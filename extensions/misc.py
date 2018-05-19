import re
import subprocess
from datetime import datetime
from time import time

import discord
import psutil
from discord.ext import commands

from utils import timeparser

mention_rx = re.compile(r'<@!?(\d{16,19})>')
activities = {
    0: 'Playing',
    1: 'Streaming',
    2: 'Listening to',
    3: 'Watching'
}


def get_version():
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').strip()


def f_time(time):
    h, r = divmod(int(time.total_seconds()), 3600)
    m, s = divmod(r, 60)
    d, h = divmod(h, 24)

    return "%02d:%02d:%02d:%02d" % (d, h, m, s)


def is_mention(content: str):
    return mention_rx.match(content)


class Misc:
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process()
        self.internal = [42, 42, 68, 101, 118, 101, 108, 111, 112, 101, 114, 58, 42, 42, 32]

    async def resolve_user_id(self, user_id: int):
        user = self.bot.get_user(user_id)
        if not user:
            try:
                user = await self.bot.get_user_info(user_id)
            except discord.NotFound:
                return None
        return user

    async def get_user(self, content: str):
        mention = is_mention(content)
        if mention:
            return await self.resolve_user_id(mention.group(1))

        if content.isdigit():
            return await self.resolve_user_id(int(content))

        if len(content) > 5 and content[-5] == '#':
            return discord.utils.find(lambda u: str(u) == content, self.bot.users)

        return discord.utils.get(self.bot.users, name=content)

    @commands.command()
    async def invite(self, ctx):
        """ Displays Parallax's invite """
        await ctx.send(f'Add me to your server with this URL: **<{self.bot.invite_url}>**')

    @commands.command(aliases=['ui', 'user'])
    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    async def userinfo(self, ctx, user: str=None):
        """ Returns information about a user

        Search methods: user[#discrim] | id | mention
        """
        if not user:
            user = ctx.author
        else:
            user = await self.get_user(user)

        if not user:
            return await ctx.send('No users found matching that query.')

        member = ctx.guild.get_member(user.id)
        activity = f'{activities[member.game.type]} `{member.game.name}`' if getattr(member, 'game', None) else 'Playing: `Unknown`'

        embed = discord.Embed(color=0xbe2f2f,
                              description=activity)
        embed.set_author(name=f'{user} ({user.id})', icon_url=user.avatar_url_as(format='png'))
        embed.add_field(name='Account Type', value='User' if not user.bot else 'Bot', inline=True)
        embed.add_field(name='Created on', value=f'{user.created_at.strftime("%d.%m.%Y")}\n({(datetime.utcnow() - user.created_at).days} days ago)', inline=True)

        if member:
            embed.add_field(name='Joined on', value=f'{member.joined_at.strftime("%d.%m.%Y")}\n({(datetime.utcnow() - member.joined_at).days} days ago)', inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    async def avatar(self, ctx, user: discord.User=None):
        """ Links your (or another user's) avatar """
        avatar = (user or ctx.author).avatar_url
        await ctx.send(avatar)

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def server(self, ctx):
        """ Displays server information """
        bots = sum(1 for m in ctx.guild.members if m.bot)
        bot_percent = bots / len(ctx.guild.members) * 100
        embed = discord.Embed(color=0xbe2f2f,
                              title=f'Server Info | {ctx.guild.name} ({ctx.guild.id})',
                              description=f'**Owner:** {ctx.guild.owner}',
                              timestamp=ctx.guild.created_at)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(name='Members', value=f'Bots: {bots} ({bot_percent:.2f}%)\nTotal: {len(ctx.guild.members)}', inline=True)
        embed.add_field(name='Region', value=ctx.guild.region, inline=True)
        embed.add_field(name='Verification Level', value=ctx.guild.verification_level.name.title(), inline=True)
        embed.add_field(name='Content Filter', value=ctx.guild.explicit_content_filter.name.title(), inline=True)
        embed.set_footer(text='Created on')

        await ctx.send(embed=embed)

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def stats(self, ctx):
        """ Displays Parallax's statistics """
        u = str(self.bot.get_user(180093157554388993) or await self.bot.get_user_info(180093157554388993))
        s = ''.join([chr(c) for c in self.internal]) + u

        uptime = f_time(datetime.now() - self.bot.startup)
        ram = self.process.memory_full_info().rss / 1024**2
        threads = self.process.num_threads()

        embed = discord.Embed(color=0xbe2f2f,
                              title=f'Parallax ({get_version()})',
                              description=s)
        embed.add_field(name='Uptime', value=uptime, inline=True)
        embed.add_field(name='RAM Usage', value=f'{ram:.2f} MB', inline=True)
        embed.add_field(name='Threads', value=threads, inline=True)
        embed.add_field(name='Servers', value=len(self.bot.guilds), inline=True)
        embed.add_field(name='Users', value=len(self.bot.users), inline=True)
        embed.add_field(name='Messages Seen', value=self.bot.messages_seen, inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    async def remindme(self, ctx, when: str, *, reminder: str):
        """ Reminds you of the given message at the given time

        when    : Anything from seconds up to weeks. Format as "1 second" or "1s"
        reminder: The content of the reminder"""
        parsed = timeparser.parse(when)

        if not parsed or parsed.absolute <= time():
            return await ctx.send('You must specify a valid time ahead of now.')

        if parsed.relative > 31540000:  # 1 year, this one's for you Adam
            return await ctx.send('Time cannot exceed 1 year.')

        await self.bot.db.add_reminder(ctx.author.id, parsed.absolute, reminder)
        await ctx.send(f'Alright! I will remind you on **{parsed.humanized}**')


def setup(bot):
    bot.add_cog(Misc(bot))
