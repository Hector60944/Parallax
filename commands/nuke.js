exports.run = async function(client, msg, args) {

	if (msg.author.id !== msg.guild.owner.user.id)
		return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Permissions Error", description: "You don't have permission to use this command" }});
	if (!msg.channel.permissionsFor(client.user).has("MANAGE_MESSAGES"))
		return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Permissions Error", description: "I'm missing the Manage Messages permission." }});

	let m = await msg.channel.send({ embed: { color: 0xbe2f2f, title: "Nuke Channel", description: ":raised_hand: Hold up fam, this will delete all (or up to 2 weeks worth of) messages. Send 'y' or 'n' to confirm/cancel." }});

	const collected = await msg.channel.awaitMessages(m => m.author.id === msg.author.id, { max: 1, time: 10000});

	if (collected.size === 0 || collected.first().content !== "y")
		return m.delete();

	await m.edit({ embed: { color: 0xbe2f2f, tite: "Nuking...", description: "Don't stop me now, I'm having such a good time..." }});

	nuke(msg);

}

function nuke(msg) {
	msg.channel.fetchMessages({limit: 100}).then(messages => {
		if (messages.size > 2) {
			let msg_array = messages.array();
			msg.channel.bulkDelete(msg_array).then(() => {
				nuke(msg)
			})
		}
	})
}
