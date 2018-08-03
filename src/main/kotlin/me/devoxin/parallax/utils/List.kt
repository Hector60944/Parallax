package me.devoxin.parallax.utils

fun <T> MutableList<T>.deplete(amount: Int): List<T>? {
    if (isEmpty()) {
        return null
    }

    val elements = take(amount)
    removeAll(elements)

    return elements
}
