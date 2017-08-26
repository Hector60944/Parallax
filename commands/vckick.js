exports.run = async function(client, msg, args) {
	if (!msg.member.hasPermission("MOVE_MEMBERS")) return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Permissions Error", description: "You don't have permission to use this command." }});
	if (msg.mentions.users.size === 0) return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Missing Mentions", description: "Mention the users you'd like to kick from their voicechannel." }});
	let channel = await msg.guild.createChannel("vckick", "voice");

	let tasks = [];

	msg.mentions.users.filter(u => msg.guild.member(u).voiceChannel && msg.guild.member(u).voiceChannel.permissionsFor(msg.guild.member(client.user)).has("MOVE_MEMBERS")).map(async m => {
		tasks.push(msg.guild.member(m).setVoiceChannel(channel));
	});

	Promise.all(tasks).then(() => {
		channel.delete();
		msg.react("☑");
	})
}
