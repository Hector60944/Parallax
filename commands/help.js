module.exports = {
	
	run: (ctx) => {

		if (ctx.args.length === 0) {

			let cmds;
		
			if (ctx.settings.owners.includes(ctx.author.id))
				cmds = Array.from(
					ctx.client.commands
					.filter(c => ctx.channel.permissionsFor(ctx.member).missing(c.permissions).length === 0)
					.keys()
				);
			else
				cmds = Array.from(
					ctx.client.commands
					.filter(c => !c.developerOnly && ctx.channel.permissionsFor(ctx.member).missing(c.permissions).length === 0)
					.keys()
				);

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

				if (ctx.client.commands.get(ctx.args[0]).usage === undefined)
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
					`**Usage:** \`${ctx.sdb.prefix}${ctx.args[0].toLowerCase()} ${command.usage}\`\n` +
					`**Description:** ${command.description || 'No description'}\n` +
					`**Aliases:** \`${command.aliases.join(' ') || 'None'}\``
				}})

			} else {

				ctx.channel.send(`Invalid command specified. Use \`${ctx.sdb.prefix}help\` to view available commands.`);

			}


		}

	},

	developerOnly: false,
	serverOwnerOnly: false,
	permissions: [],
	requires: [],
	aliases: ['h'],
	usage: '[command]',
	description: 'Displays commands or per-command help'

}
