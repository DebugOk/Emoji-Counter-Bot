#Imports 
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions,when_mentioned_or
from discord.utils import get

from datetime import datetime, timezone
import time
import os
import urllib.request
import shutil
import inspect
from zipfile import ZipFile
#Important
Prefix = '$' #Change the prefix here

client = commands.Bot(command_prefix=when_mentioned_or(Prefix))
client.remove_command("help")
ignoreChannels = [] #Add the id of your #logs channel for example
allowEval = False #Please do not enable this unless you have an reason to eval
version = 3.0
#Ready message
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

#Ensure we have a /temp directory, and if it exists we clear it
if not os.path.exists('temp'):
	os.makedirs('temp')
else:
    shutil.rmtree('temp')
    time.sleep(.6)
    os.makedirs('temp')

#Show a list of all emojis and how much they are used.
@client.command()
@has_permissions(manage_messages=True) 
async def emojis(ctx):
    await ctx.send("I'm working on it...")
    Counter = {}
    NameOnly = {}
    Emojis = []
    for Emoji in ctx.guild.emojis: #Get the emoji list ready
        if Emoji.animated: #Someone at Discord decided it was a good idea to have animated emojis prefix with an A...
            Counter["<a:{0}:{1}>".format(Emoji.name,Emoji.id)] = 0
            NameOnly["<a:{0}:{1}>".format(Emoji.name,Emoji.id)] = Emoji.name
            Emojis.append("<a:{0}:{1}>".format(Emoji.name,Emoji.id))
        else:
            Counter["<:{0}:{1}>".format(Emoji.name,Emoji.id)] = 0
            NameOnly["<:{0}:{1}>".format(Emoji.name,Emoji.id)] = Emoji.name
            Emojis.append("<:{0}:{1}>".format(Emoji.name,Emoji.id))
    for Channel in ctx.guild.text_channels:
        for Ignore in ignoreChannels:
            if not Channel.id == Ignore:
                async for message in Channel.history():
                    for Emoji in Emojis:
                        #Emoji = get(ctx.guild.emojis, name=NameOnly[Emoji]) #Idk why but this is the only way animated emojis work >.>
                        if Emoji in message.content:
                            Counter[Emoji] = Counter[Emoji]+1

    if not ignoreChannels: #This is needed so the bot works even when ignoreChannels is empty
        for Channel in ctx.guild.text_channels:
            async for message in Channel.history():
                for Emoji in Emojis:
                    if Emoji in message.content:
                         Counter[Emoji] = Counter[Emoji]+1

    message = ""
    for Key, Value in Counter.items():
        emoji = get(ctx.guild.emojis, name=NameOnly[Key]) #Idk why but this is the only way animated emojis work >.>
        message = message + "{0}: {1}\n".format(emoji,Value)
    embed = discord.Embed(title="Emoji occurrences", description=message)
    await ctx.send(embed=embed)

#Return a list of all current emojis
@client.command()
@has_permissions(manage_messages=True) 
async def emojilist(ctx):
    await ctx.send("I'm working on it...")
    emojiList = {}
    for Emoji in ctx.guild.emojis: #Get the emoji list ready
        if Emoji.animated:
            emojiList["<a:{0}:{1}>".format(Emoji.name,Emoji.id)] = ":{0}:".format(Emoji.name)
        else:
            emojiList["<:{0}:{1}>".format(Emoji.name,Emoji.id)] = ":{0}:".format(Emoji.name)
    temp = ""
    for Key, Value in emojiList.items():
        temp = temp + "{0}, {1}\n".format(Key,Value)
    f = open("temp.txt", "w")
    f.write(temp.rstrip())
    f.close()
    await ctx.send(file=discord.File('temp.txt'))

