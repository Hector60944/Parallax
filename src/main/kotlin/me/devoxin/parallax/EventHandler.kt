package me.devoxin.parallax

import me.devoxin.parallax.commands.Test
import me.devoxin.parallax.flight.Command
import me.devoxin.parallax.flight.Context
import net.dv8tion.jda.core.events.ReadyEvent
import net.dv8tion.jda.core.events.message.guild.GuildMessageReceivedEvent
import net.dv8tion.jda.core.hooks.ListenerAdapter

class EventHandler(private val defaultPrefix: String) : ListenerAdapter() {

    val commands: HashMap<String, Command> = HashMap()

    init {
        commands["test"] = Test()
    }

    override fun onReady(event: ReadyEvent) {
        Parallax.logger.info("Successfully logged in as ${event.jda.selfUser.name}")
    }

    override fun onGuildMessageReceived(event: GuildMessageReceivedEvent) {

        if (event.author.isBot || event.author.isFake) {
            return
        }

        if (!event.message.contentDisplay.startsWith(defaultPrefix)) {
            return
        }

        val content = event.message.contentRaw
                .substring(defaultPrefix.length)
                .split(" +".toRegex())

        val commandString = content[0].toLowerCase()
        val args = content.drop(1)
        val command = commands[commandString] ?: return

        command.run(Context(event, args))
    }

}
