import asyncio
import time
from datetime import datetime

import discord


class Watcher:
    def __init__(self, bot):
        self.bot = bot
        self.r = bot.r
        try:
            self.task = bot.loop.create_task(self.watch_db())
        except asyncio.CancelledError:
            pass

    async def remove_entry(self, guild_id: int, user_id: int, table: str):
        await self.r.table(table) \
            .filter({'user_id': str(user_id), 'guild_id': str(guild_id)}) \
            .delete() \
            .run(self.bot.connection)

    async def resolve_user(self, u_id: int):
        return self.bot.get_user(u_id) or await self.bot.get_user_info(u_id)

    async def watch_db(self):
        await self.bot.wait_until_ready()
        print('Watching for timed mutes and bans')

        while True:
            now = time.time()
            bans = await self.r.table('bans').run(self.bot.connection)
            mutes = await self.r.table('mutes').run(self.bot.connection)

            for entry in bans.items:
                try:
                    if int(entry['due']) > now:
                        continue

                    guild = self.bot.get_guild(int(entry['guild_id']))
                    user = await self.resolve_user(int(entry['user_id']))

                    if not guild or guild.unavailable or not guild.me.guild_permissions.ban_members:
                        continue

                    try:
                        await guild.unban(discord.Object(id=user.id), reason='[ Auto-Unban ] Expired')
                    except (discord.HTTPException, discord.Forbidden):  # !?!?
                        pass
                    else:
                        await self.remove_entry(guild.id, user.id, 'bans')
                        db = await self.r.table('settings').get(str(guild.id)).run(self.bot.connection)

                        if db is not None and db['logChannel']:
                            await self.post_modlog_entry(int(db['logChannel']), ('Unbanned', 'Unban'), user)
                except Exception as e:
                    print('Got exception in unban\n\t', e)

            for entry in mutes.items:
                try:
                    if int(entry['due']) > now:
                        continue

                    guild = self.bot.get_guild(int(entry['guild_id']))
                    user = await self.resolve_user(int(entry['user_id']))

                    if not guild or guild.unavailable or not guild.me.guild_permissions.manage_roles:
                        continue

                    db = await self.r.table('settings').get(str(guild.id)).run(self.bot.connection)
                    member = guild.get_member(user.id)

                    if not db or not member or not db['mutedRole']:
                        continue

                    await self.remove_entry(guild.id, user.id, 'mutes')

                    try:
                        await member.remove_roles(discord.Object(id=int(entry['role_id'])), reason='[ Auto-Unmute ] Expired')
                    except (discord.HTTPException, discord.Forbidden):  # !?!?
                        pass
                    else:
                        if db['logChannel']:
                            await self.post_modlog_entry(int(db['logChannel']), ('Unmuted', 'Unmute'), user)
                except Exception as e:
                    print('Got exception in unmute\n\t', e)

            bans.close()
            mutes.close()

            await asyncio.sleep(10)  # Run every 10 seconds :D

    async def post_modlog_entry(self, channel_id, action, target: discord.User):
        channel = self.bot.get_channel(channel_id)

        if channel:
            permissions = channel.permissions_for(channel.guild.me)
            if permissions.send_messages and permissions.embed_links:
                embed = discord.Embed(color=0x53dc39,
                                      title=f'**User {action[0]}**',
                                      description=f'**Target:** {target} ({target.id})\n'
                                                  f'**Reason:** [ Auto-{action[1]} ] Expired',
                                      timestamp=datetime.utcnow())
                embed.set_footer(text=f'Performed by {self.bot.user}', icon_url=self.bot.user.avatar_url_as(format='png'))
                await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Watcher(bot))


def teardown(bot):
    bot.get_cog('Watcher').task.cancel()
