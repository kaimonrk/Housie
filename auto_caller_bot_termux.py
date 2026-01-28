import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, List
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
import sqlite3
import os
import sys

# ========== YOUR CREDENTIALS ==========
API_ID = 7562199136  # Your API ID
API_HASH = "f5e3c8f6b9a4d3c2b1a7e8d9f0c4b3a2"  # You need to get this from my.telegram.org
BOT_TOKEN = "8404506808:AAF3q3eiuu-oCaNLkF_-koD3Pd8ZTGjX82s"  # Your Bot Token
# ======================================

# Bot Configuration
BOT_NAME = "AutoCallerBot"
ADMIN_ID = 7562199136  # Your Telegram User ID (for admin commands)

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database setup
DB_FILE = "caller_database.db"
EXPORT_DIR = "exports"

def init_database():
    """Initialize SQLite database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS numbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT UNIQUE,
            status TEXT DEFAULT 'pending',
            call_count INTEGER DEFAULT 0,
            last_called TIMESTAMP,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        ''')
        
        # Initialize default settings
        default_settings = [
            ('call_delay', '5'),  # 5 seconds default delay
            ('max_calls_per_number', '2'),
            ('auto_restart', 'false'),
            ('call_timeout', '30'),  # Call timeout in seconds
            ('active_hours', '9-21')  # Only call between 9 AM to 9 PM
        ]
        
        cursor.executemany('''
        INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
        ''', default_settings)
        
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized successfully")
        
        # Create exports directory
        os.makedirs(EXPORT_DIR, exist_ok=True)
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")

# Initialize database
init_database()

# Bot initialization
print("🤖 Initializing Auto Caller Bot...")
print(f"📱 Bot Token: {BOT_TOKEN[:15]}...")
print(f"🆔 API ID: {API_ID}")

try:
    app = Client(
        "auto_caller_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        workers=3
    )
    print("✅ Bot client created successfully")
except Exception as e:
    print(f"❌ Failed to create bot client: {e}")
    print("💡 Make sure your credentials are correct!")
    sys.exit(1)

# Global variables
is_calling_active = False
call_task = None
current_call_number = None

# Database helper functions
def db_query(query, params=(), fetchone=False, fetchall=False):
    """Execute SQL query"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    else:
        result = None
    
    conn.commit()
    conn.close()
    
    if result and fetchone:
        return dict(result)
    elif result and fetchall:
        return [dict(row) for row in result]
    return result

def get_setting(key):
    """Get setting value"""
    result = db_query("SELECT value FROM settings WHERE key = ?", (key,), fetchone=True)
    return result['value'] if result else None

