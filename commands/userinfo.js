module.exports = {
    
    run: async (ctx) => {

        if (ctx.args.length === 0)
            return ctx.channel.send({ embed: {
                color: 0xbe2f2f,
                title: 'Specify a user to lookup',
                description: 'Search can be: user ID, username or username#discrim'
            }}); 

        let user = ctx.utils.resolveUser(ctx, ctx.args.join(' '));
        
        if (!user && !isNaN(ctx.args.join(' '))) 
            user = await ctx.client.fetchUser(ctx.args.join(' '))
                .catch(err => { return undefined; });

        if (!user) 
            return ctx.channel.send({ embed: {
                color: 0xbe2f2f,
                title: 'Unknown User',
                description: 'Specify a mention, user ID, username or username#discrim'
            }});

        let embed = {
            color: 0xbe2f2f,
            author: {
                name: user.tag,
                icon_url: user.displayAvatarURL
            },
            description: user.id,
            fields: [
                { name: 'Bot', value: (user.bot ? 'Yes' : 'No'), inline: true },
                { name: 'Playing', value: (user.presence.game ? user.presence.game.name : 'Nothing'), inline: true }
            ]
        };

        let member = await ctx.guild.fetchMember(user.id)
            .catch(err => { return undefined; });

        if (member) {
            let kicks = await ctx.guild.fetchAuditLogs({ type: 20 })
                .catch(err => { return undefined; });
            let bans  = await ctx.guild.fetchAuditLogs({ type: 22 })
                .catch(err => { return undefined; });

            kicks = kicks ? kicks.entries.filter(e => e.targetType === 'USER' && e.target.id === user.id).size : 'None';
            bans  = bans  ? bans.entries.filter(e => e.targetType === 'USER' && e.target.id === user.id).size  : 'None';

            embed.fields.push({ name: 'History', value: `Bans: ${bans}\nKicks: ${kicks}`, inline: true });
            embed.fields.push({ name: 'Joined', value: new Date(member.joinedTimestamp).toUTCString(), inline: false })
        }

        embed.fields.push({ name: 'Created', value: `${Math.floor((Date.now() - user.createdTimestamp) / 8.64e7)} days ago`, inline: false });

        ctx.channel.send({ embed });

    },

    developerOnly: false,
	serverOwnerOnly: false,
    permissions: [],
    requires: [],
    aliases: ['ui'],
	usage: '<user>',
	description: 'Displays information about the specified user'

}