exports.run = function(client, msg, args, db, Discord) {
    if (!msg.member.permissions.has("BAN_MEMBERS"))
        return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Permissions Error", description: "You don't have permission to use this command." }});
    if (!msg.guild.me.permissions.has("MANAGE_ROLES"))
        return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Permissions Error", description: "I don't have permission to manage roles." }});
	if (msg.mentions.users.size === 0) 
        return msg.channel.sendMessage("No users specified.");
   	if (!msg.guild.roles.find("name", "Muted"))
		return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Missing Role", description: "This server doesn't have a 'Muted' role." }});

	let reason = args[msg.mentions.users.size] ? args.slice(msg.mentions.users.size).join(" ") : "Unspecified";

	msg.react("☑");

	msg.mentions.users.forEach(u => {
		msg.guild.member(u).removeRole(msg.guild.roles.find("name", "Muted"));
	});

	if (db.modlog.channel && client.channels.has(db.modlog.channel))
		client.channels.get(db.modlog.channel).send({ embed: {
			color: 0xbe2f2f,
			title: "Action: Unmute",
			fields: [
				{ name: "User(s)", value: `${msg.mentions.users.map(u => `${u.tag} (${u.id})`).join("\n")}`, inline: false },
				{ name: "Reason", value: reason, inline: false }
			],
			footer: {
				text: `Action performed by ${msg.author.tag}`
			},
			timestamp: new Date()
		}});

}
