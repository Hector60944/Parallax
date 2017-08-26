let invites = {}
const invex = /discord(?:app)?\.(?:gg|com\/invite)\/([a-z0-9]{3,16})/i

exports.run = function(client, msg, db) {
	if (!msg.member || msg.channel.permissionsFor(msg.member).has("MANAGE_MESSAGES") || !msg.channel.permissionsFor(msg.guild.me).has("MANAGE_MESSAGES") || !msg.member.bannable || !msg.member.kickable || !invex.test(msg.content)) return;

	msg.delete()
	if (!invites[msg.author.id]) {
		invites[msg.author.id] = 0;
		msg.channel.send({ embed: {
			color: 0xbe2f2f,
			title: 'Anti-Invite',
			description: ':warning: **Invite links are disabled here.**\n\nIf you continue to post them, you will be kicked and then banned.'
		}, reply: msg.author });
	};

	invites[msg.author.id]++;

	let action = "";

	if (invites[msg.author.id] % 2 === 0) {
		action = "Kick";
		msg.member.kick();
	} else if (invites[msg.author.id] % 3 === 0) {
		delete invites[msg.author.id];
		action = "Ban";
		msg.member.ban();
	}

	if (action !== "" && db.modlog.channel && client.channels.has(db.modlog.channel))
		client.channels.get(db.modlog.channel).send({ embed: {
			color: 0xbe2f2f,
			title: `Action: ${action}`,
			fields: [
				{ name: `User`, value: `${msg.author.tag} (${msg.author.id})`, inline: false },
				{ name: `Reason`, value: `Auto-${action}: Posted too many invites`, inline: false }
			],
				timestamp: new Date(),
				footer: {
					text: `Action performed automatically by Parallax`
				}
			}});
}
