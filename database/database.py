#ᴀɴɪᴢᴏɴᴇꜰʟɪx_ʙᴏᴛᴢ
#ᴀɴɪᴢᴏɴᴇꜰʟɪx on ᴛɢ

import motor.motor_asyncio
import time
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
        self.secure_tokens = self.database['secure_tokens']
        self.shortener_verifications = self.database['shortener_verifications']
        self.cooldown_data = self.database['cooldowns']
        self.sticker_data = self.database['stickers']


    # SETTINGS & FEATURE FLAGS
    async def get_settings(self):
        settings = await self.settings_data.find_one({'_id': 'bot_settings'})
        if not settings:
            default_settings = {
                '_id': 'bot_settings',
                'shortener_system': True,
                'file_delivery': True,
                'core_features': True,
                'shortener_mode': 'one_per_time', # one_per_time or based_time
                'shortener_time': 0, # Time in seconds for based_time mode
                'stream_enabled': False,
                'download_enabled': False
            }
            await self.settings_data.insert_one(default_settings)
            return default_settings

        # Ensure new fields exist for existing users
        updated = False
        if 'shortener_mode' not in settings:
            settings['shortener_mode'] = 'one_per_time'
            updated = True
        if 'shortener_time' not in settings:
            settings['shortener_time'] = 0
            updated = True
        if 'stream_enabled' not in settings:
            settings['stream_enabled'] = False
            updated = True
        if 'download_enabled' not in settings:
            settings['download_enabled'] = False
            updated = True

        if updated:
            await self.settings_data.update_one({'_id': 'bot_settings'}, {'$set': settings})

        return settings

    async def update_setting(self, key: str, value: bool):
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



    # VERIFICATION MANAGEMENT
    async def db_verify_status(self, user_id):
        user = await self.user_data.find_one({'_id': user_id})
        if user:
            return user.get('verify_status', default_verify)
        return default_verify

    async def db_update_verify_status(self, user_id, verify):
        await self.user_data.update_one({'_id': user_id}, {'$set': {'verify_status': verify}})

    async def get_verify_status(self, user_id):
        verify = await self.db_verify_status(user_id)
        return verify

    async def update_verify_status(self, user_id, verify_token="", is_verified=False, verified_time=0, link=""):
        current = await self.db_verify_status(user_id)
        current['verify_token'] = verify_token
        current['is_verified'] = is_verified
        current['verified_time'] = verified_time
        current['link'] = link
        await self.db_update_verify_status(user_id, current)

    # Set verify count (overwrite with new value)
    async def set_verify_count(self, user_id: int, count: int):
        await self.sex_data.update_one({'_id': user_id}, {'$set': {'verify_count': count}}, upsert=True)

    # Get verify count (default to 0 if not found)
    async def get_verify_count(self, user_id: int):
        user = await self.sex_data.find_one({'_id': user_id})
        if user:
            return user.get('verify_count', 0)
        return 0

    # Reset all users' verify counts to 0
    async def reset_all_verify_counts(self):
        await self.sex_data.update_many(
            {},
            {'$set': {'verify_count': 0}} 
        )

    # Get total verify count across all users
    async def get_total_verify_count(self):
        pipeline = [
            {"$group": {"_id": None, "total": {"$sum": "$verify_count"}}}
        ]
        result = await self.sex_data.aggregate(pipeline).to_list(length=1)
        return result[0]["total"] if result else 0

    # BYPASS ATTEMPT TRACKING
    async def get_bypass_record(self, identifier: str):
        return await self.bypass_data.find_one({'_id': identifier})

    async def increment_bypass_attempt(self, identifier: str):
        await self.bypass_data.update_one(
            {'_id': identifier},
            {
                '$inc': {'attempts_count': 1},
                '$set': {'last_attempt_time': time.time()}
            },
            upsert=True
        )

    async def ban_user_bypass(self, identifier: str, duration_hours: int = 24):
        if duration_hours == -1: # Permanent
            ban_expiry = 9999999999
        else:
            ban_expiry = time.time() + (duration_hours * 3600)

        await self.bypass_data.update_one(
            {'_id': identifier},
            {'$set': {
                'ban_status': True,
                'ban_expiry': ban_expiry
            }},
            upsert=True
        )

    async def reset_bypass_attempts(self, identifier: str):
        await self.bypass_data.delete_one({'_id': identifier})

    # SECURE TOKEN MANAGEMENT
    async def store_secure_token(self, token_hash: str, expiry: int):
        await self.secure_tokens.insert_one({
            '_id': token_hash,
            'expiry': expiry,
            'used': False
        })

    async def validate_and_use_token(self, token_hash: str):
        result = await self.secure_tokens.find_one({'_id': token_hash})
        if not result:
            return False

        if result['used'] or time.time() > result['expiry']:
            return False

        await self.secure_tokens.update_one({'_id': token_hash}, {'$set': {'used': True}})
        return True

    async def cleanup_tokens(self):
        await self.secure_tokens.delete_many({
            '$or': [
                {'expiry': {'$lt': time.time()}},
                {'used': True}
            ]
        })

    # SHORTENER VERIFICATION
    async def store_shortener_verification(self, user_id: str, code: str, original_url: str = ""):
        await self.shortener_verifications.update_one(
            {'_id': code},
            {'$set': {
                'user_id': user_id,
                'original_url': original_url,
                'verified_at': time.time(),
                'expires_at': time.time() + 3600 # 1 hour expiry
            }},
            upsert=True
        )

    async def verify_shortener_code(self, code: str):
        record = await self.shortener_verifications.find_one({'_id': code})
        if not record:
            return None # Not found

        if time.time() > record.get('expires_at', 0):
            await self.shortener_verifications.delete_one({'_id': code})
            return None # Expired

        return record

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

    # STICKER MAPPING
    async def add_sticker_mapping(self, keyword: str, sticker_file_id: str, admin_id: int):
        await self.sticker_data.update_one(
            {'_id': keyword.lower()},
            {'$set': {
                'sticker_file_id': sticker_file_id,
                'added_by': admin_id,
                'created_time': time.time()
            }},
            upsert=True
        )

    async def remove_sticker_mapping(self, keyword: str):
        await self.sticker_data.delete_one({'_id': keyword.lower()})

    async def get_all_stickers(self):
        docs = await self.sticker_data.find().to_list(length=None)
        # Return as a dictionary for faster lookup {keyword: file_id}
        return {doc['_id']: doc['sticker_file_id'] for doc in docs}

    # RESTART TASKS
    async def clear_all_bans(self):
        await self.banned_user_data.delete_many({})
        await self.bypass_data.delete_many({})


db = AniZoneFlix(DB_URI, DB_NAME)
