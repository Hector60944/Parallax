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
		.filter(u => ctx.guild.member(u).voiceChannel && ctx.utils.channelCheck(ctx.guild.member(u).voiceChannel, ctx.guild.me, "MOVE_MEMBERS"))
		.map((m) => tasks.push(ctx.guild.member(m).setVoiceChannel(channel)));

		Promise.all(tasks).then(async () => {
			await channel.delete();
			ctx.react("☑");
		});
		
	},

	developerOnly: false,
	serverOwnerOnly: false,
	permissions: ['MOVE_MEMBERS'],
	requires: ['MOVE_MEMBERS', 'MANAGE_CHANNELS'],
	aliases: ['vk'],
	usage: '<users>'

}
