package me.devoxin.parallax

import net.dv8tion.jda.bot.sharding.DefaultShardManagerBuilder
import net.dv8tion.jda.bot.sharding.ShardManager
import net.dv8tion.jda.core.entities.Game
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import java.io.FileReader
import java.util.*


class Parallax {

    companion object {

        val logger: Logger = LoggerFactory.getLogger("parallax")
        lateinit var shardManager: ShardManager

        @JvmStatic
        fun main(args: Array<String>) {
            val config = getConfig()

            val token = config.getProperty("token")
            val prefix = config.getProperty("prefix")

            shardManager = DefaultShardManagerBuilder()
                    .setAudioEnabled(false)
                    .setGame(Game.watching("your server | -help"))
                    .setShardsTotal(-1)
                    .setToken(token)
                    .addEventListeners(EventHandler(prefix))
                    .build()

            Database.setup()
        }

        fun getConfig(): Properties {
            val props = Properties()
            props.load(FileReader("config.properties"))
            return props
        }

    }

}
