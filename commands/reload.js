module.exports = {

    run: (ctx) => {

        let command = ctx.args[0];

        if (!command)
            return ctx.channel.send('Specify a command to reload.');

        if (!ctx.client.commands.has(command))
            return ctx.channel.send('Command not loaded.');

        ctx.client.commands.delete(command);

        try {
            ctx.client.commands.set(command, require(`../commands/${command}`));
            delete require.cache[require.resolve(`../commands/${command}`)];
            ctx.channel.send('Command reloaded.');
        } catch (e) {
            ctx.utils.log('error', e.message)
            ctx.channel.send('Failed to reload command.');
        }

    },

    developerOnly: true,
    serverOwnerOnly: false,
    permissions: [],
    aliases: [],
	usage: '[module]'

}