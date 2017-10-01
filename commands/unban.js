const mentionDetection = /<@!?\d+>/g

module.exports = {
	
	run: async (ctx) => {

		if (ctx.args.length === 0 || isNaN(ctx.args[0]))
			return ctx.channel.send({ embed: {
				color: 0xbe2f2f,
				title: 'Unban User',
				description: 'You need to specify an ID'
			}});

		const user = await ctx.guild.unban(ctx.args[0])
		.catch(err => {
			ctx.channel.send({ embed: {
				color: 0xbe2f2f,
				title: 'Cannot Unban User',
				description: err.message
			}});
		});

		if (!user)
			return;

		ctx.react('☑');

		const reason = ctx.args.slice(1).join(' ') || 'Unspecified';

		if (ctx.sdb.channels.actions && ctx.client.channels.has(ctx.sdb.channels.actions))
			ctx.client.channels.get(ctx.sdb.channels.actions).send({ embed: {
				color: ctx.settings.colours.ACTION_INFO,
				description: `[**Unbanned**]()\n**Target:** ${user.tag} (${user.id})\n**Reason:** ${reason}`,
				timestamp: new Date(),
				footer: {
					text: `Performed by ${ctx.author.tag}`,
					icon_url: ctx.author.displayAvatarURL
				}
			}});

	},

	developerOnly: false,
	serverOwnerOnly: false,
	permissions: ['BAN_MEMBERS'],
	requires: ['BAN_MEMBERS'],
	aliases: ['ub'],
	usage: '<user> [reason]',
	description: 'Removes the ban for the specified user'

}
