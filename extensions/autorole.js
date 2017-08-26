exports.run = function(client, member, db, Discord) {
    if (member.user.bot) {
        db.activeModules.autorole.bots.map(r => {
            let role = member.guild.roles.get(r)
            if (!role) return false;
            member.addRole(role)
        })
    } else {
        db.activeModules.autorole.users.map(r => {
            let role = member.guild.roles.get(r)
            if (!role) return false;
            member.addRole(role)
        })
    }
}
