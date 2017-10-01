module.exports = {
    
    run: async (ctx) => {

        const bots = ctx.guild.members.filter(m => m.user.bot).size;

        ctx.channel.send({ embed: { 
            color: ctx.settings.colours.ACTION_INFO,
            title: `Server Info | ${ctx.guild.name} (${ctx.guild.id})`,
            description: `Owner: ${ctx.guild.owner.user.tag}`,
            thumbnail: {
                url: ctx.guild.iconURL
            },
            fields: [
                { name: 'Members', value: `Bots: ${bots} (${(bots / ctx.guild.memberCount * 100).toFixed(2)}%)\nTotal: ${ctx.guild.memberCount}`, inline: true },
                { name: 'Region',  value: ctx.guild.region, inline: true },
                { name: 'Verification Level', value: verifLvl[ctx.guild.verificationLevel], inline: true },
                { name: 'Content Scanning', value: explicitContent[ctx.guild.explicitContentFilter], inline: true }
            ],
            footer: {
                text: 'Created on'
            },
            timestamp: ctx.guild.createdAt
        }});
    
    },

    developerOnly: false,
	serverOwnerOnly: false,
	permissions: [],
	requires: [],
	aliases: [],
    usage: ''
    
}

const verifLvl = {
    0: 'None',
    1: 'Low',
    2: 'Medium',
    3: 'High',
    4: 'Extreme'
}

const explicitContent = {
    0: 'Off',
    1: 'Without Role',
    2: 'All'
}