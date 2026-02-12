import datetime
from datetime import timedelta  # Added missing import
import pytz
import motor.motor_asyncio
import logging
from info import DB_URL, DB_NAME, TIMEZONE

logger = logging.getLogger(__name__)

client = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
mydb = client[DB_NAME]

class Database:
    def __init__(self):
        self.users = mydb.users
        self.blocked_users = mydb.blocked_users
        self.blocked_channels = mydb.blocked_channels
        self.files = mydb.files
        self.refer_collection = mydb.refers 
        self.misc = mydb.misc

    def new_user(self, id, name):
        return {
            "id": int(id),
            "name": name,
            }

    async def add_user(self, id, name):
        if not await self.is_user_exist(id):
            user = self.new_user(id, name)
            await self.users.insert_one(user)

    async def is_user_exist(self, id):
        return bool(await self.users.find_one({'id': int(id)}))

    async def total_users_count(self):
        return await self.users.count_documents({})

    async def get_all_users(self):
        return self.users.find({})

    async def delete_user(self, user_id):
        await self.users.delete_many({'id': int(user_id)})
        
    async def get_notcopy_user(self, user_id):
        user_id = int(user_id)
        user = await self.misc.find_one({"user_id": user_id})
        ist_timezone = pytz.timezone(TIMEZONE)

        if not user:
            res = {
                "user_id": user_id,
                "last_verified": datetime.datetime(2020, 5, 17, 0, 0, 0, tzinfo=ist_timezone),
                "second_time_verified": datetime.datetime(2019, 5, 17, 0, 0, 0, tzinfo=ist_timezone),
            }
            user = await self.misc.insert_one(res)
            user = await self.misc.find_one({"user_id": user_id})
        return user

    async def update_notcopy_user(self, user_id, value: dict):
        user_id = int(user_id)
        myquery = {"user_id": user_id}
        newvalues = {"$set": value}
        return await self.misc.update_one(myquery, newvalues)

    async def is_user_verified(self, user_id):
        return True

    async def use_second_shortener(self, user_id):
        return False

    async def get_verification_stats(self):
        return 0, 0
        
    async def is_user_in_list(self, user_id):
        user = await self.refer_collection.find_one({"user_id": int(user_id)})
        return bool(user)

    async def get_refer_points(self, user_id: int):
        user = await self.refer_collection.find_one({"user_id": int(user_id)})
        return user.get("points", 0) if user else 0

    async def add_refer_points(self, user_id: int, points: int):
        await self.refer_collection.update_one(
            {"user_id": int(user_id)}, 
            {"$set": {"points": points}}, 
            upsert=True
        )

    async def change_points(self, user_id: int, amount: int):
        current_points = await self.get_refer_points(user_id)
        new_points = current_points + amount
        if new_points < 0:
            new_points = 0 # पॉइंट्स माइनस में नहीं जाएंगे
        await self.refer_collection.update_one(
            {"user_id": int(user_id)}, 
            {"$set": {"points": new_points}}, 
            upsert=True
        )
        return new_points

    async def is_user_blocked(self, user_id: int) -> bool:
        return await self.blocked_users.find_one({"user_id": int(user_id)}) is not None

    async def block_user(self, user_id: int, reason: str = "No reason provided."):
        await self.blocked_users.update_one(
            {"user_id": int(user_id)},
            {
                "$set": {
                    "user_id": int(user_id),
                    "reason": reason,
                    "blocked_at": datetime.datetime.utcnow()
                }
            },
            upsert=True
        )

    async def unblock_user(self, user_id: int):
        await self.blocked_users.delete_one({"user_id": int(user_id)})
        
    async def get_all_blocked_users(self):
        return self.blocked_users.find({})

    async def total_blocked_count(self):
        return await self.blocked_users.count_documents({})
        
    async def is_channel_blocked(self, channel_id: int) -> bool:
        return await self.blocked_channels.find_one({"channel_id": int(channel_id)}) is not None

    async def block_channel(self, channel_id: int, reason: str = "No reason provided."):
        await self.blocked_channels.update_one(
            {"channel_id": int(channel_id)},
            {
                "$set": {
                    "channel_id": int(channel_id),
                    "reason": reason,
                    "blocked_at": datetime.datetime.utcnow()
                }
            },
            upsert=True
        )

    async def unblock_channel(self, channel_id: int):
        await self.blocked_channels.delete_one({"channel_id": int(channel_id)})

    async def get_all_blocked_channels(self):
        return self.blocked_channels.find({})

    async def get_channel_block_data(self, channel_id: int):
        return await self.blocked_channels.find_one({"channel_id": channel_id})

    async def total_blocked_channels_count(self):
        return await self.blocked_channels.count_documents({})
        
    async def get_expired(self, current_time):
        expired_users = []
        cursor = self.users.find({"expiry_time": {"$lt": current_time}})
        async for user in cursor:
            expired_users.append(user)
        return expired_users

# Inside your DB manager class
    async def get_expiring_soon(self, label, delta):
        reminder_key = f"reminder_{label}_sent"
        now = datetime.datetime.utcnow()
        target_time = now + delta
        window = timedelta(seconds=30)

        start_range = target_time - window
        end_range = target_time + window

        reminder_users = []
        cursor = self.users.find({
            "expiry_time": {"$gte": start_range, "$lte": end_range},
            reminder_key: {"$ne": True}
        })

        async for user in cursor:
            reminder_users.append(user)
            await self.users.update_one(
                {"id": user["id"]}, {"$set": {reminder_key: True}}
            )

        return reminder_users

    async def get_user(self, user_id):
        user_data = await self.users.find_one({"id": int(user_id)})
        return user_data
        
    async def update_user(self, user_data):
        await self.users.update_one(
            {"id": user_data["id"]}, 
            {"$set": user_data}, 
            upsert=True
        )

    async def has_premium_access(self, user_id):
        user_data = await self.get_user(user_id)
        if user_data:
            expiry_time = user_data.get("expiry_time")
            if expiry_time is None:
                return False
            # Check if expiry_time is naive (no timezone) or aware
            if isinstance(expiry_time, datetime.datetime):
                if datetime.datetime.now() <= expiry_time:
                    return True
                else:
                    await self.users.update_one({"id": int(user_id)}, {"$set": {"expiry_time": None}})
                    return False
        return False
            
    async def all_premium_users_count(self):
        count = await self.users.count_documents({
            "expiry_time": {"$gt": datetime.datetime.now()}
        })
        return count

    async def remove_premium_access(self, user_id):
        await self.users.update_one(
            {"id": int(user_id)}, 
            {"$set": {"expiry_time": None}}
        )
        return True

db = Database()
            
