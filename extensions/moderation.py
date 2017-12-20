import discord
from discord.ext import commands
from .utils import interaction


class Moderation:
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, reason: str = 'None specified', time: str = None):
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
    async def kick(self, ctx, member: discord.Member, reason: str = 'None specified'):
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
    async def clean(self, ctx, amount: int, filter: str=None):
        """ Deletes messages in a channel """
        pred = None

        if filter:
            if '-bot' in filter:
                pred = lambda m: m.author.bot
            if '-users' in filter:
                pred = lambda m: m.author.bot is False
        if amount <= 0:
            return await ctx.send("Who you tryna fool?")

        if amount >= 1000:
            amount = 1000

        try:
            await ctx.channel.purge(limit=amount + 1, check=pred)
        except discord.HTTPException:
            await ctx.send("The bot is missing permissions to delete messages.")

def setup(bot):
    bot.add_cog(Moderation(bot))
