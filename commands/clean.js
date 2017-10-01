module.exports = {
	
	run: async function(ctx) {

		if (ctx.args.length === 0)
			return ctx.channel.send("You need to specify the number of messages to delete.");

		const messagecount = parseInt(ctx.args[0]);

		if (!messagecount || messagecount < 1 || messagecount > 100)
			return ctx.channel.send("Invalid amount specified.");

		let messages = (await ctx.channel.fetchMessages({ limit: 100 })).array();
		let mentions = ctx.mentions.users.size > 0 ? ctx.mentions.users.array().map(u => u.id) : [];

		if (mentions.length > 0) 
			messages = messages.filter(m => mentions.includes(m.author.id));

		if (ctx.switches.bot) 
			messages = messages.filter(u => u.author.bot);
		else if (ctx.switches.user)
			messages = messages.filter(u => !u.author.bot);
		
		if (ctx.switches.bot || ctx.switches.user) {
			messages.length = messages.length > messagecount ? messagecount : messages.length
		} else {
			messages.length = messages.length > messagecount + 1 ? messagecount + 1 : messages.length
		}

		if (messages.length < 2) messages.map(m => m.delete());
		else ctx.channel.bulkDelete(messages);

	},
	
	developerOnly: false,
	serverOwnerOnly: false,
	permissions: ['MANAGE_MESSAGES'],
	requires: ['MANAGE_MESSAGES'],
	aliases: ['d', 'purge', 'prune', 'clear', 'delete', 'remove'],
	usage: '<amount> [-bot|-user]',
	description: 'Removes the specified amount of messages from the channel'

}
