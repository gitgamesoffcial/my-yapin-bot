import time
import yapin

# Initialize the Bot using the correct library name
bot = yapin.Bot()

# --- ⚙️ CONFIGURATION CONSTANTS ⚙️ ---
HONEYPOT_CHANNEL_ID = "ed036818-8611-4e3e-ac25-2008a4f98aa4"
LOG_CHANNEL_ID = "5e00c3a6-d488-408f-9cfc-c1ba63044c91"

# Platform UUID Security Identifiers
OWNER_USER_ID = "93e63418-8579-4f90-8a4f-456c9f2cb6db"
MANAGEMENT_ROLE_ID = "93e63418-8579-4f90-8a4f-456c9f2cb6db"
ADMIN_ROLE_ID = "e477c56a-6550-493b-b825-a837940b8bdf"
SENIOR_MOD_ROLE_ID = "5c0b2360-dadb-409c-b53b-33bb57ed0e9d"
MOD_ROLE_ID = "bd8e4337-3fc0-4a38-aa13-4e2ca4506e05"
JUNIOR_MOD_ROLE_ID = "7abff3dd-e833-4702-8acf-1660a802123d"


def log_event(text_message: str):
    """Utility to print logs locally to the terminal AND transmit them live to your Yapin channel"""
    print(f"[LOG] {text_message}")

    if LOG_CHANNEL_ID == "YOUR_LOG_CHANNEL_ID_HERE" or not LOG_CHANNEL_ID.strip():
        return

    try:
        bot.send(LOG_CHANNEL_ID, f"📋 {text_message}")
    except Exception as e:
        print(f"[ERROR] Failed sending live log update to Yapin chat: {e}")


def is_authorized(msg) -> bool:
    """Helper function to validate the user against structural platform IDs"""
    user_id = getattr(msg.author, "id", "")
    if str(user_id) == OWNER_USER_ID:
        return True

    if getattr(msg.author, "is_owner", False):
        return True

    allowed_role_ids = {
        MANAGEMENT_ROLE_ID,
        ADMIN_ROLE_ID,
        SENIOR_MOD_ROLE_ID,
        MOD_ROLE_ID,
        JUNIOR_MOD_ROLE_ID
    }

    user_roles = getattr(msg.author, "roles", [])
    for role in user_roles:
        r_id = getattr(role, "id", "")
        if str(r_id) in allowed_role_ids:
            return True

    return False


# --- 1. HONEYPOT & EVENT TRACKING EVENT LISTENER ---
@bot.on("on_message")
def on_message(msg):
    if msg.author == bot.user:
        return

    # 🛑 HONEYPOT SYSTEM CHECK
    if str(msg.channel_id) == HONEYPOT_CHANNEL_ID:
        log_event(f"🚨 HONEYPOT TRIGGERED by @{msg.author}! Content: '{msg.content}'")

        try:
            bot.delete(msg.channel_id, msg.id)
            log_event(f"🗑️ Honeypot trace message purged from feed successfully.")
        except Exception as delete_error:
            log_event(f"❌ Failed to delete honeypot message: {delete_error}")

        try:
            bot.ban(msg.server_id, f"@{msg.author}", reason="Honeypot violation: Typing in restricted channel.")
            bot.send(msg.channel_id, f"💥 *Bang!* @{msg.author} touched the honeypot, their trace was wiped, and they have been permanently banned.")
        except Exception as ban_error:
            log_event(f"❌ Failed to execute honeypot ban on @{msg.author}: {ban_error}")
        return

    # Log ordinary chat interactions to both the terminal and your log channel layout
    log_event(f"Message from @{msg.author} in #{msg.channel_id}: '{msg.content}'")


# --- 2. SERVER CHANGE LOGGING EVENT LISTENERS ---
@bot.on("on_member_join")
def on_member_join(member):
    log_event(f"📥 Member Joined: @{member.username} (ID: {member.id}) has entered the server.")


@bot.on("on_member_leave")
def on_member_leave(member):
    log_event(f"📤 Member Left: @{member.username} (ID: {member.id}) has departed or been kicked.")


@bot.on("on_channel_create")
def on_channel_create(channel):
    log_event(f"🛠️ Channel Created: #{channel.name}")


@bot.on("on_channel_delete")
def on_channel_delete(channel):
    log_event(f"🗑️ Channel Removed: #{channel.name}")


# --- 3. UTILITY & MODERATION COMMANDS ---

# 🏓 PING COMMAND WITH MILLISECONDS
@bot.command("ping", "Checks if the bot is alive and calculates ping latency.")
def ping(msg):
    try:
        # Start a local execution timer
        start_time = time.perf_counter()

        # Calculate API latency if message timestamp metadata is present
        timestamp = getattr(msg, "timestamp", None) or getattr(msg, "created_at", None)

        if timestamp:
            # Measure platform API round-trip delay relative to current system epoch time
            latency = round((time.time() - float(timestamp)) * 1000)
            # Prevent negative anomaly layouts if system clocks sync slightly out of order
            if latency < 0:
                latency = round((time.perf_counter() - start_time) * 1000)
        else:
            # Fallback local calculation loop speed
            latency = round((time.perf_counter() - start_time) * 1000)

        msg.reply(f"🏓 Pong! Start-Gun-Bot is online. Latency: **{latency}ms**")
        log_event(f"ℹ️ Utility check: Ping requested by @{msg.author} ({latency}ms)")
    except Exception as e:
        print(f"Ping Error: {e}")

