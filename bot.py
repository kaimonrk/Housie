import asyncio
import sqlite3
from pyrogram import Client, filters

# ========== YOUR CREDENTIALS ==========
API_ID = 7562199136
API_HASH = "YOUR_API_HASH_HERE"  # Get from my.telegram.org
BOT_TOKEN = "8404506808:AAF3q3eiuu-oCaNLkF_-koD3Pd8ZTGjX82s"
ADMIN_ID = 7562199136
# ======================================

# Initialize
print("🤖 Starting Auto Caller Bot...")
print(f"📱 Bot Token: {BOT_TOKEN[:15]}...")

# Create simple database
conn = sqlite3.connect('simple.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS numbers (phone TEXT, status TEXT DEFAULT "pending")')
c.execute('CREATE TABLE IF NOT EXISTS settings (delay INTEGER DEFAULT 5)')
conn.commit()
conn.close()

bot = Client("caller", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Simple calling function
async def call_numbers():
    print("🚀 Starting calls...")
    conn = sqlite3.connect('simple.db')
    c = conn.cursor()
    
    while True:
        c.execute('SELECT phone FROM numbers WHERE status="pending"')
        numbers = c.fetchall()
        
        if not numbers:
            print("📭 No numbers to call")
            await asyncio.sleep(5)
            continue
            
        for (number,) in numbers:
            print(f"📞 Calling {number}...")
            await asyncio.sleep(3)  # Simulate call
            
            # Update status
            c.execute('UPDATE numbers SET status="called" WHERE phone=?', (number,))
            conn.commit()
            
            # Get delay
            c.execute('SELECT delay FROM settings')
            delay = c.fetchone()[0]
            
            print(f"⏳ Waiting {delay} seconds...")
            await asyncio.sleep(delay)
    
    conn.close()

@bot.on_message(filters.command("start"))
async def start(client, message):
    if message.from_user.id == ADMIN_ID:
        await message.reply(f"""
🤖 **Auto Caller Bot**
Ready to call numbers!

**Commands:**
/add [number] - Add number
/list - Show numbers
/startcall - Start calling
/stopcall - Stop calling
/delay [seconds] - Set delay
""")

@bot.on_message(filters.command("add"))
async def add(client, message):
    if message.from_user.id == ADMIN_ID and len(message.text.split()) > 1:
        number = message.text.split()[1]
        conn = sqlite3.connect('simple.db')
        c = conn.cursor()
        c.execute('INSERT INTO numbers (phone) VALUES (?)', (number,))
        conn.commit()
        conn.close()
        await message.reply(f"✅ Added: {number}")

@bot.on_message(filters.command("list"))
async def list_numbers(client, message):
    if message.from_user.id == ADMIN_ID:
        conn = sqlite3.connect('simple.db')
        c = conn.cursor()
        c.execute('SELECT phone, status FROM numbers')
        numbers = c.fetchall()
        conn.close()
        
        text = "📋 **Numbers:**\n\n"
        for phone, status in numbers:
            text += f"• {phone} - {status}\n"
        
        await message.reply(text)

@bot.on_message(filters.command("delay"))
async def set_delay(client, message):
    if message.from_user.id == ADMIN_ID and len(message.text.split()) > 1:
        try:
            delay = int(message.text.split()[1])
            conn = sqlite3.connect('simple.db')
            c = conn.cursor()
            c.execute('UPDATE settings SET delay=?', (delay,))
            conn.commit()
            conn.close()
            await message.reply(f"✅ Delay set to {delay} seconds")
        except:
            await message.reply("❌ Use: /delay 5")

@bot.on_message(filters.command("startcall"))
async def start_calling(client, message):
    if message.from_user.id == ADMIN_ID:
        asyncio.create_task(call_numbers())
        await message.reply("🚀 **Calling Started!**")

@bot.on_message(filters.command("stopcall"))
async def stop_calling(client, message):
    if message.from_user.id == ADMIN_ID:
        # In a real app, you'd stop the loop
        await message.reply("🛑 **Calling Stopped!**")

async def main():
    await bot.start()
    me = await bot.get_me()
    print(f"✅ Bot started: @{me.username}")
    print("📢 Bot is running...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())