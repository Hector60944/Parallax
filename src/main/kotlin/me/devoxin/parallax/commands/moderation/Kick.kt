package me.devoxin.parallax.commands.moderation

import me.devoxin.parallax.flight.Command
import me.devoxin.parallax.flight.CommandCategory
import me.devoxin.parallax.flight.CommandProperties
import me.devoxin.parallax.flight.Context
import me.devoxin.parallax.utils.await
import me.devoxin.parallax.utils.opt
import me.devoxin.parallax.utils.tag
import net.dv8tion.jda.core.Permission


@CommandProperties(
        description = "Kicks a user from the server",
        triggers = ["k"],
        botPermissions = [Permission.KICK_MEMBERS],
        userPermissions = [Permission.KICK_MEMBERS],
        category = CommandCategory.Moderation
)
class Kick : Command {

    override suspend fun run(ctx: Context) {
        val user = ctx.args.resolveMember() ?: return ctx.send("You need to specify a valid user/ID")
        val reason = ctx.args.resolveString(true).opt("No reason specified")

        if (!ctx.member.canInteract(user)) {
            return ctx.send("Role hierarchy prevents you from doing that.")
        }

        if (!ctx.selfMember.canInteract(user)) {
            return ctx.send("Role hierarchy prevents me from doing that.")
        }

        ctx.guild.controller.kick(user, "[ ${ctx.author.tag()} ] $reason").await()
        ctx.message.addReaction("\uD83D\uDC4C").await()
    }

}
