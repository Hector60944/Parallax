package me.devoxin.parallax.utils

import kotlinx.coroutines.experimental.future.await
import net.dv8tion.jda.core.entities.User
import net.dv8tion.jda.core.requests.RestAction


fun <T> MutableList<T>.deplete(amount: Int): List<T>? {
    if (isEmpty()) {
        return null
    }

    val elements = take(amount)
    removeAll(elements)

    return elements
}


fun String.opt(default: String): String {
    return if (isNullOrEmpty()) {
        default
    } else {
        toString()
    }
}


suspend fun <T> RestAction<T>.await(): T {
    return submit().await()
}

fun User.tag(): String {
    return "$name#$discriminator"
}
