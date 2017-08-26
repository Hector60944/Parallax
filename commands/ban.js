const timeRX = /^\d+[a-z]\b/

exports.run = function(client, msg, args, gdb) {
	if (!msg.guild.member(client.user).hasPermission("BAN_MEMBERS")) 
		return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Permissions Error", description: "I don't have permission to ban members." }});
	
	if (msg.mentions.users.size === 0) 
		return msg.channel.send("No users specified.");

	let unbanTime = false;
	let deleteAll = args.slice(msg.mentions.users.size)[0] === "-d";

	if (timeRX.test(args[args.length - 1])) {
		let timeArg = args[args.length - 1];

		let unit = timeArg.slice(timeArg.length - 1);
		let time = timeArg.slice(0, timeArg.length - unit.length);

		unbanTime = parseTime(time, unit);
	}

	if (unbanTime === null)
		return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Ban Failed", description: "The time format specified is invalid." }});

	msg.react("☑");

	let uban = msg.mentions.users.filter(u => msg.guild.member(u).bannable && msg.member.highestRole.comparePositionTo(msg.guild.member(u).highestRole) > 0)
	let reason = args[msg.mentions.users.size] ? args.slice(msg.mentions.users.size) : "Unspecified";

	if (reason && typeof reason === 'object') {
		reason = reason.slice((deleteAll ? 1 : 0), (unbanTime ? reason.length - 1 : reason.length));
		reason = reason.join(" ");
	}	

	uban.forEach((m) => {
		msg.guild.member(m).ban({ reason: `Banned by ${msg.author.username} for ${reason}`, days: (deleteAll ? 7 : 0) });
		if (unbanTime) {
			if (!database[msg.guild.id])
				database[msg.guild.id] = [];
			database[msg.guild.id].push({ id: m.id, time: unbanTime });
		}
	});

	let embed = {
		color: 0xbe2f2f,
		title: `Action: ${unbanTime ? `Softban` : `Ban`}`,
		fields: [
			{ name: "User(s)", value: `${uban.map(k => `${k.tag} (${k.id})`).join("\n")}` },
			{ name: "Reason", value: reason }
		],
		footer: {
			text: `Action performed by ${msg.author.tag}`
		},
		timestamp: new Date()
	}

	if (unbanTime)
		embed.fields.push({ name: `Unban Date`, value: new Date(unbanTime).toLocaleString() });

	if (gdb.modlog.channel && client.channels.has(gdb.modlog.channel))
		client.channels.get(gdb.modlog.channel).send({ embed });
}

exports.permissions = ['BAN_MEMBERS'];

function parseTime(time, unit) {

	switch (unit) {
		case "s":
			return Date.now() + (1000 * time);
		case "m":
			return Date.now() + (60000 * time);
		case "h":
			return Date.now() + (3600000 * time);
		case "d":
			return Date.now() + (86400000 * time);
		case "w":
			return Date.now() + (604800000 * time);
		default:
			return null;
	}

}