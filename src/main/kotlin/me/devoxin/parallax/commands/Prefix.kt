package me.devoxin.parallax.commands

import me.devoxin.parallax.Database
import me.devoxin.parallax.flight.Command
import me.devoxin.parallax.flight.CommandProperties
import me.devoxin.parallax.flight.Context


@CommandProperties(description = "Sets the server prefix", developerOnly = true)
class Prefix : Command {

    override suspend fun run(ctx: Context) {
        val newPrefix = ctx.resolveString()

        if (newPrefix.isEmpty()) {
            return ctx.send("ok so you want a blank prefix")
        }

        Database.setPrefix(ctx.guild.id, newPrefix)
        ctx.send("k done")
    }

}