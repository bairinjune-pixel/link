import asyncio
import logging
import aiohttp
import traceback
import random
import string
from datetime import datetime, timedelta, date, time
import pytz
from database.users_db import db
from Script import script
from info import PING_INTERVAL, URL

# -------------------------- LOGGER INITIALIZATION -------------------------- #
logger = logging.getLogger(__name__)

# -------------------------- TEMPORARY DATA STORAGE -------------------------- #
class temp:
    ME = None
    BOT = None
    U_NAME = None
    B_NAME = None
    
# -------------------------- PING SERVER -------------------------- #
async def ping_server():
    while True:
        await asyncio.sleep(PING_INTERVAL)
        try:
            if not URL:
                logger.warning("⚠️ URL not found in info.py for ping_server")
                continue
                
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(URL) as resp:
                    logging.info(f"✅ Pinged server: {resp.status}")
        except asyncio.TimeoutError:
            logger.warning("⚠️ Timeout: Could not ping server!")
        except Exception as e:
            logger.error(f"❌ Exception while pinging server: {e}")
            traceback.print_exc()

# -------------------------- FILE SIZE CONVERTER -------------------------- #
def get_size(size: int) -> str:
    """Bytes to readable format converter"""
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units) - 1:
        size /= 1024.0
        i += 1
    return f"{size:.2f} {units[i]}"

def humanbytes(size: int) -> str:
    """Alternative bytes converter"""
    if size is None:
        return "0 B"
    power = 2 ** 10
    n = 0
    power_labels = {0: "B", 1: "KB", 2: "MB", 3: "GB", 4: "TB"}
    while size >= power and n < 4:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}"
    
# -------------------------- READABLE TIME FORMATTER -------------------------- #
def get_readable_time(seconds: int) -> str:
    """Seconds to readable time (e.g., 1h 30m 10s)"""
    if not seconds:
        return "0s"
        
    time_list = []
    time_suffix = ["s", "m", "h", " days"]
    count = 0
    while count < 4:
        count += 1
        if count < 3:
            seconds, result = divmod(seconds, 60)
        elif count == 3:
            seconds, result = divmod(seconds, 60)
        else:
            seconds, result = divmod(seconds, 24)
        if seconds == 0 and result == 0:
            break
        time_list.append(f"{int(result)}{time_suffix[count - 1]}")
    time_list.reverse()
    return ": ".join(time_list)
        
