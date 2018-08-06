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
        description = "Bans a user from the server",
        triggers = ["b"],
        category = CommandCategory.Moderation,
        botPermissions = [Permission.BAN_MEMBERS],
        userPermissions = [Permission.BAN_MEMBERS]
)
class Ban : Command {

    override suspend fun run(ctx: Context) {
        val userId = ctx.args.resolveMemberId() ?: return ctx.send("You need to specify a valid user/ID")
        val reason = ctx.args.resolveString(true).opt("No reason specified")

        val member = ctx.guild.getMemberById(userId)

        if (member != null) {
            if (!ctx.member.canInteract(member)) {
                return ctx.send("Role hierarchy prevents you from doing that.")
            }

            if (!ctx.selfMember.canInteract(member)) {
                return ctx.send("Role hierarchy prevents me from doing that.")
            }
        }

        ctx.guild.controller.ban(userId, 7, "[ ${ctx.author.tag()} ] $reason").queue({
            ctx.message.addReaction("\uD83D\uDC4C").queue()
            //ctx.dispatchModLogEntry(Context.Severity.HIGH, "Banned", user, reason)
        }, {
            if (it is IllegalArgumentException) {
                ctx.send("Unable to ban: the user ID `$userId` is invalid.")
            } else {
                ctx.send(it.toString())
            }
        })
    }

}
