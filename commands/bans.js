exports.run = async function(client, msg, args) {

    if (!msg.guild.me.hasPermission("BAN_MEMBERS"))
        return msg.channel.send({ embed: {
            color: 0xbe2f2f,
            title: "Permissions Error",
            description: "I don't have permission to fetch bans."
        }});

    let m = await msg.channel.send({ embed: {
        color: 0xbe2f2f,
        title: "Fetching offenders...",
        description: ":eyes:"
    }});

    let bans = await msg.guild.fetchBans();

    let fields = [];

    if (bans.size === 0)
        fields.push({ name: "No bans found", value: "No bans were found for this server.", inline: false });
    else
        bans.map(u => {
            fields.push({ name: `${u.user.tag} (${u.user.id})`, value: u.reason || "No reason specified", inline: false });
        });

    m.edit({ embed: {
        color: 0xbe2f2f,
        title: `Bans (${fields.length} results)`,
        fields: fields,
        footer: {
            text: "Page 1/1"
        }
    }});

}
