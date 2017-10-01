const mentionDetection = /<@!?\d+>/g

module.exports = {
	
	run: async (ctx) => {

		if (ctx.mentions.users.size === 0)	
			return ctx.channel.send({ embed: {
				color: 0xbe2f2f,
				title: 'Missing Mentions',
				description: 'Mention the user you\'d like to mute.'
			}});

		if (!ctx.guild.roles.find('name', 'Muted')) {
			let role = await ctx.guild.createRole({
				name: 'Muted',
				permissions: []
			});
			ctx.guild.channels
			.filter(c => c.type === 'text')
			.map(c => c.overwritePermissions(role, { SEND_MESSAGES: false, ADD_REACTIONS: false }) );
		}

		const reason = ctx.args.join(' ').replace(mentionDetection, '') || 'Unspecified';
		const user = ctx.mentions.users.first();

		if (!ctx.utils.canInteract(ctx.member, ctx.guild.member(user)))
			return ctx.channel.send({ embed: {
				color: 0xbe2f2f,
				title: 'Unable to Mute',
				description: 'The target user has an equivalent or higher role than you'
			}});

		ctx.guild.member(user).addRole(ctx.guild.roles.find('name', 'Muted'), reason);
		ctx.react("☑");
		
		if (ctx.sdb.channels.actions && ctx.client.channels.has(ctx.sdb.channels.actions))
				ctx.client.channels.get(ctx.sdb.channels.actions).send({ embed: {
					color: ctx.settings.colours.ACTION_MINOR,
					description: `[**Muted**]()\n**Target:** ${user.tag} (${user.id})\n**Reason:**${reason}`,
					timestamp: new Date(),
					footer: {
						text: `Performed by ${ctx.author.tag}`,
						icon_url: ctx.author.displayAvatarURL
					}
				}});
	
	},

	developerOnly: false,
	serverOwnerOnly: false,
	permissions: ['KICK_MEMBERS'],
	requires: ['MANAGE_ROLES'],
	aliases: ['m'],
	usage: '<user> [reason]',
	description: 'Prevents the specified user from talking in the server'

}
