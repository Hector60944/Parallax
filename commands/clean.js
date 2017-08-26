exports.run = async function(client, msg, args) {
	if (!msg.channel.permissionsFor(msg.member.id).has("MANAGE_MESSAGES")) 
		return msg.channel.send("", { embed: { color: 0xbe2f2f, title: "Permissions Error", description: "You don't have permission to use this command." }});
	if (!msg.channel.permissionsFor(client.user.id).has("MANAGE_MESSAGES")) 
		return msg.channel.send("", { embed: { color: 0xbe2f2f, title: "Permissions Error", description: ":warning: Missing 'Manage Messages' permission." }});

	let messagecount = parseInt(args[0]) ? parseInt(args[0]) : 1;

	let messages = await msg.channel.fetchMessages({limit: 100});
	let mentions = msg.mentions.users.size > 0 ? msg.mentions.users.array().map(u => u.id) : [];
	messages = messages.array();

	if (mentions.length > 0) messages = messages.filter(m => mentions.includes(m.author.id));
	if (args[1] && args[1] === "--bot") 
		messages = messages.filter(u => u.author.bot);
	else if (args[1] && args[1] === "--user")
		messages = messages.filter(u => !u.author.bot);
	
	if (args[1] && (args[1] === "--bot" || args[1] === "--user")) {
		messages.length = messages.length > messagecount ? messagecount : messages.length
	} else {
		messages.length = messages.length > messagecount + 1 ? messagecount + 1 : messages.length
	}
	

	if (messages.length < 2) messages.map(m => m.delete());
	else msg.channel.bulkDelete(messages);
}
