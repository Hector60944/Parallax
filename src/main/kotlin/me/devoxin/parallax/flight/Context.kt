package me.devoxin.parallax.flight

import me.devoxin.parallax.utils.await
import me.devoxin.parallax.utils.splice
import me.devoxin.parallax.utils.split
import net.dv8tion.jda.core.JDA
import net.dv8tion.jda.core.entities.*
import net.dv8tion.jda.core.events.message.guild.GuildMessageReceivedEvent
import java.util.regex.Pattern

class Context(event: GuildMessageReceivedEvent, private val args: List<String>) {

    val jda: JDA = event.jda
    val message: Message = event.message
    val author: User = event.author
    val member: Member = event.member
    val channel: TextChannel = event.channel
    val guild: Guild = event.guild


    suspend fun send(content: String, codeblock: Boolean = false) {
        val limit = if (codeblock) 1950 else 2000
        val pages = split(content, limit)

        for (page in pages) {
            channel.sendMessage(page).await()
        }
    }


    // Arg-Parsing stuff

    fun resolveUser(consumeRest: Boolean = false): User? {
        val end = if (consumeRest) args.size else 1
        val target = args.splice(0, end)?.joinToString(" ") ?: return null
        System.out.println(target)

        val hasSnowflake = snowflakeMatch.matcher(target)

        return when {
            hasSnowflake.find() -> {
                guild.getMemberById(hasSnowflake.group())
            }
            target.length > 5 && target[target.length - 5].toString() == "#" -> {
                val tag = target.split("#")
                guild.members.find { it.user.name == tag[0] && it.user.discriminator == tag[1] }
            }
            else -> {
                guild.members.find { it.user.name == target }
            }
        }?.user
    }



    companion object {
        val snowflakeMatch: Pattern = Pattern.compile("[0-9]{17,20}")
    }

}