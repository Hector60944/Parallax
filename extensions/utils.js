const jsonw = require('./jsonw.js');
const chalk = require('chalk');

module.exports = {

    time: (time, formal) => {

        time = time / 1000;
        let days    = Math.floor(time % 31536000 / 86400),
        hours   = Math.floor(time % 31536000 % 86400 / 3600),
        minutes = Math.floor(time % 31536000 % 86400 % 3600 / 60),
        seconds = Math.round(time % 31536000 % 86400 % 3600 % 60);
        days    = days    > 9 ? days    : "0" + days
        hours   = hours   > 9 ? hours   : "0" + hours
        minutes = minutes > 9 ? minutes : "0" + minutes
        seconds = seconds > 9 ? seconds : "0" + seconds
        if (formal)
            return `${days > 0 ? `${days} days, ` : ``}${(hours || days) > 0 ? `${hours} hours, ` : ``}${minutes} minutes and ${seconds} seconds`
        else
            return `${days > 0 ? `${days}:` : ``}${(hours || days) > 0 ? `${hours}:` : ``}${minutes}:${seconds}`

    },

    createDB: (id, db) => {
        
        db[id] = template;
        
    },
        
    updateDB: (id, db) => {
                
        jsonw(`/root/parallax/storage/db.json`, db).catch(console.warn);
        
    },

    canPost: (channel, embed) => {

        if (embed)
            return channel.permissionsFor(channel.guild.me).has(['SEND_MESSAGES', 'EMBED_LINKS']);
        else
            return channel.permissionsFor(channel.guild.me).has('SEND_MESSAGES');

    },

    resolveUser: (client, ctx, search) => {
        
        if (ctx.mentions.users.size > 0)
            return ctx.mentions.users.first();

        if (!search)
            return undefined;

        if (!isNaN(search)) 
            return client.users.get(search);

        if (search.includes('#'))
            return client.users.filter(u => u.tag === search).first();
        else
            return client.users.filter(u => u.username === search).first();

    },
    
    canInteract: (user1, user2) => {
        return user1.id === user1.guild.ownerID || user1.highestRole.comparePositionTo(user2.highestRole) > 0
    },

    channelCheck: (channel, user, permissions) => {
        return channel.permissionsFor(user).has(permissions)
    },

    log: (type, content) => {

        if (type === 'info')
            console.log(chalk.green(`[${new Date().toLocaleTimeString()}] [INFO] ${content}`));
        else if (type === 'warn')
            console.log(chalk.yellow(`[${new Date().toLocaleTimeString()}] [WARN] ${content}`));
        else if (type === 'error')
            console.log(chalk.red(`[${new Date().toLocaleTimeString()}] [ERR ] ${content}`));
        else
            console.log(chalk.white(`[${new Date().toLocaleTimeString()}] [INFO] ${content}`));
    }

}

const template = {
	channels: {
		actions : "",
		join : "",
		leave : ""
	},
	raid: false,
	invites: false,
	autorole: {
		bots: [],
		users: []
    },
    assignable: [],
    bans: [],
    mutes: [],
    prefix: require("../storage/settings.json").prefix,
}