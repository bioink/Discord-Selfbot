import discord
from discord.ext import commands
import requests
import asyncio

prefix = ','

bot = commands.Bot(
    command_prefix=prefix, 
    description='not a selfbot', 
    self_bot=True, 
    help_command=None
)

react_users = {}
afk_users = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command(name='help')
async def help(ctx):
    """Show a list of available commands."""
    help_text = """
**Bioinks SelfBot Menu**

**General Commands:**
`ping` - Test command to check if the bot is active.
`afk <message>` - Set an AFK status with a custom message.
`clearstatus` - Clear any custom status.

**Reaction Commands:**
`sr <user_id> <emoji1> <emoji2> ...` - Start reacting to a user's messages with specified emojis.
`srs <user_id>` - Stop reacting to a user's messages.

**Custom Status Commands:**
`streaming <activity>` - Set your status to "Streaming <activity>".
`playing <activity>` - Set your status to "Playing <activity>".
`watching <activity>` - Set your status to "Watching <activity>".

**Remote Control Commands:**
`remote <user_id>` - Authorize a user to control the selfbot.
`remoteremove <user_id>` - Remove a user's authorization for remote control.
`showremotes` - Show the list of all authorized users.

**Spam Commands:**
`pack` - Start spamming messages from the predefined list.
`stop` - Stop spamming messages.

**Voice Commands:**
`vc <voice_channel_id>` - Join a voice channel by its ID.
`leavevc` - Disconnect from the current voice channel.

**Note:** Use these commands responsibly and in compliance with Discord's Terms of Service.
"""
    await ctx.send(f"```{help_text}```")

@bot.command()
async def sr(ctx, user_id: int, *emojis):
    """Start reacting to a user's messages with specified emojis."""
    if not emojis:
        await ctx.send("Please set at least **one** emoji man...")
        return
    react_users[user_id] = emojis
    await ctx.send(f"```Started reacting to messages from user ID: {user_id} with emojis: {' '.join(emojis)}```")

@bot.command()
async def srs(ctx, user_id: int):
    """Stop reacting to a user's messages."""
    if user_id in react_users:
        del react_users[user_id]
        await ctx.send(f"```Stopped reacting to messages from user ID: {user_id}```")
    else:
        await ctx.send(f"```No reactions were set for user ID: {user_id}```")

@bot.command()
async def afk(ctx, *, message="I am currently AFK."):
    """Set an AFK status with a custom message."""
    afk_users[ctx.author.id] = message
    await ctx.send(f"```{ctx.author.display_name} is now AFK: {message}```")

@bot.command()
async def streaming(ctx, *, activity: str):
    """Set streaming status with the specified activity."""
    streaming_activity = discord.Streaming(name=activity, url="https://twitch.tv/placeholder")
    await bot.change_presence(activity=streaming_activity)
    await ctx.send(f"```Set your status to: Streaming {activity}```")

@bot.command()
async def playing(ctx, *, activity: str):
    """Set playing status with the specified activity."""
    playing_activity = discord.Game(name=activity)
    await bot.change_presence(activity=playing_activity)
    await ctx.send(f"```Set your status to: Playing {activity}```")

@bot.command()
async def watching(ctx, *, activity: str):
    """Set watching status with the specified activity."""
    watching_activity = discord.Activity(type=discord.ActivityType.watching, name=activity)
    await bot.change_presence(activity=watching_activity)
    await ctx.send(f"```Set your status to: Watching {activity}```")

@bot.command()
async def clearstatus(ctx):
    """Clear any custom status."""
    await bot.change_presence(activity=None)
    await ctx.send(f"```Cleared your current status.```")

autorespond_users = {}

@bot.command(name='autorespond')
async def autorespond(ctx, user_id: int, *, message: str):
    """
    Set up an automatic response for a specific user's pings.
    :param user_id: The ID of the user to respond to
    :param message: The custom auto-response message
    """
    autorespond_users[user_id] = message
    await ctx.send(f"```Auto-response set for user ID: {user_id}.\nMessage: {message}```")

@bot.command(name='autorespondend')
async def autorespondend(ctx, user_id: int):
    """
    Remove auto-response for a specific user.
    :param user_id: The ID of the user to stop responding to
    """
    if user_id in autorespond_users:
        del autorespond_users[user_id]
        await ctx.send(f"```Auto-response removed for user ID: {user_id}.```")
    else:
        await ctx.send(f"```No auto-response set for user ID: {user_id}.```")

@bot.event
async def on_message(message):
    if message.author.id in autorespond_users and bot.user.mentioned_in(message):
        response_message = autorespond_users[message.author.id]
        try:
            await message.channel.send(response_message)
        except Exception as e:
            print(f"Failed to send auto-response: {e}")

