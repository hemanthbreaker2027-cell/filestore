#ᴀɴɪᴢᴏɴᴇꜰʟɪx_ʙᴏᴛᴢ
#ᴀɴɪᴢᴏɴᴇꜰʟɪx on ᴛɢ

import motor.motor_asyncio
import time
import secrets
import uuid
import pymongo, os
from config import DB_URI, DB_NAME
import logging

dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]

logging.basicConfig(level=logging.INFO)

default_verify = {
    'is_verified': False,
    'verified_time': 0,
    'verify_token': "",
    'link': ""
}

def new_user(id):
    return {
        '_id': id,
        'verify_status': {
            'is_verified': False,
            'verified_time': "",
            'verify_token': "",
            'link': ""
        }
    }

class AniZoneFlix:

    def __init__(self, DB_URI, DB_NAME):
        self.dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
        self.database = self.dbclient[DB_NAME]

        self.channel_data = self.database['channels']
        self.admins_data = self.database['admins']
        self.user_data = self.database['users']
        self.sex_data = self.database['sex']
        self.banned_user_data = self.database['banned_user']
        self.autho_user_data = self.database['autho_user']
        self.del_timer_data = self.database['del_timer']
        self.fsub_data = self.database['fsub']   
        self.rqst_fsub_data = self.database['request_forcesub']
        self.rqst_fsub_Channel_data = self.database['request_forcesub_channel']
        self.bypass_data = self.database['bypass_attempts']
        self.settings_data = self.database['settings']
        self.cooldown_data = self.database['cooldowns']
        self.sessions = self.database['sessions']


    # SETTINGS & FEATURE FLAGS
    async def get_settings(self):
        settings = await self.settings_data.find_one({'_id': 'bot_settings'})

        default_settings = {
            '_id': 'bot_settings',
            'shortener_system': True,
            'file_delivery': True,
            'core_features': True,
            'shorten_admins': True,
            'daily_verify_limit': 5, # How many deals per verification
            'verify_expiry': 86400 # 24 hours
        }

        if not settings:
            await self.settings_data.insert_one(default_settings)
            return default_settings

        # Ensure all fields exist
        updated = False
        for field, default in default_settings.items():
            if field not in settings:
                settings[field] = default
                updated = True

        if updated:
            await self.settings_data.update_one({'_id': 'bot_settings'}, {'$set': settings})

        return settings

    async def update_setting(self, key: str, value):
        await self.settings_data.update_one(
            {'_id': 'bot_settings'},
            {'$set': {key: value}},
            upsert=True
        )


    # USER DATA
    async def present_user(self, user_id: int):
        found = await self.user_data.find_one({'_id': user_id})
        return bool(found)

    async def add_user(self, user_id: int):
        await self.user_data.insert_one({'_id': user_id})
        return

    async def full_userbase(self):
        user_docs = await self.user_data.find().to_list(length=None)
        user_ids = [doc['_id'] for doc in user_docs]
        return user_ids

    async def del_user(self, user_id: int):
        await self.user_data.delete_one({'_id': user_id})
        return


    # ADMIN DATA
    async def admin_exist(self, admin_id: int):
        found = await self.admins_data.find_one({'_id': admin_id})
        return bool(found)

    async def add_admin(self, admin_id: int):
        if not await self.admin_exist(admin_id):
            await self.admins_data.insert_one({'_id': admin_id})
            return

    async def del_admin(self, admin_id: int):
        if await self.admin_exist(admin_id):
            await self.admins_data.delete_one({'_id': admin_id})
            return

    async def get_all_admins(self):
        users_docs = await self.admins_data.find().to_list(length=None)
        user_ids = [doc['_id'] for doc in users_docs]
        return user_ids


    # BAN USER DATA
    async def ban_user_exist(self, user_id: int):
        found = await self.banned_user_data.find_one({'_id': user_id})
        return bool(found)

    async def add_ban_user(self, user_id: int):
        if not await self.ban_user_exist(user_id):
            await self.banned_user_data.insert_one({'_id': user_id})
            return

    async def del_ban_user(self, user_id: int):
        if await self.ban_user_exist(user_id):
            await self.banned_user_data.delete_one({'_id': user_id})
            return

    async def get_ban_users(self):
        users_docs = await self.banned_user_data.find().to_list(length=None)
        user_ids = [doc['_id'] for doc in users_docs]
        return user_ids



    # AUTO DELETE TIMER SETTINGS
    async def set_del_timer(self, value: int):        
        existing = await self.del_timer_data.find_one({})
        if existing:
            await self.del_timer_data.update_one({}, {'$set': {'value': value}})
        else:
            await self.del_timer_data.insert_one({'value': value})

    async def get_del_timer(self):
        data = await self.del_timer_data.find_one({})
        if data:
            return data.get('value', 900)
        return 900


    # CHANNEL MANAGEMENT
    async def channel_exist(self, channel_id: int):
        found = await self.fsub_data.find_one({'_id': channel_id})
        return bool(found)

    async def add_channel(self, channel_id: int):
        if not await self.channel_exist(channel_id):
            await self.fsub_data.insert_one({'_id': channel_id})
            return

    async def rem_channel(self, channel_id: int):
        if await self.channel_exist(channel_id):
            await self.fsub_data.delete_one({'_id': channel_id})
            return

    async def show_channels(self):
        channel_docs = await self.fsub_data.find().to_list(length=None)
        channel_ids = [doc['_id'] for doc in channel_docs]
        return channel_ids

    
