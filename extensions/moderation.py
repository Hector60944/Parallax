from datetime import datetime

import discord
from discord.ext import commands
from utils import interaction


class Helpers:
    def __init__(self, bot):
        self.bot = bot

    async def get_warns(self, user: int, guild_id: int):
        warns = await self.bot.r.table('warns').get(str(user)).run(self.bot.connection)

        if warns and str(guild_id) in warns:
            return warns[str(guild_id)]

        return 0

    async def set_warns(self, user: int, guild_id: int, warns: int):
        await self.bot.r.table('warns') \
            .insert({'id': str(user), str(guild_id): warns}, conflict='update') \
            .run(self.bot.connection)

    async def post_modlog_entry(self, guild_id: int, action: str, target: discord.User, moderator: discord.User, reason: str):
        config = await self.bot.db.get_config(guild_id)

        if config['logChannel']:
            channel = self.bot.get_channel(int(config['logChannel']))
            if channel:
                permissions = channel.permissions_for(channel.guild.me)
                if permissions.send_messages and permissions.embed_links:
                    embed = discord.Embed(color=0xbe2f2f,
                                          title=f'**User {action}**',
                                          description=f'**Target:** {target} ({target.id})\n'
                                                      f'**Reason:** {reason}',
                                          timestamp=datetime.now())
                    embed.set_footer(text=f'Performed by {moderator}', icon_url=moderator.avatar_url_as(format='png'))
                    await channel.send(embed=embed)


class Moderation:
    def __init__(self, bot):
        self.bot = bot
        self.helpers = Helpers(bot)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member, reason: commands.clean_content(fix_channel_mentions=True)='None specified', time: str=None):
        """ Bans a user from the server """
        if not interaction.check_hierarchy(ctx.me, member):
            return await ctx.send("Role hierarchy prevents me from doing that.")

        if not interaction.check_hierarchy(ctx.author, member, owner_check=True):
            return await ctx.send("Role hierarchy prevents you from doing that.")

        await member.ban(reason=f'[ {ctx.author} ] {reason}', delete_message_days=7)
        await ctx.message.add_reaction('🔨')
        await self.helpers.post_modlog_entry(ctx.guild.id, 'Banned', member, ctx.author, reason)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member, *, reason: commands.clean_content(fix_channel_mentions=True)='None specified'):
        """ Kicks a user from the server """
        if not interaction.check_hierarchy(ctx.me, member):
            return await ctx.send("Role hierarchy prevents me from doing that.")

        if not interaction.check_hierarchy(ctx.author, member, owner_check=True):
            return await ctx.send("Role hierarchy prevents you from doing that.")

        await member.kick(reason=f'[ {ctx.author} ] {reason}')
        await ctx.message.add_reaction('👢')
        await self.helpers.post_modlog_entry(ctx.guild.id, 'Kicked', member, ctx.author, reason)

    @commands.command(aliases=['d', 'purge', 'prune', 'clear', 'delete', 'remove'])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.guild_only()
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
    @commands.guild_only()
    async def warn(self, ctx, member: discord.Member, *, reason: commands.clean_content(fix_channel_mentions=True)='None specified'):
        """ Issues a warning to the given user """
        if not interaction.check_hierarchy(ctx.me, member):
            return await ctx.send("Role hierarchy prevents me from doing that.")

        if not interaction.check_hierarchy(ctx.author, member, owner_check=True):
            return await ctx.send("Role hierarchy prevents you from doing that.")

        threshold = (await self.bot.db.get_config(ctx.guild.id))['warnThreshold']
        current_warns = await self.helpers.get_warns(member.id, ctx.guild.id) + 1

        if threshold != 0:
            amount = current_warns % threshold

            if amount == 0:
                await member.ban(reason=f'[ {ctx.author} ] Too many warnings', delete_message_days=7)
                await ctx.send(f'Banned **{member.name}** for hitting the warning limit ({threshold}/{threshold})')
            else:
                await ctx.send(f'Warned **{member}** for **{reason}** (Warnings: {amount}/{threshold})')
        else:
            await ctx.send(f'Warned **{member}** for **{reason}** (Warnings: {current_warns})')

        await self.helpers.set_warns(member.id, ctx.guild.id, current_warns)
        await self.helpers.post_modlog_entry(ctx.guild.id, 'Warned', member, ctx.author, reason)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    async def mute(self, ctx, member: discord.Member, reason: commands.clean_content(fix_channel_mentions=True)='None specified', time: str=None):
        """ Mutes the specified user """
        if not interaction.check_hierarchy(ctx.me, member):
            return await ctx.send("Role hierarchy prevents me from doing that.")

        if not interaction.check_hierarchy(ctx.author, member, owner_check=True):
            return await ctx.send("Role hierarchy prevents you from doing that.")

        config = await self.bot.db.get_config(ctx.guild.id)
        if not config['mutedRole']:
            return await ctx.send('A muted role hasn\'t been configured for this server. '
                                  'You can change the role by using the `config` command.')

        role = discord.utils.get(ctx.guild.roles, id=int(config['mutedRole']))

        if not role:
            return await ctx.send('A muted role was configured for this server but no longer exists. '
                                  'You can change the role by using the `config` command.')

        if role.position > ctx.me.top_role.position:
            return await ctx.send('The muted role\'s position is higher than my top role. Unable to assign the role')

        await member.add_roles(role, reason=f'[ {ctx.author} ] {reason}')
        await ctx.send('Muted')
        await self.helpers.post_modlog_entry(ctx.guild.id, 'Muted', member, ctx.author, reason)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    async def unmute(self, ctx, member: discord.Member, *, reason: commands.clean_content(fix_channel_mentions=True)='None specified'):
        """ Unmutes the specified user """
        if not interaction.check_hierarchy(ctx.me, member):
            return await ctx.send("Role hierarchy prevents me from doing that.")

        if not interaction.check_hierarchy(ctx.author, member, owner_check=True):
            return await ctx.send("Role hierarchy prevents you from doing that.")

        config = await self.bot.db.get_config(ctx.guild.id)
        if not config['mutedRole']:
            return await ctx.send('A muted role hasn\'t been configured for this server. '
                                  'You can change the role by using the `config` command.')

        role = discord.utils.get(ctx.guild.roles, id=int(config['mutedRole']))

        if not role:
            return await ctx.send('A muted role was configured for this server but no longer exists. '
                                  'You can change the role by using the `config` command.')

        if role.position > ctx.me.top_role.position:
            return await ctx.send('The muted role\'s position is higher than my top role. Unable to unassign the role')

        await member.remove_roles(role, reason=f'[ {ctx.author} ] {reason}')
        await ctx.send('Unmuted')
        await self.helpers.post_modlog_entry(ctx.guild.id, 'Unmuted', member, ctx.author, reason)


def setup(bot):
    bot.add_cog(Moderation(bot))
