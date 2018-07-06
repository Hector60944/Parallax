from datetime import datetime

import discord
import pytz
from discord.ext import commands


class Profile:
    def __init__(self, bot):
        self.bot = bot

    async def update_profile(self, user_id: int, profile: dict):
        profile.update({'id': str(user_id)})
        await self.bot.r.table('profiles') \
            .insert(profile, conflict='update') \
            .run(self.bot.connection)

    async def get_profile(self, user_id: int):
        return await self.bot.r.table('profiles') \
            .get(str(user_id)) \
            .default({
                'timezone': None,
                'notes': {}
            }) \
            .run(self.bot.connection)

    @commands.group()
    async def profile(self, ctx):
        if not ctx.invoked_subcommand:
            _help = await self.bot.formatter.format_help_for(ctx, ctx.command)

            for page in _help:
                await ctx.send(page)

    @profile.command()
    async def show(self, ctx, *, user: discord.User=None):
        """ Check your, or another user's profile """
        user = user or ctx.author
        profile = await self.get_profile(user.id)

        tz = pytz.timezone(profile['timezone']) if profile['timezone'] else None

        await ctx.send(f'''**{user.name}\'s profile**\n```prolog
Timezone    : {profile['timezone'] or 'Unknown'}
Current Time: {datetime.now(tz).strftime('%H:%M:%S')}
Note        : {profile['notes'].get(str(ctx.guild.id))}
```''')

    @profile.command()
    async def timezone(self, ctx, *, tz: str):
        """ Sets your profile timezone

        For best results, format like `Europe/London` or `Europe/Amsterdam` etc"""
        try:
            pytz.timezone(tz)
        except pytz.exceptions.UnknownTimeZoneError:
            await ctx.send('Unknown timezone. For best results, format like `Europe/London` or `Europe/Amsterdam` etc')
        else:
            profile = await self.get_profile(ctx.author.id)
            profile['timezone'] = tz
            await self.update_profile(ctx.author.id, profile)
            await ctx.send('Timezone updated!')

    @profile.command(name='listtimezones', aliases=['listtz', 'ltz'])
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.user)
    async def list_timezones(self, ctx):
        """ Displays a list of all valid timezones """
        tzs = '\r\n'.join(pytz.all_timezones).encode()
        await ctx.send(file=discord.File(tzs, filename='timezones.txt'))

    @profile.command(aliases=['notes'])
    async def note(self, ctx, *, message: commands.clean_content(fix_channel_mentions=True)=None):
        """ Sets a note on your profile for this server """
        profile = await self.get_profile(ctx.author.id)
        profile['notes'][str(ctx.guild.id)] = message
        await self.update_profile(ctx.author.id, profile)
        await ctx.send('Note updated!')


def setup(bot):
    bot.add_cog(Profile(bot))
