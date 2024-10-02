import discord
from discord.ext import commands
from discord import SlashCommandGroup

class Meme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    laudepe = SlashCommandGroup(name="laudepe", description="Jise Pata Hai Use Pata Hai")

    @laudepe.command(name="dusro", description="Jise Pata Hai Use Pata Hai")
    async def dusro(self, ctx, name_1: str = 'Mai', name_2: str = 'Leaf'):

        meme_url = f"https://api.memegen.link/images/custom/{name_1}/{name_2}_ke_laude_me.png?background=https://i.imgur.com/VyLho2N.png"

        await ctx.respond(meme_url)

    @laudepe.command(name="apna", description="Jise Pata Hai Use Pata Hai")
    async def apna(self, ctx, name: str = 'Leaf'):

        meme_url = f"https://api.memegen.link/images/custom/{name}/mera_laude_me.png?background=https://i.imgur.com/VyLho2N.png"

        await ctx.respond(meme_url)

    @laudepe.command(name="dono", description="Jise Pata Hai Use Pata Hai")
    async def dono(self, ctx):

        meme_url = f"https://api.memegen.link/images/custom/ye_sab/apne_apne_laude_me.png?background=https://i.imgur.com/VyLho2N.png"

        await ctx.respond(meme_url)

def setup(bot):
    bot.add_cog(Meme(bot))