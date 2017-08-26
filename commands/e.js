const inspector = require('util').inspect;

module.exports = {
	
	run: (ctx) => {

		let silent = ctx.args[0] === "-s"
		if (silent) 
			ctx.args = ctx.args.slice(1);
		try {

			let code = eval(ctx.args.join(" "));
			if (typeof code !== 'string')
				code = inspector(code, { depth: 0 });

			code = code.replace(new RegExp(ctx.client.token, 'gi'), '');

			if (!silent)
				ctx.channel.send(code, { code: 'js' });

		}catch (e) {

			if (!silent) 
				ctx.channel.send(e.message, { code: 'js' });

		}

	},

	developerOnly: true,

	permissions: []

}