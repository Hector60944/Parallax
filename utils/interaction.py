class HierarchicalError(Exception):
    def __init__(self, message):
        self.message = message


def _check_hierarchy(member, member2, self_check):
    if member.guild.owner_id == member2.id:
        if self_check:
            raise HierarchicalError('I cannot perform the requested action on the server owner.')
        else:
            raise HierarchicalError('You cannot perform that action on the server owner.')

    if not self_check:
        if not member.guild.owner_id == member.id or member.top_role > member2.top_role:
            raise HierarchicalError('You cannot perform that action on a member who is higher than you.')

    if not member.top_role > member2.top_role:
        raise HierarchicalError('The target member is has an equivalent or higher role than you.')


def check_hierarchy(ctx, target):
    _check_hierarchy(ctx.me, target, True)
    _check_hierarchy(ctx.author, target, False)


def check_bot_has(ctx, **permissions):
    channel_permissions = ctx.channel.permissions_for(ctx.guild.me)
    return all(getattr(channel_permissions, k, None) is v for k, v in permissions.items())


def check_user_has(ctx, **permissions):
    channel_permissions = ctx.channel.permissions_for(ctx.author)
    return all(getattr(channel_permissions, k, None) is v for k, v in permissions.items())
