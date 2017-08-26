module.exports = {
	
	run: async (ctx) => {
		if (ctx.args.length === 0)
			return ctx.channel.send({ embed: { 
				color: 0xbe2f2f, 
				description: `All options need to be prefixed with \`${ctx.sdb.prefix}${ctx.command}\`\n\n` +
				`**prefix** - Set a new server-wide prefix\n` +
				`**events** - Set logging channels for specific events\n` + 
				`**modlog** - Set a logging channel for moderation actions\n` +
				`**autorole** - Configure auto-roles for users/bots upon joining\n` +
				`**antiping** - Discipline users who try ping everyone/here\n` + 
				`**assignable** - Setup self-assignable roles for users\n` +
				`**invites** - Toggles whether invites are allowed in the server\n` +
				`**raidpro** - Toggles raid protection (BETA)`
			}});

		if (args[0] === "prefix") {
			if (!args[1])
				return module.exports.sendHelp(ctx, 'prefix', '{{p}}{{c}} {{s}} <prefix>')
			ctx.sdb.prefix = args[1];
			module.exports.changeSuccess(ctx, 'prefix', args[1]);
		}

		if (args[0] === "channels") {
			if (!args[1])
				return module.exports.sendHelp(ctx, 'events', '{{p}}{{c}} {{s}} <join|leave|actions> [clear]\n\nParallax will use the current channel as the target.')

			if (!ctx.sdb.channels[args[1]]) 
				return module.exports.sendHelp(ctx, 'events', '{{p}}{{c}} {{s}} <join|leave|actions> [clear]\n\nParallax will use the current channel as the target.')

			let channel = args[2] === 'clear' ? '' : ctx.channel.id
			ctx.sdb.modlog[args[1]] = channel
			module.exports.changeSuccess(ctx, `Events (${args[1]})`, (channel ? `<#${ctx.channel.id}>` : 'empty.'));

		}

		if (args[0] === "assignable") {
			if (!args[1]) 
				return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Self-Assignable Roles", description: "You can manage self-assignable roles by doing `-manage assignable < add | remove > role name`" }});
			if (!args[2]) 
				return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Self-Assignable Roles", description: "You must specify a role name" }});

			let role = msg.guild.roles.find("name", args.slice(2).join(" "));
			if (args[1] === "add") {
				if (!role) 
					return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Self-Assignable Roles", description: "No role with that name was found." }});
				if (db.assignable.includes(role.id)) 
					return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Self-Assignable Roles", description: "That role is already self-assignable." }});
				db.assignable.push(role.id)
				utils.db.updateDB(msg.guild.id, db);
				msg.channel.send({ embed: { color: 0xbe2f2f, title: `Server Settings Updated` }});
			} else if (args[1] === "remove") {
				if (!role) 
					return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Self-Assignable Roles", description: "No role with that name was found." }});
				if (!db.assignable.includes(role.id)) 
					return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Self-Assignable Roles", description: "That role is not self-assignable." }});
				db.assignable.splice(db.assignable.indexOf(role.id), 1)
				utils.db.updateDB(msg.guild.id, db);
				msg.channel.send({ embed: { color: 0xbe2f2f, title: `Server Settings Updated` }});
			} else {
				return msg.channel.send('Invalid method. (add/remove)')
			}
		}

		if (args[0] === "autorole") {
			if (!args[1]) 
				return msg.channel.send({ embed: { color: 0xbe2f2f, title: "AutoRole", description: "You can manage autoroles by doing `-manage autorole < bots | users > < add | remove > role name`" }});
			if (!args[2]) 
				return msg.channel.send({ embed: { color: 0xbe2f2f, title: "AutoRole", description: "No method specified. (< add | remove >)" }});
			if (!args[3]) 
				return msg.channel.send({ embed: { color: 0xbe2f2f, title: "AutoRole", description: "No role name specified." }});

			let role = msg.guild.roles.find("name", args.slice(3).join(" "))
			if (!role) 
				return msg.channel.send({ embed: { color: 0xbe2f2f, title: "AutoRole", description: "No role with that name found." }});

			if (args[1] === "bots" || args[1] === "users") {
				if (args[2] === "add") {
					if (db.activeModules.autorole[args[1]].indexOf(role.id) !== -1) 
						return msg.channel.send({ embed: { color: 0xbe2f2f, title: "AutoRole", description: "That role is currently being assigned." }});
					db.activeModules.autorole[args[1]].push(role.id);
					utils.db.updateDB(msg.guild.id, db);
					msg.channel.send({ embed: { color: 0xbe2f2f, title: "AutoRole", description: `Auto-Role: Added **${role.name}** to ${args[1]}` }});
				} else if (args[2] === "remove") {
					if (db.activeModules.autorole[args[1]].indexOf(role.id) === -1) 
						return msg.channel.send({ embed: { color: 0xbe2f2f, title: "AutoRole", description: "That role isn't currently being assigned." }});
					db.activeModules.autorole[args[1]].splice(db.activeModules.autorole[args[1]].indexOf(role.id), 1)
					utils.db.updateDB(msg.guild.id, db);
					msg.channel.send({ embed: { color: 0xbe2f2f, title: "AutoRole", description: `Auto-Role: Removed **${role.name}** from ${args[1]}` }});
				}
			} else {
				return msg.channel.send('Invalid category. (bots/users)')
			}
		}

		if (args[0] === "antiping") {
			if (!args[1]) 
				return msg.channel.send({ embed: { color: 0xbe2f2f, title: "AntiPing", description: "Anti-Ping can automatically ban/kick anyone who tries to ping everyone/here\n\n`-manage antiping < kick | ban | off >`" }});
		
			if (args[1] === "off") {
				db.activeModules.antiping = 0;
				utils.db.updateDB(msg.guild.id, db);
				msg.channel.send({ embed: { color: 0xbe2f2f, title: `Server Settings Updated` }});
			} else if (args[1] === "kick") {
				db.activeModules.antiping = 1;
				utils.db.updateDB(msg.guild.id, db);
				msg.channel.send({ embed: { color: 0xbe2f2f, title: `Server Settings Updated` }});
			} else if (args[1] === "ban") {
				db.activeModules.antiping = 2;
				utils.db.updateDB(msg.guild.id, db);
				msg.channel.send({ embed: { color: 0xbe2f2f, title: `Server Settings Updated` }});
			} else {
				return msg.channel.send('Invalid action. (off/kick/ban)')
			}
		}
	},

	sendHelp: async (ctx, category, description) => {
		await ctx.channel.send({
			embed: {
				color: 0xbe2f2f,
				title: `Help for ${category}`,
				description: description.replace(/\{\{p\}\}/g, ctx.sdb.prefix).replace(/\{\{c\}\}/g, ctx.command).replace(/\{\{s\}\}/g, category)
			}
		})
	},

	changeSuccess: async (ctx, category, newSetting) => {
		await ctx.channel.send({
			embed: {
				color: 0xbe2f2f,
				title: `Server Settings Updated`,
				description: `${category} is now \`${newSetting}\``
			}
		})
	},

	developerOnly: false,
	serverOwnerOnly: false,
	permissions: ['MANAGE_GUILD']

}