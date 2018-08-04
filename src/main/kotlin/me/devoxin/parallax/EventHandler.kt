package me.devoxin.parallax

import kotlinx.coroutines.experimental.async
import me.devoxin.parallax.flight.Command
import me.devoxin.parallax.flight.CommandProperties
import me.devoxin.parallax.flight.Context
import net.dv8tion.jda.core.Permission
import net.dv8tion.jda.core.entities.Member
import net.dv8tion.jda.core.events.ReadyEvent
import net.dv8tion.jda.core.events.message.guild.GuildMessageReceivedEvent
import net.dv8tion.jda.core.hooks.ListenerAdapter
import org.reflections.Reflections

class EventHandler(private val defaultPrefix: String) : ListenerAdapter() {

    private lateinit var botId: String
    private val commands: HashMap<String, Command> = HashMap()

    init {
        val start = System.currentTimeMillis()

        val loader = Reflections("me.devoxin.parallax.commands")
        loader.getTypesAnnotatedWith(CommandProperties::class.java).forEach {
            val cmd = it.newInstance() as Command

            commands[it.simpleName.toLowerCase()] = cmd
        }

        val end = System.currentTimeMillis()
        Parallax.logger.info("Successfully loaded ${commands.size} commands in ${end - start}ms")
    }

    override fun onReady(event: ReadyEvent) {
        Parallax.logger.info("Successfully logged in as ${event.jda.selfUser.name}")
        botId = event.jda.selfUser.id
    }

    override fun onGuildMessageReceived(event: GuildMessageReceivedEvent) {

        if (event.author.isBot || event.author.isFake) {
            return
        }

        val prefix = Database.getPrefix(event.guild.id, defaultPrefix)
        val wasMentioned = event.message.contentRaw.startsWith("<@$botId>")
                || event.message.contentRaw.startsWith("<@!$botId>")

        if (!event.message.contentDisplay.startsWith(prefix) && !wasMentioned) {
            return
        }

        val triggerLength = if (wasMentioned) event.guild.selfMember.asMention.length + 1 else prefix.length
        val cleanTrigger = if (wasMentioned) "@${event.guild.selfMember.effectiveName} " else prefix

        val content = event.message.contentRaw
                .substring(triggerLength)
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
            command.run(Context(cleanTrigger, event, args))
        }
    }

    fun executePermissionCheck(member: Member, permissions: Array<Permission>): Array<Permission> {
        return permissions.filterNot { member.hasPermission(it) }.toTypedArray()
    }

}
