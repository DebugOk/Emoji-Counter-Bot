import discord
from datetime import datetime, timezone, date
from discord.ext import commands
from discord.ext.commands import has_permissions
client = commands.Bot(command_prefix='$')
client.remove_command("help")

ignoreChannels = [830131334349324388]

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.command()
@has_permissions(manage_messages=True) 
async def emojis(ctx):
    await ctx.send("I'm working on it...")
    Counter = {}
    Emojis = []
    for Emoji in ctx.guild.emojis: #Get the emoji list ready
        Counter["<:{0}:{1}>".format(Emoji.name,Emoji.id)] = 0
        Emojis.append("<:{0}:{1}>".format(Emoji.name,Emoji.id))

    for Channel in ctx.guild.text_channels:
        for Ignore in ignoreChannels:
            if not Channel.id == Ignore:
                async for message in Channel.history():
                    for Emoji in Emojis:
                        if Emoji in message.content:
                            Counter[Emoji] = Counter[Emoji]+1


    #await ctx.send(Emojis)
    

    message = ""
    for Key, Value in Counter.items():
        message = message + "{0}: {1}\n".format(Key,Value)
    embed = discord.Embed(title="Emoji occurrences", description=message)
    await ctx.send(embed=embed)

@emojis.error
async def kick_error(ctx, error):
    await ctx.send("You don't have permission to do that or an error occured!")


@client.command()
async def ping(ctx):
    await ctx.message.delete()
    print("Running test command!")
    embedVar = discord.Embed(title="Pong!", description="Got a reply in {0}".format(round(client.latency, 1)), color=0x4287f5,timestamp=datetime.now())
    msg = await ctx.send(embed=embedVar)
    await msg.delete(delay=5)

@client.event
async def on_command_error(ctx, error):
    if not isinstance(error, commands.CheckFailure): 
        print(error)
        await ctx.message.add_reaction('❌')
        await ctx.reply("No such command or an error occured!", mention_author=False)


client.run('')