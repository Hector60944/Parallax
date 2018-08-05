package me.devoxin.parallax.commands.configuration

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


    }

}