@bot.command("mute", "Mutes a user by giving them the Muted role.")
def mute(msg):
    if not is_authorized(msg):
        msg.reply("❌ **Access Denied.** You do not have permission to use mute!")
        log_event(f"⚠️ UNAUTHORIZED USE: @{msg.author} tried to use /mute!")
        return

    if not msg.args:
        msg.reply("⚠️ Please specify a user to mute! Example: `/mute @username spamming`")
        return

    parts = msg.args.split(" ", 1)
    target_user = parts[0]
    reason = parts[1] if len(parts) > 1 else "Muted by a moderator"

    try:
        bot.add_role(msg.server_id, target_user, "Muted")
        msg.reply(f"🤐 {target_user} has been muted. Reason: *{reason}*")
        log_event(f"🤐 Moderator mute: {target_user} was muted by @{msg.author} for: {reason}")
    except Exception as e:
        msg.reply(f"❌ Failed to mute {target_user}. Make sure a 'Muted' role exists and I have permission to manage it!")
        print(f"Mute Error: {e}")

@bot.command("gun", "Bans a user from the server.")
def gun(msg):
    if not is_authorized(msg):
        msg.reply("❌ **Access Denied.** You do not have permission to use gun!")
        log_event(f"⚠️ UNAUTHORIZED USE: @{msg.author} tried to use /gun!")
        return

    if not msg.args:
        msg.reply("⚠️ Please specify a user to ban! Example: `/gun @username rules`")
        return

    parts = msg.args.split(" ", 1)
    target_user = parts[0]
    reason = parts[1] if len(parts) > 1 else "Hit by the !gun command"

    try:
        bot.ban(msg.server_id, target_user, reason=reason)
        msg.reply(f"💥 *Bang!* {target_user} has been banned. Reason: *{reason}*")
        log_event(f"🔨 Moderator ban: {target_user} was banned by @{msg.author} for: {reason}")
    except Exception as e:
        msg.reply(f"❌ Failed to ban {target_user}. Check my server permissions!")

@bot.command("getout", "Kicks a user from the server.")
def getout(msg):
    if not is_authorized(msg):
        msg.reply("❌ **Access Denied.** You do not have permission to use getout!")
        log_event(f"⚠️ UNAUTHORIZED USE: @{msg.author} tried to use /getout!")
        return

    if not msg.args:
        msg.reply("⚠️ Please specify a user to kick! Example: `/getout @username`")
        return

    parts = msg.args.split(" ", 1)
    target_user = parts[0]
    reason = parts[1] if len(parts) > 1 else "Ordered to GET OUT"

    try:
        bot.kick(msg.server_id, target_user, reason=reason)
        msg.reply(f"🚪 *Whoosh!* {target_user} was kicked. Reason: *{reason}*")
        log_event(f"🥾 Moderator kick: {target_user} was kicked by @{msg.author} for: {reason}")
    except Exception as e:
        msg.reply(f"❌ Failed to kick {target_user}. Check my server permissions!")

@bot.command("clear", "Clears recent chat messages.")
def clear(msg):
    if not is_authorized(msg):
        msg.reply("❌ **Access Denied.** You do not have permission to use clear!")
        log_event(f"⚠️ UNAUTHORIZED USE: @{msg.author} tried to use /clear!")
        return

    amount = 10
    if msg.args:
        try:
            amount = int(msg.args.strip())
        except ValueError:
            msg.reply("⚠️ Please provide a valid number! Example: `/clear 20`")
            return

    try:
        messages_list = bot.messages(msg.channel_id)

        if messages_list:
            message_ids = [m.id for m in messages_list[:amount] if hasattr(m, 'id')]
            if message_ids:
                bot.bulk_delete(msg.channel_id, message_ids)
                msg.reply(f"🧹 Cleared {len(message_ids)} messages!")
                log_event(f"🧹 Chat cleared: @{msg.author} removed {len(message_ids)} messages in #{msg.channel_id}")
                return

        msg.reply("🤷 No messages found to clear.")
    except Exception as e:
        msg.reply("❌ Server clear error. Ensure my role tier is positioned at the top slot!")
        print(f"Clear Error Trace: {e}")


# --- 4. STARTUP STATUS LOG ---
@bot.on("on_ready")
def on_ready():
    print(f"Start-Gun-Bot is online and logged in as {bot.user}!")
    log_event("Security core online. Precision ms diagnostic timers armed.")

bot.run()
