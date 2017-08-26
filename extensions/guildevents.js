exports.start = (runtime) => {

	runtime.client.on('guildMemberAdd', (member) => {
		const sdb = runtime.db[member.guild.id];

		if (sdb && sdb.modlog.join && runtime.client.channels.has(sdb.modlog.join)) {

			let creation = runtime.utils.time(new Date().getTime() - member.user.createdAt.getTime(), true);
			runtime.client.channels.get(sdb.modlog.join).send({ embed: {
				color: 0xFF4500,
				author: {
					name: `${member.user.tag} (${member.user.id})`,
					icon_url: member.user.displayAvatarURL
				},
				description: 'User Joined',
				timestamp: new Date(),
				footer: {
					text: `Created ${creation} ago`
				}
			}})

		}

		// TODO: Assignable roles

	});

	runtime.client.on('guildMemberRemove', (member) => {
		const sdb = runtime.db[member.guild.id];
		
		if (sdb && sdb.modlog.leave && runtime.client.channels.has(sdb.modlog.leave)) {
		
			runtime.client.channels.get(sdb.modlog.join).send({ embed: {
				color: 0xFF4500,
				author: {
					name: `${member.user.tag} (${member.user.id})`,
					icon_url: member.user.displayAvatarURL
				},
				description: 'User Left',
				timestamp: new Date(),
			}})
		
		}
	});

}