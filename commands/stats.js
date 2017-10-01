module.exports = {
	
	run: async (ctx) => {

		ctx.channel.send({ embed: {
			color: 0xbe2f2f,
			title: `Parallax v${ctx.settings.version}`,
			fields: [
				{ name: "Uptime",     value: ctx.utils.time(process.uptime() * 1000, false),		   	   inline: true },
				{ name: "RAM Usage",  value: `${(process.memoryUsage().rss / 1024 / 1024).toFixed(2)} MB`, inline: true },
				{ name: "Ping",       value: `${ctx.client.pings[0]} ms`,							       inline: true },
				{ name: "Node",       value: process.version, 											   inline: true },
				{ name: "Discord.JS", value: ctx.Discord.version,  								     	   inline: true },
				{ name: "Servers",    value: ctx.client.guilds.size, 								       inline: true }
			]
		}});

	},

	developerOnly: false,
	serverOwnerOnly: false,
	permissions: [],
	requires: [],
	aliases: [],
	usage: '',
	description: 'Displays bot statistics'

}