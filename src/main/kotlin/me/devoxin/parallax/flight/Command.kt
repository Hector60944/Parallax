package me.devoxin.parallax.flight

public interface Command {

    suspend fun run(ctx: Context)

    fun properties(): CommandProperties {
        return this.javaClass.getAnnotation(CommandProperties::class.java)
    }

}
