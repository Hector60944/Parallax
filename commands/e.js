const inspector = require('util').inspect;

module.exports = {
	
	run: (ctx) => {

		try {
			let code = eval(ctx.args.join(' '));
			if (typeof code !== 'string')
				code = inspector(code, { depth: 0 });

			code = code.replace(new RegExp(ctx.client.token, 'gi'), '');

			if (!ctx.switches.silent)
				ctx.channel.send(code, { code: 'js' });

		}catch (e) {

			if (!ctx.switches.silent) 
				ctx.channel.send(e.message, { code: 'js' });

		}

	},

	developerOnly: true,
	serverOwnerOnly: false,
	permissions: []

}