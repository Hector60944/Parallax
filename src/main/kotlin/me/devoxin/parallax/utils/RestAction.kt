package me.devoxin.parallax.utils

import kotlinx.coroutines.experimental.future.await
import net.dv8tion.jda.core.requests.RestAction

suspend fun <T> RestAction<T>.await(): T {
    return submit().await()
}