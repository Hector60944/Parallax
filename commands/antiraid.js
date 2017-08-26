exports.run = function(client, msg, args, db, Discord, settings) {
	if (msg.author.id !== settings.ownerid && msg.author.id !== msg.guild.owner.user.id && !msg.member.permissions.has("MANAGE_GUILD"))
		return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Permissions Error", description: "You don't have permission to use this command." }});
	db.activeModules.raid = !db.activeModules.raid
	utils.db.updateDB(msg.guild.id, db);
	msg.channel.send({ embed: { color: 0xbe2f2f, title: "Settings Updated", description: `Server settings saved. (Anti-Raid: ${db.activeModules.raid ? "enabled" : "disabled"})` }});
}