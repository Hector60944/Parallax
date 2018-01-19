import discord
from discord.ext import commands
from utils import interaction


class Helpers:
    def __init__(self, bot):
        self.bot = bot

    async def get_warns(self, user: int):
        warns = await self.bot.r.table('warns').get(str(user)).default({'warns': 0}).run(self.bot.connection)
        return warns['warns']

    async def set_warns(self, user: int, warns: int):
        await self.bot.r.table('warns').insert({'id': str(user), 'warns': warns}, conflict='replace').run(self.bot.connection)


class Moderation:
    def __init__(self, bot):
        self.bot = bot
        self.helpers = Helpers(bot)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, reason: str='None specified', time: str=None):
        """ Bans a user from the server """
        if not interaction.check_hierarchy(ctx.guild.me, member):
            return await ctx.send("Role hierarchy prevents me from doing that.")

        if not interaction.check_hierarchy(ctx.author, member, owner_check=True):
            return await ctx.send("Role hierarchy prevents you from doing that.")

        await member.ban(reason=f'[ {ctx.author} ] {reason}')
        await ctx.message.add_reaction('🔨')

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str='None specified'):
        """ Kicks a user from the server """
        if not interaction.check_hierarchy(ctx.guild.me, member):
            return await ctx.send("Role hierarchy prevents me from doing that.")

        if not interaction.check_hierarchy(ctx.author, member, owner_check=True):
            return await ctx.send("Role hierarchy prevents you from doing that.")

        await member.kick(reason=f'[ {ctx.author} ] {reason}')
        await ctx.message.add_reaction('👢')

    @commands.command(aliases=['d', 'purge', 'prune', 'clear', 'delete', 'remove'])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clean(self, ctx, amount: int, options: str=None, *users: discord.Member):
        """ Deletes messages in a channel

        You can remove messages sent by bots by specifying 'bot' as the filter.
        You can remove messages by users by specifying 'user' as the filter.
        You can remove messages by specific users by mentioning them after specifying 'user' as the filter.
        """
        pred = None

        if options:
            if 'bot' in options:
                pred = lambda m: m.author.bot  # noqa: E731
            if 'user' in options:
                if users:
                    pred = lambda m: any(m.author.id == u.id for u in users)  # noqa: E731
                else:
                    pred = lambda m: not m.author.bot  # noqa: E731

        if amount <= 0:
            return await ctx.send("Specify an amount above 0")

        if amount > 1000:
            amount = 1000

        try:
            await ctx.channel.purge(limit=amount, check=pred)
        except discord.HTTPException:
            await ctx.send("An unknown error occurred while cleaning the channel.")
        except discord.NotFound:
            pass

    @commands.command(aliases=['w'])
    @commands.has_permissions(ban_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str='None specified'):
        """ Issues a warning to the given user """
        if not interaction.check_hierarchy(ctx.guild.me, member):
            return await ctx.send("Role hierarchy prevents me from doing that.")

        if not interaction.check_hierarchy(ctx.author, member, owner_check=True):
            return await ctx.send("Role hierarchy prevents you from doing that.")

        warns = await self.helpers.get_warns(member.id) + 1
        await self.helpers.set_warns(member.id, warns)
        await ctx.send(f"Warned **{member}** for **{reason}** (Warnings: {warns})")

        # Eventually this will check against the server's settings. If warns > threshold then: kick or ban. **TODO

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def mute(self, ctx, member: discord.Member, reason: str='None specified', time: str=None):
        """ Mutes the specified user """
        if not interaction.check_hierarchy(ctx.guild.me, member):
            return await ctx.send("Role hierarchy prevents me from doing that.")

        if not interaction.check_hierarchy(ctx.author, member, owner_check=True):
            return await ctx.send("Role hierarchy prevents you from doing that.")

        # Also TODO

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unmute(self, ctx, member: discord.Member, *, reason: str='None specified'):
        """ Unmutes the specified user """
        if not interaction.check_hierarchy(ctx.guild.me, member):
            return await ctx.send("Role hierarchy prevents me from doing that.")

        if not interaction.check_hierarchy(ctx.author, member, owner_check=True):
            return await ctx.send("Role hierarchy prevents you from doing that.")


def setup(bot):
    bot.add_cog(Moderation(bot))
