package me.devoxin.parallax.flight

import me.devoxin.parallax.utils.await
import me.devoxin.parallax.utils.deplete
import me.devoxin.parallax.utils.split
import net.dv8tion.jda.core.JDA
import net.dv8tion.jda.core.entities.*
import net.dv8tion.jda.core.events.message.guild.GuildMessageReceivedEvent
import java.util.regex.Pattern

class Context(event: GuildMessageReceivedEvent, args: List<String>) {

    val args = args.toMutableList()
    val jda: JDA = event.jda
    val message: Message = event.message
    val author: User = event.author
    val member: Member = event.member
    val selfMember: Member = event.guild.selfMember
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

    fun resolveMember(consumeRest: Boolean = false): Member? {
        val amount = if (consumeRest) args.size else 1
        val target = args.deplete(amount)?.joinToString(" ") ?: return null

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
        }
    }


    fun resolveUser(consumeRest: Boolean = false): User? {
        return resolveMember(consumeRest)?.user
    }


    fun resolveTextChannel(consumeRest: Boolean = false): TextChannel? {
        val amount = if (consumeRest) args.size else 1
        val target = args.deplete(amount)?.joinToString(" ") ?: return null

        val hasSnowflake = snowflakeMatch.matcher(target)

        return when {
            hasSnowflake.find() -> {
                guild.getTextChannelById(hasSnowflake.group())
            }
            else -> {
                guild.textChannels.find { it.name == target }
            }
        }
    }

    fun resolveRole(consumeRest: Boolean = false): Role? {
        val amount = if (consumeRest) args.size else 1
        val target = args.deplete(amount)?.joinToString(" ") ?: return null

        val hasSnowflake = snowflakeMatch.matcher(target)

        return when {
            hasSnowflake.find() -> {
                guild.getRoleById(hasSnowflake.group())
            }
            else -> {
                guild.roles.find { it.name == target }
            }
        }
    }

    fun resolveSnowflake(): String? {
        val target = args.deplete(1)?.joinToString(" ") ?: return null
        val match = snowflakeMatch.matcher(target)

        return if (match.matches()) match.group() else null
    }

    fun resolveString(consumeRest: Boolean = false): String {
        val amount = if (consumeRest) args.size else 1
        return args.deplete(amount)?.joinToString(" ") ?: ""
    }


    companion object {
        val snowflakeMatch: Pattern = Pattern.compile("[0-9]{17,20}")
    }

}