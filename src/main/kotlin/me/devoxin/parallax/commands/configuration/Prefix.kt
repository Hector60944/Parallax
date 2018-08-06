package me.devoxin.parallax.commands.configuration

import me.devoxin.parallax.Database
import me.devoxin.parallax.flight.Command
import me.devoxin.parallax.flight.CommandCategory
import me.devoxin.parallax.flight.CommandProperties
import me.devoxin.parallax.flight.Context
import net.dv8tion.jda.core.Permission


@CommandProperties(
        description = "Sets the server prefix",
        userPermissions = [Permission.MANAGE_SERVER],
        category = CommandCategory.Configuration
)
class Prefix : Command {

    override suspend fun run(ctx: Context) {
        val newPrefix = ctx.args.resolveString()

        if (newPrefix.isEmpty()) {
            return ctx.send("Prefix may not be blank.")
        }

        Database.setPrefix(ctx.guild.id, newPrefix)
        ctx.send("Updated server prefix.")
    }

}
