const mentionDetection = /<@!?\d+>/g

module.exports = {
	
	run: (ctx) => {

		if (ctx.mentions.users.size === 0)	
			return ctx.channel.send({ embed: {
				color: 0xbe2f2f,
				title: 'Missing Mentions',
				description: 'Mention the user you\'d like to unmute.'
			}});

		if (!ctx.guild.roles.find('name', 'Muted'))
			return ctx.channel.send({ embed: {
				color: 0xbe2f2f,
				title: 'Missing \'Muted\' Role',
				description: 'This server doesn\'t have a `Muted` role.\n\nParallax will automatically create a `Muted` role upon using the `mute` command.	'
			}});

		const reason = `${ctx.author.tag}: ${ctx.args.join(' ').replace(mentionDetection, '') || 'Unspecified'}`;
		const user = ctx.mentions.users.first();

		if (!ctx.utils.canInteract(ctx.member, ctx.guild.member(user)))
			return ctx.channel.send({ embed: {
				color: 0xbe2f2f,
				title: 'Unable to Mute',
				description: 'The target user has an equivalent or higher role than you'
			}});

		ctx.guild.member(user).removeRole(ctx.guild.roles.find('name', 'Muted'), reason);

		if (ctx.sdb.channels.actions && client.channels.has(ctx.sdb.channels.actions))
			client.channels.get(ctx.sdb.channels.actions).send({ embed: {
				color: 0xbe2f2f,
				description: `**User Unmuted**\n**Target:** ${user.tag} (${user.id})\n**Reason:** ${reason}`,
				footer: {
					text: `Action performed by ${ctx.author.tag}`
				},
				timestamp: new Date()
			}});
	
	},

	developerOnly: false,
	serverOwnerOnly: false,
	permissions: ['KICK_MEMBERS'],
	aliases: ['um'],
	usage: '<users> [reason]'

}
