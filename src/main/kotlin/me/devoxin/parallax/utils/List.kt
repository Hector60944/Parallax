package me.devoxin.parallax.utils

fun <T> List<T>.splice(start: Int, end: Int): List<T>? {
    if (isEmpty()) {
        return null
    }

    val elements = mutableListOf<T>()

    for (i in end - 1 downTo start) {
        if (i < 0 || i > size) {
            break
        }

        elements.add(get(i))
        dropLast(1)
    }

    elements.reverse()
    return elements.toList()
}
