package me.devoxin.parallax

import net.dv8tion.jda.core.events.ReadyEvent
import net.dv8tion.jda.core.events.message.guild.GuildMessageReceivedEvent
import net.dv8tion.jda.core.hooks.ListenerAdapter

class EventHandler(private val defaultPrefix: String) : ListenerAdapter() {

    override fun onReady(event: ReadyEvent) {
        Parallax.logger.info("Successfully logged in as ${event.jda.selfUser.name}")
    }

    override fun onGuildMessageReceived(event: GuildMessageReceivedEvent) {

    }

}