def check_hierarchy(member, member2, owner_check=False):
    if member.guild.owner_id == member2.id:
        return False

    if owner_check:
        return member.guild.owner_id == member.id or member.top_role > member2.top_role

    return member.top_role > member2.top_role


def check_bot_has(ctx, **permissions):
    channel_permissions = ctx.channel.permissions_for(ctx.guild.me)
    return all(getattr(channel_permissions, k, None) is v for k, v in permissions.items())


def check_user_has(ctx, **permissions):
    channel_permissions = ctx.channel.permissions_for(ctx.author)
    return all(getattr(channel_permissions, k, None) is v for k, v in permissions.items())
