package me.devoxin.parallax.utils

import net.dv8tion.jda.core.entities.Guild
import net.dv8tion.jda.core.entities.Member
import net.dv8tion.jda.core.entities.Role
import net.dv8tion.jda.core.entities.TextChannel
import java.util.regex.Pattern

class ArgParser(private val args: MutableList<String>, private val guild: Guild) {

    companion object {
        val snowflakeMatch: Pattern = Pattern.compile("[0-9]{17,20}")
    }

    private fun parseSnowflake(arg: String): String? {
        val match = snowflakeMatch.matcher(arg)
        return if (match.find()) match.group() else null
    }

    fun resolveTextChannelId(consumeRest: Boolean = false): String? {
        val amount = if (consumeRest) args.size else 1
        val target = args.deplete(amount)?.joinToString(" ") ?: return null

        return parseSnowflake(target) ?: guild.textChannels.firstOrNull { it.name == target }?.id
    }

    fun resolveTextChannel(consumeRest: Boolean = false): TextChannel? {
        val id = resolveTextChannelId(consumeRest) ?: return null
        return guild.getTextChannelById(id)
    }

    fun resolveMemberId(consumeRest: Boolean = false): String? {
        val amount = if (consumeRest) args.size else 1
        val target = args.deplete(amount)?.joinToString(" ") ?: return null

        return parseSnowflake(target) ?: if (target.length > 5 && target[target.length - 5].toString() == "#") {
            val tag = target.split("#")
            guild.members.find { it.user.name == tag[0] && it.user.discriminator == tag[1] }?.user?.id
        } else {
            guild.members.find { it.user.name == target }?.user?.id
        }
    }

    fun resolveMember(consumeRest: Boolean = false): Member? {
        val id = resolveMemberId(consumeRest) ?: return null
        return guild.getMemberById(id)
    }

    fun resolveRoleId(consumeRest: Boolean = false): String? {
        val amount = if (consumeRest) args.size else 1
        val target = args.deplete(amount)?.joinToString(" ") ?: return null

        return parseSnowflake(target) ?: guild.roles.firstOrNull { it.name == target }?.id
    }

    fun resolveRole(consumeRest: Boolean = false): Role? {
        val id = resolveRoleId(consumeRest) ?: return null
        return guild.getRoleById(id)
    }

    fun resolveString(consumeRest: Boolean = false, cleanContent: Boolean = false): String {
        val amount = if (consumeRest) args.size else 1
        return args.deplete(amount)?.joinToString(" ") ?: ""
    }

}