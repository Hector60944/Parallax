package me.devoxin.parallax.commands

import me.devoxin.parallax.flight.Command
import me.devoxin.parallax.flight.CommandProperties
import me.devoxin.parallax.flight.Context


@CommandProperties(description = "Testing invalid args")
class ipt : Command {

    override suspend fun run(ctx: Context) {
        val role = ctx.resolveRole()
                ?: return ctx.send("${ctx.trigger}ipt <role>")

        ctx.send(role.name)
    }

}