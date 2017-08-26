module.exports = {

	run: async (client, msg, args, db, Discord, settings) => {
		msg.channel.send({ embed: {
			color: 0xbe2f2f,
			title: `Server Settings | ${msg.guild.name}`,
			description: `Prefix: ${db.prefix}`,
			fields: [
				{ name: "Mod Log", 			 	 value: (db.modlog.actions ? "None" : `<#${db.modlog.channel}>`), inline: true },
				{ name: "Join Channel", 		 value: (db.modlog.join    ? "None" : `<#${db.modlog.join}>`),    inline: true },
				{ name: "Leave Channel", 		 value: (db.modlog.leave   ? "None" : `<#${db.modlog.leave}>`),   inline: true },
				{ name: "Self-Assignable Roles", value: (db.assignable     ? "None" : db.assignable.filter(r => msg.guild.roles.has(r)).map(r => msg.guild.roles.get(r).name).join(", ")), inline: false },
				{ name: "Channel Logging", 	 	 value: (db.activeModules.logger.length > 0 ? db.activeModules.logger.filter(c => msg.guild.channels.get(c)).map(c => msg.guild.channels.get(c).name).join(", ") : "None"), inline: false },
				{ name: "Autorole", 			 value: `Users: ${db.activeModules.autorole.users.length === 0 ? "None" : db.activeModules.autorole.users.filter(r => msg.guild.roles.get(r)).map(r => msg.guild.roles.get(r).name).join(", ")}\n` +
														`Bots:  ${db.activeModules.autorole.bots.length === 0 ? "None" : db.activeModules.autorole.bots.filter(r => msg.guild.roles.get(r)).map(r => msg.guild.roles.get(r).name).join(", ")}`, inline: false },
				{ name: "Invite Protection", 	 value: (db.activeModules.invites  ? "Enabled" : "Disabled"), inline: true },
				{ name: "Raid Protection", 	 	 value: (db.activeModules.raid ? "Enabled" : "Disabled"), inline: true }
			]
		}})
	},

	developerOnly: false,
    serverOwnerOnly: false,
	permissions: ['MANAGE_GUILD']
	
}
