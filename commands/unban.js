const mentionDetection = /<@!?\d+>/g

module.exports = {
	
	run: async (ctx) => {

		if (ctx.args.length === 0 || isNaN(ctx.args[0]))
			return msg.channel.send({ embed: {
				color: 0xbe2f2f,
				title: 'Unban',
				description: 'You need to specify an ID'
			}});

		const user = await ctx.guild.unban(ctx.args[0])
		.catch(err => {
			return ctx.channel.send({ embed: {
				color: 0xbe2f2f,
				title: 'Cannot Unban User',
				description: `Discord returned: \`${err.message}\``
			}})
		});

		msg.react('☑');

		const reason = `${ctx.author.tag}: ${ctx.args.replace(mentionDetection, '').join(' ') || 'Unspecified'}`;

		if (ctx.sdb.channels.actions && client.channels.has(ctx.sdb.channels.actions))
			client.channels.get(ctx.sdb.channels.actions).send({ embed: {
				color: 0xbe2f2f,
				description: `**User Unbanned**\n**Target:** ${user.tag} (${user.id})\n**Reason:** ${reason}`,
				footer: {
					text: `Action performed by ${ctx.author.tag}`
				},
				timestamp: new Date()
			}});

		/*
		const bans = await msg.guild.fetchBans();

		if (!bans.has(args[0]))
			return msg.channel.send({ embed: {
				color: 0xbe2f2f,
				title: 'Unban Cancelled',
				description: 'No bans exist matching that ID'
			}});

		banned = bans.get(args[0])

		let m = await msg.channel.send({ embed: {
			color: 0xbe2f2f,
			title: 'Unban User',
			fields: [
				{ name: `${bans.length} results`, value: bans.map((u, i) =>  `[${i + 1}] ${u.tag} (${u.id})`).join('\n'), inline: false }
			],
			footer: {
				text: `Select 1 - ${bans.length} | c to cancel`
			}
		}});

		let collected = await msg.channel.awaitMessages(msgs => msgs.author.id === msg.author.id && (msgs.content >= 1 && msgs.content <= bans.length || msgs.content === 'c'), { max: 1, time: 15000 });

		if (collected.size === 0 || collected.first().content === 'c') {
			collected.size > 0 && collected.first().delete();
			return m.delete();
		}

		m.delete();

		let selected = bans[collected.first().content - 1];
		collected.first().delete();

		*/		

	},

	developerOnly: false,
	serverOwnerOnly: false,
	permissions: ['BAN_MEMBERS'],
	aliases: ['ub'],
	usage: '<user id> [reason]'

}