# Get current mode of a channel
    async def get_channel_mode(self, channel_id: int):
        data = await self.fsub_data.find_one({'_id': channel_id})
        return data.get("mode", "off") if data else "off"

    # Set mode of a channel
    async def set_channel_mode(self, channel_id: int, mode: str):
        await self.fsub_data.update_one(
            {'_id': channel_id},
            {'$set': {'mode': mode}},
            upsert=True
        )

    # REQUEST FORCE-SUB MANAGEMENT

    # Add the user to the set of users for a   specific channel
    async def req_user(self, channel_id: int, user_id: int):
        try:
            await self.rqst_fsub_Channel_data.update_one(
                {'_id': int(channel_id)},
                {'$addToSet': {'user_ids': int(user_id)}},
                upsert=True
            )
        except Exception as e:
            print(f"[DB ERROR] Failed to add user to request list: {e}")


    # Method 2: Remove a user from the channel set
    async def del_req_user(self, channel_id: int, user_id: int):
        # Remove the user from the set of users for the channel
        await self.rqst_fsub_Channel_data.update_one(
            {'_id': channel_id}, 
            {'$pull': {'user_ids': user_id}}
        )

    # Check if the user exists in the set of the channel's users
    async def req_user_exist(self, channel_id: int, user_id: int):
        try:
            found = await self.rqst_fsub_Channel_data.find_one({
                '_id': int(channel_id),
                'user_ids': int(user_id)
            })
            return bool(found)
        except Exception as e:
            print(f"[DB ERROR] Failed to check request list: {e}")
            return False  


    # Method to check if a channel exists using show_channels
    async def reqChannel_exist(self, channel_id: int):
    # Get the list of all channel IDs from the database
        channel_ids = await self.show_channels()
        #print(f"All channel IDs in the database: {channel_ids}")

    # Check if the given channel_id is in the list of channel IDs
        if channel_id in channel_ids:
            #print(f"Channel {channel_id} found in the database.")
            return True
        else:
            #print(f"Channel {channel_id} NOT found in the database.")
            return False



    # COOLDOWN MANAGEMENT
    async def check_cooldown(self, identifier: str, cooldown_seconds: int = 5):
        record = await self.cooldown_data.find_one({'_id': identifier})
        if not record:
            return True

        last_time = record.get('last_time', 0)
        if time.time() - last_time < cooldown_seconds:
            return False
        return True

    async def update_cooldown(self, identifier: str):
        await self.cooldown_data.update_one(
            {'_id': identifier},
            {'$set': {'last_time': time.time()}},
            upsert=True
        )


    # VERIFICATION MANAGEMENT (DEALS SYSTEM)
    async def get_verify_deals(self, user_id: int):
        user = await self.sex_data.find_one({'_id': user_id})
        if user:
            return user.get('deals', 0)
        return 0

    async def use_deal(self, user_id: int):
        await self.sex_data.update_one(
            {'_id': user_id},
            {'$inc': {'deals': -1}}
        )

    async def refill_deals(self, user_id: int):
        settings = await self.get_settings()
        limit = settings.get('daily_verify_limit', 5)
        await self.sex_data.update_one(
            {'_id': user_id},
            {'$set': {'deals': limit, 'last_verify': int(time.time())}},
            upsert=True
        )

    # Legacy method compatibility
    async def get_verify_count(self, user_id: int):
        return await self.get_verify_deals(user_id)

    async def check_daily_limit(self, user_id: int):
        deals = await self.get_verify_deals(user_id)
        return deals > 0, deals


    # CODEFLIX NETWORK - SESSION MANAGEMENT
    async def create_verification_session(self, user_id, bot_username, context="frontend"):
        session_id = str(uuid.uuid4())
        await self.sessions.insert_one({
            "session_id": session_id,
            "user_id": str(user_id),
            "bot_username": bot_username,
            "status": "pending",
            "expiry": int(time.time() + 300),
            "secure_token": None,
            "context": context # "frontend" or "api"
        })
        return session_id

    async def get_session_by_token(self, token):
        return await self.sessions.find_one({"secure_token": token, "status": "verified"})

    async def mark_session_used(self, session_id):
        await self.sessions.update_one(
            {"session_id": session_id},
            {"$set": {"status": "used"}}
        )

    async def cleanup_sessions(self):
        await self.sessions.delete_many({"expiry": {"$lt": time.time()}})


    # RESTART TASKS
    async def clear_all_bans(self):
        await self.banned_user_data.delete_many({})


db = AniZoneFlix(DB_URI, DB_NAME)
