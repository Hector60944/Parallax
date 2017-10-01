module.exports = {
    
    run: async (ctx) => {

        ctx.channel.send({ embed: {
			color: ctx.settings.colours.ACTION_INFO,
			description: 
			'[**Add Parallax**](https://discordapp.com/oauth2/authorize?permissions=8&scope=bot&client_id=252232935820754955) | ' +
			'[**Get Support**](https://discord.gg/xvtH2Yn)'
		}});
    
    },

    developerOnly: false,
	serverOwnerOnly: false,
	permissions: [],
	requires: [],
	aliases: [],
    usage: '',
	description: 'Displays the relevant invite links for the bot'
    
}