exports.run = async function(client, msg, args, db) {
	if (!msg.member.hasPermission("BAN_MEMBERS"))
		return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Permissions Error", description: "You don't have permission to use this command." }});
	if (!msg.guild.member(client.user).hasPermission("BAN_MEMBERS"))
		return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Permissions Error", description: "I don't have permission to ban members." }});

	if (!args[0]) return msg.channel.send({ embed: {
		color: 0xbe2f2f,
		title: "Unban Cancelled",
		description: "No users specified"
	}});

	let bans = await msg.guild.fetchBans();
	bans = bans.filter(usr => usr.username.toLowerCase().includes(args.join(" ").toLowerCase())).array();

	if (bans.length === 0) return msg.channel.send({ embed: {
		color: 0xbe2f2f,
		title: "Unban Cancelled",
		description: "No bans matched your query"
	}})

	let m = await msg.channel.send({ embed: {
		color: 0xbe2f2f,
		title: "Unban User",
		fields: [
			{ name: `${bans.length} results`, value: bans.map((u, i) =>  `[${i + 1}] ${u.tag} (${u.id})`).join("\n"), inline: false }
		],
		footer: {
			text: `Select 1 - ${bans.length} | c to cancel`
		}
	}});


	let collected = await msg.channel.awaitMessages(msgs => msgs.author.id === msg.author.id && (msgs.content >= 1 && msgs.content <= bans.length || msgs.content === "c"), { max: 1, time: 15000 });

	if (collected.size === 0 || collected.first().content === 'c') {
		collected.size > 0 && collected.first().delete();
		return m.delete();
	}

	m.delete();

	let selected = bans[collected.first().content - 1];
	collected.first().delete();

	msg.react("☑");

	msg.guild.unban(selected.id);

	if (db.modlog.channel && client.channels.has(db.modlog.channel))
		client.channels.get(db.modlog.channel).send({ embed: {
			color: 0xbe2f2f,
			title: "Action: Unban",
			fields: [
				{ name: `User`, value: `${selected.tag} (${selected.id})`, inline: false },
				{ name: `Reason`, value: `-`, inline: false }
			],
			footer: {
				text: `Action performed by ${msg.author.tag}`,
				timestamp: new Date()
			}
		}});
	//let reason = args[userMentions.size] ? args.slice(userMentions.size).join(" ") : "Unspecified"
}
