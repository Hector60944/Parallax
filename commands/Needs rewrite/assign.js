module.exports = {
	
	run: (ctx) => {

		let role = msg.guild.roles.find("name", args.join(" "))
		if (!role && args[0] !== "list") 
			return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Role Assignment", description: `Role not found.\nTo view a list of assignable roles, send '${gdb.prefix}assign list'` }});

		if (args[0] === "list") {
			if (gdb.assignable.length === 0) 
				return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Role Assignment", description: `There are no self-assignable roles.` }});

			let assignable = gdb.assignable.filter(r => msg.guild.roles.get(r) && !msg.member.roles.has(r))
			let unassignable = gdb.assignable.filter(r => msg.guild.roles.get(r) && msg.member.roles.has(r))
			return msg.channel.send({ embed: { 
				color: 0xbe2f2f, 
				fields: [
					{ name: "Assignable", value: assignable.length > 0 ? assignable.sort().map(r => msg.guild.roles.get(r).name).join("\n") : "None", inline: true },
					{ name: "Unassignable", value: unassignable.length > 0 ? unassignable.sort().map(r => msg.guild.roles.get(r).name).join("\n") : "None", inline: true },
				]
			}});
		}

		if (!gdb.assignable.includes(role.id))
			return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Role Assignment", description: `That role isn't self-assignable.` }});
		if (msg.member.roles.has(role.id)) {
			msg.member.removeRole(role).then(() => {
				return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Role Assignment", description: `You have been unassigned **${role.name}**` }});
			}).catch(e => {
				return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Role Assignment", description: `Unassign Error: ${e.message}` }});
			})
		} else {
			msg.member.addRole(role).then(() => {
				return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Role Assignment", description: `You have been assigned **${role.name}**.\nUse the same command to unassign it.` }});
			}).catch(e => {
				return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Role Assignment", description: `Assign Error: ${e.message}` }});
			})
		}

	},

	developerOnly: false,

	permissions: ['MANAGE_ROLES']

}
