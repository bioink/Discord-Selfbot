import discord
from discord.ext import commands, tasks
import requests
import asyncio
import aiohttp 
import itertools
import pytz
from datetime import datetime
import nacl
print(pytz.all_timezones)


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
**The Help Menu**

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

react_users = {}

@bot.command()
async def sr(ctx, user_id: int, *emojis):
    """Start reacting to a user's messages with specified emojis."""
    if not emojis:
        await ctx.send("Please set at least **one** emoji man...")
        return
    react_users[user_id] = emojis
    await ctx.send(f"```Started reacting to messages from user ID: {user_id} with emojis: {' '.join(emojis)}```")

@bot.command(name='srs')
async def srs(ctx, user_id: int):
    """Stop reacting to a user's messages."""
    if user_id in react_users:
        del react_users[user_id]
        await ctx.send(f"```Stopped reacting to messages from user ID: {user_id}```")
    else:
        await ctx.send(f"```No reactions were set for user ID: {user_id}```")

@bot.event
async def on_message(message):
    """React to messages for users in the react_users dictionary."""
    if message.author.id in react_users:
        emojis = react_users[message.author.id]
        for emoji in emojis:
            try:
                await message.add_reaction(emoji)
            except discord.Forbidden:
                print(f"Unable to react with {emoji} due to insufficient permissions.")
            except discord.HTTPException:
                print(f"Failed to react with {emoji} due to an HTTP error.")
    await bot.process_commands(message)

sniped_messages = {}
sniped_reactions = {}
sniped_edits = {}

@bot.event
async def on_message_delete(message):
    """Stores the last deleted message in a channel."""
    if not message.author.bot:
        sniped_messages[message.channel.id] = {
            "author": str(message.author),
            "content": message.content or "Embedded content/attachment",
            "time": message.created_at
        }

@bot.command(name='snipe')
async def snipe(ctx):
    """Snipes the last deleted message in the channel."""
    channel_id = ctx.channel.id
    if channel_id in sniped_messages:
        msg = sniped_messages[channel_id]
        await ctx.send(
            f"**Author:** {msg['author']}\n"
            f"**Time:** {msg['time']}\n"
            f"**Message:** {msg['content']}"
        )
    else:
        await ctx.send("```There's nothing to snipe in this channel```")

@bot.event
async def on_reaction_remove(reaction, user):
    """Stores the last removed reaction in a channel."""
    if not user.bot:
        sniped_reactions[reaction.message.channel.id] = {
            "message": reaction.message.content,
            "emoji": str(reaction.emoji),
            "user": str(user),
            "time": reaction.message.created_at
        }

@bot.command(name='rs')
async def reaction_snipe(ctx):
    """Snipes the last removed reaction in the channel."""
    channel_id = ctx.channel.id
    if channel_id in sniped_reactions:
        react = sniped_reactions[channel_id]
        await ctx.send(
            f"**User:** {react['user']}\n"
            f"**Time:** {react['time']}\n"
            f"**Message:** {react['message']}\n"
            f"**Reaction Removed:** {react['emoji']}"
        )
    else:
        await ctx.send("```There's no reaction to snipe in this channel```")

@bot.event
async def on_message_edit(before, after):
    """Stores the last edited message in a channel."""
    if not before.author.bot:
        sniped_edits[before.channel.id] = {
            "author": str(before.author),
            "before": before.content or "Embedded content/attachment",
            "after": after.content or "Embedded content/attachment",
            "time": before.created_at
        }

