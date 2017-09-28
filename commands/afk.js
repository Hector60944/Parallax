const fs = require("fs")

let permitted = ["180093157554388993", "284122164582416385", "180808090659061762"]

exports.run = async (runtime) => {
    if (args[0] === "exit") {

        if (!afkusers[msg.author.id] || !afkusers[msg.author.id].afk) 
			return msg.channel.send({ embed: { color: 0xbe2f2f, title: "AFK Status", description: `You are not AFK`}});

        afkusers[msg.author.id].afk = false
		dumpafkusers(afkusers);
		msg.channel.send({ embed: {
			color: 0xbe2f2f,
			title: "AFK Status",
			description: `You are no longer AFK.\n\nYou have **${afkusers[msg.author.id].mentions.length}** mentions\nView them with ${gdb.prefix}afk mentions`
		}});

    } else if (args[0] === "mentions") {

        if (!afkusers[msg.author.id]) 
			return msg.channel.send({ embed: { color: 0xbe2f2f, title: "AFK Status", description: `You are not AFK`}});
        if (afkusers[msg.author.id].mentions.length === 0) 
			return msg.channel.send({ embed: { color: 0xbe2f2f, title: "AFK Status", description: `You have no mentions.`}});
			
        msg.author.send(afkusers[msg.author.id].mentions.join("\n"), {split: true});
        afkusers[msg.author.id].mentions = [];
		dumpafkusers(afkusers);

	} else if (args[0] === "dispafk") {

		if (!afkusers[msg.author.id]) 
			return msg.channel.send({ embed: { color: 0xbe2f2f, title: "AFK Status", description: `You are not AFK`}});
		
		if (!args[1])
			return msg.channel.send({ embed: { color: 0xbe2f2f, title: "AFK Status", description: "dispafk < on | off >" }});

		if (args[1] === "on") {
			afkusers[msg.author.id].dispafk = true;
			msg.channel.send({ embed: { color: 0xbe2f2f, title: "AFK Status", description: "'is AFK' will display on pings." }});
		} else if (args[1] === "off") {
			afkusers[msg.author.id].dispafk = false;
			msg.channel.send({ embed: { color: 0xbe2f2f, title: "AFK Status", description: "'is AFK' will no longer display on pings." }});
		} else {
			return msg.channel.send({ embed: { color: 0xbe2f2f, title: "AFK Status", description: "Unrecognised argument." }});
		}

    } else {
        if (afkusers[msg.author.id] && afkusers[msg.author.id].afk) {
            msg.channel.send({ embed: { color: 0xbe2f2f, title: "AFK Status", description: `AFK status updated.`}});
            afkusers[msg.author.id].msg = args.join(" ")
			dumpafkusers(afkusers);
        } else {
            afkusers[msg.author.id] = {"afk" : true, "msg" : args.join(" "), "mentions" : [], "icon" : "", dispafk: true}
        	msg.channel.send({ embed: { color: 0xbe2f2f, title: "AFK Status", description: `You are now AFK.\nSend '${gdb.prefix}afk exit' to exit AFK.`}});
			dumpafkusers(afkusers);
        }
    }
}

exports.help = 'succ';