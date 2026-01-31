
import telebot
import requests
import json

# Telegram Bot Token
BOT_TOKEN = "8404506808:AAF3q3eiuu-oCaNLkF_-koD3Pd8ZTGjX82s"

# Facebook Report API Endpoint (This is a placeholder, you'll need to find the actual API endpoint)
FACEBOOK_REPORT_API = "https://www.facebook.com/akilizz.khangem"

# Initialize Telegram Bot
bot = telebot.TeleBot(BOT_TOKEN)

def report_facebook_profile(profile_link, reason):
    """
    Report a Facebook profile using the Facebook API.
    Note: You'll need valid Facebook API credentials and the correct API endpoint.
    """
    # Extract user ID from the profile link
    try:
        user_id = profile_link.split("facebook.com/")[1].split("/")[0]
    except IndexError:
        return "Invalid Facebook profile link."

    # Prepare the data for the report
    report_data = {
        "uid": user_id,
        "reason": reason,
        "access_token": "YOUR_FACEBOOK_ACCESS_TOKEN"  # Replace with a valid access token
    }

    try:
        response = requests.post(FACEBOOK_REPORT_API, data=report_data)
        response_json = response.json()

        if response_json.get("success"):
            return f"Successfully reported profile: {profile_link}"
        else:
            return f"Failed to report profile: {profile_link}. Error: {response_json.get('error_msg', 'Unknown error')}"
    except requests.exceptions.RequestException as e:
        return f"Failed to report profile: {profile_link}. Error: {str(e)}"

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Welcome! Send me a list of Facebook profile links to report.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    # Split the message into lines, each line is assumed to be a profile link
    profile_links = message.text.splitlines()

    results = []
    for link in profile_links:
        result = report_facebook_profile(link.strip(), "Violation of terms")  # Reason can be customized
        results.append(result)

    # Send the report results back to the user
    bot.send_message(message.chat.id, "\n".join(results))

if __name__ == '__main__':
    bot.polling()
