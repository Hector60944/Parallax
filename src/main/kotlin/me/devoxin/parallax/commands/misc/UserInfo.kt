package me.devoxin.parallax.commands.misc

import me.devoxin.parallax.flight.Command
import me.devoxin.parallax.flight.CommandProperties
import me.devoxin.parallax.flight.Context


@CommandProperties(
        description = "View information about a user"

)
class UserInfo : Command {

    override suspend fun run(ctx: Context) {
        val user = ctx.args.resolveMemberId() ?: return ctx.send("Invalid user/ID specified.")
    }

}
