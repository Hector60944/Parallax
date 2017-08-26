let raids = {};

exports.run = function(client, msg, db, Discord) {

	if (!msg.member.bannable) return; /* !msg.guild.member(client.user).permissions.has("BAN_MEMBERS") || */

	if (!raids[msg.author.id]) raids[msg.author.id] = [];

	raids[msg.author.id].push(msg.content);

	if (raids[msg.author.id].length === 1) {
		setTimeout(() => {
			if (raids[msg.author.id].length >= 5) {
				msg.member.ban(1).catch(err => {});
				if (db.modlog.channel && client.channels.has(db.modlog.channel))
					client.channels.get(db.modlog.channel).send({ embed: {
						color: 0xbe2f2f,
						title: "Action: Ban",
						fields: [
							{ name: `User`, value: `${msg.author.tag} (${msg.author.id})`, inline: false },
							{ name: `Reason`, value: `Auto-Ban: Spamming/Raider`, inline: false }
						],
						footer: {
							text: "Action performed automatically by Parallax"
						},
						timestamp: new Date()
					}});
			}
			delete raids[msg.author.id];

		}, 3000)
	}
}
