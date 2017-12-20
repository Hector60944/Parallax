import discord
from discord.ext import commands
from utils import interaction


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
    async def clean(self, ctx, amount: int, predicate: str=None, *users: discord.Member):
        """ Deletes messages in a channel 
        
        You can remove messages sent by bots by specifying 'bot' as the filter.
        You can remove messages by users by specifying 'user' as the filter.
        You can remove messages by specific users by mentioning them after specifying 'user' as the filter.
        """
        pred = None

        if predicate:
            if 'bot' in predicate:
                pred = lambda m: m.author.bot
            if 'user' in predicate:
                if users:
                    pred = lambda m: any([m.author.id == u.id for u in users])
                else:
                    pred = lambda m: not m.author.bot

        if amount <= 0:
            return await ctx.send("Who you tryna fool? (Amount needs to be higher than 0)")

        if amount > 1000:
            amount = 1000

        try:
            await ctx.channel.purge(limit=amount + 1, check=pred)
        except discord.HTTPException:
            await ctx.send("An unknown error occurred while cleaning the channel.")
        except discord.NotFound:
            await ctx.send("An error occurred while deleting: Tried to delete a message that doesn't exist within the channel.")

def setup(bot):
    bot.add_cog(Moderation(bot))
