exports.run = function(client, msg, args, gdb) {
	if (!msg.member.permissions.has("MANAGE_NICKNAMES"))
		return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Permissions Error", description: "You don't have permission to use this command." }});
	if (!msg.guild.member(client.user).permissions.has("MANAGE_NICKNAMES"))
		return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Permissions Error", description: "I don't have permissions to manage nicknames." }});

	if (msg.mentions.users.size === 0)
		return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Command Cancelled", description: "No users specified."}});

	msg.react("☑");

	let newnick = args.slice(msg.mentions.users.size).join(" ");
	msg.mentions.users.forEach(x => {
		msg.guild.member(x).setNickname(newnick)
	});

	if (gdb.modlog.channel && client.channels.has(gdb.modlog.channel))
		client.channels.get(gdb.modlog.channel).send({ embed: {
			color: 0xbe2f2f,
			title: "Action: Nickname Change",
			fields: [
				{ name: "User(s)", value: `${msg.mentions.users.map(k => `${k.tag} (${k.id})`).join("\n")}`, inline: false },
				{ name: "Nickname", value: newnick, inline: false }
			],
			footer: {
				text: `Action performed by ${msg.author.tag}`
			},
			timestamp: new Date()
		}});

}
