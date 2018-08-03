package me.devoxin.parallax.flight

import kotlinx.coroutines.experimental.async

interface CoroutineCommand : Command {

    suspend fun runAsync(ctx: Context)

    override fun run(ctx: Context) {
        async {
            runAsync(ctx)
        }
    }

}