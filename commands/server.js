exports.run = async (client, msg, args) => {

    msg.channel.send({ embed: { 
        color: 0xbe2f2f,
        title: `Server Info | ${msg.guild.name} (${msg.guild.id})`,
        description: `Owner: ${msg.guild.owner.user.tag}`,
        thumbnail: {
            url: msg.guild.iconURL
        },
        fields: [
            { name: 'Members', value: `Bots: ${msg.guild.members.filter(m => m.user.bot).size} (${(msg.guild.members.filter(m => m.user.bot).size / msg.guild.memberCount * 100).toFixed(2)}%)\nTotal: ${msg.guild.memberCount}`, inline: true },
            { name: 'Region',  value: msg.guild.region, inline: true },
            { name: 'Verification Level', value: verifLvl[msg.guild.verificationLevel], inline: true },
            { name: 'Content Scanning', value: explicitContent[msg.guild.explicitContentFilter], inline: true }
        ],
        footer: {
            text: 'Created on'
        },
        timestamp: msg.guild.createdAt
    }})

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