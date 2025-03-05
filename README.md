# 📘 Bioink's Selfbot

Welcome to **Bioink's Selfbot**! This selfbot provides numerous features that enhance your Discord experience with automation, utility, and fun. Please note that using selfbots is against Discord's Terms of Service, so use responsibly and at your own risk.

## 🚀 Features

- **AFK System**: Set custom AFK messages and notify users when you're AFK.
- **Custom Status**: Update your profile to show streaming, watching, or playing statuses dynamically.
- **Message Reaction**: Automatically react to specific users' messages with custom emojis.
- **Spam Control**: Playfully spam predefined messages or stop spamming with a single command.
- **Voice Channel Controls**: Join or leave voice channels by their IDs.
- **Remote Control**: Authorize specific users to control your selfbot remotely.
- **Dependency Installation Command**: Easily install necessary dependencies for the selfbot.

## ⚙️ Commands

### General Commands:
- `ping` - Test command to check if the bot is active.
- `afk <message>` - Set an AFK status with a custom message.
- `clearstatus` - Clear any custom status.

### Reaction Commands:
- `sr <user_id> <emoji1> <emoji2> ...` - Start reacting to a user's messages with specified emojis.
- `srs <user_id>` - Stop reacting to a user's messages.

### Custom Status Commands:
- `streaming <activity>` - Set your status to "Streaming <activity>".
- `playing <activity>` - Set your status to "Playing <activity>".
- `watching <activity>` - Set your status to "Watching <activity>".

### Remote Control Commands:
- `remote <user_id>` - Authorize a user to control the selfbot.
- `remoteremove <user_id>` - Remove a user's authorization for remote control.
- `showremotes` - Show the list of all authorized users.

### Spam Commands:
- `pack` - Start spamming messages from the predefined list.
- `stop` - Stop spamming messages.

### Voice Commands:
- `vc <voice_channel_id>` - Join a voice channel by its ID.
- `leavevc` - Disconnect from the current voice channel.

### Setup Command:
- `download_requirements` - Provides instructions to download and install required dependencies.

### Example of Dependency Installation:
To run this selfbot, ensure you have Python 3.8 or higher installed, and execute the following command:
```bash
pip install -r requirements.txt
```

---

## 📁 File Structure

- `bot.py` - The main selfbot script.
- `requirements.txt` - List of Python dependencies.

---

## ⚠️ Disclaimer

This bot is for educational purposes only. Using selfbots on Discord violates their [Terms of Service](https://discord.com/terms). Proceed at your own risk, as your account may be banned.

---

## 🛠️ Setup Instructions

1. Clone this repository:
   ```bash
   git clone https://github.com/bioink/Discord-Selfbot.git
   cd Discord-Selfbot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add your bot token:
   Open `main.py` and replace `TOKEN OVER HERE` with your Discord token.

4. Run the selfbot:
   ```bash
   python main.py
   ```

5. Use the commands as mentioned in the features section!

---

## 🤝 Contributing

Contributions are welcome! Feel free to submit a pull request or raise an issue.

---

## 👨‍💻 Author

Made with ❤️ by [Bioink](https://github.com/bioink). Check out my other projects on [GitHub](https://github.com/bioink).

## 10 ⭐ FOR MORE COMMANDS!
