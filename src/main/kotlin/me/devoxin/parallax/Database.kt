package me.devoxin.parallax

import com.rethinkdb.RethinkDB
import com.rethinkdb.net.Connection

class Database {

    companion object {

        val r = RethinkDB.r
        val connection: Connection = r.connection().db("parallax").connect()


        fun getPrefix(guildId: String, default: String): String {
            return r.table("prefixes")
                    .get(guildId)
                    .getField("prefix")
                    .default_(default)
                    .run(connection)
        }

        fun setPrefix(guildId: String, prefix: String) {
            r.table("prefixes")
                    .insert(
                            r.hashMap("id", guildId)
                                    .with("prefix", prefix)
                    )
                    .optArg("conflict", "update")
                    .run<Connection>(connection)
        }

    }

}