module.exports = {
    
    run: async (ctx) => {

        let user = ctx.utils.resolveUser(ctx.client, ctx, ctx.args[0]);

        if (!user)
            return ctx.channel.send({ embed: {
                color: 0xbe2f2f,
                title: 'Failed to resolve user',
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

        let member = ctx.guild.members.get(user.id);

        if (member) {

            let kicks = await ctx.guild.fetchAuditLogs({ type: 20 })
            .catch(console.warn);
            let bans  = await ctx.guild.fetchAuditLogs({ type: 22 })
            .catch(console.warn);

            kicks = kicks ? kicks.entries.filter(e => e.targetType === 'USER' && e.target.id === user.id).size : 'None';
            bans  = bans  ? bans.entries.filter(e => e.targetType === 'USER' && e.target.id === user.id).size  : 'None';

            embed.fields.push({ name: 'History', value: `Bans: ${bans}\nKicks: ${kicks}`, inline: true });
            embed.fields.push({ name: 'Joined', value: member.joinedAt.toUTCString(), inline: false })
        }

        embed.fields.push({ name: 'Created', value: `${ctx.utils.time((new Date().getTime() - user.createdAt.getTime() / 1000), true)} ago`, inline: false });

        ctx.channel.send({ embed });

    },

    developerOnly: false,
	serverOwnerOnly: false,
	permissions: []

}