package me.devoxin.parallax.flight

import me.devoxin.parallax.Database
import me.devoxin.parallax.utils.*
import net.dv8tion.jda.core.EmbedBuilder
import net.dv8tion.jda.core.JDA
import net.dv8tion.jda.core.entities.*
import net.dv8tion.jda.core.events.message.guild.GuildMessageReceivedEvent
import java.time.Instant
import java.util.function.Predicate
import java.util.regex.Pattern

class Context(
        val trigger: String,
        event: GuildMessageReceivedEvent,
        args: List<String>
) {

    val jda: JDA = event.jda
    val message: Message = event.message
    val author: User = event.author
    val member: Member = event.member
    val selfMember: Member = event.guild.selfMember
    val channel: TextChannel = event.channel
    val guild: Guild = event.guild
    val args = ArgParser(args.toMutableList(), guild)


    fun send(content: String, codeblock: Boolean = false) {
        val limit = if (codeblock) 1950 else 2000
        val pages = split(content, limit)

        for (page in pages) {
            channel.sendMessage(page).queue()
        }
    }

    fun embed(builder: EmbedBuilder.() -> Unit) {
        channel.sendMessage(EmbedBuilder().setColor(0xbe2f2f).apply(builder).build()).queue()
    }

    suspend fun sendAsync(content: String, codeblock: Boolean = false) {
        val limit = if (codeblock) 1950 else 2000
        val pages = split(content, limit)

        for (page in pages) {
            channel.sendMessage(page).await()
        }
    }

    fun dispatchModLogEntry(severity: Severity, action: String, target: Member, reason: String) {
        dispatchModLogEntry(severity, action, target.user, reason)
    }

    fun dispatchModLogEntry(severity: Severity, action: String, target: User, reason: String) {
        val channelId = Database.getModlog(guild.id) ?: return
        val channel = guild.getTextChannelById(channelId) ?: return

        channel.sendMessage(EmbedBuilder()
                .setColor(severity.color)
                .setTitle("**User $action**")
                .setDescription("**Target:** ${target.tag()} (${target.id})\n**Reason:** $reason")
                .setFooter("Performed by ${author.tag()}", author.avatarUrl)
                .setTimestamp(Instant.now())
                .build()
        ).queue()
    }


    enum class Severity(val color: Int) {
        LOW(0x53dc39),
        MEDIUM(0xEFD344),
        HIGH(0xbe2f2f)
    }

}
