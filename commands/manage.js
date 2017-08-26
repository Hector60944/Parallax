exports.run = async function(client, msg, args, db, Discord, settings) {
	if (!msg.member.permissions.has('MANAGE_GUILD') && msg.author.id !== settings.ownerid)
		return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Permissions Error", description: "You don't have permission to use this command." }});
	if (!args[0])
		return msg.channel.send({ embed: { 
			color: 0xbe2f2f, 
			description: `All options need to be prefixed with \`${db.prefix}manage\`\n\n` +
			`**prefix** - Set a new server-wide prefix\n` +
			`**events** - Set logging channels for specific events\n` + 
			`**modlog** - Set a logging channel for moderation actions\n` +
			`**autorole** - Configure auto-roles for users/bots upon joining\n` +
			`**antiping** - Discipline users who try ping everyone/here\n` + 
			`**assignable** - Setup self-assignable roles for users`,
		}});

	if (args[0] === "prefix") {
		if (!args[1])
			return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Setting Unchanged", description: "A new prefix must be specified" }});
		db.prefix = args[1];
		utils.db.updateDB(msg.guild.id, db);
		msg.channel.send({ embed: { color: 0xbe2f2f, title: `Server Settings Updated` }});
	}

	if (args[0] === "events") {
		if (!args[1]) 
			return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Server Events", description: "You can manage events with `-manage events < join | leave > < channel mention | clear >`" }});
		if (msg.mentions.channels.size === 0 && args[2] !== "clear") 
			return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Server Events", description: "Channel mention is a required parameter." }});

		if (args[1] === "join" || args[1] === "leave") {
			db.modlog[args[1]] = args[2] === "clear" ? "" : msg.mentions.channels.first().id;
			utils.db.updateDB(msg.guild.id, db);
			msg.channel.send({ embed: { color: 0xbe2f2f, title: `Server Settings Updated` }});
		} else {
			return msg.channel.send('Invalid event. (join/leave)')
		}
	}

	if (args[0] === "modlog") {
		if (msg.mentions.channels.size === 0 && args[1] !== "clear") 
			return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Server Modlog", description: "Channel mention is a required parameter." }});
		db.modlog.channel = args[1] === "clear" ? "" : msg.mentions.channels.first().id;
		utils.db.updateDB(msg.guild.id, db);
		msg.channel.send({ embed: { color: 0xbe2f2f, title: `Server Settings Updated` }});
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
}