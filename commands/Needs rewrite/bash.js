const sf   = require("snekfetch");
const bash = require("child_process");

module.exports = {
	
	run: (ctx) => {

		if (ctx.args.length === 0) 
			return ctx.channel.send("No arguments passed");
			
		bash.exec(ctx.args.join(" "), {shell : '/bin/bash' }, async (e, stdout, stderr) => {
			if (!stdout && !stderr)
				return ctx.react("☑");

			if (stdout.length > 2000 || stderr.length > 2000) {
				let res = await sf.post("https://hastebin.com/documents").send(`OUT:\n${stdout}\n\nERR:\n${stderr}`);
				if (res.status === 200)
					ctx.channel.send({ embed: { color: 0xbe2f2f, title: "Click to view output", url: `https://hastebin.com/${res.body.key}` }});
				else
					ctx.channel.send(` Server returned ${res.status} while posting.`);
			} else {
				if (stdout) 
					ctx.channel.send(stdout, { code: 'js' });
				if (stderr) 
					ctx.channel.send(stderr, { code: 'js' });
			}
		});

	},

	developerOnly: true,

	permissions: []

}