exports.run = function(client, msg, args, db, Discord, settings) {
	if (msg.author.id !== settings.ownerid && msg.author.id !== msg.guild.owner.user.id && !msg.member.hasPermission("MANAGE_GUILD"))
		return msg.channel.send({ embed: { color: 0xbe2f2f, title: "Permissions Error", description: "You don't have permission to use this command." }});
	db.activeModules.invites = !db.activeModules.invites
	utils.db.updateDB(msg.guild.id, db);
	msg.channel.send({ embed: { color: 0xbe2f2f, title: "Settings Updated", description: `Server settings saved. (Invite Protection: ${db.activeModules.invites ? "enabled" : "disabled"})` }});
}
