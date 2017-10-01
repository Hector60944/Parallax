module.exports = {
	
	run: (ctx) => {

		ctx.channel.send(":warning: Restarting...").then(() => {
			ctx.client.destroy();
			process.exit();
		});

	},

	developerOnly: true,
	serverOwnerOnly: false,
	permissions: [],
	requires: [],
	aliases: [],
	usage: '',
	description: 'Reboots the bot'

}