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

    async def get_expired(self, table: str):
        t = time.time()

        return await self.r.table(table) \
            .filter(self.r.row['due'].coerce_to('number') <= t) \
            .coerce_to('array') \
            .run(self.bot.connection)

    async def resolve_user(self, u_id: int):
        return self.bot.get_user(u_id) or await self.bot.get_user_info(u_id)

    async def watch_db(self):
        await self.bot.wait_until_ready()
        print('Watching for timed mutes and bans')

        while True:
            bans = await self.get_expired('bans')
            mutes = await self.get_expired('mutes')

            for entry in bans:
                try:
                    guild = self.bot.get_guild(int(entry['guild_id']))
                    user = await self.resolve_user(int(entry['user_id']))

                    if not guild or guild.unavailable or not guild.me.guild_permissions.ban_members:
                        continue

                    try:
                        await guild.unban(discord.Object(id=user.id), reason='[ AutoMod ] Ban Expired')
                    except discord.NotFound:  # User was unbanned before Parallax could unban
                        await self.bot.db.remove_timed_entry(guild.id, user.id, 'bans')
                    except (discord.HTTPException, discord.Forbidden) as exception:  # !?!?
                        print('Failed to unban member {} in guild {}:\n\t'.format(user.id, guild.id), exception)
                    else:
                        await self.bot.db.remove_timed_entry(guild.id, user.id, 'bans')
                        db = await self.r.table('settings').get(str(guild.id)).run(self.bot.connection)

                        if db is not None and db['logChannel']:
                            await self.post_modlog_entry(int(db['logChannel']), ('Unbanned', 'Ban'), user)
                except Exception as e:
                    print('Exception in unban:\n\t', e)

            for entry in mutes:
                try:
                    guild = self.bot.get_guild(int(entry['guild_id']))
                    user = await self.resolve_user(int(entry['user_id']))

                    if not guild or guild.unavailable or not guild.me.guild_permissions.manage_roles:
                        continue

                    db = await self.r.table('settings').get(str(guild.id)).run(self.bot.connection)
                    member = guild.get_member(user.id)

                    if not db or not member or not db['mutedRole']:
                        continue

                    await self.bot.db.remove_timed_entry(guild.id, user.id, 'mutes')

                    try:
                        await member.remove_roles(discord.Object(id=int(entry['role_id'])), reason='[ AutoMod ] Mute Expired')
                    except (discord.HTTPException, discord.Forbidden) as exception:  # !?!?
                        print('Failed to unmute member {} in guild {}:\n\t'.format(member.id, guild.id), exception)
                    else:
                        if db['logChannel']:
                            await self.post_modlog_entry(int(db['logChannel']), ('Unmuted', 'Mute'), user)
                except Exception as e:
                    print('Exception in unmute:\n\t', e)

            await asyncio.sleep(10)  # Run every 10 seconds :D

    async def post_modlog_entry(self, channel_id, action, target: discord.User):
        channel = self.bot.get_channel(channel_id)

        if channel:
            permissions = channel.permissions_for(channel.guild.me)
            if permissions.send_messages and permissions.embed_links:
                embed = discord.Embed(color=0x53dc39,
                                      title=f'**User {action[0]}**',
                                      description=f'**Target:** {target} ({target.id})\n'
                                                  f'**Reason:** [ AutoMod ] {action[1]} Expired',
                                      timestamp=datetime.utcnow())
                embed.set_footer(text=f'Performed by {self.bot.user}', icon_url=self.bot.user.avatar_url_as(format='png'))
                await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Watcher(bot))


def teardown(bot):
    bot.get_cog('Watcher').task.cancel()