@bot.command(name='es')
async def edit_snipe(ctx):
    """Snipes the last edited message in the channel."""
    channel_id = ctx.channel.id
    if channel_id in sniped_edits:
        edit = sniped_edits[channel_id]
        await ctx.send(
            f"**Author:** {edit['author']}\n"
            f"**Time:** {edit['time']}\n"
            f"**Before:** {edit['before']}\n"
            f"**After:** {edit['after']}"
        )
    else:
        await ctx.send("```There's no edited message to snipe in this channel```")

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    """Get information about a user."""
    member = member or ctx.author
    name = member.name
    id = member.id
    joined_at = member.joined_at.strftime('%Y-%m-%d %H:%M:%S')
    roles = [role.name for role in member.roles]
    await ctx.send(f"User Name: ```{name}```\nUser ID: ```{id}```\nJoined At: ```{joined_at}```\nRoles: {', '.join(roles)}")


status_list = itertools.cycle(["👋🏼", "⭐", "😱", "🙏"])

@tasks.loop(seconds=5)
async def change_status():
    current_status = next(status_list)
    await bot.change_presence(activity=discord.Game(name=current_status))

@bot.command(name='statuschange')
async def start_status(ctx):
    if not change_status.is_running():
        change_status.start()
        await ctx.send("Started changing statuses every 5 seconds.")

@bot.command(name='stopstatus')
async def stop_status(ctx):
    if change_status.is_running():
        change_status.stop()
        await ctx.send("Stopped changing statuses.")

@bot.command(name='copyserver')
async def copyserver(ctx, source_server_id: int, target_server_id: int):
    source_server = bot.get_guild(source_server_id)
    target_server = bot.get_guild(target_server_id)

    if not source_server:
        await ctx.send(f"```Source server with ID {source_server_id} not found```")
        return

    if not target_server:
        await ctx.send(f"```Target server with ID {target_server_id} not found```")
        return

    await ctx.send(f"```Starting to copy server structure from {source_server.name} to {target_server.name}. This may take some time...```")

    try:
        await target_server.edit(name=source_server.name)
        if source_server.icon:
            icon_bytes = await source_server.icon.read()
            await target_server.edit(icon=icon_bytes)
    except Exception as e:
        await ctx.send(f"```Failed to update server name or icon: {e}```")

    for channel in target_server.channels:
        try:
            await channel.delete()
            await asyncio.sleep(1)
        except Exception as e:
            print(f"```Could not delete channel {channel.name}: {e}```")

    for role in source_server.roles[::-1]:
        if role.is_default():
            continue
        try:
            await target_server.create_role(
                name=role.name,
                permissions=role.permissions,
                color=role.color,
                hoist=role.hoist,
                mentionable=role.mentionable
            )
            await asyncio.sleep(1)
        except Exception as e:
            print(f"```Could not copy role {role.name}: {e}```")

    for category in source_server.categories:
        try:
            new_category = await target_server.create_category(
                name=category.name,
                overwrites=category.overwrites
            )
            await asyncio.sleep(1)
            for channel in category.channels:
                if isinstance(channel, discord.TextChannel):
                    await new_category.create_text_channel(
                        name=channel.name,
                        topic=channel.topic,
                        nsfw=channel.nsfw,
                        slowmode_delay=channel.slowmode_delay
                    )
                elif isinstance(channel, discord.VoiceChannel):
                    await new_category.create_voice_channel(
                        name=channel.name,
                        bitrate=channel.bitrate,
                        user_limit=channel.user_limit
                    )
                await asyncio.sleep(1)
        except Exception as e:
            print(f"```Could not copy category {category.name}: {e}```")

    await ctx.send("```Server copy complete```")

