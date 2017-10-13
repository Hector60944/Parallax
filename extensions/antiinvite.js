let invites = {}
const invex = /discord(?:app)?\.(?:gg|com\/invite)\/([a-z0-9]{3,16})/i

module.exports = {
	
	run: async (ctx) => {

		if (ctx.bot || ctx.utils.channelCheck(ctx.channel, ctx.member, ['MANAGE_MESSAGES']) || !ctx.utils.channelCheck(ctx.channel, ctx.guild.me, ['MANAGE_MESSAGES']) || !ctx.member.bannable || !ctx.member.kickable || !invex.test(ctx.content)) 
			return;

		ctx.delete()

		if (!invites[ctx.author.id] || invites[ctx.author.id] % 3 === 0) {
			invites[ctx.author.id] = 0;
			ctx.channel.send("Invite links aren't allowed here", { reply: ctx.author });
		};

		invites[ctx.author.id]++;

		let action = invites % 2 === 0 ? 'Kicked' : (invites % 3 === 0 ? 'Banned' : undefined);

		if (invites[ctx.author.id] % 2 === 0) 
			ctx.member.kick();

		if (invites[ctx.author.id] % 3 === 0) 
			ctx.member.ban();

		if (action && ctx.sdb.channels.actions && ctx.client.channels.has(ctx.sdb.channels.actions))
			ctx.client.channels.get(ctx.sdb.channels.actions).send({ embed: {
				color: (invites % 2 === 0 ? ctx.settings.colours.ACTION_MODERATE : ctx.settings.colours.ACTION_SEVERE),
				description: `[**${action}**]()\n**Target:** ${ctx.author.tag} (${ctx.author.id})\n**Reason:** Auto-${action} for advertising`,
				timestamp: new Date(),
				footer: {
					text: `Performed by ${ctx.client.user.tag}`,
					icon_url: ctx.client.user.displayAvatarURL
				}
			}});
			
	}

}
