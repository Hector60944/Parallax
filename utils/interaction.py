class HierarchicalError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def _check_hierarchy(member, member2, self_check, suppress=False):
    if member.guild.owner_id == member2.id:
        if suppress:
            return

        if self_check:
            raise HierarchicalError('I cannot perform the requested action on the server owner.')
        else:
            raise HierarchicalError('You cannot perform that action on the server owner.')

    if not self_check:
        if member.guild.owner_id != member.id and member.top_role <= member2.top_role and not suppress:
            raise HierarchicalError('The target member has an equivalent or higher role than you.')
    else:
        if member.top_role <= member2.top_role and not suppress:
            raise HierarchicalError('The target member has an equivalent or higher role than me.')


def check_hierarchy(ctx, target):
    _check_hierarchy(ctx.me, target, True)
    _check_hierarchy(ctx.author, target, False)


def check_bot_has(ctx, **permissions):
    channel_permissions = ctx.channel.permissions_for(ctx.guild.me)
    return all(getattr(channel_permissions, k, None) is v for k, v in permissions.items())


def check_user_has(ctx, **permissions):
    channel_permissions = ctx.channel.permissions_for(ctx.author)
    return all(getattr(channel_permissions, k, None) is v for k, v in permissions.items())
