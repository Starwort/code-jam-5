from discord.ext import commands


# predicate that tests if the user is Starwort, Suhail, or Bonnie
async def check(ctx):
    #      |<---Starwort--->|  |<----Bonnie---->|  |<----Suhail---->|
    ids = [232948417087668235, 124316478978785283, 131131701148647424]
    return ctx.author.id in ids


# discord check version of the above
def _check():
    return commands.check(check)