authorized_users = set()


@bot.command()
async def remote(ctx, user_id: int):
    """Authorize a user to control the selfbot."""
    authorized_users.add(user_id)
    await ctx.send(f"```User ID: {user_id} has been authorized for remote control.```")

@bot.command()
async def remoteremove(ctx, user_id: int):
    """Remove a user's authorization."""
    if user_id in authorized_users:
        authorized_users.remove(user_id)
        await ctx.send(f"```User ID: {user_id} has been removed from remote control access.```")
    else:
        await ctx.send(f"```User ID: {user_id} is not authorized for remote control.```")

@bot.command()
async def showremotes(ctx):
    """Show the list of all authorized users."""
    if authorized_users:
        user_list = '\n'.join(str(user_id) for user_id in authorized_users)
        await ctx.send(f"```Authorized users:\n{user_list}```")
    else:
        await ctx.send("```No users are currently authorized for remote control.```")

@bot.event
async def on_message(message):
    if message.author.id != bot.user.id and message.author.id not in authorized_users:
        return

pack_messages = [
    "# NIGGA BUILT LIKE AN AUTISTIC CHICKEN",
    "# TALK TOO MUCH LMAOAOOA",
    "# QUIT TALKING",
    "# YOU'RE TALKING WAY TOO MUCH MAN!",
    "# BIOINK OWNS YOU MAN 💔😱🌈",
    "# you hear that? a penny dropped out of someones wallet! go get it boy'!",
    "# FILTHY JEW",
    "# stop talking when daddy's here baby",
    "# don't worry baby daddy's here"
]

spamming = False

@bot.command(name='pack')
async def pack(ctx):
    """Start spamming messages from the pack_messages list."""
    global spamming
    spamming = True
    await ctx.message.delete()
    while spamming:
        for message in pack_messages:
            if not spamming:
                break
            await ctx.send(message)
            await asyncio.sleep(1)

@bot.command(name='stop')
async def stop(ctx):
    """Stop spamming messages."""
    global spamming
    spamming = False
    await ctx.send("```Success: Stopped spamming messages.```", delete_after=5)

@bot.command(name='vc')
async def join_vc(ctx, vc_id: int):
    """
    Command to join a voice channel by its ID.
    :param vc_id: The ID of the voice channel to join
    """
    voice_channel = bot.get_channel(vc_id)
    if voice_channel is None:
        await ctx.send("```Invalid voice channel ID. Please provide a valid one.```")
        return

    if not isinstance(voice_channel, discord.VoiceChannel):
        await ctx.send("```The provided ID does not belong to a voice channel.```")
        return

    try:
        await voice_channel.connect()
        await ctx.send(f"```Successfully joined the voice channel: {voice_channel.name}```")
    except discord.ClientException:
        await ctx.send("```Already connected to a voice channel. Disconnect first before joining another.```")
    except Exception as e:
        await ctx.send(f"```Failed to join the voice channel. Error: {str(e)}```")

@bot.command(name='leavevc')
async def leave_vc(ctx):
    """
    Command to leave the current voice channel.
    """
    if ctx.voice_client is None:
        await ctx.send("```Not currently connected to any voice channel.```")
        return

    try:
        await ctx.voice_client.disconnect()
        await ctx.send("```Disconnected from the voice channel.```")
    except Exception as e:
        await ctx.send()

@bot.command()
async def ping(ctx):
    """Test command to check if the bot is active."""
    await ctx.send(f"```Pong! Latency: {round(bot.latency * 1000)}ms```")

@bot.event
async def on_message(message):
    if message.author.id in afk_users:
        del afk_users[message.author.id]
        await message.channel.send(f"```AFK removed, welcome back {message.author.display_name}!```")

    for user_id, afk_message in afk_users.items():
        if user_id == message.author.id:
            continue
        if message.mentions and user_id in [mention.id for mention in message.mentions]:
            await message.channel.send(f"```{bot.get_user(user_id).display_name} is currently AFK: {afk_message}```")
        elif isinstance(message.channel, discord.DMChannel) and message.author.id == user_id:
            await message.channel.send(f"```{bot.get_user(user_id).display_name} is currently AFK: {afk_message}```")
    
    if message.author.id in react_users:
        emojis = react_users[message.author.id]
        for emoji in emojis:
            try:
                await message.add_reaction(emoji)
            except discord.Forbidden:
                print(f"Unable to react with {emoji}")
            except discord.HTTPException:
                print(f"Invalid emoji: {emoji}")

    await bot.process_commands(message)

bot.run('TOKEN OVER HERE')
