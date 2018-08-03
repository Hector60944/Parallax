package me.devoxin.parallax.commands

import me.devoxin.parallax.flight.Context
import me.devoxin.parallax.flight.CoroutineCommand

class Test : CoroutineCommand {

    override suspend fun runAsync(ctx: Context) {

        val user = ctx.resolveUser()

        if (user != null) {
            ctx.send("${user.name}#${user.discriminator} <a:trashdoves:393764497967415296>")
        } else {
            ctx.send("nope")
        }

    }

}