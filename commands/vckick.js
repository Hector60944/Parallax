module.exports = {
	
	run: async (ctx) => {
		
		if (ctx.mentions.users.size === 0)	
			return ctx.channel.send({ embed: {
				color: 0xbe2f2f,
				title: "Missing Mentions",
				description: "Mention the users you'd like to kick from their voicechannel."
			}});

		let channel = await ctx.guild.createChannel("temporary", "voice");

		let tasks = [];

		ctx.mentions.users
		.filter(u => msg.guild.member(u).voiceChannel && ctx.utils.channelCheck(msg.guild.member(u).voiceChannel, ctx.guild.me, "MOVE_MEMBERS"))
		.map((m) => tasks.push(msg.guild.member(m).setVoiceChannel(channel)));

		Promise.all(tasks).then(() => {
			channel.delete();
			msg.react("☑");
		})
		
	},

	developerOnly: false,
	serverOwnerOnly: false,
	permissions: ['MOVE_MEMBERS'],
	aliases: ['vk'],
	usage: '<users>'

}
