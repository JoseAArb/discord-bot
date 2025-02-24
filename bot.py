import discord
import asyncio
import datetime
import os
import ssl
import certifi
import pytz  # Import pytz for timezone handling

ssl_context = ssl.create_default_context(cafile=certifi.where())

# Load bot token from .env file
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Define the timezone you want to use (change accordingly)
LOCAL_TIMEZONE = pytz.timezone("America/New_York")  # Example: Eastern Time (ET)

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Assignment due date reminders (YYYY-MM-DD HH:MM format)
report_dates = {
    "2025-02-27 23:59": "Progress Report 3",
    "2025-03-06 23:59": "Progress Report 4",
    "2025-03-13 23:59": "Progress Report 5",
    "2025-04-03 23:59": "Progress Report 6",
    "2025-04-10 23:59": "Progress Report 7",
    "2025-04-17 23:59": "Progress Report 8",
    "2025-04-24 23:59": "Progress Report 9",
    "2025-05-01 23:59": "Progress Report 10",
}

due_dates = {
    "2025-03-30 23:59": "Midterm Presentation Submission",
    "2025-05-07 23:59": "Final Paper Submission",
    "2025-05-09 23:59": "Final Presentation Submission"
}

# Meeting schedule (day-specific times in 24-hour format)
meeting_schedule = {
    "Monday": "21:00",   
    "Thursday": "20:30", 
    "Saturday": "18:00"    
}

# Function to find the correct channel by name
async def get_channel_by_name(guild, channel_name):
    for channel in guild.text_channels:
        if channel.name == channel_name:
            return channel
    return None

async def send_reminders():
    await client.wait_until_ready()
    
    while not client.is_closed():
        # Get the current time in UTC and convert it to the local timezone
        now_utc = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        now = now_utc.astimezone(LOCAL_TIMEZONE)  # Convert to your local timezone

        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%Y-%m-%d")
        current_day = now.strftime("%A")  # Get current day (Monday, Thursday, etc.)

        # Calculate upcoming dates
        one_week_before = (now + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        three_days_before = (now + datetime.timedelta(days=3)).strftime("%Y-%m-%d")
        one_day_before = (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        # Get tomorrow's date to check for meeting reminders
        tomorrow = (now + datetime.timedelta(days=1)).strftime("%A")

        for guild in client.guilds:
            due_dates_channel = await get_channel_by_name(guild, "due_dates")
            meeting_channel = await get_channel_by_name(guild, "meeting_reminders")

            # Assignment reminders (1 week, 3 days, 1 day before, and on due date)
            for due_date_time, message in due_dates.items():
                due_date = due_date_time.split(" ")[0]  # Extract only the date
                
                if due_dates_channel:
                    if current_date == due_date and current_time == "12:00":
                        await due_dates_channel.send(f"@everyone 🚨 **DUE TODAY:** {message}")
                    elif current_date == one_day_before and current_time == "12:00":
                        await due_dates_channel.send(f"@everyone ⚠️ **1 day left!** {message}")
                    elif current_date == three_days_before and current_time == "12:00":
                        await due_dates_channel.send(f"@everyone ⏳ **3 days left!** {message}")
                    elif current_date == one_week_before and current_time == "12:00":
                        await due_dates_channel.send(f"@everyone 📅 **1 week left!** {message}")

            # Report reminders (only sends on the due date)
            for report_date_time, report_message in report_dates.items():
                report_date = report_date_time.split(" ")[0]  # Extract only the date

                if due_dates_channel:  # Uses the same channel as due_dates
                    if current_date == report_date and current_time == "12:00":
                        await due_dates_channel.send(f"@Jose 📝 **REPORT DUE TODAY:** {report_message}")

            # Meeting reminders:
            if meeting_channel:
                # 1️⃣ **Reminder the day before at 12:00 PM**
                if tomorrow in meeting_schedule and current_time == "12:00":
                    meeting_time_24hr = meeting_schedule[tomorrow]
                    meeting_time_12hr = datetime.datetime.strptime(meeting_time_24hr, "%H:%M").strftime("%I:%M %p")
                    await meeting_channel.send(f"@everyone 🔔 Reminder: You have a meeting **tomorrow** at {meeting_time_12hr}!")

                # 2️⃣ **Reminder 10 minutes before the meeting**
                if current_day in meeting_schedule:
                    meeting_time_24hr = meeting_schedule[current_day]
                    
                    # Convert meeting time to a datetime object with the correct timezone
                    meeting_hour, meeting_minute = map(int, meeting_time_24hr.split(":"))
                    meeting_datetime = now.replace(hour=meeting_hour, minute=meeting_minute, second=0, microsecond=0)

                    # Calculate 10 minutes before the meeting
                    reminder_datetime = meeting_datetime - datetime.timedelta(minutes=10)
                    reminder_time = reminder_datetime.strftime("%H:%M")
                    meeting_time_12hr = meeting_datetime.strftime("%I:%M %p")

                    if current_time == reminder_time:
                        await meeting_channel.send(f"@everyone ⏳ **10-Minute Warning!** Meeting starts at {meeting_time_12hr}!")

        await asyncio.sleep(60)  # Check every minute

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user}')
    client.loop.create_task(send_reminders())

client.run(TOKEN)
