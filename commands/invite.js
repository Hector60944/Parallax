exports.run = function(client, msg, args) {
	msg.channel.send({ embed: {
		color: 0xbe2f2f,
		fields: [
			{ name: "Links", value: "[Invite](https://discordapp.com/oauth2/authorize?permissions=8&scope=bot&client_id=252232935820754955)", inline: false }
		]
	}});
}
