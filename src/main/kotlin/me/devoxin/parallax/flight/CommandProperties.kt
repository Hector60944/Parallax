package me.devoxin.parallax.flight

import net.dv8tion.jda.core.Permission


@Retention(AnnotationRetention.RUNTIME)
@Target(AnnotationTarget.CLASS)
annotation class CommandProperties(
        val description: String = "",
        val triggers: Array<String> = [],
        val developerOnly: Boolean = false,
        val category: CommandCategory = CommandCategory.Misc,
        val botPermissions: Array<Permission> = [],
        val userPermissions: Array<Permission> = []
)

enum class CommandCategory {
    Admin,
    Configuration,
    Misc,
    Moderation,
    Profile,
    Tags
}