from discord.ext.commands import BadArgument, Converter, UserConverter


class IDConverter(Converter):
    async def convert(self, ctx, argument):
        try:
            user = await UserConverter().convert(ctx, argument)
        except BadArgument:
            try:
                return int(argument)
            except ValueError:
                raise BadArgument('invalid user/id was specified')
        else:
            return user.id
