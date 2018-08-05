package me.devoxin.parallax.commands.configuration

import me.devoxin.parallax.Database
import me.devoxin.parallax.flight.Command
import me.devoxin.parallax.flight.CommandCategory
import me.devoxin.parallax.flight.CommandProperties
import me.devoxin.parallax.flight.Context
import net.dv8tion.jda.core.Permission


@CommandProperties(
        description = "Sets the channel used for moderation logs",
        userPermissions = [Permission.MANAGE_SERVER],
        category = CommandCategory.Configuration
)
class ModLog : Command {

    override suspend fun run(ctx: Context) {
        val channel = ctx.resolveTextChannel(true)

        Database.setModlog(ctx.guild.id, channel?.id)

        if (channel == null) {
            ctx.send("Mod-log cleared.")
        } else {
            ctx.send("Mod-log set to ${channel.asMention}")
        }
    }

}
