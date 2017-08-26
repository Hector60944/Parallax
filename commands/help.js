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

			if (ctx.client.commands.has(ctx.args[0]))
				ctx.channel.send(ctx.client.commands.get(ctx.args[0]).help || 'No help is available for this command.');
			else
				ctx.channel.send(`Invalid command specified. Use \`${ctx.sdb.prefix}help\` to view available commands.`);


		}

	},

	developerOnly: false,

	permissions: []

}
