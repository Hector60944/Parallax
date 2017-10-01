module.exports = {
	
	run: async (ctx) => {

		if (ctx.args.length === 0)
			return ctx.channel.send({ embed: { 
				color: 0xbe2f2f, 
				description: `All options need to be prefixed with \`${ctx.sdb.prefix}${ctx.command}\`\n\n` +
				`\`\`\`\n` +
				`prefix     - Set a new server-wide prefix\n` +
				`channels   - Set logging channels\n` + 
				`autorole   - Configure auto-roles for new members\n` +
				`assignable - Setup self-assignable roles\n` +
				`invites    - Toggles auto invite deletion\n` +
				`raidpro    - Toggles raid protection (BETA)` +
				`\n\`\`\``
			}});

		if (ctx.args[0] === 'prefix') {
			if (!ctx.args[1])
				return module.exports.sendHelp(ctx, 'prefix', '{{p}}{{c}} {{s}} <prefix>', 'Change the prefix of the bot for the entire server');
			ctx.sdb.prefix = ctx.args[1];
			module.exports.changeSuccess(ctx, `Set the prefix to \`${ctx.args[1]}\``);
		}

		if (ctx.args[0] === 'channels') {
			if (!ctx.args[1] || ctx.sdb.channels[ctx.args[1]] === undefined)
				return module.exports.sendHelp(ctx, 'channels', '{{p}}{{c}} {{s}} < join | leave | actions > [clear]', 'Link the current channel with the specified event');

			let channel = (ctx.args[2] && ctx.args[2] === 'clear' ? '' : ctx.channel.id)
			ctx.sdb.channels[ctx.args[1]] = channel
			module.exports.changeSuccess(ctx, (channel ? `<#${ctx.channel.id}> is now the \`${ctx.args[1]}\` channel` : `Cleared the \`${ctx.args[1]}\` channel`));

		}

		if (ctx.args[0] === 'assignable') {
			if (ctx.args.length < 3 || (ctx.args[1] !== 'add' && ctx.args[1] !== 'remove'))
					return module.exports.sendHelp(ctx, 'assignable', '{{p}}{{c}} {{s}} <add|remove> <role name>', 'Make roles self-assignable by users');

			const role = ctx.guild.roles.find('name', ctx.args.slice(2).join(' '));
			if (!role)
				return ctx.channel.send({ embed: {
					color: 0xbe2f2f,
					title: 'Self-Assignable Roles',
					description: 'A role with that name wasn\'t found'
				}});
			
			if (ctx.args[1] === 'add') {
				if (ctx.sdb.assignable.includes(role.id)) 
					return ctx.channel.send({ embed: { color: 0xbe2f2f, title: 'Self-Assignable Roles', description: 'That role is already self-assignable.' }});
				ctx.sdb.assignable.push(role.id)
				module.exports.changeSuccess(ctx, `Added \`${role.name}\` to self-assignable roles`);
			} else if (ctx.args[1] === 'remove') {
				if (!ctx.sdb.assignable.includes(role.id)) 
					return ctx.channel.send({ embed: { color: 0xbe2f2f, title: 'Self-Assignable Roles', description: 'That role is not currently self-assignable.' }});
				ctx.sdb.assignable.splice(ctx.sdb.assignable.indexOf(role.id), 1)
				module.exports.changeSuccess(ctx, `Removed \`${role.name}\` from self-assignable roles`);
			}
		}

		if (ctx.args[0] === 'autorole') {
			if (ctx.args.length < 4 || (ctx.args[1] !== 'bots' && ctx.args[1] !== 'users') || (ctx.args[2] !== 'add' && ctx.args[2] !== 'remove'))
				return module.exports.sendHelp(ctx, 'autorole', '{{p}}{{c}} {{s}} < bots | users > < add | remove > <role name>', 'Change what roles are assigned to bots/users upon joining');

			const role = ctx.guild.roles.find('name', ctx.args.slice(3).join(' '));
			if (!role)
				return ctx.channel.send({ embed: {
					color: 0xbe2f2f,
					title: 'AutoRole',
					description: 'A role with that name wasn\'t found'
				}});

			if (ctx.args[2] === 'add') {
				if (ctx.sdb.autorole[ctx.args[1]].includes(role.id))
					return ctx.channel.send({ embed: { color: 0xbe2f2f, title: 'AutoRole', description: 'That role is currently active.' }});
				ctx.sdb.autorole[ctx.args[1]].push(role.id);
				ctx.channel.send({ embed: { color: 0xbe2f2f, title: 'AutoRole', description: `Added \`${role.name}\` to ${ctx.args[1]}` }});
			} else if (ctx.args[2] === 'remove') {
				if (!ctx.sdb.autorole[ctx.args[1]].includes(role.id))
					return msg.channel.send({ embed: { color: 0xbe2f2f, title: 'AutoRole', description: 'That role isn\'t currently being assigned.' }});
				ctx.sdb.autorole[ctx.args[1]].splice(ctx.sdb.autorole[ctx.args[1]].indexOf(role.id), 1)
				ctx.channel.send({ embed: { color: 0xbe2f2f, title: 'AutoRole', description: `Removed \`${role.name}\` from ${ctx.args[1]}` }});
			}
		}

		if (ctx.args[0] === 'invites') {
			if (ctx.args.length !== 2 || (ctx.args[1] !== 'on' && ctx.args[1] !== 'off'))
				return module.exports.sendHelp(ctx, 'invites', '{{p}}{{c}} {{s}} < on | off >', 'Toggles deletion of Discord invite links');

			let option = ctx.args[1] === 'on';
			ctx.sdb.invites = option;
			module.exports.sendHelp(ctx, `Anti-Invite ${option ? 'enabled' : 'disabled'}`);			
		}

		if (ctx.args[0] === 'raidpro') {
			if (ctx.args.length !== 2 || (ctx.args[1] !== 'on' && ctx.args[1] !== 'off'))
				return module.exports.sendHelp(ctx, 'raidpro', '{{p}}{{c}} {{s}} < on | off >', 'Toggles server raid protection');

			let option = ctx.args[1] === 'on';
			ctx.sdb.raid = option;
			module.exports.sendHelp(ctx, `Raid Protection ${option ? 'enabled' : 'disabled'}`);			
		}
		
	},

	sendHelp: async (ctx, category, usage, description) => {
		usage = usage.replace(/\{\{p\}\}/g, ctx.sdb.prefix).replace(/\{\{c\}\}/g, ctx.command).replace(/\{\{s\}\}/g, category)
		await ctx.channel.send({
			embed: {
				color: 0xbe2f2f,
				title: `Help for ${category}`,
				description: `\`${usage}\`\n\n${description}`
			}
		})
	},

	changeSuccess: async (ctx, description) => {
		await ctx.channel.send({
			embed: {
				color: 0xbe2f2f,
				title: `Server Settings Updated`,
				description: description
			}
		})
	},

	developerOnly: false,
	serverOwnerOnly: false,
	permissions: ['MANAGE_GUILD'],
	requires: [],
	aliases: [],
	usage: ''

}