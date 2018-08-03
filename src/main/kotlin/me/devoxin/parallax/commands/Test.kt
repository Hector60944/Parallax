package me.devoxin.parallax.commands

import me.devoxin.parallax.flight.Context
import me.devoxin.parallax.flight.CoroutineCommand

class Test : CoroutineCommand {

    override suspend fun runAsync(ctx: Context) {

        val user = ctx.resolveUser()
        val channel = ctx.resolveTextChannel()
        val role = ctx.resolveRole()

        ctx.send("User: ${user?.name ?: "who is this"}\n" +
                "Channel: ${channel?.name ?: "stop hiding channels from me"}\n" +
                "Role: ${role?.name ?: "???"}")

    }

}