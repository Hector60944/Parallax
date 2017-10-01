const timeRX = /^\d+[a-z]\b/
const mentionDetection = /<@!?\d+>/g

module.exports = {
	
	run: async (ctx) => {

		if (ctx.mentions.users.size === 0) //&& isNaN(ctx.args[0])) // Resolve IDs
			return ctx.channel.send({ embed: {
				color: 0xbe2f2f,
				title: 'Missing Mentions',
				description: 'Mention the user you\'d like to ban.'
			}});

		let reason = ctx.filtered.join(' ').replace(mentionDetection, '') || 'Unspecified';
		const user = ctx.mentions.users.first();

		if (!ctx.utils.canInteract(ctx.member, ctx.guild.member(user)))
			return ctx.channel.send({ embed: {
				color: 0xbe2f2f,
				title: 'Unable to Mute',
				description: 'The target user has an equivalent or higher role than you'
			}});

		let unbanTime;
		
		if (timeRX.test(ctx.args[ctx.args.length - 1])) {
			let timeArg = ctx.args[ctx.args.length - 1];
		
			let unit = timeArg.slice(timeArg.length - 1);
			let time = timeArg.slice(0, timeArg.length - unit.length);
		
			unbanTime = parseTime(time, unit);
		}

		if (unbanTime && reason !== 'Unspecified') {
			let temp = reason.split(' ');
			reason = temp.slice(0, temp.length - 1).join(' ');
		}
		
		/*
		if (unbanTime) {
			if (!database[msg.guild.id])
				database[msg.guild.id] = [];
			database[msg.guild.id].push({ id: m.id, time: unbanTime });
		*/

		let banOptions = {
			reason: reason,
			days: (ctx.switches.d || ctx.switches.delete ? 7 : 0)
		}

		ctx.guild.ban(user, banOptions);
		ctx.react("☑");

		let embed = {
			color: ctx.settings.colours.ACTION_SEVERE,
			description: `[**Banned**]()\n**Target:** ${user.tag} (${user.id})\n**Reason:**${reason}`,
			timestamp: new Date(),
			footer: {
				text: `Performed by ${ctx.author.tag}`,
				icon_url: ctx.author.displayAvatarURL
			}
		}

		if (unbanTime)
			embed.description += `\n\n**Unban Date:** ${new Date(unbanTime).toLocaleString()}`;
		
		if (ctx.sdb.channels.actions && ctx.client.channels.has(ctx.sdb.channels.actions))
				ctx.client.channels.get(ctx.sdb.channels.actions).send({ embed });
	
	},

	developerOnly: false,
	serverOwnerOnly: false,
	permissions: ['BAN_MEMBERS'],
	requires: ['BAN_MEMBERS'],
	aliases: ['b'],
	usage: '<user> [reason] [time]',
	description: 'Bans the specified user from the server'

}

function parseTime(time, unit) {
	switch (unit) {
		case "s":
			return Date.now() + (1000 * time);
		case "m":
			return Date.now() + (60000 * time);
		case "h":
			return Date.now() + (3600000 * time);
		case "d":
			return Date.now() + (86400000 * time);
		case "w":
			return Date.now() + (604800000 * time);
		default:
			return null;
	}
}