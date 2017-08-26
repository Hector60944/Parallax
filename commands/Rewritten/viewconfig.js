module.exports = {

	run: async (ctx) => {

		const autorole = {
			users: ctx.sdb.autorole.users.filter(r => ctx.guild.roles.has(r)).map(r => ctx.guild.roles.get(r).name).sort().join(', '),
			bots:  ctx.sdb.autorole.bots.filter(r => ctx.guild.roles.has(r)).map(r => ctx.guild.roles.get(r).name).sort().join(', ')
		}

		ctx.channel.send({ embed: {
			color: 0xbe2f2f,
			title: `Server Settings`,
			description: `Change these settings with \`${ctx.sdb.prefix}config\``,
			fields: [
				{ name: 'Mod-Log', 		 value: (ctx.sdb.modlog.actions  ? `<#${ctx.sdb.modlog.actions}>` : 'None'), inline: true },
				{ name: 'Join Channel',  value: (ctx.sdb.modlog.join     ? `<#${ctx.sdb.modlog.join}>`    : 'None'), inline: true },
				{ name: 'Leave Channel', value: (ctx.sdb.modlog.leave    ? `<#${ctx.sdb.modlog.leave}>`   : 'None'), inline: true },
				{ name: 'Autorole', 	 value: `\`Users:\` ${autorole.users || 'None'}\n` +
												`\`Bots :\` ${autorole.bots  || 'None'}`, 	  				         inline: false },
				{ name: 'Anti-Invite', 	 value: (ctx.sdb.invites         ? 'Enabled' : 'Disabled'), 			  	 inline: true },
				{ name: 'Anti-Raid', 	 value: (ctx.sdb.raid 		     ? 'Enabled' : 'Disabled'), 			  	 inline: true },
				{ name: '\u200B', 		 value: '\u200B', 															 inline: true }
			]
		}})

	},

	developerOnly: false,
    serverOwnerOnly: false,
	permissions: ['MANAGE_GUILD']
	
}
