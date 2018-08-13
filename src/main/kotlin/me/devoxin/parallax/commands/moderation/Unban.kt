package me.devoxin.parallax.commands.moderation

import me.devoxin.parallax.flight.Command
import me.devoxin.parallax.flight.CommandCategory
import me.devoxin.parallax.flight.CommandProperties
import me.devoxin.parallax.flight.Context
import me.devoxin.parallax.utils.opt
import me.devoxin.parallax.utils.tag
import net.dv8tion.jda.core.Permission
import net.dv8tion.jda.core.exceptions.ErrorResponseException


@CommandProperties(
        description = "Unbans a user from the server",
        triggers = ["ub"],
        category = CommandCategory.Moderation,
        botPermissions = [Permission.BAN_MEMBERS],
        userPermissions = [Permission.BAN_MEMBERS]
)
class Unban : Command {

    override suspend fun run(ctx: Context) {
        val userId = ctx.args.resolveMemberId() ?: return ctx.send("You need to specify a valid user/ID")
        val reason = ctx.args.resolveString(true).opt("No reason specified")

        ctx.guild.getBanById(userId).queue({
            // Prompt for unban
            //ctx.send("**${it.user.tag()}** was banned with reason: **${it.reason}**\n\nUnban? (y/n)")
            ctx.embed {
                setTitle("**${it.user.tag()}**")
                setDescription(it.reason)
                setFooter("Proceed with unban? (y/n)", null)
            }
        }, {
            if (it is ErrorResponseException) {
                return@queue ctx.send("No bans associated with that ID. Check the ID and try again.")
            } else {
                ctx.send(it.toString())
            }
        })
    }

}
