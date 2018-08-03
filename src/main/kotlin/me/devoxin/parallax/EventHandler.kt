package me.devoxin.parallax

import kotlinx.coroutines.experimental.async
import me.devoxin.parallax.commands.Ban
import me.devoxin.parallax.commands.Prefix
import me.devoxin.parallax.flight.Command
import me.devoxin.parallax.flight.Context
import net.dv8tion.jda.core.Permission
import net.dv8tion.jda.core.entities.Member
import net.dv8tion.jda.core.events.ReadyEvent
import net.dv8tion.jda.core.events.message.guild.GuildMessageReceivedEvent
import net.dv8tion.jda.core.hooks.ListenerAdapter

class EventHandler(private val defaultPrefix: String) : ListenerAdapter() {

    private val commands: HashMap<String, Command> = HashMap()

    init {
        commands["ban"] = Ban()
        commands["prefix"] = Prefix()
    }

    override fun onReady(event: ReadyEvent) {
        Parallax.logger.info("Successfully logged in as ${event.jda.selfUser.name}")
    }

    override fun onGuildMessageReceived(event: GuildMessageReceivedEvent) {

        if (event.author.isBot || event.author.isFake) {
            return
        }

        val prefix = Database.getPrefix(event.guild.id, defaultPrefix)

        if (!event.message.contentDisplay.startsWith(prefix)) {
            return
        }

        val content = event.message.contentRaw
                .substring(defaultPrefix.length)
                .split(" +".toRegex())

        val commandString = content[0].toLowerCase()
        val args = content.drop(1)
        val command = commands[commandString] ?: return

        val userMissing = executePermissionCheck(event.member, command.properties().userPermissions)
        val botMissing = executePermissionCheck(event.guild.selfMember, command.properties().botPermissions)

        if (userMissing.isNotEmpty()) {
            return event.channel.sendMessage(
                    "**You need the following permissions:**\n${userMissing.joinToString("\n")}"
            ).queue()
        }

        if (botMissing.isNotEmpty()) {
            return event.channel.sendMessage(
                    "**I need the following permissions:**\n${botMissing.joinToString("\n")}"
            ).queue()
        }

        async {
            command.run(Context(event, args))
        }
    }

    fun executePermissionCheck(member: Member, permissions: Array<Permission>): Array<Permission> {
        return permissions.filterNot { member.hasPermission(it) }.toTypedArray()
    }

}
