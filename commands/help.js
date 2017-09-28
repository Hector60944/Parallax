module.exports = {
	
	run: (ctx) => {

		if (ctx.args.length === 0) {

			let cmds;
		
			if (ctx.author.id === ctx.settings.ownerid)
				cmds = Array.from(ctx.client.commands.keys());
			else
				cmds = Array.from(ctx.client.commands.filter(c => !c.developerOnly).keys());

			ctx.channel.send({ embed: {
				color: 0xbe2f2f,
				title: `Commands (${cmds.length})`,
				description: cmds.sort().join(', '),
				footer: {
					text: `Use ${ctx.sdb.prefix}help <command> for per-command help`
				}
			}});

		} else {

			if (ctx.client.commands.has(ctx.args[0])) {

				if (!ctx.client.commands.get(ctx.args[0]).help)
					return ctx.channel.send({ embed: {
						color: 0xbe2f2f,
						title: 'No help available',
						description: 'No help documentation was found for that command.'
					}});

				const command = ctx.client.commands.get(ctx.args[0]);

				ctx.channel.send({ embed: {
					color: 0xbe2f2f,
					title: `Help for ${ctx.args[0].toLowerCase()}`,
					description: 
					`**Usage:** ${ctx.sdb.prefix}${ctx.args[0].toLowerCase()} ${command.usage}\n` +
					`**Description:**${command.desc}\n` +
					`**Aliases:** ${command.aliases.join('\n') || 'None'}`
				}})

			} else {

				ctx.channel.send(`Invalid command specified. Use \`${ctx.sdb.prefix}help\` to view available commands.`);

			}


		}

	},

	developerOnly: false,
	serverOwnerOnly: false,
	permissions: [],
	aliases: ['h'],
	usage: '[command]'

}
