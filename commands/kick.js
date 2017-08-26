module.exports = {

	run: (ctx) => {
		if (!msg.member.hasPermission("KICK_MEMBERS")) 
			return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Permissions Error", description: "You don't have permission to use this command." }});
		if (!msg.guild.member(client.user).hasPermission("KICK_MEMBERS")) 
			return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Permissions Error", description: "I don't have permission to kick members." }});
		if (msg.mentions.users.size === 0) 
			return msg.channel.send("No users specified.");
		let ukick = msg.mentions.users.filter(u => msg.guild.member(u).kickable && msg.member.highestRole.comparePositionTo(msg.guild.member(u).highestRole) > 0)
		let reason = args[msg.mentions.users.size] ? args.slice(msg.mentions.users.size).join(" ") : "Unspecified"

		msg.react("☑");

		ukick.forEach((m) => {
			msg.guild.member(m).kick(`${msg.author.username} kicked for ${reason}`)
		});

		if (gdb.modlog.channel && client.channels.has(gdb.modlog.channel))
			client.channels.get(gdb.modlog.channel).send({ embed: {
				color: 0xFFA500,
				title: "Action: Kick",
				fields: [
					{ name: "User(s)", value: `${ukick.map(k => `${k.tag} (${k.id})`).join("\n")}`, inline: false },
					{ name: "Reason", value: reason, inline: false }
				],
				footer: {
					text: `Action performed by ${msg.author.tag}`
				},
				timestamp: new Date()
			}});
	},

	developerOnly: false,

	permissions: ['KICK_MEMBERS']
	
}