@bot.command(name='time')
async def time(ctx, *, country: str):
    country_to_timezone = {
        "uae": "Asia/Dubai",
        "italy": "Europe/Rome",
        "usa": "America/New_York",
        "india": "Asia/Kolkata",
        "japan": "Asia/Tokyo",
        "china": "Asia/Shanghai",
        "australia": "Australia/Sydney",
        "canada": "America/Toronto",
        "brazil": "America/Sao_Paulo",
        "south africa": "Africa/Johannesburg",
        "germany": "Europe/Berlin",
        "france": "Europe/Paris",
        "mexico": "America/Mexico_City",
        "russia": "Europe/Moscow",
        "uk": "Europe/London",
        "saudi arabia": "Asia/Riyadh",
        "argentina": "America/Argentina/Buenos_Aires",
        "egypt": "Africa/Cairo",
        "thailand": "Asia/Bangkok",
        "south korea": "Asia/Seoul",
        "new zealand": "Pacific/Auckland",
        "spain": "Europe/Madrid",
        "pakistan": "Asia/Karachi",
        "singapore": "Asia/Singapore",
    }

    country = country.lower()

    if country in country_to_timezone:
        timezone = pytz.timezone(country_to_timezone[country])
        current_time = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        await ctx.send(f"```Current time in {country.title()} is {current_time}```")
    else:
        await ctx.send(f"```Sorry, I don't recognize the country '{country}'. Please make sure it's in the list or add it to the dictionary.```")


@bot.command(name='status')
async def set_status(ctx, *, status: str):
    """
    Set your Discord status to DND, Online, Idle, Offline, or Mobile.
    Usage: ,status <dnd|online|idle|offline|mobile>
    """
    status = status.lower()

    try:
        if status == "dnd":
            await bot.change_presence(status=discord.Status.dnd)
            await ctx.send("```Your status has been set to Do Not Disturb (DND).```")
        elif status == "online":
            await bot.change_presence(status=discord.Status.online)
            await ctx.send("```Your status has been set to Online.```")
        elif status == "idle":
            await bot.change_presence(status=discord.Status.idle)
            await ctx.send("```Your status has been set to Idle.```")
        elif status == "offline":
            await bot.change_presence(status=discord.Status.offline)
            await ctx.send("```Your status has been set to Offline (Invisible).```")
        elif status == "mobile":
            mobile_activity = discord.Activity(type=discord.ActivityType.custom, name="\U0001f4f1")
            await bot.change_presence(status=discord.Status.online, activity=mobile_activity)
            await ctx.send("```Your status has been set to Mobile (📱).```")
        else:
            await ctx.send("```Invalid status. Use dnd, online, idle, offline, or mobile.```")
    except Exception as e:
        await ctx.send(f"```Failed to set status. Error: {e}```")

@bot.command()
async def afk(ctx, *, message="I am currently AFK."):
    """Set an AFK status with a custom message."""
    afk_users[ctx.author.id] = message
    await ctx.send(f"```{ctx.author.display_name} is now AFK: {message}```")

@bot.command()
async def streaming(ctx, *, activity: str):
    """Set streaming status with the specified activity."""
    streaming_activity = discord.Streaming(name=activity, url="https://twitch.tv/r3alwyldstyl3")
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

@bot.command(name='delete')
async def delete(ctx, amount: int):
    """
    Deletes the specified number of your recent messages.
    Usage: ,delete <amount>
    """
    if amount < 1:
        await ctx.send("```Please specify a valid number of messages to delete.```")
        return

    await ctx.message.delete()
    deleted = 0

    async for message in ctx.channel.history(limit=500):
        if message.author.id == bot.user.id:
            await message.delete()
            deleted += 1
            if deleted >= amount:
                break

    await ctx.send(f"```Deleted {deleted} messages.```", delete_after=5)


import aiohttp

@bot.command(name='setpfp')
async def set_pfp(ctx, image_url: str):
    """
    Changes your profile picture.
    Usage: ,setpfp <image_url>
    """
    await ctx.message.delete()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status != 200:
                    await ctx.send("```Failed to fetch the image. Please provide a valid URL.```")
                    return
                
                image_data = await response.read()

        await bot.user.edit(avatar=image_data)
        await ctx.send("```Profile picture updated successfully.```")
    except discord.Forbidden:
        await ctx.send("```You do not have permission to change the profile picture.```")
    except Exception as e:
        await ctx.send(f"```An error occurred: {e}```")


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

bot.run('put token here ')
