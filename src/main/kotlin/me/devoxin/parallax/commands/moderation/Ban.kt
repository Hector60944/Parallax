package me.devoxin.parallax.commands.moderation

import me.devoxin.parallax.Database
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
        val user = ctx.resolveMember() ?: return ctx.send("You need to specify a valid user/ID")
        val reason = ctx.resolveString(true).opt("No reason specified")

        if (!ctx.member.canInteract(user)) {
            return ctx.send("Role hierarchy prevents you from doing that.")
        }

        if (!ctx.selfMember.canInteract(user)) {
            return ctx.send("Role hierarchy prevents me from doing that.")
        }

        ctx.guild.controller.ban(user, 7, "[ ${ctx.author.tag()} ] $reason").await()
        ctx.message.addReaction("\uD83D\uDC4C").await()

        val channelId = Database.getModlog(ctx.guild.id) ?: return
        val channel = ctx.jda.getTextChannelById(channelId) ?: return

        channel.sendMessage("some dude got bent lul rip").queue()
    }

}
