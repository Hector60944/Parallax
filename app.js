const utils    = require('./extensions/utils.js');
const settings = require('./storage/settings.json');
const fs       = require('fs');

utils.log('info', 'Initialising Parallax');

const Discord  = require('discord.js');
const client   = new Discord.Client({ fetchAllMembers: true });

const db  = require('./storage/db.json');
const afk = require('./storage/afk.json');

const extensions = {
	invite: require('./extensions/antiinvite.js').run,
	raid:   require('./extensions/antiraid.js').run,
}

client.commands = new Discord.Collection();

client.once('ready', () => {
	utils.log('info', `Logged in as ${client.user.username}`);
	require('./extensions/guildevents.js').start({ client, db, utils })

	client.guilds
	.filter(g => !db[g.id])
	.map(g => utils.createDB(g.id, db));

});

client.on('ready', () => client.user.setPresence({ game: { name: `${settings.prefix}help | v${settings.version}`, type: 0 } }) );

client.on('guildCreate', g => {
	if (g.members.filter(m => m.user.bot).size / g.members.size > 0.65 || g.members.filter(m => !m.user.bot).size < 5) 
		return g.leave();
	
	if (!db[g.id])
		utils.createDB(g.id, db);
});

client.on('guildDelete', g => {
	if (db[g.id])
		delete db[g.id];
});

client.on('message', ctx => {
	if (ctx.author.bot || !ctx.guild || !ctx.member || !db[ctx.guild.id]) return;

	if (ctx.channel.id !== '110373943822540800' && ctx.mentions.users.size > 0) {
		ctx.mentions.users.filter(u => afk[u.id] && afk[u.id].afk).map(u => {
			ctx.channel.send({ embed: { 
				color: 0xbe2f2f, 
				title: `${u.username} ${afk[u.id].dispafk ? 'is AFK' : ''}`, 
				description: `${afk[u.id].msg}`, 
				thumbnail: { 
					url: afk[u.id].icon || '' 
				}
			}});
			afk[u.id].mentions.push(`[${new Date().toGMTString()}] **${ctx.author.tag}** > ${ctx.guild.name} -> ${ctx.cleanContent}`);
		});
	}

	let sdb = db[ctx.guild.id];

	if (ctx.isMentioned(client.user.id) && ctx.content.toLowerCase().includes('help'))
		return ctx.channel.send({ embed: { 
			color: 0xbe2f2f, 
			title: 'Mention Help', 
			description: `Server Prefix: ${sdb.prefix}\n\nTo view my commands, send ${sdb.prefix}help`
		}});

	//if (db.activeModules.invites)  modules.invite(client, msg, db);
	//if (db.activeModules.raid)     modules.raid(client, msg, db, Discord);

	if (!ctx.content.toLowerCase().startsWith(sdb.prefix)) return;

	ctx.command  = ctx.content.toLowerCase().substring(sdb.prefix.length).split(' ')[0];
	ctx.args     = ctx.content.trim().split(' ').slice(1);
	ctx.filtered = ctx.content.trim().split(' ').slice(1).filter(a => !a.startsWith('-'));
	ctx.switches = resolveSwitches(ctx.content.trim().split(' ').slice(1));

	if (!client.commands.has(ctx.command)) {
		const findByAlias = client.commands.findKey(cmd => cmd.aliases && cmd.aliases.includes(ctx.command));
		if (!findByAlias)
			return;

		ctx.invokedCommand = ctx.command;
		ctx.command = findByAlias;
	}

	if (!ctx.guild.me.permissions.has('ADMINISTRATOR'))
		return ctx.channel.send({ embed: {
			color: 0xbe2f2f,
			title: 'Missing Permissions',
			description: 'Parallax requires `ADMINISTRATOR` permissions to run.'
		}});

	ctx.Discord  = Discord;
	ctx.client   = client;
	ctx.settings = settings;
	ctx.utils    = utils;
	ctx.sdb      = sdb;

	const command = client.commands.get(ctx.command);
	const missing = ctx.channel.permissionsFor(ctx.member).missing(command.permissions);

	if (command.developerOnly && ctx.author.id !== settings.ownerid)
		missing.push('BOT_OWNER');

	if (command.serverOwnerOnly && ctx.author.id !== ctx.guild.ownerID)
		missing.push('SERVER_OWNER');

	if (missing.length > 0)
		return ctx.channel.send({ embed: {
			color: 0xbe2f2f,
			title: 'Missing Required Permissions',
			description: missing.join('\n')
		}});
		
	try {
		command.run(ctx);
	} catch(e) {
		utils.log('error', `Command ${ctx.command} failed. ${ctx.args ? `Parameters: ${ctx.args.join(' ')}` : ''}\nStack: ${e.stack.split('\n').slice(0, 3).join('\n')}`)
		ctx.channel.send('An error has occurred while processing the command. The error has been logged.');
	}

});

fs.readdir('./commands/', (err, files) => {

	if (err)
		return utils.log('error', 'Failed to read command directory!')

	for (let file of files) {
		file = file.split('.')[0];
		try {
			client.commands.set(file, require(`./commands/${file}`));
			delete require.cache[require.resolve(`./commands/${file}`)];
		} catch (e) {
			utils.log('error', `${file} failed to load.`)
		}
	}

});

function resolveSwitches(args) {
	let switches = {}
	args
	.filter(a => (a.startsWith('--') && a.length > 2) || (a.startsWith('-') && a.length > 1))
	.map(a => switches[a.replace(/\-/g, '').toLowerCase()] = true);
	return switches;
}

/*
setInterval(() => {

	let temp = {};

	for (let g in database) {
		let filtered = database[g].filter(ban => Date.now() >= ban.time);
		if (filtered.length >= 1) temp[g] = filtered;
	}

	if (Object.keys(temp).length === 0) return;

	for (let g in temp) {
		if (!client.guilds.has(g) || !client.guilds.get(g).me.hasPermission('BAN_MEMBERS')) continue;
		temp[g].forEach(u => { client.guilds.get(g).unban(u.id) });
		database[g] = database[g].filter(ban => Date.now() <= ban.time);
	}

	utils.db.writeBanDB(database);

}, 10000);
*/

client.login(settings.token);