def update_setting(key, value):
    """Update setting value"""
    db_query("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))

def add_number(phone_number):
    """Add a phone number to database"""
    try:
        # Clean phone number
        phone_number = phone_number.strip()
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
        
        db_query("INSERT OR IGNORE INTO numbers (phone_number) VALUES (?)", (phone_number,))
        logger.info(f"✅ Number added: {phone_number}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to add number: {e}")
        return False

def get_pending_numbers():
    """Get list of pending numbers"""
    return db_query("""
        SELECT phone_number FROM numbers 
        WHERE (status = 'pending' OR status = 'failed') 
        AND call_count < ?
        ORDER BY added_at ASC
        LIMIT 100
    """, (int(get_setting('max_calls_per_number')),), fetchall=True)

def mark_number_called(phone_number, status='completed'):
    """Update number status after call"""
    db_query("""
        UPDATE numbers 
        SET status = ?, call_count = call_count + 1, last_called = datetime('now')
        WHERE phone_number = ?
    """, (status, phone_number))

def get_statistics():
    """Get calling statistics"""
    result = db_query("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
            SUM(call_count) as total_calls
        FROM numbers
    """, fetchone=True)
    
    return result

def is_within_active_hours():
    """Check if current time is within active hours"""
    active_hours = get_setting('active_hours') or '9-21'
    try:
        start_hour, end_hour = map(int, active_hours.split('-'))
        current_hour = datetime.now().hour
        
        if start_hour <= current_hour < end_hour:
            return True
        return False
    except:
        return True

# Main calling function (Simulated)
async def make_call(phone_number):
    """Make a call to phone number"""
    global current_call_number
    
    try:
        current_call_number = phone_number
        logger.info(f"📞 Calling {phone_number}...")
        
        # Simulate call with timeout
        timeout = int(get_setting('call_timeout') or 30)
        
        # Here you would integrate with actual calling service
        # For now, we simulate the call
        await asyncio.sleep(3)  # Simulate call duration
        
        # Simulate success (80% success rate)
        import random
        success = random.random() < 0.8
        
        if success:
            logger.info(f"✅ Call completed: {phone_number}")
            return True, "Call completed successfully"
        else:
            logger.warning(f"❌ Call failed: {phone_number}")
            return False, "Call failed or no answer"
            
    except asyncio.TimeoutError:
        logger.error(f"⏰ Call timeout: {phone_number}")
        return False, "Call timeout"
    except Exception as e:
        logger.error(f"⚠️ Call error: {e}")
        return False, f"Error: {str(e)}"
    finally:
        current_call_number = None

async def calling_loop():
    """Main calling loop"""
    global is_calling_active
    
    logger.info("🚀 Starting calling loop...")
    
    while is_calling_active:
        try:
            # Check active hours
            if not is_within_active_hours():
                logger.info("⏰ Outside active hours, pausing...")
                await asyncio.sleep(300)  # Wait 5 minutes
                continue
            
            # Get pending numbers
            pending_numbers = get_pending_numbers()
            
            if not pending_numbers:
                logger.info("📭 No numbers to call")
                
                if get_setting('auto_restart') == 'false':
                    logger.info("🛑 Auto restart disabled, stopping...")
                    is_calling_active = False
                    break
                
                logger.info("⏳ Waiting for new numbers...")
                await asyncio.sleep(10)
                continue
            
            # Process each number
            for number_data in pending_numbers:
                if not is_calling_active:
                    break
                
                phone_number = number_data['phone_number']
                
                # Make the call
                success, message = await make_call(phone_number)
                
                # Update database
                status = 'completed' if success else 'failed'
                mark_number_called(phone_number, status)
                
                # Wait for delay
                delay = int(get_setting('call_delay') or 5)
                logger.info(f"⏳ Waiting {delay} seconds...")
                
                # Countdown with status updates
                for remaining in range(delay, 0, -1):
                    if not is_calling_active:
                        break
                    await asyncio.sleep(1)
                
                if not is_calling_active:
                    break
            
        except Exception as e:
            logger.error(f"❌ Error in calling loop: {e}")
            await asyncio.sleep(5)
    
    logger.info("🛑 Calling loop stopped")

# ========== TELEGRAM BOT HANDLERS ==========

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """Start command"""
    # Check if user is admin
    if message.from_user.id != ADMIN_ID:
        await message.reply_text("🚫 You are not authorized to use this bot!")
        return
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Start Calling", callback_data="start_calling")],
        [InlineKeyboardButton("🛑 Stop Calling", callback_data="stop_calling")],
        [InlineKeyboardButton("📊 Statistics", callback_data="show_stats")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
        [InlineKeyboardButton("📱 Add Numbers", callback_data="add_numbers")],
        [InlineKeyboardButton("📋 Number List", callback_data="number_list")]
    ])
    
    await message.reply_text(
        f"🤖 **Auto Caller Bot v1.0**\n\n"
        f"**Owner:** {message.from_user.first_name}\n"
        f"**User ID:** `{ADMIN_ID}`\n\n"
        "Ready to start auto calling with configurable delays!",
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN
    )

@app.on_message(filters.command("add"))
async def add_number_command(client: Client, message: Message):
    """Add single number"""
    if message.from_user.id != ADMIN_ID:
        return
    
    args = message.text.split()
    
    if len(args) < 2:
        await message.reply_text(
            "📝 **Add Phone Number**\n\n"
            "Usage: `/add +1234567890`\n"
            "Or: `/add 1234567890`\n\n"
            "Example: `/add +919876543210`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    phone_number = args[1]
    
    if add_number(phone_number):
        await message.reply_text(f"✅ **Number Added!**\n`{phone_number}`")
    else:
        await message.reply_text("❌ Failed to add number. It might already exist.")

@app.on_message(filters.command("addbulk"))
async def add_bulk_command(client: Client, message: Message):
    """Add multiple numbers"""
    if message.from_user.id != ADMIN_ID:
        return
    
    await message.reply_text(
        "📥 **Add Multiple Numbers**\n\n"
        "Send numbers separated by commas or new lines:\n\n"
        "**Format:**\n"
        "```\n"
        "+919876543210\n"
        "+919876543211\n"
        "+919876543212\n"
        "```\n\n"
        "Or comma separated:\n"
        "`+919876543210, +919876543211, +919876543212`",
        parse_mode=ParseMode.MARKDOWN
    )

@app.on_message(filters.text & filters.private)
async def handle_text_messages(client: Client, message: Message):
    """Handle text messages (for bulk add)"""
    if message.from_user.id != ADMIN_ID:
        return
    
    # Check if it's a command
    if message.text.startswith('/'):
        return
    
    # Handle bulk numbers
    text = message.text.strip()
    
    if any(char.isdigit() for char in text.replace('+', '').replace(',', '').replace('\n', '')):
        numbers = []
        for line in text.split('\n'):
            for num in line.split(','):
                num = num.strip()
                if num:
                    numbers.append(num)
        
        added = 0
        failed = 0
        
        for num in numbers:
            if add_number(num):
                added += 1
            else:
                failed += 1
        
        await message.reply_text(
            f"📊 **Bulk Add Results**\n\n"
            f"✅ Added: {added}\n"
            f"❌ Failed: {failed}\n"
            f"📱 Total: {added + failed}"
        )

@app.on_message(filters.command("startcall"))
async def start_calling_command(client: Client, message: Message):
    """Start calling"""
    global is_calling_active, call_task
    
    if message.from_user.id != ADMIN_ID:
        return
    
    if is_calling_active:
        await message.reply_text("⚠️ **Already Calling!**\nUse `/stopcall` to stop.")
        return
    
    is_calling_active = True
    call_task = asyncio.create_task(calling_loop())
    
    stats = get_statistics()
    
    await message.reply_text(
        "🚀 **Auto Calling STARTED!**\n\n"
        f"📞 **Status:** Active\n"
        f"⏱️ **Delay:** {get_setting('call_delay')}s\n"
        f"🔄 **Max Calls:** {get_setting('max_calls_per_number')}\n"
        f"📊 **Pending:** {stats['pending']}\n"
        f"⏰ **Active Hours:** {get_setting('active_hours')}\n\n"
        "Use `/stopcall` to stop.",
        parse_mode=ParseMode.MARKDOWN
    )

@app.on_message(filters.command("stopcall"))
async def stop_calling_command(client: Client, message: Message):
    """Stop calling"""
    global is_calling_active, call_task
    
    if message.from_user.id != ADMIN_ID:
        return
    
    if not is_calling_active:
        await message.reply_text("❌ No active calling session!")
        return
    
    is_calling_active = False
    
    if call_task:
        call_task.cancel()
        try:
            await call_task
        except asyncio.CancelledError:
            pass
    
    await message.reply_text(
        "🛑 **Calling STOPPED!**\n\n"
        "All calls have been paused.",
        parse_mode=ParseMode.MARKDOWN
    )

@app.on_message(filters.command("status"))
async def status_command(client: Client, message: Message):
    """Show current status"""
    if message.from_user.id != ADMIN_ID:
        return
    
    stats = get_statistics()
    
    status_text = (
        "📊 **Current Status**\n\n"
        f"📞 **Calling Active:** {'✅ Yes' if is_calling_active else '❌ No'}\n"
        f"📱 **Current Number:** {current_call_number or 'None'}\n\n"
        f"📈 **Statistics**\n"
        f"• Total Numbers: {stats['total']}\n"
        f"• Completed: {stats['completed']}\n"
        f"• Failed: {stats['failed']}\n"
        f"• Pending: {stats['pending']}\n"
        f"• Total Calls: {stats['total_calls']}\n\n"
        f"⚙️ **Settings**\n"
        f"• Delay: {get_setting('call_delay')}s\n"
        f"• Max Calls: {get_setting('max_calls_per_number')}\n"
        f"• Active Hours: {get_setting('active_hours')}"
    )
    
    await message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)

@app.on_message(filters.command("list"))
async def list_command(client: Client, message: Message):
    """Show number list"""
    if message.from_user.id != ADMIN_ID:
        return
    
    numbers = db_query("""
        SELECT phone_number, status, call_count, 
               datetime(last_called) as last_called 
        FROM numbers 
        ORDER BY last_called DESC NULLS LAST, id ASC
        LIMIT 20
    """, fetchall=True)
    
    if not numbers:
        await message.reply_text("📭 **No numbers in database!**")
        return
    
    text = "📋 **Recent Numbers**\n\n"
    
    for num in numbers:
        status_icon = {
            'completed': '✅',
            'failed': '❌',
            'pending': '⏳'
        }.get(num['status'], '❓')
        
        last_called = num['last_called'][:16] if num['last_called'] else 'Never'
        
        text += f"{status_icon} `{num['phone_number']}`\n"
        text += f"   Calls: {num['call_count']} | Last: {last_called}\n\n"
    
    stats = get_statistics()
    text += f"📊 **Total:** {stats['total']} numbers"
    
    await message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

@app.on_message(filters.command("settings"))
async def settings_command(client: Client, message: Message):
    """Show settings"""
    if message.from_user.id != ADMIN_ID:
        return
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏱️ Set Delay", callback_data="set_delay"),
            InlineKeyboardButton("🔄 Max Calls", callback_data="set_max_calls")
        ],
        [
            InlineKeyboardButton("⏰ Active Hours", callback_data="set_hours"),
            InlineKeyboardButton("♻️ Auto Restart", callback_data="toggle_restart")
        ],
        [
            InlineKeyboardButton("📤 Export Data", callback_data="export_data"),
            InlineKeyboardButton("🗑️ Clear All", callback_data="clear_confirm")
        ]
    ])
    
    settings_text = (
        "⚙️ **Bot Settings**\n\n"
        f"⏱️ **Call Delay:** {get_setting('call_delay')} seconds\n"
        f"🔄 **Max Calls/Number:** {get_setting('max_calls_per_number')}\n"
        f"⏰ **Active Hours:** {get_setting('active_hours')}\n"
        f"♻️ **Auto Restart:** {get_setting('auto_restart')}\n"
        f"⏳ **Call Timeout:** {get_setting('call_timeout')} seconds\n\n"
        f"📞 **Current Status:** {'Active' if is_calling_active else 'Inactive'}"
    )
    
    await message.reply_text(settings_text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    """Show help"""
    help_text = """
🤖 **Auto Caller Bot - Help Guide**

**Basic Commands:**
/start - Start the bot
/add +1234567890 - Add single number
/addbulk - Add multiple numbers
/startcall - Start auto calling
/stopcall - Stop calling
/status - Check current status
/list - Show number list
/settings - Configure settings
/help - Show this message

**Features:**
• Auto calling with delay
• Call success/failure tracking
• Configurable settings
• Time-based calling (active hours)
• Data export
• Statistics

**Setup Instructions:**
1. Add numbers using /add or /addbulk
2. Configure settings in /settings
3. Start calling with /startcall
4. Monitor with /status

**Note:** This is a simulation bot. For actual calling, integrate with Twilio or other VoIP services.
"""
    
    await message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

# Callback query handler
@app.on_callback_query()
async def handle_callback(client, callback_query):
    """Handle callback queries"""
    if callback_query.from_user.id != ADMIN_ID:
        await callback_query.answer("🚫 Not authorized!", show_alert=True)
        return
    
    data = callback_query.data
    
    if data == "start_calling":
        await start_calling_command(client, callback_query.message)
        await callback_query.answer()
    
    elif data == "stop_calling":
        await stop_calling_command(client, callback_query.message)
        await callback_query.answer()
    
    elif data == "show_stats":
        await status_command(client, callback_query.message)
        await callback_query.answer()
    
    elif data == "settings":
        await settings_command(client, callback_query.message)
        await callback_query.answer()
    
    elif data == "number_list":
        await list_command(client, c