#Return a zip of all current emojis
@client.command()
@has_permissions(manage_messages=True) 
async def emojidump(ctx):
    await ctx.send("I'm working on it...")
    emojiList = []
    for Emoji in ctx.guild.emojis: 
        if Emoji.animated:
            fileName = "temp/{0}.gif".format(Emoji.name)
        else:
            fileName = "temp/{0}.png".format(Emoji.name)
        
        if not os.path.exists(fileName):
            with open (fileName, 'wb') as outFile:
                req = urllib.request.Request(Emoji.url, headers={'User-Agent': 'Mozilla/5.0'})
                data = urllib.request.urlopen(req).read()
                outFile.write(data)
        
        emojiList.append(fileName)
    
    zipObj = ZipFile('temp/emojiDump.zip', 'w')
    for filePath in emojiList:
        zipObj.write(filePath)
    zipObj.close()

    await ctx.send("Done",file=discord.File('temp/emojiDump.zip'))

#Ping command
@client.command()
async def ping(ctx):
    embedVar = discord.Embed(title="Pong!", description="Got a reply in {0}".format(round(client.latency, 1)), color=0x4287f5,timestamp=datetime.now())
    await ctx.send(embed=embedVar)

#Eval for debugging
@client.command(name='eval', pass_context=True)
@has_permissions(administrator=True) 
async def eval_(ctx, *, command):
    if not allowEval:
        await ctx.send("Eval has been disabled. If you have access to this bot's source you can enable it by setting `allowEval` to true.")
        return
    try:
        res = eval(command)
        if inspect.isawaitable(res): 
            embed = discord.Embed(title="Eval result", description="```{0}```".format(str(await res)))
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Eval result", description="```{0}```".format(str(res)))
            await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send("Eval unsuccessful!\n```{0}```".format(e))

#Help command
@client.command()
async def help(ctx):
    embed = discord.Embed(title="Help", description="Current prefix: {0}\n\nCurrent version: {1}".format(Prefix,version), color=0x08ffa0, timestamp=datetime.now())
    embed.add_field(name="emojis", value="This command will search for how many messages contain each custom emoji.\n\n**Required permissions:** Manage messages", inline=True)
    embed.add_field(name="emojilist",value="This command will put all of the server's custom emoji name's and their fancy programmer name's into a handy txt file.\n\n**Required permission:** Manage messages",inline=True)
    embed.add_field(name="emojidump",value="This command will download a copy of every custom emoji in the server and put them into a zip file, then upload that zip file for downloading.\n\n**Required permissions:** Manage messages",inline=True)
    embed.add_field(name="ping",value="This will check how fast the bot can reach Discord. It doesn't do anything special.\n\n**Required permissions:** *None*",inline=True)
    if allowEval:
        embed.add_field(name="eval",value="This is a testing command that allows for single line Python code execution. **This should normally be disabled! If you don't use this then disable this command!**\n\n**Required permissions:** Administrator",inline=True)
    embed.add_field(name="help",value="I wonder what this does...\n\n**Required permissions:** *None*",inline=True)

    #If you don't want to credit me/change the credit you can comment/edit the line below
    embed.set_author(name="Bot created by DebugOk#6605", url="https://ko-fi.com/debugok", icon_url="https://cdn.discordapp.com/avatars/282227463642415104/f6d632f4fa73a7ff947ebba43277cf11.webp")
    #If you don't want to credit me/change the credit you can comment/edit the line above
    
    await ctx.send(embed=embed)

#Main error thing
@client.event
async def on_command_error(ctx, error):
    print(error)
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found\n```{0}```".format(error))
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to do that!\n```{0}```".format(error))
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You are missing a required argument!\n```{0}```".format(error))
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid argument!\n```{0}```".format(error))
    elif isinstance(error, commands.CommandError) or isinstance(error,commands.CommandInvokeError):
        await ctx.message.add_reaction('???')
        try:
            await ctx.send("An error has occured!\n```{0}```".format(error)) #This error can possibly go past Discord's character limit. Better safe then sorry.
        except:
            await ctx.send("An error has occured!")
    else: 
        await ctx.send("An unknown error has occured!")

#Sign in
client.run('')