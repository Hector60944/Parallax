package me.devoxin.parallax

import com.zaxxer.hikari.HikariDataSource
import java.sql.Connection
import java.sql.Types

class Database {

    companion object {

        val pool = HikariDataSource()
        var calls = 0

        fun getConnection(): Connection {
            if (!pool.isRunning) {
                pool.jdbcUrl = "jdbc:sqlite:parallax.db"
            }

            ++calls
            return pool.connection
        }

        fun setup() {
            getConnection().use {
                val statement = it.createStatement()

                val columns = "id TEXT PRIMARY KEY NOT NULL," +
                        "modOnly INTEGER NOT NULL," +
                        "antiInvite INTEGER NOT NULL," +
                        "autoDehoist INTEGER NOT NULL," +
                        "prefix TEXT"

                statement.execute("CREATE TABLE IF NOT EXISTS settings($columns);")
            }
        }

        fun ensureGuildSettings(guildId: String) {
            getConnection().use {
                val statement = it.prepareStatement("SELECT EXISTS(SELECT 1 FROM settings WHERE id=?) AS res;")
                statement.setString(1, guildId)

                val result = statement.executeQuery()
                val entryExists = result.next() && result.getInt("res") == 1

                if (!entryExists) {
                    val create = it.prepareStatement("INSERT INTO settings VALUES (?, ?, ?, ?, ?);")
                    create.setString(1, guildId)
                    create.setInt(2, 0)
                    create.setInt(3, 0)
                    create.setInt(4, 0)
                    create.setNull(5, Types.VARCHAR)
                    create.execute()
                }
            }
        }


        fun getPrefix(guildId: String, default: String): String {
            getConnection().use {
                val statement = it.prepareStatement("SELECT prefix FROM settings WHERE id=?")
                statement.setString(1, guildId)

                val result = statement.executeQuery()

                return if (result.next()) result.getString("prefix") else default
            }
        }

        fun setPrefix(guildId: String, prefix: String) {
            Parallax.logger.info("Ensuring guild settings")
            ensureGuildSettings(guildId)

            Parallax.logger.info("Setting prefix")
            getConnection().use {
                val statement = it.prepareStatement("UPDATE settings SET prefix=? WHERE id=?")
                statement.setString(1, prefix)
                statement.setString(2, guildId)
                statement.execute()
            }
        }

    }

}