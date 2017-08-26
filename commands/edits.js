exports.run = async function(client, msg, args, db, Discord, settings) {

	if (!args[0]) return msg.channel.send(
		new Discord.RichEmbed()
		.setColor("#be2f2f")
		.setTitle("Invalid Message ID")
		.setDescription("Please specify a valid message ID")
	);

	let ms = await msg.channel.send({ embed:
		new Discord.RichEmbed()
		.setColor("#be2f2f")
		.setTitle("Searching for messages...")
		.setDescription(":eyes:")
	});

	let m = await msg.channel.fetchMessage(args[0])
	.catch(err => {}) //send it to no where

	if (!m || !m.edits || m.edits.length <= 1)
		return ms.edit({embed:
			new Discord.RichEmbed()
			.setColor("#be2f2f")
			.setTitle("Unable to Find Message")
			.setDescription("There were no edits/messages linked to the ID.")
		});

	ms.edit({embed:
		new Discord.RichEmbed()
		.setColor("#be2f2f")
		.setTitle("__Message Sent by: " + m.author.username + "__")
		.addField("Edits:", m.edits.slice(1).reverse().join("\n"))
	});

}
