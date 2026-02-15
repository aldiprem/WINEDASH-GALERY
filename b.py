import aiofiles
import os
from telethon.tl.types import User, Chat, Channel
import shutil
import io
import re
import json
import math
import time
import pytz
import random
import asyncio
import logging
import hashlib
import sys
import string
import uuid
import httpx
import imageio
import urllib.parse
import itertools
import requests
import sqlite3
import aiohttp
import base64
import subprocess
import threading
import tempfile
from telethon.extensions import markdown
from collections import defaultdict
from threading import Lock
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from telethon import TelegramClient, events, Button, hints, errors, types
from telethon.errors import BotResponseTimeoutError
from telethon.tl.functions.messages import (
    GetHistoryRequest,
    SendMessageRequest
)
from telethon.tl.functions.payments import (
    GetPaymentFormRequest,
    SendStarsFormRequest,
    GetStarsStatusRequest
)
from telethon import functions
from telethon.errors import UserNotParticipantError
from telethon.utils import get_peer_id
from telethon.tl.types import (
    PeerChannel,
    InputPeerUser,
    InputPeerChannel,
    InputReplyToMessage,
    InputBotInlineResultPhoto,
    InputBotInlineMessageText,
    InputWebDocument,
    StarGiftAttributeModel,
    StarGiftAttributeBackdrop,
    StarGiftAttributePattern,
    StarGiftAttributeOriginalDetails,
    InputSavedStarGiftUser,
    InputInvoiceStarGiftTransfer,
    DocumentAttributeCustomEmoji,
    InputPaymentCredentials,
    DataJSON,
    MessageEntityBlockquote,
    UpdateNewMessage,
    ChannelParticipantsBanned,
    ChatBannedRights,
    ChannelParticipantsKicked,
    ChannelParticipantsAdmins,
    MessageMediaWebPage,
    WebPage,
    InputWebDocument,
    DocumentAttributeImageSize
)
from telethon.tl.functions.channels import EditBannedRequest, GetParticipantRequest
from telethon.extensions.markdown import DEFAULT_DELIMITERS
from io import BytesIO

API_ID = 24576633
API_HASH = "29931cf620fad738ee7f69442c98e2ee"
BOT_TOKEN = "7564872741:AAGdWxmkCGCTmZQYsMP8R3IGXBeb94iyK0U"
BOT_TOKEN2 = "8529748208:AAExQJjRlNYRspA-QIMviJQABfQ4QXgMwvY"
PHONE_NUMBER = "+62 812 88721195"

PHONE_UB1 = "+1 646 577 3643"

bot = TelegramClient("giftbot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)
logs = TelegramClient("logsbot", API_ID, API_HASH).start(bot_token=BOT_TOKEN2)
userbot = TelegramClient("gifubot1", API_ID, API_HASH).start(PHONE_NUMBER)

userbot1 = TelegramClient("gifubot", API_ID, API_HASH).start(PHONE_UB1)

db_lock = threading.Lock()
conn = None
cur = None
DB_PATH = "gift.db"
def get_db():
    global conn, cur
    with db_lock:
        if conn is None:
            conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
            cur = conn.cursor()
        return conn, cur

def init_database():
    global conn, cur
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        fullname TEXT,
        username TEXT,
        joined_at TEXT,
        first_start TEXT,
        last_start TEXT,
        last_nego INTEGER DEFAULT 0
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS gifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        owner_id INTEGER,
        slug TEXT,
        api_owner_id INTEGER,
        model TEXT,
        model_rarity TEXT,
        background TEXT,
        background_rarity TEXT,
        symbol TEXT,
        symbol_rarity TEXT,
        original_details TEXT,
        pay_method TEXT DEFAULT 'saldo',
        availability_issued INTEGER,
        availability_total TEXT,
        price INTEGER DEFAULT 0,
        is_transferred INTEGER DEFAULT 0,
        status_tfo TEXT DEFAULT NULL,
        buyer_id INTEGER,
        pending_msg_id INTEGER,
        pending_tfo_at INTEGER,
        is_sold INTEGER DEFAULT 0,
        is_listed INTEGER DEFAULT 1,
        gift_string_id TEXT,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS impersonations (
        owner_id INTEGER,
        target_id INTEGER,
        PRIMARY KEY(owner_id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS nego_sessions (
        user_id INTEGER PRIMARY KEY,
        slug TEXT,
        owner_id INTEGER,
        base_price INTEGER
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS nego_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT,
        owner_id INTEGER,
        user_id INTEGER,
        fixed_price INTEGER,
        offer_price INTEGER,
        created_at INTEGER
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_sold_gifts (
        user_id INTEGER,
        slug TEXT,
        PRIMARY KEY(user_id, slug),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_search_gifts (
        user_id INTEGER,
        gift_name TEXT,
        PRIMARY KEY(user_id, gift_name),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_search_models (
        user_id INTEGER,
        model_name TEXT,
        PRIMARY KEY(user_id, model_name),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_search_backdrops (
        user_id INTEGER,
        backdrop_name TEXT,
        PRIMARY KEY(user_id, backdrop_name),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_search_simbols (
        user_id INTEGER,
        simbol_name TEXT,
        PRIMARY KEY(user_id, simbol_name),
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_search_prices (
        user_id INTEGER PRIMARY KEY,
        price_min INTEGER,
        price_max INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_search_sortby (
        user_id INTEGER PRIMARY KEY,
        sort_by TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS gift_previews (
        slug TEXT PRIMARY KEY,
        file_path TEXT,
        created_at INTEGER
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS gift_rent (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        slug TEXT UNIQUE,
        model TEXT,
        background TEXT,
        symbol TEXT,
        rarity TEXT,
        gift_address TEXT,
        owner_address TEXT,
        price INTEGER DEFAULT 0,
        status TEXT DEFAULT 'available',
        created_at INTEGER,
        channel_msg_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS gift_rent_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT,
        duration_text TEXT,
        duration_seconds INTEGER,
        price TEXT,
        created_at INTEGER,
        FOREIGN KEY (slug) REFERENCES gift_rent(slug)
    )
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS gift_rent_store (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT,
        user_id INTEGER,
        store_text TEXT,
        created_at INTEGER,
        FOREIGN KEY (slug) REFERENCES gift_rent(slug)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS gift_scanned (
        slug TEXT PRIMARY KEY,
        message_id INTEGER,
        text TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS gift_up_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        slug TEXT,
        timestamp INTEGER
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_balance (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER DEFAULT 0
    )
    """)
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS deposit_qris (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        transaction_id TEXT NOT NULL,
        amount INTEGER NOT NULL,
        status TEXT NOT NULL,
        created_at INTEGER NOT NULL,
        expired_at INTEGER NOT NULL,
        paid_at INTEGER,
        last_check INTEGER,
        message_id INTEGER,
        topic_msg_id INTEGER,
        chat_id INTEGER
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS up_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT,
        user_id INTEGER,
        chat_id INTEGER,
        msg_id INTEGER,
        created_at INTEGER
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tfo_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT,
        chat_id BIGINT,
        msg_id BIGINT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS withdraw_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        withdraw_id TEXT UNIQUE,
        user_id INTEGER,
        amount INTEGER,
        account_info TEXT,
        status TEXT,
        created_at INTEGER,
        updated_at INTEGER,
        topic_msg_id INTEGER,
        user_msg_id INTEGER,
        extra TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ticket_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword_text TEXT UNIQUE,
        created_by INTEGER,
        created_at INTEGER,
        expire_at INTEGER,
        max_users INTEGER
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ticket_claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        user_id INTEGER,
        claimed_at INTEGER,
        UNIQUE(session_id, user_id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS gift_offer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        offer_id TEXT UNIQUE,
        mode TEXT,
        created_by INTEGER,
        created_at INTEGER,
        end_at INTEGER,
        status TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS gift_offer_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        offer_id TEXT,
        owner_username TEXT,
        slug TEXT,
        start_bid INTEGER,
        created_at INTEGER
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS stars_orders (
        user_id INTEGER PRIMARY KEY,
        gift_type TEXT DEFAULT NULL,
        gift_id   INTEGER DEFAULT NULL,
        price_rp  INTEGER DEFAULT 0,
        qty       INTEGER DEFAULT 1,
        note      TEXT DEFAULT '',
        send_to   TEXT DEFAULT '',
        total_price_rp INTEGER DEFAULT 0,
        last_status TEXT DEFAULT NULL,
        send_mode TEXT DEFAULT 'Unhide',
        send_from TEXT DEFAULT ''
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admin_pers (
        cmd TEXT PRIMARY KEY,
        reply TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_referral (
        user_id INTEGER PRIMARY KEY,
        referred_by INTEGER,
        total_ref INTEGER DEFAULT 0
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS unique_gifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        msg_id INTEGER,
        slug TEXT UNIQUE,
        gift_id INTEGER,
        title TEXT,
        stars INTEGER,
        model TEXT,
        background TEXT,
        symbol TEXT,
        peer_id INTEGER,
        sender_id INTEGER,
        used INTEGER DEFAULT 0,
        received_at INTEGER
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS limited_profiles (
        owner_peer_id INTEGER PRIMARY KEY,
        requested_by INTEGER,
        name TEXT,
        username TEXT,
        type TEXT,
        image_path TEXT,
        gift_total INTEGER,
        gifts_json TEXT,
        saved_at INTEGER,
        last_updated INTEGER,
        is_active INTEGER DEFAULT 1
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS limited_owners (
        peer_id INTEGER PRIMARY KEY,
        username TEXT,
        type TEXT,
        added_by INTEGER,
        added_at INTEGER
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pending_limited_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_peer_id INTEGER UNIQUE,
        requested_by INTEGER,
        requested_at INTEGER
    )
    """)
    cur.execute("""CREATE TABLE IF NOT EXISTS limited_gifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_peer_id INTEGER,
        gift_id INTEGER,
        title TEXT,
        stars INTEGER,
        is_limited INTEGER,
        is_upgradable INTEGER,
        model TEXT,
        background TEXT,
        symbol TEXT,
        detected_at INTEGER,
        UNIQUE(owner_peer_id, gift_id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS mines_games (
        user_id INTEGER PRIMARY KEY,
        level TEXT,
        bombs INTEGER,
        boxes INTEGER,
        multiplier_step REAL,
        bet INTEGER DEFAULT 0,
        last_bet INTEGER DEFAULT 0,
        current_multiplier REAL DEFAULT 0,
        opened_boxes INTEGER DEFAULT 0,
        predict_msg_id INTEGER,
        status TEXT DEFAULT 'idle',
        created_at TEXT,
        bet_source TEXT DEFAULT 'saldo',
        result TEXT DEFAULT 'LOSE',
        cashout_multiplier REAL DEFAULT 0
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS mines_stats (
        user_id INTEGER PRIMARY KEY,
        total_games INTEGER DEFAULT 0,
        total_win INTEGER DEFAULT 0,
        total_lose INTEGER DEFAULT 0,
        highest_multiplier REAL DEFAULT 0,
        total_profit INTEGER DEFAULT 0
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS wicash_wallet (
        user_id INTEGER PRIMARY KEY,
        wicash INTEGER DEFAULT 0
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS mines_sessions (
        user_id INTEGER PRIMARY KEY,
        bomb_positions TEXT,
        opened_positions TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS mines_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        level TEXT,
        bet INTEGER,
        payout INTEGER,
        profit INTEGER,
        created_at TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS mines_bank (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        total_profit INTEGER DEFAULT 0
    )
    """)
    cur.execute("INSERT OR IGNORE INTO mines_bank (id, total_profit) VALUES (1, 0)")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vouchers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        total_claims INTEGER,
        wicash_amount INTEGER,
        claimed_count INTEGER DEFAULT 0,
        created_at TEXT,
        status TEXT DEFAULT 'pending' -- pending, active, finished
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS voucher_claims (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voucher_code TEXT,
        user_id INTEGER,
        claimed_at TEXT
    )
    """)

def init_limited_db():
    cur.execute("""
    CREATE TABLE IF NOT EXISTS limited_profiles (
        owner_peer_id INTEGER PRIMARY KEY,
        name TEXT,
        username TEXT,
        type TEXT,
        image_path TEXT,
        gift_total INTEGER,
        gifts_json TEXT,
        saved_at INTEGER,
        last_updated INTEGER,
        is_active INTEGER DEFAULT 1
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS limited_owners (
        peer_id INTEGER PRIMARY KEY,
        username TEXT,
        type TEXT,
        added_by INTEGER,
        added_at INTEGER
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pending_limited_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_peer_id INTEGER UNIQUE,
        requested_by INTEGER,
        requested_at INTEGER
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS limited_gifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_peer_id INTEGER,
        gift_id INTEGER,
        title TEXT,
        stars INTEGER,
        is_limited INTEGER,
        is_upgradable INTEGER,
        model TEXT,
        background TEXT,
        symbol TEXT,
        detected_at INTEGER,
        UNIQUE(owner_peer_id, gift_id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS uploaded_gifts (
        gift_id INTEGER PRIMARY KEY,
        title TEXT,
        image_path TEXT,
        saved_at INTEGER
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tp_sessions (
        user_id INTEGER PRIMARY KEY,
        selection TEXT DEFAULT '24j',
        direction TEXT DEFAULT 'updown',
        sort TEXT DEFAULT 'percent',
        order_mode TEXT DEFAULT 'hightlow',
        price_mode TEXT DEFAULT 'idr'
    )
    """)
    conn.commit()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS currency_price (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        rupiah INTEGER,
        usd REAL,
        rub REAL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS gift_search (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        tp TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        title TEXT,
        percent TEXT,
        ton REAL,
        rupiah INTEGER,
        usd REAL,
        rub REAL,
        image_url TEXT,
        UNIQUE(user_id, tp, title)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS gift_stringify (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE,
        gift_id INTEGER,
        internal_id INTEGER,
        title TEXT,
        num INTEGER,
        owner_name TEXT,
        owner_address TEXT,
        gift_address TEXT,
        value_amount INTEGER,
        value_currency TEXT,
        availability_issued INTEGER,
        availability_total INTEGER,
        require_premium INTEGER,
        resale_ton_only INTEGER,
        theme_available INTEGER,
        raw_text TEXT,
        json_data TEXT,
        last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

    # ================= AUTO ADD MISSING COLUMNS =================
    cur.execute("PRAGMA table_info(gift_stringify)")
    existing = [c[1] for c in cur.fetchall()]
    
    columns = {
        "gift_id": "INTEGER",
        "internal_id": "INTEGER",
        "title": "TEXT",
        "num": "INTEGER",
        "owner_name": "TEXT",
        "owner_address": "TEXT",
        "gift_address": "TEXT",
        "value_amount": "INTEGER",
        "value_currency": "TEXT",
        "availability_issued": "INTEGER",
        "availability_total": "INTEGER",
        "require_premium": "INTEGER",
        "resale_ton_only": "INTEGER",
        "theme_available": "INTEGER",
        "raw_text": "TEXT",
        "json_data": "TEXT"
    }
    
    for col, typ in columns.items():
        if col not in existing:
            cur.execute(f"ALTER TABLE gift_stringify ADD COLUMN {col} {typ}")
    
    conn.commit()

    cur.execute("PRAGMA table_info(tp_sessions)")
    user_columns = [col[1] for col in cur.fetchall()]
    if "direction" not in user_columns:
        cur.execute("ALTER TABLE tp_sessions ADD COLUMN direction TEXT DEFAULT 'updown'")
    if "sort" not in user_columns:
        cur.execute("ALTER TABLE tp_sessions ADD COLUMN sort TEXT DEFAULT 'percent'")
    if "order_mode" not in user_columns:
        cur.execute("ALTER TABLE tp_sessions ADD COLUMN order_mode TEXT DEFAULT 'hightlow'")
    if "price_mode" not in user_columns:
        cur.execute("ALTER TABLE tp_sessions ADD COLUMN price_mode TEXT DEFAULT 'idr'")
        conn.commit()
    
    cur.execute("PRAGMA table_info(gifts)")
    user_columns = [col[1] for col in cur.fetchall()]
    if "gift_string_id" not in user_columns:
        cur.execute("ALTER TABLE gifts ADD COLUMN gift_string_id TEXT")
        conn.commit()
    conn.commit()

init_database()
init_limited_db()
EXPORT_PATH = "/root/project/website/export/data.json"
EXPORT_PATH = "/root/project/website/export/data.json"
PREVIEW_DIR = "/root/project/website/previews"
STRINGIFY_DIR = "/root/project/website/stringify/json"
os.makedirs(STRINGIFY_DIR, exist_ok=True)
BOT_USERNAME = "marketaldibot"
GITHUB_PAGES_URL = "https://aldiprem.github.io/WINEDASH-GALERY/"
CHANNEL_MAP = {}
GROUP_ADMIN = -1002646211591
CHANNEL_PENDING = -1002482135331
CHANNEL_BACKUP = -1003155643162
CHANNEL_RENTAL = -1003138087713
CHANNEL_OFFER = -1003276073139
CHLOGS = -1003366237185
CHANNEL_CARI = -1002216382737
CHANNEL_MINES = -1003357530170
CHANNEL_TON = -1002551569177
CHANNEL_SUBSCRIBE = "@winedash"
CHAT_SCAN_ID = -1002207404929
OWNER_ID = [7998861975, 7988486507]
OWNER_SALDO = {7998861975, 7988486507}
ADMIN_ID = [7912936140, 7901961686, 7541857268, 7988486507, 6874740506, 6991845547, 5171503598, 7980255933, 7998861975]
GLOBAL_USER_ID = 0
IMGBB_API_KEY = "2509f613707dfee5602a5d5fc0fb377d"
MIN_BET = 5_000
MAX_BET = 1_000_000_000
BET_STEP = 5_000
pending_bukti = {}
contact_sessions = {}
forward_map = {}
transfer_sessions = {}
nego_sessions = {}
waiting_payment_input = {}
search_price_sessions = {}
active_search_sessions = {}
user_photos = {}
active_inline_pages = {}
rent_sessions = {}
selected_gifts = {}
selected_prices = {}
active_price_sessions = {}
pending_store_input = {}
waiting_up_input = {}
deposit_sessions = {}
withdraw_sessions = {}
withdraw_proof_sessions = {}
deposit_report_session = {}
admin_rdeposit_session = {}
user_state = {}
user_claim = {}
PAGES_STATE = {}
LAST_PING = time.time()
state = {}
mines_bet_sessions = {}
RESULT_CACHE = {}
active_sessions = set()
transfer_confirmed = set()
processing_gift = set()
processing_users = set()
MAX_TICKET_USERS = 10
TICKET_DURATION_MIN = 30
DEFAULT_DELIMITERS['^^'] = lambda *a, **k: MessageEntityBlockquote(*a, **k, collapsed=True)
RESULTS_PER_PAGE = 30
GIFTS_PER_PAGE = 20
TZ_JAKARTA = pytz.timezone("Asia/Jakarta")
GIFT_LINK_PATTERN = re.compile(r"^https://t\.me/nft/([A-Za-z0-9_-]+)$")
LINK_PATTERN = re.compile(r"(?:https?://)?t\.me/nft/([A-Za-z0-9_-]+)")
RE_OFFER_ID = re.compile(r"Format\s+offer\s+#([A-Za-z0-9]+)", re.IGNORECASE)
RE_USERNAME = re.compile(r"Username:\s*(@[A-Za-z0-9_]+)", re.IGNORECASE)
RE_LINK = re.compile(r"Link\s+gift:\s*(\S+)", re.IGNORECASE)
RE_START_BID = re.compile(r"Start\s+bid:\s*([0-9\.]+)", re.IGNORECASE)
CASHIFY_QRIS_V2_URL = "https://cashify.my.id/api/generate/v2/qris"
CASHIFY_CHECK_STATUS_URL = "https://cashify.my.id/api/generate/check-status"
QR_STYLISH_URL = "https://larabert-qrgen.hf.space/v1/create-qr-code"
HEADERS_CASHIFY = {
    "Content-Type": "application/json",
    "x-license-key": "cashify_2861a98069d596a1bf38a5aa794660a3a2bc0a4ff92478248dfacf488829a1d5",
}

CURRENCY_SYMBOLS = {
    "idr": "Rp",
    "usd": "$",
    "rub": "₽",
    "eur": "€",
    "gbp": "£",
    "jpy": "¥",
    "cny": "¥",
    "krw": "₩",
    "try": "₺",
    "inr": "₹"
}

FIAT_PAIRS = {
    "usd": None,
    "idr": "USDTIDR",
    "rub": "USDTRUB"
}

MINES_LEVELS = {
    "easy":   {"bombs": 2,  "tiles": 15,  "inc": 0.1},
    "normal": {"bombs": 4,  "tiles": 24, "inc": 0.15},
    "hard":   {"bombs": 8,  "tiles": 36, "inc": 0.25},
    "devil":  {"bombs": 12, "tiles": 36, "inc": 0.5},
}

TEMPLATE_BANTUAN = {
    "1️⃣": 45,
    "2️⃣": 47,
    "3️⃣": 39,
    "4️⃣": 41,
    "5️⃣": 51,
}

GIFT_SENDER_BOTS = {
    "@rawmpas": userbot1
}

tp_mapping = {
    "12j": "12h",
    "24j": "24h",
    "30j": "30h",
    "3h": "3d",
    "7h": "7d",
    "30h": "30d"
}

GIFT_STARS_CATALOG = {
    "🧸": {"gift_id": 5170233102089322756, "price_rp": 4000},
    "💝": {"gift_id": 5170145012310081615, "price_rp": 4000},
    "🎁": {"gift_id": 5170250947678437525, "price_rp": 7000},
    "🌹": {"gift_id": 5168103777563050263, "price_rp": 7000},
    "🎂": {"gift_id": 5170144170496491616, "price_rp": 13500},
    "🚀": {"gift_id": 5170564780938756245, "price_rp": 13500},
    "💐": {"gift_id": 5170314324215857265, "price_rp": 13500},
    "🏆": {"gift_id": 5168043875654172773, "price_rp": 27000},
    "💍": {"gift_id": 5170690322832818290, "price_rp": 27000}
}

slug_channel_map = {
    "BDayCandle": (-1003062734410, 21),
    "BerryBox": (-1003062734410, 4),
    "BlingBlinky": (-1003062734410, 654),
    "BowTie": (-1003062734410, 20),
    "BunnyMuffin": (-1003062734410, 5),
    "CandyCane": (-1003062734410, 22),
    "CloverPin": (-1003062734410, 8),
    "CookieHeart": (-1003062734410, 23),
    "CrystalBall": (-1003062734410, 50),
    "DeskCalendar": (-1003062734410, 24),
    "DiamondRing": (-1003062734410, 25),
    "EasterEgg": (-1003062734410, 26),
    "EternalCandle": (-1003062734410, 27),
    "FaithAmulet": (-1003062734410, 341),
    "GingerCookie": (-1003062734410, 28),
    "HangingStar": (-1003062734410, 57),
    "HappyBrownie": (-1003062734410, 336),
    "HolidayDrink": (-1003062734410, 29),
    "HomemadeCake": (-1003062734410, 58),
    "HypnoLollipop": (-1003062734410, 59),
    "IceCream": (-1003062734410, 337),
    "InstantRamen": (-1003062734410, 338),
    "IonicDryer": (-1003062734410, 126),
    "JackInTheBox": (-1003062734410, 60),
    "JellyBunny": (-1003062734410, 61),
    "JesterHat": (-1003062734410, 63),
    "JingleBells": (-1003062734410, 62),
    "LightSword": (-1003062734410, 64),
    "LolPop": (-1003062734410, 66),
    "LoveCandle": (-1003062734410, 67),
    "LovePotion": (-1003062734410, 68),
    "LunarSnake": (-1003062734410, 65),
    "MadPumpkin": (-1003062734410, 131),
    "MoneyPot": (-1003062734410, 653),
    "MousseCake": (-1003062734410, 339),
    "PartySparkler": (-1003062734410, 70),
    "PetSnake": (-1003062734410, 69),
    "RecordPlayer": (-1003062734410, 73),
    "RestlessJar": (-1003062734410, 71),
    "PrettyPosy": (-1003062734410, 655),
    "SakuraFlower": (-1003062734410, 74),
    "SantaHat": (-1003062734410, 75),
    "SleighBell": (-1003062734410, 83),
    "SnakeBox": (-1003062734410, 72),
    "SnowGlobe": (-1003062734410, 78),
    "SnowMittens": (-1003062734410, 76),
    "SpicedWine": (-1003062734410, 79),
    "SpringBasket": (-1003062734410, 340),
    "SpyAgaric": (-1003062734410, 80),
    "StarNotepad": (-1003062734410, 81),
    "StellarRocket": (-1003062734410, 120),
    "SwissWatch": (-1003062734410, 77),
    "TamaGadget": (-1003062734410, 84),
    "TopHat": (-1003062734410, 85),
    "ToyBear": (-1003062734410, 86),
    "ValentineBox": (-1003062734410, 151),
    "VintageCigar": (-1003062734410, 88),
    "VoodooDoll": (-1003062734410, 87),
    "WhipCupcake": (-1003062734410, 111),
    "WinterWreath": (-1003062734410, 91),
    "WitchHat": (-1003062734410, 82),
    "XmasStocking": (-1003062734410, 92),
    "ArtisanBrick": (-1003062734410, 159),
    "AstralShard": (-1003062734410, 160),
    "BigYear": (-1003062734410, 161),
    "BondedRing": (-1003062734410, 162),
    "CupidCharm": (-1003062734410, 163),
    "DurovsCap": (-1003062734410, 164),
    "ElectricSkull": (-1003062734410, 165),
    "EternalRose": (-1003062734410, 166),
    "EvilEye": (-1003062734410, 167),
    "FlyingBroom": (-1003062734410, 168),
    "FreshSocks": (-1003062734410, 169),
    "GemSignet": (-1003062734410, 170),
    "GenieLamp": (-1003062734410, 171),
    "HeartLocket": (-1003062734410, 172),
    "HeroicHelmet": (-1003062734410, 173),
    "HexPot": (-1003062734410, 175),
    "InputKey": (-1003062734410, 176),
    "JollyChimp": (-1003062734410, 177),
    "JoyfulBundle": (-1003062734410, 178),
    "KissedFrog": (-1003062734410, 179),
    "LootBag": (-1003062734410, 180),
    "LowRider": (-1003062734410, 181),
    "LushBouquet": (-1003062734410, 182),
    "MagicPotion": (-1003062734410, 183),
    "MightyArm": (-1003062734410, 184),
    "MiniOscar": (-1003062734410, 185),
    "MoonPendant": (-1003062734410, 186),
    "NailBracelet": (-1003062734410, 187),
    "NekoHelmet": (-1003062734410, 188),
    "ParfumeBottle": (-1003062734410, 189),
    "PlushPepe": (-1003062734410, 190),
    "PreciousPeach": (-1003062734410, 191),
    "ScaredCat": (-1003062734410, 192),
    "SharpTongue": (-1003062734410, 193),
    "SignetRing": (-1003062734410, 194),
    "SkullFlower": (-1003062734410, 196),
    "SkyStilettos": (-1003062734410, 197),
    "SignetRing": (-1003062734410, 194),
    "SnoopCigar": (-1003062734410, 198),
    "SnoopDogg": (-1003062734410, 199),
    "SwagBag": (-1003062734410, 201),
    "TrappedHeart": (-1003062734410, 202),
    "WestsideSign": (-1003062734410, 203),
    "DepositLogs": (-1003516589535, 2),
    "GiftSoldOut": (-1003516589535, 4),
    "WithdrawLogs": (-1003516589535, 3)
}

def generate_gift_string_id():
    chars = string.ascii_letters + string.digits
    raw = ''.join(random.choice(chars) for _ in range(20))
    return '-'.join(raw[i:i+5] for i in range(0, 20, 5))

def encode_filters_to_base64(filter_data):
    import json
    import base64
    
    json_string = json.dumps(filter_data)
    return base64.b64encode(json_string.encode()).decode()

# ===== FUNGSI UNTUK MEMBUAT LINK MINI APP =====
def create_mini_app_link(filter_data):
    encoded = encode_filters_to_base64(filter_data)
    return f"https://t.me/{BOT_USERNAME}/gifts?startapp={encoded}"

# ===== FUNGSI UNTUK MEMBUAT BUTTON URL DI ATAS =====
def create_top_url_button(text, url):
    return Button.url(text, url)

# ===== FUNGSI UNTUK MEMBUAT BUTTON INLINE =====
def create_inline_button(text, data):
    return Button.inline(text, data)

def stringify_to_json(result):
    gift = result.gift

    data = {
        "id": gift.id,
        "gift_id": gift.gift_id,
        "slug": gift.slug,
        "title": gift.title,
        "num": gift.num,
        "availability_issued": gift.availability_issued,
        "availability_total": gift.availability_total,
        "require_premium": gift.require_premium,
        "resale_ton_only": gift.resale_ton_only,
        "theme_available": gift.theme_available,
        "owner_name": gift.owner_name,
        "owner_address": gift.owner_address,
        "gift_address": gift.gift_address,
        "value_amount": gift.value_amount,
        "value_currency": gift.value_currency,
        "attributes": [convert_attribute(a) for a in gift.attributes]
    }

    return data

async def save_stringify(slug, result):
    gift = result.gift

    raw = result.stringify()
    json_obj = stringify_to_json(result)

    cur.execute("""
        INSERT INTO gift_stringify (
            slug,
            gift_id,
            internal_id,
            title,
            num,
            owner_name,
            owner_address,
            gift_address,
            value_amount,
            value_currency,
            availability_issued,
            availability_total,
            require_premium,
            resale_ton_only,
            theme_available,
            raw_text,
            json_data
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(slug) DO UPDATE SET
            gift_id=excluded.gift_id,
            internal_id=excluded.internal_id,
            title=excluded.title,
            num=excluded.num,
            owner_name=excluded.owner_name,
            owner_address=excluded.owner_address,
            gift_address=excluded.gift_address,
            value_amount=excluded.value_amount,
            value_currency=excluded.value_currency,
            availability_issued=excluded.availability_issued,
            availability_total=excluded.availability_total,
            require_premium=excluded.require_premium,
            resale_ton_only=excluded.resale_ton_only,
            theme_available=excluded.theme_available,
            raw_text=excluded.raw_text,
            json_data=excluded.json_data,
            last_update=CURRENT_TIMESTAMP
    """, (
        slug,
        gift.gift_id,
        gift.id,
        gift.title,
        gift.num,
        gift.owner_name,
        gift.owner_address,
        gift.gift_address,
        gift.value_amount,
        gift.value_currency,
        gift.availability_issued,
        gift.availability_total,
        int(gift.require_premium),
        int(gift.resale_ton_only),
        int(gift.theme_available),
        raw,
        json.dumps(json_obj)
    ))

    conn.commit()

def convert_document(doc):
    if not doc:
        return None

    return {
        "id": doc.id,
        "access_hash": doc.access_hash,
        "date": doc.date.isoformat() if doc.date else None,
        "mime_type": doc.mime_type,
        "size": doc.size,
        "dc_id": doc.dc_id
    }


def convert_attribute(attr):
    base = {
        "type": attr.__class__.__name__,
        "name": getattr(attr, "name", None),
        "rarity": getattr(attr, "rarity_permille", None)
    }

    # ================= MODEL / PATTERN =================
    if hasattr(attr, "document") and attr.document:
        base["document"] = convert_document(attr.document)

    # ================= BACKDROP =================
    if hasattr(attr, "backdrop_id"):
        base.update({
            "backdrop_id": attr.backdrop_id,
            "center_color": getattr(attr, "center_color", None),
            "edge_color": getattr(attr, "edge_color", None),
            "pattern_color": getattr(attr, "pattern_color", None),
            "text_color": getattr(attr, "text_color", None),
        })

    return base

async def export_stringify_json_files():
    import os
    import json

    BASE_DIR = "/root/project/website/stringify/json"
    os.makedirs(BASE_DIR, exist_ok=True)

    cur.execute("SELECT slug FROM gifts")
    rows = cur.fetchall()

    total = len(rows)
    success = 0

    for (slug,) in rows:
        try:
            result = await userbot(
                functions.payments.GetUniqueStarGiftRequest(slug=slug)
            )

            raw_text = result.stringify()
            json_obj = stringify_to_json(result)

            # ================= SAVE DB =================
            cur.execute("""
                INSERT INTO gift_stringify (slug, raw_text, json_data)
                VALUES (?, ?, ?)
                ON CONFLICT(slug) DO UPDATE SET
                    raw_text=excluded.raw_text,
                    json_data=excluded.json_data,
                    last_update=CURRENT_TIMESTAMP
            """, (slug, raw_text, json.dumps(json_obj)))

            conn.commit()

            # ================= SAVE FILE =================
            path = os.path.join(BASE_DIR, f"{slug}.json")

            with open(path, "w", encoding="utf-8") as f:
                json.dump(json_obj, f, indent=2, ensure_ascii=False)

            success += 1

        except Exception as e:
            print(f"❌ stringify gagal {slug}: {e}")

    print(f"✅ Export stringify: {success}/{total}")

def push_json_stringify_to_github():
    import subprocess
    import os
    import sys

    repo_path = "/root/project/website"
    stringify_dir = os.path.join(repo_path, "stringify/json")

    try:
        print("🔍 Mengecek perubahan stringify JSON...")

        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )

        rebase_dir = os.path.join(repo_path, ".git", "rebase-merge")
        if os.path.exists(rebase_dir):
            print("⚠️ Git sedang rebase, skip push")
            return

        status_lines = result.stdout.strip().splitlines()
        changed = any("stringify/json" in line for line in status_lines)

        if not changed:
            print("ℹ️ Tidak ada perubahan stringify")
            return

        # ================= BRANCH =================
        branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        branch = branch_result.stdout.strip()

        print(f"ℹ️ Branch: {branch}")

        # ================= ADD =================
        subprocess.run(
            ["git", "add", "stringify/json"],
            cwd=repo_path,
            check=True
        )

        # ================= COMMIT =================
        commit_check = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=repo_path
        )

        if commit_check.returncode != 0:
            subprocess.run(
                ["git", "commit", "-m", "auto update stringify json"],
                cwd=repo_path,
                check=True
            )
            print("✅ Commit berhasil")

        # ================= SYNC =================
        print("🔄 Sync remote...")

        subprocess.run(
            ["git", "stash", "push", "--include-untracked"],
            cwd=repo_path,
            check=False
        )

        subprocess.run(
            ["git", "pull", "--rebase", "origin", branch],
            cwd=repo_path,
            check=True
        )

        subprocess.run(
            ["git", "stash", "pop"],
            cwd=repo_path,
            check=False
        )

        # ================= PUSH =================
        subprocess.run(
            ["git", "push", "origin", branch],
            cwd=repo_path,
            check=True
        )

        print("🚀 stringify JSON berhasil dipush")

    except Exception as e:
        print(f"❌ Push stringify gagal: {e}")
        sys.exit(1)

async def heartbeat():
    global LAST_PING
    while True:
        await asyncio.sleep(10)
        if time.time() - LAST_PING > 60:
            print("💀 BOT HANG → RESTART")
            os.execv(sys.executable, [sys.executable] + sys.argv)

def extract_gift_id(slug: str) -> str:
    if "-" in slug:
        return slug.split("-")[-1]
    return slug

def push_previews_to_github():
    import glob
    import os
    import subprocess

    repo_path = "/root/project/website"
    previews_dir = os.path.join(repo_path, "previews")

    try:
        all_previews = glob.glob(os.path.join(previews_dir, "*.jpg"))

        if not all_previews:
            print("ℹ️ Tidak ada file preview untuk dipush, skip git push")
            return

        # ==============================
        # CEK STATUS GIT
        # ==============================
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )

        if not result.stdout.strip():
            print("ℹ️ Tidak ada perubahan di Git, skip git push")
            return

        # ==============================
        # ADD FILE
        # ==============================
        subprocess.run(
            ["git", "add"] + all_previews,
            cwd=repo_path,
            check=True
        )

        # ==============================
        # COMMIT (JANGAN FAIL KALAU KOSONG)
        # ==============================
        subprocess.run(
            ["git", "commit", "-m", "auto update preview images"],
            cwd=repo_path,
            check=False
        )

        # ==============================
        # AUTO SYNC DENGAN REMOTE
        # ==============================
        subprocess.run(
            ["git", "pull", "--rebase", "origin", "css"],
            cwd=repo_path,
            check=True
        )

        # ==============================
        # PUSH
        # ==============================
        subprocess.run(
            ["git", "push", "origin", "css"],
            cwd=repo_path,
            check=True
        )

        print("🚀 previews berhasil dipush ke GitHub")

    except subprocess.CalledProcessError as e:
        print(f"❌ Gagal push previews ke GitHub: {e}")

async def get_raw_gift_image(client, gift):
    from io import BytesIO
    from PIL import Image

    try:
        data = await client.download_media(gift.photo, file=bytes)
        return Image.open(BytesIO(data))
    except:
        return None

async def sync_stargift_png():
    import os
    import re
    from PIL import Image

    SAVE_DIR = "/root/project/website/images/gifts"
    os.makedirs(SAVE_DIR, exist_ok=True)

    print("🔄 Sinkronisasi PNG StarGift dimulai...")

    # =========================
    # Helper: Convert title → CamelCase clean
    # =========================
    def clean_title(title: str) -> str:
        # Ambil hanya huruf & angka sebagai kata
        words = re.findall(r"[A-Za-z0-9]+", title)

        # Capitalize tiap kata lalu gabung
        return "".join(word.capitalize() for word in words)

    # =========================
    # Ambil katalog StarGift
    # =========================
    try:
        res = await userbot(functions.payments.GetStarGiftsRequest(hash=0))
        gifts = res.gifts or []
    except Exception as e:
        print(f"❌ Gagal ambil katalog: {e}")
        return

    valid = [g for g in gifts if getattr(g, "id", None) and getattr(g, "title", None)]

    if not valid:
        print("⚠️ Tidak ada gift valid")
        return

    # =========================
    # Map title → gift
    # =========================
    gift_map = {}
    for g in valid:
        file_title = clean_title(g.title)
        gift_map[file_title] = g

    existing_files = {f for f in os.listdir(SAVE_DIR) if f.endswith(".png")}

    saved = 0
    updated = 0
    deleted = 0

    # =========================
    # SAVE / UPDATE PNG
    # =========================
    for title, gift in gift_map.items():
        file_name = f"{title}.png"
        file_path = os.path.join(SAVE_DIR, file_name)

        try:
            img = await get_raw_gift_image(userbot, gift)
            if not img:
                continue

            if img.mode != "RGBA":
                img = img.convert("RGBA")

            img.save(file_path, "PNG")

            if file_name in existing_files:
                updated += 1
            else:
                saved += 1

        except Exception as e:
            print(f"❌ Error simpan {title}: {e}")

    # =========================
    # DELETE FILE YANG SUDAH TIDAK ADA
    # =========================
    current_titles = {f"{t}.png" for t in gift_map.keys()}

    for file in existing_files:
        if file not in current_titles:
            try:
                os.remove(os.path.join(SAVE_DIR, file))
                deleted += 1
            except:
                pass

    # =========================
    # LOG RESULT
    # =========================
    print("✅ Sinkronisasi selesai:")
    print(f"   ➕ Added: {saved}")
    print(f"   🔄 Updated: {updated}")
    print(f"   🗑️ Deleted: {deleted}")

async def save_preview_to_github(slug: str):
    os.makedirs(PREVIEW_DIR, exist_ok=True)

    temp_path = await fetch_preview_from_webpagebot(slug)
    if not temp_path or not os.path.exists(temp_path):
        return None

    final_path = os.path.join(PREVIEW_DIR, f"{slug}.jpg")

    if os.path.abspath(temp_path) != os.path.abspath(final_path):
        shutil.copyfile(temp_path, final_path)

    cur.execute("""
        INSERT OR REPLACE INTO gift_previews (slug, file_path, created_at)
        VALUES (?, ?, ?)
    """, (slug, final_path, int(time.time())))
    conn.commit()

    return final_path

def push_user_json_to_github(user_id: int):
    import subprocess, os

    repo_path = "/root/project/website"
    file_rel = f"users/json/{user_id}.json"
    file_path = os.path.join(repo_path, file_rel)

    try:
        if not os.path.exists(file_path):
            print("⚠️ user json tidak ada")
            return

        # cek rebase
        if os.path.exists(os.path.join(repo_path, ".git", "rebase-merge")):
            print("⚠️ Git sedang rebase, skip push")
            return

        subprocess.run(["git", "add", file_rel], cwd=repo_path, check=True)

        # cek perubahan
        diff = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=repo_path
        )

        if diff.returncode == 0:
            print("ℹ️ Tidak ada perubahan user json")
            return

        subprocess.run(
            ["git", "commit", "-m", f"auto update user {user_id}"],
            cwd=repo_path,
            check=True
        )

        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True
        ).stdout.strip()

        subprocess.run(["git", "pull", "--rebase", "origin", branch], cwd=repo_path, check=True)
        subprocess.run(["git", "push", "origin", branch], cwd=repo_path, check=True)

        print(f"🚀 User {user_id} pushed")

    except Exception as e:
        print("❌ push user error:", e)

def export_user_to_json(user_id: int):
    import os, json

    conn, cur = get_db()

    cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    balance = row[0] if row else 0

    data = {
        "user_id": user_id,
        "balance": balance
    }

    repo_path = "/root/project/website"
    path = os.path.join(repo_path, f"users/json/{user_id}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return path

def push_json_to_github():
    repo_path = "/root/project/website"
    json_path = os.path.join(repo_path, "export/data.json")

    try:
        print("🔍 Memvalidasi file data.json...")

        if not os.path.exists(json_path):
            print("⚠️ data.json belum ada, skip push")
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        conn, cur = get_db()

        json_modified = False

        for item in data:
            if "image" in item:
                del item["image"]
                json_modified = True

            if "nama" not in item and "name" in item:
                item["nama"] = item["name"].split('#')[0].strip()
                json_modified = True

            # ✅ TAMBAHAN BARU: SLUG ID
            slug = item.get("slug")
            if "slug_id" not in item and slug:
                cur.execute("SELECT gift_string_id FROM gifts WHERE slug=?", (slug,))
                row = cur.fetchone()
                if row and row[0]:
                    item["slug_id"] = row[0]
                    json_modified = True

        if json_modified:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )

        rebase_dir = os.path.join(repo_path, ".git", "rebase-merge")
        if os.path.exists(rebase_dir):
            print("⚠️ Git sedang rebase, skip push")
            return

        status_lines = result.stdout.strip().splitlines()
        json_changed = any("export/data.json" in line for line in status_lines)

        if not json_changed and not json_modified:
            print("ℹ️ data.json tidak berubah, skip git push")
            return

        branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        current_branch = branch_result.stdout.strip()

        subprocess.run(["git", "add", "export/data.json"], cwd=repo_path, check=True)

        commit_result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=repo_path
        )

        if commit_result.returncode != 0:
            subprocess.run(
                ["git", "commit", "-m", "auto update data.json"],
                cwd=repo_path,
                check=True
            )

        subprocess.run(
            ["git", "pull", "--rebase", "origin", current_branch],
            cwd=repo_path,
            check=True
        )

        subprocess.run(
            ["git", "push", "origin", current_branch],
            cwd=repo_path,
            check=True
        )

        print("🚀 data.json berhasil dipush")

    except Exception as e:
        print(f"❌ Error tidak terduga: {e}")

def export_to_json():
    import os, json

    conn, cur = get_db()

    EXPORT_PATH = "/root/project/website/export/data.json"
    os.makedirs(os.path.dirname(EXPORT_PATH), exist_ok=True)

    cur.execute("""
        SELECT
            slug,
            model,
            model_rarity,
            background,
            background_rarity,
            symbol,
            symbol_rarity,
            price,
            gift_string_id
        FROM gifts
        WHERE is_listed=1 AND is_sold=0
        ORDER BY id DESC
    """)

    rows = cur.fetchall()
    merged = []

    for (
        slug,
        model, model_rarity,
        bg, bg_rarity,
        symbol, symbol_rarity,
        price,
        gift_string_id
    ) in rows:

        gift_id = extract_gift_id(slug)
        base_name = slug.split('-')[0]

        item = {
            "id": gift_id,
            "name": f"{base_name} #{gift_id}",
            "slug": slug,
            "model": f"{model} ({model_rarity})" if model else "",
            "symbol": f"{symbol} ({symbol_rarity})" if symbol else "",
            "bg": f"{bg} ({bg_rarity})" if bg else "",
            "price": price or 0,
            "saldo": price or 0,
            "posting": "https://t.me/market_wine/57/None",
            "image": f"https://aldiprem.github.io/WINEDASH-GALERY/previews/{slug}.jpg",
            "slug_id": gift_string_id or ""
        }

        merged.append(item)

    with open(EXPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=4, ensure_ascii=False)

    print(f"✅ data.json berhasil dibuat ({len(merged)} item)")

def export_single_gift_to_json(slug):
    import json, os

    conn, cur = get_db()

    EXPORT_PATH = "/root/project/website/export/data.json"
    os.makedirs(os.path.dirname(EXPORT_PATH), exist_ok=True)

    if os.path.exists(EXPORT_PATH):
        with open(EXPORT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    cur.execute("""
        SELECT
            slug,
            model, model_rarity,
            background, background_rarity,
            symbol, symbol_rarity,
            price,
            gift_string_id
        FROM gifts
        WHERE slug=?
    """, (slug,))

    row = cur.fetchone()
    if not row:
        return

    (
        slug,
        model, model_rarity,
        bg, bg_rarity,
        symbol, symbol_rarity,
        price,
        gift_string_id
    ) = row

    gift_id = extract_gift_id(slug)
    base_name = slug.split('-')[0]

    new_item = {
        "id": gift_id,
        "name": f"{base_name} #{gift_id}",
        "slug": slug,

        "model": f"{model} ({model_rarity})" if model else "",
        "symbol": f"{symbol} ({symbol_rarity})" if symbol else "",
        "bg": f"{bg} ({bg_rarity})" if bg else "",

        "price": price or 0,
        "saldo": price or 0,
        "posting": "https://t.me/market_wine/57/None",
        "image": f"https://aldiprem.github.io/WINEDASH-GALERY/previews/{slug}.jpg",

        # ✅ TAMBAHAN BARU
        "slug_id": gift_string_id or ""
    }

    found = False
    for i, item in enumerate(data):
        if item["slug"] == slug:
            data[i] = new_item
            found = True
            break

    if not found:
        data.append(new_item)

    with open(EXPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"✅ Incremental export: {slug}")
  
async def upload_to_imgbb(image_bytes: io.BytesIO) -> str:
    image_bytes.seek(0)
    encoded = base64.b64encode(image_bytes.read()).decode()
    url = f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data={"image": encoded}) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            return data.get("data", {}).get("url")

def get_tp_price_mode(user_id: int):
    cur.execute(
        "SELECT price_mode FROM tp_sessions WHERE user_id = ?",
        (user_id,)
    )
    row = cur.fetchone()
    return row[0] if row and row[0] else "idr"

def get_tp_order(user_id: int) -> str:
    cur.execute("SELECT order_mode FROM tp_sessions WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    return row[0] if row and row[0] else "hightlow"

def get_tp_sort(user_id: int) -> str:
    cur.execute("SELECT sort FROM tp_sessions WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    return row[0] if row and row[0] else "percent"

def set_tp_direction(user_id: int, direction: str):
    cur.execute("""
        INSERT INTO tp_sessions (user_id, direction)
        VALUES (?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET direction = excluded.direction
    """, (user_id, direction))
    conn.commit()
    
def get_tp_direction(user_id: int) -> str:
    cur.execute("SELECT direction FROM tp_sessions WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    return row[0] if row and row[0] else "updown"

async def get_ton_usdt_price():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=TONUSDT"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            return float((await r.json())["price"])
            
async def get_usdt_to_currency(currency: str):
    if currency == "usd":
        return 1.0
    pair = FIAT_PAIRS.get(currency)
    if not pair:
        raise ValueError("Fiat tidak didukung")
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={pair}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            return float((await r.json())["price"])
            
@bot.on(events.NewMessage(pattern=r"^/price\s+(\d+(?:\.\d+)?)\s+(\w+)$"))
async def price_handler(event):
    amount = float(event.pattern_match.group(1))
    currency = event.pattern_match.group(2).lower()

    symbol = CURRENCY_SYMBOLS.get(currency)
    if not symbol:
        return await event.reply("❌ Mata uang tidak didukung.")

    try:
        ton_price_usdt = await get_ton_usdt_price()
        rate = await get_usdt_to_currency(currency)

        result = ton_price_usdt * rate * amount

        formatted = f"{result:,.0f}".replace(",", ".")
        await event.reply(
            f"💎 **Harga TON**\n\n"
            f"1 $TON = {symbol}{formatted} {currency.upper()}"
        )

    except Exception as e:
        await event.reply(f"❌ Gagal mengambil harga TON\n\n{e}")

def format_currency(value, currency):
    if value is None:
        return None

    try:
        value = float(value)
    except:
        return None

    if currency == "idr":
        return f"Rp{int(value):,}".replace(",", ".")
    elif currency == "usd":
        return f"${value:,.2f}"
    elif currency == "rub":
        return f"₽{value:,.2f}"

    return None

def canonical_title(t: str) -> str:
    if not t:
        return ""

    t = t.replace("'", "’").strip()
    tl = t.replace(" ", "").lower()

    if tl == "durovscap":
        return "Durov’s Cap"

    if tl in ["khabibspapakha", "khabibspapakhas"]:
        return "Khabib’s Papakha"

    if tl == "ufcstrike":
        return "UFC Strike"

    if tl == "ufcstrikes":
        return ""

    return t

async def create_pricegift_grid(user_id: int, selection: str):
    # ===== AMBIL DATA GLOBAL =====
    cur.execute("""
        SELECT gs.title, gs.percent, gs.ton, gs.rupiah, gs.usd, gs.rub
        FROM gift_search gs
        WHERE gs.user_id = ? AND gs.tp = ?
        ORDER BY gs.timestamp DESC
        LIMIT 120
    """, (user_id, selection))
    grid_rows = cur.fetchall()

    if not grid_rows:
        return None

    # ===== AMBIL IMAGE PATH DARI uploaded_gifts =====
    image_map = {}
    cur.execute("SELECT title, image_path FROM uploaded_gifts")
    for t, path in cur.fetchall():
        t_norm = t.replace("'", "’").strip().lower()
        if t_norm not in image_map:
            image_map[t_norm] = path

    seen = set()
    unique_grid_rows = []
    
    for row in grid_rows:
        title = canonical_title(row[0])
        key = title.lower()
    
        if not title or key in seen:
            continue
    
        seen.add(key)
        unique_grid_rows.append(
            (title, *row[1:])
        )
    
        if len(unique_grid_rows) >= 60:
            break
    
    grid_rows = unique_grid_rows

    parsed_rows = []
    for row in grid_rows:
        title, percent, ton, rupiah, usd, rub = row
        title_norm = title.replace("'", "’").strip().lower()

        # Mapping khusus
        if title_norm == "durov's cap":
            title_norm = "durov’s cap"
        elif title_norm in ["khabibs papakha", "khabibs papakhas"]:
            title_norm = "khabib’s papakha"
        elif title_norm == "ufcstrike":
            title_norm = "ufc strike"

        image_path = image_map.get(title_norm)

        try:
            p = float(str(percent or "0").replace("%", ""))
        except:
            p = 0.0

        parsed_rows.append((p, (title, percent, ton, rupiah, usd, rub, image_path)))

    # ===== URUTKAN PERCENT DENGAN LOGIKA MARKET =====
    non_zero = []
    zeros = []
    
    for p, row in parsed_rows:
        if p == 0:
            zeros.append((p, row))
        else:
            non_zero.append((p, row))
    
    # urut berdasarkan BESAR PERUBAHAN (ABS), terbesar → terkecil
    non_zero.sort(key=lambda x: abs(x[0]), reverse=True)
    
    ordered = []
    
    # 1️⃣ TOP GAINER (+ terbesar)
    for p, row in non_zero:
        if p > 0:
            ordered.append((p, row))
            break
    
    # 2️⃣ TOP LOSER (- terbesar / paling minus)
    for p, row in non_zero:
        if p < 0:
            ordered.append((p, row))
            break
    
    # 3️⃣ SISANYA (selain 2 di atas), tetap berdasarkan ABS desc
    for item in non_zero:
        if item not in ordered:
            ordered.append(item)
    
    # 4️⃣ 0% PALING AKHIR
    ordered.extend(zeros)
    
    # hasil akhir
    grid_rows = [row for p, row in ordered]

    # ====== GRID CONFIG ======
    COLS = 6
    BOX_W, BOX_H = 400, 200
    GAP = 28
    rows_count = math.ceil(len(grid_rows) / COLS)
    canvas_w = GAP + COLS * (BOX_W + GAP)
    canvas_h = GAP + rows_count * (BOX_H + GAP)

    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 255))
    draw = ImageDraw.Draw(canvas)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()

    def round_rect(draw, xy, radius, fill):
        draw.rounded_rectangle(xy, radius=radius, fill=fill)

    LEFT_PADDING = 20

    for idx, row in enumerate(grid_rows):
        title, percent, ton, rupiah, usd, rub, image_path = row
        col = idx % COLS
        row_idx = idx // COLS
        x = GAP + col * (BOX_W + GAP)
        y = GAP + row_idx * (BOX_H + GAP)

        # WARNA CARD
        try:
            p = float(str(percent or "0").replace("%", ""))
            if p > 0:
                box_bg = (83, 199, 83)
            elif p < 0:
                box_bg = (255, 92, 92)
            else:
                box_bg = (169, 169, 169)
        except:
            p = 0
            box_bg = (169, 169, 169)

        round_rect(draw, (x, y, x + BOX_W, y + BOX_H), 35, box_bg)

        # FOTO GIFT
        img_x, img_y = x + LEFT_PADDING, y + 20
        img_width, img_height = 120, 120
        if image_path:
            try:
                img = Image.open(image_path).convert("RGBA")
                ratio = min(120 / img.width, 120 / img.height)
                img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)
                img_width, img_height = img.width, img.height
                canvas.paste(img, (img_x, img_y), img)
            except:
                fallback_img = Image.new("RGBA", (img_width, img_height), (200, 200, 200, 255))
                canvas.paste(fallback_img, (img_x, img_y))
        else:
            fallback_img = Image.new("RGBA", (img_width, img_height), (200, 200, 200, 255))
            canvas.paste(fallback_img, (img_x, img_y))

        # PANEL TEXT
        if p > 0:
            panel_color = (58, 185, 58)
        elif p < 0:
            panel_color = (255, 128, 128)
        else:
            panel_color = (169, 169, 169)

        panel_x = img_x + img_width + 10
        panel_y = img_y
        panel_w = BOX_W - (panel_x - x) - 20
        panel_h = 120
        round_rect(draw, (panel_x, panel_y, panel_x + panel_w, panel_y + panel_h), 18, panel_color)

        text_x = panel_x + 12
        text_y = panel_y + 6
        line = 40

        draw.text((text_x, text_y), f"{percent or '0%'}", font=font_small, fill=(0, 0, 0))
        text_y += line
        draw.text((text_x, text_y), f"{ton} TON", font=font_small, fill=(0, 0, 0))
        text_y += line

        idr_text = format_currency(rupiah, "idr")
        if idr_text:
            draw.text((text_x, text_y), idr_text, font=font_small, fill=(0, 0, 0))

        draw.text((img_x, y + BOX_H - 45), title, font=font, fill=(0, 0, 0))

    out = io.BytesIO()
    canvas.save(out, "PNG")
    out.seek(0)
    out.name = f"all_gifts_{user_id}.png"
    return out

async def update_currency_price():
    async for msg in userbot.iter_messages(CHANNEL_TON, limit=1):
        if msg.text:
            lines = msg.text.splitlines()
            rupiah = usd = rub = None
            for line in lines:
                # Ambil hanya angka dan titik/komanya
                if "Rp" in line:
                    match = re.search(r"[\d,]+", line)
                    if match:
                        rupiah = int(match.group(0).replace(",", ""))
                elif "$" in line:
                    match = re.search(r"[\d.]+", line)
                    if match:
                        usd = float(match.group(0))
                elif "₽" in line:
                    match = re.search(r"[\d.]+", line)
                    if match:
                        rub = float(match.group(0))
            if rupiah is not None and usd is not None and rub is not None:
                cur.execute("""
                INSERT INTO currency_price(rupiah, usd, rub) VALUES(?, ?, ?)
                """, (rupiah, usd, rub))
                conn.commit()
                return rupiah, usd, rub
    return None, None, None

def flatten_rgba(img, bg_color=(0, 0, 0)):
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, bg_color)
        bg.paste(img, mask=img.split()[3])  # pakai alpha
        return bg
    return img.convert("RGB")

async def get_raw_gift_image(userbot, gift):
    import io, os, uuid, subprocess
    from PIL import Image

    doc = getattr(gift, "sticker", None) or getattr(gift, "document", None)

    # 1️⃣ gift.photo
    try:
        if gift.photo and gift.photo.sizes:
            largest = max(
                gift.photo.sizes,
                key=lambda s: (getattr(s, "w", 0) or 0) * (getattr(s, "h", 0) or 0)
            )
            b = await userbot.download_file(largest.location)
            return Image.open(io.BytesIO(b)).convert("RGBA")
    except:
        pass

    # 2️⃣ thumbs
    try:
        if doc and getattr(doc, "thumbs", None):
            for t in doc.thumbs:
                if getattr(t, "bytes", None):
                    return Image.open(io.BytesIO(t.bytes)).convert("RGBA")
                if getattr(t, "location", None):
                    b = await userbot.download_file(t.location)
                    return Image.open(io.BytesIO(b)).convert("RGBA")
    except:
        pass

    # 3️⃣ thumbnail
    try:
        data = await userbot.download_media(doc, thumb=-1)
        if isinstance(data, bytes):
            return Image.open(io.BytesIO(data)).convert("RGBA")
        if isinstance(data, str) and os.path.exists(data):
            img = Image.open(data).convert("RGBA")
            os.remove(data)
            return img
    except:
        pass

    # 4️⃣ full file fallback
    try:
        tmp = f"/tmp/{uuid.uuid4().hex}"
        path = await userbot.download_media(doc, file=tmp)

        if path and os.path.exists(path):
            if path.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                img = Image.open(path).convert("RGBA")
                os.remove(path)
                return img

            out = f"/tmp/{uuid.uuid4().hex}.png"
            subprocess.run(
                ["ffmpeg", "-y", "-i", path, "-vframes", "1", out],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            if os.path.exists(out):
                img = Image.open(out).convert("RGBA")
                os.remove(path)
                os.remove(out)
                return img
            os.remove(path)
    except:
        pass

    return None

async def send_limited_detail(event, owner_peer_id):
    cur.execute("""
        SELECT name, username, type, gift_total, image_path
        FROM limited_profiles
        WHERE owner_peer_id = ?
          AND requested_by = ?
          AND is_active = 1
    """, (owner_peer_id, event.sender_id))

    owner = cur.fetchone()
    if not owner:
        return await event.answer(
            "❌ Owner tidak ditemukan atau bukan milik anda.",
            alert=True
        )

    name, username, owner_type, gift_total, image_path = owner

    mention = f"[{name}](tg://user?id={owner_peer_id})"
    msg = f"""
🔎 **DETAIL {owner_type.upper()} GIFT LIMITED**

**Name:** {mention}
**Username:** @{username}
**User ID:** `{owner_peer_id}`
**Total Gift:** {gift_total}

^^__tekan tombol di bawah untuk melihat list gift__^^
"""

    buttons = [
        [Button.inline("🎁 LIST GIFT", data=f"view_limited:{owner_peer_id}:0")],
        [Button.inline("🔄 REFRESH 🔄", data=f"refresh_limited:{owner_peer_id}")],
        [Button.inline("🔙 KEMBALI", data="list_limited")]
    ]

    await event.delete()
    if image_path and os.path.exists(image_path):
        await event.respond(msg, file=image_path, buttons=buttons)
    else:
        await event.respond(msg, buttons=buttons)

def get_bandar_bank():
    cur.execute("SELECT total_profit FROM mines_bank WHERE id=1")
    return cur.fetchone()[0] or 0

def add_bandar_profit(amount: int):
    cur.execute("""
        UPDATE mines_bank
        SET total_profit = total_profit + ?
        WHERE id=1
    """, (amount,))

def should_force_bomb(bet, current_mult, step):
    bandar_profit = get_bandar_bank()

    current_potential = int(bet * current_mult)
    next_potential = int(bet * (current_mult + step))

    # bandar hanya boleh bayar dari profit
    if next_potential > bandar_profit:
        return True

    return False

async def download_gift_raw_image(gift):
    import io, os, uuid, subprocess
    from PIL import Image

    # 1️⃣ gift.photo
    if getattr(gift, "photo", None) and getattr(gift.photo, "sizes", None):
        largest = max(
            gift.photo.sizes,
            key=lambda s: (getattr(s, "w", 0) or 0) * (getattr(s, "h", 0) or 0)
        )
        b = await userbot.download_file(largest.location)
        return Image.open(io.BytesIO(b)).convert("RGB")

    # 2️⃣ sticker / document
    doc = getattr(gift, "sticker", None) or getattr(gift, "document", None)
    if not doc:
        return None

    tmp = await userbot.download_media(doc, file=f"/tmp/{uuid.uuid4().hex}")
    if not tmp or not os.path.exists(tmp):
        return None

    ext = os.path.splitext(tmp)[1].lower()

    # image
    if ext in (".png", ".jpg", ".jpeg", ".webp"):
        img = Image.open(tmp).convert("RGB")
        os.remove(tmp)
        return img

    # video / tgs
    out = f"/tmp/{uuid.uuid4().hex}.png"
    subprocess.run(
        ["ffmpeg", "-y", "-i", tmp, "-vframes", "1", out],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    os.remove(tmp)

    if os.path.exists(out):
        img = Image.open(out).convert("RGB")
        os.remove(out)
        return img

    return None

async def edit_predict_buttons(user_id, boxes, per_row, bomb_positions):
    cur.execute("""
        SELECT predict_msg_id
        FROM mines_games
        WHERE user_id=?
    """, (user_id,))
    r = cur.fetchone()
    if not r or not r[0]:
        return

    msg_id = r[0]

    buttons = []
    idx = 0
    while idx < boxes:
        row = []
        for _ in range(per_row):
            if idx >= boxes:
                break

            if idx in bomb_positions:
                row.append(Button.inline("💣", data=b"noop"))
            else:
                row.append(Button.inline("✅", data=b"noop"))
            idx += 1
        buttons.append(row)

    try:
        await bot.edit_message(
            CHANNEL_MINES,
            msg_id,
            buttons=buttons
        )
    except:
        pass

def get_per_row(level):
    return {
        "easy": 3,
        "normal": 4,
        "hard": 6,
        "devil": 6
    }.get(level, 4)

def save_mines_history(user_id, level, bet, payout):
    profit = payout - bet

    cur.execute("""
        INSERT INTO mines_history
        (user_id, level, bet, payout, profit, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        level,
        bet,
        payout,
        profit,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()

def gifts_to_dict(saved_gifts):
    result = []
    for saved in saved_gifts:
        gift = saved.gift
        d = {
            "gift_id": getattr(gift, "id", None),
            "title": getattr(gift, "title", "N/A"),
            "stars": getattr(gift, "stars", 0),
            "limited": getattr(gift, "is_limited", False),
            "upgradable": getattr(gift, "is_upgradable", False),
            "symbol": getattr(gift, "symbol", "🎁")
        }
        result.append(d)
    return result

async def render_profile_image(peer, gifts):
    import io, os, uuid, math, subprocess
    from PIL import Image, ImageDraw, ImageFont

    async def get_gift_image(saved):
        gift = saved.gift
        doc = getattr(gift, "sticker", None) or getattr(gift, "document", None)

        try:
            if hasattr(gift, "photo") and gift.photo and getattr(gift.photo, "sizes", None):
                largest = max(
                    gift.photo.sizes,
                    key=lambda s: (getattr(s, "w", 0) or 0) * (getattr(s, "h", 0) or 0)
                )
                b = await userbot.download_file(largest.location)
                return Image.open(io.BytesIO(b)).convert("RGBA")
        except: pass

        try:
            if doc is not None and getattr(doc, "thumbs", None):
                for t in doc.thumbs:
                    if hasattr(t, "bytes") and t.bytes:
                        try: return Image.open(io.BytesIO(t.bytes)).convert("RGBA")
                        except: pass
                    if hasattr(t, "location"):
                        try:
                            b = await userbot.download_file(t.location)
                            return Image.open(io.BytesIO(b)).convert("RGBA")
                        except: pass
        except: pass

        try:
            data = await userbot.download_media(doc, thumb=-1)
            if isinstance(data, (bytes, bytearray)): return Image.open(io.BytesIO(data)).convert("RGBA")
            if isinstance(data, str) and os.path.exists(data):
                img = Image.open(data).convert("RGBA")
                os.remove(data)
                return img
        except: pass

        try:
            tmp_in = f"/tmp/{uuid.uuid4().hex}"
            path = await userbot.download_media(doc, file=tmp_in)
            if isinstance(path, str) and os.path.exists(path):
                ext = os.path.splitext(path)[1].lower()
                if ext in (".png", ".jpg", ".jpeg", ".webp"):
                    img = Image.open(path).convert("RGBA")
                    os.remove(path)
                    return img
        except: pass

        return None

    counted = {}
    for s in gifts:
        gid = getattr(s.gift, "id", None)
        if gid is None: continue
        counted.setdefault(gid, {"saved": s, "count": 0})
        counted[gid]["count"] += 1

    thumbs = []
    for g in counted.values():
        img = await get_gift_image(g["saved"])
        if img: thumbs.append((img, g["count"], g["saved"].gift))

    if not thumbs:
        raise RuntimeError("Tidak ada thumbnail gift")

    COLS, BOX, BOX_H, GAP = 3, 360, 360, 28
    rows = math.ceil(len(thumbs)/COLS)
    canvas_w = GAP + COLS*(BOX + GAP)
    canvas_h = GAP + rows*(BOX_H + GAP)

    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0,0,0,255))
    draw = ImageDraw.Draw(canvas)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    except: font = ImageFont.load_default()

    corner_radius = 45
    box_bg = (28,28,29,255)

    def round_rect(draw, xy, radius, fill):
        x1, y1, x2, y2 = xy
        draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill)

    for idx, (img, count, gift_obj) in enumerate(thumbs):
        col = idx % COLS
        row = idx // COLS
        x = GAP + col*(BOX + GAP)
        y = GAP + row*(BOX_H + GAP)

        round_rect(draw, (x, y, x+BOX, y+BOX_H), radius=corner_radius, fill=box_bg)

        img_h_space = BOX_H - 85
        img_w_space = BOX - 55
        ratio = min(img_w_space/img.width, img_h_space/img.height)*0.95
        new_w, new_h = int(img.width*ratio), int(img.height*ratio)
        im_resized = img.resize((new_w, new_h), Image.LANCZOS)
        px, py = x + (BOX - new_w)//2, y + 22 + (img_h_space - new_h)//2
        canvas.paste(im_resized, (px, py), im_resized)

        text = f"{gift_obj.title or 'Gift'}  x{count}"
        tb = draw.textbbox((0,0), text, font=font)
        tw, th = tb[2]-tb[0], tb[3]-tb[1]
        tx, ty = x+25, y + BOX_H - 55
        overlay = Image.new("RGBA", (tw+20, th+20), (0,0,0,190))
        canvas.paste(overlay, (tx-10, ty-10), overlay)
        draw.text((tx, ty), text, font=font, fill=(255,255,255,255))

    out = io.BytesIO()
    canvas.convert("RGB").save(out, format="JPEG", quality=92)
    out.seek(0)
    out.name = f"profile_{peer.id}.jpg"
    return out

async def fetch_saved_gifts(peer):
    gifts = []
    offset = ""
    while True:
        res = await userbot(functions.payments.GetSavedStarGiftsRequest(
            peer=peer,
            offset=offset,
            limit=100,
            exclude_unsaved=False,
            exclude_saved=False,
            exclude_unlimited=False,
            exclude_unique=False,
            sort_by_value=False,
            exclude_upgradable=False,
            exclude_unupgradable=False
        ))
        gifts.extend(res.gifts)
        if not getattr(res, "next_offset", None):
            break
        offset = res.next_offset
    return gifts

def safe(v):
    if v is None:
        return None
    if isinstance(v, (str, int, float, bool)):
        return v
    if isinstance(v, bytes):
        return v.hex()
    if isinstance(v, dict):
        return {k: safe(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [safe(x) for x in v]
    return str(v)


def stringify_saved_gifts(saved_gifts):
    out = []
    for s in saved_gifts:
        try:
            d = s.to_dict()
            out.append({k: safe(v) for k, v in d.items()})
        except:
            pass
    return out

def star_gift_to_safe_dict(gift):
    try:
        data = gift.to_dict()
    except Exception:
        data = {}

    return {
        "id": getattr(gift, "id", None),
        "title": data.get("title") or getattr(gift, "title", ""),
        "stars": data.get("stars", getattr(gift, "stars", 0)),
        "limited": data.get("limited", False),
        "upgradable": data.get("upgradable", False),
        "symbol": (
            data.get("symbol")
            or data.get("emoji")
            or "🎁"
        ),
        "raw": data
    }

def extract_gift_emoji(gift):
    for attr in ("emoji", "symbol"):
        if hasattr(gift, attr) and getattr(gift, attr):
            return getattr(gift, attr)

    if hasattr(gift, "title") and gift.title:
        for ch in gift.title:
            if ch in "🎁🎉⭐💎🔥❤️💫🌟":
                return ch

    return "🎁"

async def render_delete_limited(event, rows):
    user_id = event.sender_id
    selected = state[user_id]["selected"]

    buttons, row_btn = [], []

    for i, (peer_id, username) in enumerate(rows, 1):
        base = f"@{username}" if username else str(peer_id)
        label = f"✅ {base}" if peer_id in selected else base

        row_btn.append(
            Button.inline(label, data=f"toggle_delete_limited:{peer_id}")
        )

        if len(row_btn) == 3:
            buttons.append(row_btn)
            row_btn = []

    if row_btn:
        buttons.append(row_btn)

    buttons.append([
        Button.inline("🗑️ CONFIRM DELETE", data="confirm_delete_limited"),
        Button.inline("🔙 KEMBALI", data="list_limited")
    ])

    await event.edit(
        "🗑️ **PILIH AKUN / CHANNEL YANG AKAN DIHAPUS**\n\n"
        "__Klik untuk memilih (toggle).__",
        buttons=buttons
    )

async def build_gift_grid(userbot, gifts, peer_id):
    import io, os, math, uuid
    from PIL import Image, ImageDraw, ImageFont

    # =========================
    # GROUP BY GIFT ID
    # =========================
    counted = {}
    for saved in gifts:
        gift = getattr(saved, "gift", None)
        gid = getattr(gift, "id", None)
        if not gid:
            continue

        counted.setdefault(gid, {
            "saved": saved,
            "count": 0
        })
        counted[gid]["count"] += 1

    groups = list(counted.values())
    if not groups:
        return None

    # =========================
    # IMAGE FETCHER (SUPER SAFE)
    # =========================
    async def get_gift_image(saved):
        gift = saved.gift
        doc = getattr(gift, "sticker", None) or getattr(gift, "document", None)

        # 1️⃣ PHOTO (jarang tapi paling bersih)
        try:
            photo = getattr(gift, "photo", None)
            if photo and getattr(photo, "sizes", None):
                largest = max(
                    photo.sizes,
                    key=lambda s: (s.w or 0) * (s.h or 0)
                )
                b = await userbot.download_file(largest.location)
                if b:
                    return Image.open(io.BytesIO(b)).convert("RGBA")
        except:
            pass

        # 2️⃣ THUMB BYTES
        try:
            if doc and getattr(doc, "thumbs", None):
                for t in doc.thumbs:
                    if getattr(t, "bytes", None):
                        return Image.open(io.BytesIO(t.bytes)).convert("RGBA")
        except:
            pass

        # 3️⃣ DOWNLOAD MEDIA (bytes ATAU file path)
        try:
            data = await userbot.download_media(doc, thumb=-1)
            if isinstance(data, (bytes, bytearray)):
                return Image.open(io.BytesIO(data)).convert("RGBA")
            if isinstance(data, str) and os.path.exists(data):
                return Image.open(data).convert("RGBA")
        except:
            pass

        return None

    # =========================
    # COLLECT THUMBS
    # =========================
    thumbs = []
    for g in groups:
        img = await get_gift_image(g["saved"])
        if img:
            thumbs.append((img, g["count"]))

    # =========================
    # FALLBACK (WAJIB)
    # =========================
    if not thumbs:
        img = Image.new("RGB", (700, 420), (18, 18, 18))
        d = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36
            )
        except:
            font = ImageFont.load_default()

        d.text(
            (50, 170),
            "NO GIFT PREVIEW AVAILABLE",
            fill=(255, 255, 255),
            font=font
        )

        out = io.BytesIO()
        img.save(out, format="JPEG", quality=92)
        out.seek(0)
        out.name = f"limited_{peer_id}.jpg"
        return out

    # =========================
    # RENDER GRID
    # =========================
    COLS = 3
    BOX = 340
    GAP = 30
    rows = math.ceil(len(thumbs) / COLS)

    canvas = Image.new(
        "RGB",
        (
            GAP + COLS * (BOX + GAP),
            GAP + rows * (BOX + GAP)
        ),
        (0, 0, 0)
    )
    draw = ImageDraw.Draw(canvas)

    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28
        )
    except:
        font = ImageFont.load_default()

    for i, (img, count) in enumerate(thumbs):
        col = i % COLS
        row = i // COLS

        x = GAP + col * (BOX + GAP)
        y = GAP + row * (BOX + GAP)

        img = img.resize((280, 280), Image.LANCZOS)
        canvas.paste(img, (x + 30, y + 20), img)

        draw.text(
            (x + 20, y + BOX - 45),
            f"x{count}",
            font=font,
            fill=(255, 255, 255)
        )

    out = io.BytesIO()
    canvas.save(out, format="JPEG", quality=92)
    out.seek(0)
    out.name = f"limited_{peer_id}.jpg"
    return out

def reconnect_database():
    global conn, cur
    try:
        if conn:
            conn.close()
    except:
        pass
    
    time.sleep(0.5)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
    cur = conn.cursor()
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn, cur

async def transfer_unique_gift(userbot, target, msg_id: int):
    if not (-2_147_483_648 <= msg_id <= 2_147_483_647):
        raise ValueError("msg_id bukan INT32")

    stargift = InputSavedStarGiftUser(
        msg_id=int(msg_id)
    )
    to = await userbot.get_input_entity(target)
    invoice = InputInvoiceStarGiftTransfer(
        stargift=stargift,
        to_id=to
    )
    form = await userbot(
        GetPaymentFormRequest(invoice=invoice)
    )

    await userbot(
        SendStarsFormRequest(
            form_id=form.form_id,
            invoice=invoice
        )
    )

    print(f"[TFO SUCCESS] msg_id={msg_id} → {target}")

async def process_referral_bonus(buyer_id: int, base_price: int):
    try:
        cur.execute("SELECT referred_by FROM users WHERE user_id=?", (buyer_id,))
        row = cur.fetchone()

        if not row:
            print(f"ℹ️ Buyer {buyer_id} tidak punya referral.")
            return

        referred_by = row[0]
        if not referred_by:
            print(f"ℹ️ Buyer {buyer_id} tidak punya referral.")
            return

        referral_id = int(referred_by)

        bonus = int(base_price * 0.01)
        if bonus <= 0:
            print(f"ℹ️ Bonus referral = 0, skip.")
            return

        cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (referral_id,))
        row_ref = cur.fetchone()
        ref_balance = row_ref[0] if row_ref else 0

        new_ref_balance = ref_balance + bonus

        if row_ref is None:
            cur.execute(
                "INSERT INTO user_balance (user_id, balance) VALUES (?, ?)",
                (referral_id, new_ref_balance)
            )
        else:
            cur.execute(
                "UPDATE user_balance SET balance=? WHERE user_id=?",
                (new_ref_balance, referral_id)
            )

        conn.commit()
        
        msg = f"""
💰 **You receive `{bonus}` from 1% fee for your referral purchase!**
        """

        try:
            print(f"🎁 Referral Bonus: {referral_id} dapat +{bonus} (1% dari {base_price})")
            await logs.send_message(CHLOGS, f"User {referral_id} mendapatkan bonus referral: {bonus}")
            await bot.send_message(
                referral_id,
                msg,
                parse_mode="markdown"
            )
        except:
            pass

    except Exception as e:
        print(f"❌ Error process_referral_bonus: {e}")

def get_referrer(user_id):
    cur.execute("SELECT referred_by FROM user_referral WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    return row[0] if row else None

def add_new_user_with_ref(user_id, ref_id):
    if get_referrer(user_id) is not None:
        return False
    
    cur.execute("""
        INSERT OR REPLACE INTO user_referral (user_id, referred_by, total_ref)
        VALUES (?, ?, 0)
    """, (user_id, ref_id))

    cur.execute("""
        UPDATE user_referral
        SET total_ref = COALESCE(total_ref,0) + 1
        WHERE user_id=?
    """, (ref_id,))
    
    conn.commit()
    return True

def create_user_if_not_exist(user_id):
    cur.execute("SELECT user_id FROM user_referral WHERE user_id=?", (user_id,))
    if not cur.fetchone():
        cur.execute("INSERT INTO user_referral (user_id, referred_by, total_ref) VALUES (?, NULL, 0)", (user_id,))
        conn.commit()

def get_or_create_stars_order(user_id: int) -> dict:
    cur.execute("""
        SELECT gift_type, gift_id, qty, note, send_to, price_rp, total_price_rp,
               last_status, send_mode, send_from
        FROM stars_orders
        WHERE user_id = ?
    """, (user_id,))
    row = cur.fetchone()

    if row:
        (gift_type, gift_id, qty, note, send_to, price_rp, total_price_rp,
         last_status, send_mode, send_from) = row

        qty = qty or 1
        price_rp = price_rp or 0
        total_price_rp = total_price_rp or (price_rp * qty)
        last_status = last_status or ""
        send_mode = send_mode or "Unhide"
        send_from = send_from or ""
    else:
        gift_type = ""
        gift_id = 0
        qty = 1
        note = ""
        send_to = ""
        price_rp = 0
        total_price_rp = 0
        last_status = ""
        send_mode = "Unhide"
        send_from = ""
        cur.execute("""
            INSERT INTO stars_orders (
                user_id, gift_type, gift_id, qty, note, send_to,
                price_rp, total_price_rp, last_status, send_mode, send_from
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, gift_type, gift_id, qty, note, send_to,
              price_rp, total_price_rp, last_status, send_mode, send_from))
        conn.commit()

    return {
        "user_id": user_id,
        "gift_type": gift_type,
        "gift_id": gift_id,
        "qty": qty,
        "note": note,
        "send_to": send_to,
        "price_rp": price_rp,
        "total_price_rp": total_price_rp,
        "last_status": last_status,
        "send_mode": send_mode,
        "send_from": send_from,
    }


def update_stars_order(
    user_id,
    gift_type=None,
    gift_id=None,
    qty=None,
    note=None,
    send_to=None,
    price_rp=None,
    total_price_rp=None,
    last_status=None,
    send_mode=None,
    send_from=None
):
    order = get_or_create_stars_order(user_id)

    new_gift_type   = gift_type   if gift_type   is not None else order["gift_type"]
    new_gift_id     = gift_id     if gift_id     is not None else order["gift_id"]
    new_qty         = qty         if qty         is not None else order["qty"]
    new_note        = note        if note        is not None else order["note"]
    new_send_to     = send_to     if send_to     is not None else order["send_to"]
    new_price_rp    = price_rp    if price_rp    is not None else order["price_rp"]
    new_last_status = last_status if last_status is not None else order["last_status"]
    new_send_mode   = send_mode   if send_mode   is not None else order["send_mode"]
    new_send_from   = send_from   if send_from   is not None else order["send_from"]

    # kalau price_rp masih 0 dan gift_type valid, ambil dari katalog
    if new_price_rp == 0 and new_gift_type:
        cfg = GIFT_STARS_CATALOG.get(new_gift_type) or {}
        new_price_rp = cfg.get("price_rp", 0)
        if new_gift_id == 0:
            new_gift_id = cfg.get("gift_id", 0)

    # hitung total kalau belum dikasih manual
    if total_price_rp is not None:
        new_total_price_rp = total_price_rp
    else:
        new_total_price_rp = (new_price_rp or 0) * (new_qty or 1)

    cur.execute("""
        UPDATE stars_orders
        SET gift_type = ?, gift_id = ?, qty = ?, note = ?, send_to = ?,
            price_rp = ?, total_price_rp = ?, last_status = ?,
            send_mode = ?, send_from = ?
        WHERE user_id = ?
    """, (
        new_gift_type,
        new_gift_id,
        new_qty,
        new_note,
        new_send_to,
        new_price_rp,
        new_total_price_rp,
        new_last_status,
        new_send_mode,
        new_send_from,
        user_id
    ))
    conn.commit()

async def get_userbot_stars_balance(userbot_client):
    try:
        status = await userbot_client(GetStarsStatusRequest(peer=types.InputPeerSelf()))
        balance = getattr(getattr(status, "balance", None), "amount", 0)
        currency = getattr(getattr(status, "balance", None), "currency", "")
        return balance, currency
    except Exception as e:
        print(f"⚠ Gagal ambil saldo Stars userbot: {e}")
        return 0, ""

async def send_stars_gift(
    userbot_client,
    gift_id: int,
    qty: int,
    send_to_list,
    note: str,
    hide_sender: bool = False
):
    if not send_to_list:
        return 0, []

    print(f"[DEBUG] send_stars_gift called hide_sender={hide_sender}")

    total_sent = 0
    failed_targets = []

    send_to_cycle = itertools.cycle(send_to_list)

    for _ in range(qty):
        target = next(send_to_cycle)
        raw_target = target

        if isinstance(target, str):
            t = target.strip()
            target_for_entity = t
        else:
            target_for_entity = target

        try:
            peer = await userbot_client.get_input_entity(target_for_entity)
        except Exception as e:
            print(f"⚠ Gagal resolve target {raw_target}: {e}")
            failed_targets.append(str(raw_target))
            continue

        print(f"[DEBUG] building invoice for {raw_target}, hide_name={hide_sender}")

        invoice = types.InputInvoiceStarGift(
            peer=peer,
            gift_id=gift_id,
            hide_name=hide_sender,   # <- INI YANG BENER
            include_upgrade=False,
            message=types.TextWithEntities(text=note or "", entities=[])
        )

        try:
            payment_form = await userbot_client(functions.payments.GetPaymentFormRequest(invoice=invoice))
            await userbot_client(functions.payments.SendStarsFormRequest(
                form_id=payment_form.form_id,
                invoice=invoice
            ))
            total_sent += 1
            await asyncio.sleep(0.3)
        except Exception as e:
            print(f"⚠ Gagal kirim gift {gift_id} ke {raw_target}: {e}")
            failed_targets.append(str(raw_target))
            continue

    return total_sent, failed_targets

def format_gift_name(gift_key: str) -> str:
    if not gift_key:
        return "-"
    cfg = GIFT_STARS_CATALOG.get(gift_key) or {}
    price = cfg.get("price_rp", 0)
    if not price:
        return gift_key.upper()
    price_fmt = f"Rp{price:,}".replace(",", ".")
    return f"{gift_key.upper()} ({price_fmt})"

def get_text_size(draw, text, font):
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        return draw.textsize(text, font=font)

def build_inline_grid_from_slugs(slugs_with_price):
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_size = 72

    photo_imgs = []

    for slug, price in slugs_with_price[:RESULTS_PER_PAGE]:
        cur.execute("SELECT file_path FROM gift_previews WHERE slug=?", (slug,))
        row = cur.fetchone()
        if not row:
            continue
        fp = row[0]
        if not fp or not os.path.exists(fp):
            continue

        try:
            img = Image.open(fp).convert("RGBA")
        except Exception:
            continue

        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(font_path, font_size) if os.path.exists(font_path) else ImageFont.load_default()

        price_text = f"Rp{price:,}".replace(",", ".")
        tw, th = get_text_size(draw, price_text, font)
        padding = 10

        # kotak hitam transparan di kanan atas
        draw.rectangle(
            [img.width - tw - padding*2, padding, img.width - padding, padding + th + 5],
            fill=(0, 0, 0, 150)
        )
        draw.text(
            (img.width - tw - padding*1.5, padding),
            price_text,
            font=font,
            fill=(255, 255, 255)
        )

        photo_imgs.append(img.convert("RGB"))

    if not photo_imgs:
        return None

    n = len(photo_imgs)
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)
    widths, heights = zip(*(i.size for i in photo_imgs))
    cell_w = max(widths)
    cell_h = max(heights)

    grid = Image.new("RGB", (cols * cell_w, rows * cell_h), (255, 255, 255))

    i = 0
    for r in range(rows):
        for c in range(cols):
            if i >= n:
                break
            img = photo_imgs[i]
            gx = c * cell_w
            gy = r * cell_h
            grid.paste(img, (gx, gy))
            i += 1

    output = io.BytesIO()
    grid.save(output, format="JPEG")
    output.seek(0)
    output.name = "inline_search_grid.jpg"
    return output

def parse_dot_price(text: str) -> int:
    clean = text.replace(".", "").strip()
    if not clean.isdigit():
        raise ValueError("Format harga tidak valid")
    return int(clean)

def make_rdeposit_session_id(user_id: int, transaction_id: str) -> str:
    base = f"{user_id}:{transaction_id}"
    h = hashlib.sha256(base.encode()).hexdigest()
    return h[:10]

def calculate_deal_price_from_nego_fee(nego_fee: int) -> int:
    if nego_fee <= 0:
        return 0
    deal = int(nego_fee / 1.02)
    return deal

def generate_withdraw_id(length: int = 25) -> str:
    import string, random
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))

def save_tfo_message(slug: str, chat_id: int, msg_id: int):
    try:
        cur.execute(
            "INSERT INTO tfo_messages (slug, chat_id, msg_id) VALUES (?, ?, ?)",
            (slug.lower(), int(chat_id), int(msg_id))
        )
        conn.commit()
    except Exception as e:
        print(f"⚠️ Gagal simpan tfo_messages {slug} {chat_id}/{msg_id}: {e}")

def generate_offer_id(length: int = 15) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def is_offer_active(offer_id: str) -> bool:
    cur.execute("""
        SELECT end_at, status
        FROM gift_offer
        WHERE offer_id=?
    """, (offer_id,))
    row = cur.fetchone()
    if not row:
        return False

    end_at, status = row
    now_ts = int(time.time())

    if now_ts >= end_at:
        try:
            cur.execute("UPDATE gift_offer SET status='expired' WHERE offer_id=?", (offer_id,))
            conn.commit()
        except:
            pass
        return False

    if status != "active":
        return False

    return True

async def delete_all_tfo_messages(slug: str):
    slug_lower = slug.lower()
    try:
        cur.execute("SELECT chat_id, msg_id FROM tfo_messages WHERE slug=?", (slug_lower,))
        rows = cur.fetchall()
        if not rows:
            return

        for chat_id, msg_id in rows:
            try:
                await bot.delete_messages(chat_id, msg_id)
            except Exception as e:
                print(f"⚠️ Gagal hapus msg TFO {slug} di {chat_id}/{msg_id}: {e}")

        cur.execute("DELETE FROM tfo_messages WHERE slug=?", (slug_lower,))
        conn.commit()
    except Exception as e:
        print(f"⚠️ Error delete_all_tfo_messages {slug}: {e}")

async def get_ton_prices_from_binance(amount: float):
    ton_usdt = await get_ton_usdt_price()
    usd = round(amount * ton_usdt, 2)
    idr = round(amount * ton_usdt * await get_usdt_to_currency("idr"), 0)
    rub = round(amount * ton_usdt * await get_usdt_to_currency("rub"), 2)
    return idr, usd, rub

async def monitor_price():
    print("🚀 Monitor Price berjalan...")
    me = await userbot.get_me()

    # ===== util background berdasarkan persen =====
    def bg_from_percent(percent: str):
        try:
            val = float(percent.replace("%", ""))
            if val > 0:
                return (83, 199, 83)       # hijau
            elif val < 0:
                return (255, 92, 92)       # merah
            else:
                return (169, 169, 169)     # abu-abu untuk 0%
        except:
            return (169, 169, 169)

    def flatten_rgba(img, bg_color):
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, bg_color)
            bg.paste(img, mask=img.split()[3])
            return bg
        return img.convert("RGB")

    def normalize_title(t: str):
        if not t:
            return ""
        t = t.replace("'", "’").strip()
        tl = t.replace(" ", "").lower()
    
        if tl == "durovscap":
            return "Durov’s Cap"
        if tl in ["khabibspapakha", "khabibspapakhas"]:
            return "Khabib’s Papakha"
    
        if tl == "ufcstrike":
            return "UFC Strike"
    
        if tl == "ufcstrikes":
            return ""
    
        return t

    while True:
        try:
            cur.execute("""
                DELETE FROM gift_search
                WHERE lower(replace(title,' ','')) IN ('ufcstrike','ufcstrikes','ufcstrike')
                AND percent LIKE '-%'
            """)
            
            cur.execute("""
                DELETE FROM uploaded_gifts
                WHERE lower(replace(title,' ','')) IN ('ufcstrike','ufcstrikes')
            """)
            
            conn.commit()
          
            # ===== AMBIL SEMUA TP =====
            cur.execute("SELECT DISTINCT selection FROM tp_sessions")
            tp_rows = cur.fetchall()
            if not tp_rows:
                tp_rows = [("24j",)]

            # ===== INLINE QUERY =====
            results = await userbot.inline_query("peektgbot", "All Gifts")
            if not results:
                print("❌ Inline result kosong")
                await asyncio.sleep(60)
                continue

            await results[0].click(me.id)
            await asyncio.sleep(5)

            raw_text = None
            async for msg in userbot.iter_messages(me.id, limit=20):
                if msg.text and "Details ⬇️" in msg.text:
                    raw_text = msg.text
                    break

            if not raw_text:
                print("⚠️ Detail market tidak ditemukan")
                await asyncio.sleep(60)
                continue

            lines = [
                l.strip() for l in
                raw_text.split("Details ⬇️", 1)[1].splitlines()
                if l.strip()
            ]

            PATTERN = re.compile(
                r"^(.+?)\s+([+-]?\d+(?:\.\d+)?%)?\s+—\s+([\d.]+)\s+TON$"
            )

            # ===== RATE =====
            ton_usdt = await get_ton_usdt_price()
            usdt_idr = await get_usdt_to_currency("idr")
            usdt_rub = await get_usdt_to_currency("rub")

            saved_count = 0
            img_saved = 0
            now = int(time.time())

            # ===== AMBIL KATALOG GIFT SEKALI =====
            catalog = await userbot(functions.payments.GetStarGiftsRequest(hash=0))
            gift_map = {}
            for g in catalog.gifts or []:
                title_norm = normalize_title(getattr(g, "title", None))
                if title_norm:
                    gift_map[title_norm] = g

            for line in lines:
                m = PATTERN.match(line)
                if not m:
                    continue

                title, percent, ton = m.groups()
                percent = percent or "0%"
                ton_value = float(ton)

                raw_cmp = title.replace(" ", "").lower()
                if raw_cmp == "ufcstrikes":
                    cur.execute("DELETE FROM gift_search WHERE lower(title) LIKE '%ufcstrikes%'")
                    cur.execute("DELETE FROM uploaded_gifts WHERE lower(title) LIKE '%ufcstrikes%'")
                    conn.commit()
                    continue

                if title.replace(" ", "").lower() == "ufcstrikes":
                    cur.execute("DELETE FROM gift_search WHERE title LIKE '%UFCStrikes%'")
                    cur.execute("DELETE FROM uploaded_gifts WHERE title LIKE '%UFCStrikes%'")
                    conn.commit()
                    continue

                usd = ton_value * ton_usdt
                rupiah = int(usd * usdt_idr)
                rub = usd * usdt_rub

                title_norm = canonical_title(title)
                if not title_norm:
                    continue
                  
                for (tp,) in tp_rows:
                    # ===== HAPUS DUPLIKAT LAMA JIKA ADA =====
                    cur.execute("""
                        DELETE FROM gift_search
                        WHERE user_id=? AND tp=? AND title!=? AND title LIKE ?
                    """, (GLOBAL_USER_ID, tp, title_norm, f"%{title_norm}%"))

                    cur.execute("""
                        INSERT INTO gift_search (
                            user_id, tp, title, percent, ton, rupiah, usd, rub
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(user_id, tp, title) DO UPDATE SET
                            percent=excluded.percent,
                            ton=excluded.ton,
                            rupiah=excluded.rupiah,
                            usd=excluded.usd,
                            rub=excluded.rub,
                            timestamp=CURRENT_TIMESTAMP
                    """, (
                        GLOBAL_USER_ID,
                        tp,
                        title_norm,
                        percent,
                        ton_value,
                        rupiah,
                        usd,
                        rub
                    ))
                    saved_count += 1

                # ===== BUAT / UPDATE FOTO =====
                gift = gift_map.get(title_norm)
                if not gift:
                    continue

                try:
                    img = await get_raw_gift_image(userbot, gift)
                    if not img:
                        continue

                    bg = bg_from_percent(percent)
                    img = flatten_rgba(img, bg)

                    image_path = f"/tmp/market_gift_{gift.id}.jpg"
                    img.save(image_path, "JPEG", quality=95)

                    # ===== HAPUS DUPLIKAT LAMA DI uploaded_gifts =====
                    cur.execute("""
                        DELETE FROM uploaded_gifts
                        WHERE title!=? AND title LIKE ?
                    """, (title_norm, f"%{title_norm}%"))

                    cur.execute("""
                        INSERT INTO uploaded_gifts (
                            gift_id, title, image_path, saved_at
                        )
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(gift_id) DO UPDATE SET
                            title=excluded.title,
                            image_path=excluded.image_path,
                            saved_at=excluded.saved_at
                    """, (
                        gift.id,
                        title_norm,
                        image_path,
                        now
                    ))

                    img_saved += 1

                except Exception as e:
                    print(f"🖼 IMAGE ERROR {title_norm}: {e}")

            if saved_count > 0:
                conn.commit()
                print(
                    f"✅ Market updated: {saved_count} item | "
                    f"🖼 Image updated: {img_saved}"
                )
            else:
                print("⚠️ Tidak ada data market yang tersimpan")

        except Exception as e:
            print("❌ Monitor error:", e)

        await asyncio.sleep(3600)

async def monitor_up():
    while True:
        try:
            now_ts = int(time.time())
            batas = now_ts - 24 * 3600  # 24 jam

            # ambil maksimal beberapa dulu biar gak berat
            cur.execute("""
                SELECT id, chat_id, msg_id 
                FROM up_messages
                WHERE created_at <= ?
                LIMIT 50
            """, (batas,))
            rows = cur.fetchall()

            if rows:
                print(f"🧹 monitor_up: menemukan {len(rows)} pesan kadaluarsa")
            for row in rows:
                row_id, chat_id, msg_id = row
                try:
                    await bot.delete_messages(chat_id, msg_id)
                except Exception as e:
                    print(f"⚠️ Gagal delete pesan up_messages id={row_id} chat={chat_id} msg={msg_id}: {e}")

                # hapus dari DB apapun hasil delete
                try:
                    cur.execute("DELETE FROM up_messages WHERE id=?", (row_id,))
                    conn.commit()
                except Exception as e:
                    print(f"⚠️ Gagal hapus row up_messages id={row_id} dari DB: {e}")

        except Exception as e:
            print(f"❌ Error di monitor_up: {e}")

        await asyncio.sleep(60)

async def _resolve_target_user(bot, raw_user: str):
    raw_user = raw_user.strip()

    # Kalau full digit -> user_id langsung
    if raw_user.isdigit():
        return int(raw_user)

    # kalau ada @ di depan, hapus
    if raw_user.startswith("@"):
        raw_user = raw_user[1:]

    try:
        ent = await bot.get_entity(raw_user)
        if isinstance(ent, (types.User,)):
            return ent.id
        # fallback kalau bukan user (channel/group)
        return None
    except Exception as e:
        print(f"⚠️ Gagal resolve user '{raw_user}': {e}")
        return None

def generate_qris_v2(amount: int):
    payload = {
        "qr_id": "42e37037-03c9-44c3-88e3-10648c2b9ff3",
        "amount": amount,
        "useUniqueCode": True,
        "packageIds": ["com.gojek.gopaymerchant"],
        "expiredInMinutes": 5,
        "qrType": "dynamic",
        "paymentMethod": "qris",
        "useQris": True
    }

    try:
        resp = requests.post(
            CASHIFY_QRIS_V2_URL,
            json=payload,
            headers=HEADERS_CASHIFY,
            timeout=15
        )
        data = resp.json()
        if resp.status_code != 200:
            return {"success": False, "error": f"HTTP {resp.status_code}: {data}"}

        if data.get("status") == 200 and "data" in data:
            return {"success": True, "data": data["data"]}
        else:
            return {"success": False, "error": f"Respon tidak valid: {data}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_status(transaction_id: str):
    payload = {"transactionId": transaction_id}

    try:
        resp = requests.post(
            CASHIFY_CHECK_STATUS_URL,
            json=payload,
            headers=HEADERS_CASHIFY,
            timeout=15
        )
        data = resp.json()
        if resp.status_code != 200:
            return {"success": False, "error": f"HTTP {resp.status_code}: {data}"}

        if data.get("status") == 200 and "data" in data:
            return {"success": True, "data": data["data"]}
        else:
            return {"success": False, "error": f"Respon tidak valid: {data}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def build_qr_image_url(qr_string: str) -> str:
    params = {
        "size": "500x500",
        "style": "2",
        "color": "ea580c",
        "data": qr_string
    }
    return f"{QR_STYLISH_URL}?{urllib.parse.urlencode(params)}"

async def monitor_deposit_qris():
    print("✅ monitor_deposit_qris berjalan...")
    tz = pytz.timezone("Asia/Jakarta")
    
    def reconnect_db():
        """Fungsi untuk reconnect database"""
        global conn, cur
        try:
            conn.close()
        except:
            pass
        
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cur = conn.cursor()
        print("✅ Database reconnected successfully")
        return conn, cur

    while True:
        try:
            # =========================
            # CEK DAN BUAT KONEKSI DATABASE JIKA TERUTUP
            # =========================
            global conn, cur
            try:
                # Test koneksi database
                cur.execute("SELECT 1")
            except Exception as db_err:
                if "closed" in str(db_err).lower() or "cannot operate" in str(db_err):
                    print("⚠️ Database connection closed, reconnecting...")
                    conn, cur = reconnect_db()
                else:
                    raise db_err

            now_ts = int(time.time())

            cur.execute("""
                SELECT id, user_id, transaction_id, amount, status, created_at, expired_at,
                       message_id, chat_id, topic_msg_id
                FROM deposit_qris
                WHERE status='pending'
            """)
            rows = cur.fetchall()

            for (row_id, user_id, transaction_id, amount, status_row,
                 created_at, expired_at, message_id, chat_id, topic_msg_id) in rows:
                
                # =========================
                # CEK EXPIRED LOKAL (BY TIME)
                # =========================
                if now_ts > expired_at:
                    try:
                        cur.execute("""
                            UPDATE deposit_qris
                            SET status='expired', last_check=?
                            WHERE id=?
                        """, (now_ts, row_id))
                        conn.commit()
                    except Exception as update_err:
                        if "closed" in str(update_err).lower():
                            print("⚠️ Database closed during update, reconnecting...")
                            conn, cur = reconnect_db()
                            # Coba lagi setelah reconnect
                            cur.execute("""
                                UPDATE deposit_qris
                                SET status='expired', last_check=?
                                WHERE id=?
                            """, (now_ts, row_id))
                            conn.commit()
                        else:
                            raise update_err

                    if message_id and chat_id:
                        try:
                            await bot.delete_messages(chat_id, message_id)
                        except Exception as e:
                            print(f"⚠️ Gagal hapus pesan QRIS expired (local) tx={transaction_id}: {e}")

                    if topic_msg_id:
                        try:
                            deposit_key = "DepositLogs"
                            if deposit_key in slug_channel_map:
                                dep_chat_id, dep_topic_id = slug_channel_map[deposit_key]

                                amount_fmt = f"Rp{amount:,}".replace(",", ".")
                                expired_local_str = datetime.now(tz).strftime("%d-%m-%Y %H:%M:%S")

                                topic_text_expired = f"""
🚫 **DEPOSIT EXPIRED TIMEOUT**

👤 **User:** [{user_id}](tg://user?id={user_id})
📄 **Transaction ID:** `{transaction_id}`
💰 **Nominal:** `{amount_fmt}`
⏱️ **Status:** EXPIRED
🕒 **Waktu:** `{expired_local_str}`

^^__Deposit ini expired karena melewati batas waktu pembayaran setelah 5 menit!.__^^
                                """.strip()

                                try:
                                    await bot.edit_message(dep_chat_id, topic_msg_id, topic_text_expired)
                                except Exception as e:
                                    if "Content of the message was not modified" in str(e):
                                        print(f"ℹ️ Topic deposit {row_id} sudah text EXPIRED(local), skip edit.")
                                    else:
                                        print(f"⚠️ Gagal edit topic_msg_id expired(local) {topic_msg_id}: {e}")
                            else:
                                print("ℹ️ slug_channel_map tidak punya key 'deposit' saat expired lokal, skip edit topic.")
                        except Exception as e:
                            print(f"⚠️ Error edit topic_msg_id expired(local) untuk tx={transaction_id}: {e}")

                    try:
                        amount_fmt = f"Rp{amount:,}".replace(",", ".")
                        msg_user = f"""
🚫 **__EXPIRED DEPOSIT REQUEST__**

**Transaction ID:** `{transaction_id}`
**Nominal:** {amount_fmt}

%%__Klik tombol dibawah ini jika anda ingin melakukan tindakan dibawah ini!__
- **💳 DEPOSIT ULANG:** Untuk melakukan deposit kembali.
- **📮 LAPORAN DEPOSIT:** Untuk laporan transaction id deposit anda yang gagal, seperti bot tidak mendeteksi qris bahwa sudah anda scan dan berhasil transfer, tindakan ini membutuhkan bukti screenshot segera persiapkan terlebih dahulu sebelum menekan tombol.%%
                        """

                        buttons = [
                            [Button.inline("💳 DEPOSIT ULANG", data="deposit")],
                            [Button.inline("📮 LAPORAN DEPOSIT", data=f"rdeposit_{transaction_id}")]
                        ]

                        await bot.send_message(
                            user_id,
                            msg_user,
                            buttons=buttons
                        )
                    except Exception as e:
                        print(f"⚠️ Gagal kirim notif expired deposit ke {user_id}: {e}")

                    continue

                # =========================
                # CEK STATUS KE API
                # =========================
                result = check_status(transaction_id)
                if not result["success"]:
                    continue

                data = result["data"]
                status_api = data.get("status", "").lower()
                now_str = datetime.now(tz).strftime("%d-%m-%Y %H:%M:%S")

                # ============ STATUS PAID ============
                if status_api == "paid":
                    try:
                        cur.execute("""
                            UPDATE deposit_qris
                            SET status='paid', paid_at=?, last_check=?
                            WHERE id=?
                        """, (now_ts, now_ts, row_id))
                        conn.commit()
                    except Exception as update_err:
                        if "closed" in str(update_err).lower():
                            print("⚠️ Database closed during paid update, reconnecting...")
                            conn, cur = reconnect_db()
                            # Coba lagi setelah reconnect
                            cur.execute("""
                                UPDATE deposit_qris
                                SET status='paid', paid_at=?, last_check=?
                                WHERE id=?
                            """, (now_ts, now_ts, row_id))
                            conn.commit()
                        else:
                            raise update_err

                    # Update user balance dengan handle reconnection
                    try:
                        cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (user_id,))
                        row_bal = cur.fetchone()
                        if row_bal is None:
                            cur.execute(
                                "INSERT INTO user_balance (user_id, balance) VALUES (?, ?)",
                                (user_id, amount)
                            )
                        else:
                            new_balance = (row_bal[0] or 0) + amount
                            cur.execute(
                                "UPDATE user_balance SET balance=? WHERE user_id=?",
                                (new_balance, user_id)
                            )
                        conn.commit()
                    except Exception as balance_err:
                        if "closed" in str(balance_err).lower():
                            print("⚠️ Database closed during balance update, reconnecting...")
                            conn, cur = reconnect_db()
                            # Coba lagi setelah reconnect
                            cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (user_id,))
                            row_bal = cur.fetchone()
                            if row_bal is None:
                                cur.execute(
                                    "INSERT INTO user_balance (user_id, balance) VALUES (?, ?)",
                                    (user_id, amount)
                                )
                            else:
                                new_balance = (row_bal[0] or 0) + amount
                                cur.execute(
                                    "UPDATE user_balance SET balance=? WHERE user_id=?",
                                    (new_balance, user_id)
                                )
                            conn.commit()
                        else:
                            raise balance_err

                    if message_id and chat_id:
                        try:
                            await bot.delete_messages(chat_id, message_id)
                        except Exception as e:
                            print(f"⚠️ Gagal hapus pesan QRIS PAID tx={transaction_id}: {e}")

                    try:
                        cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (user_id,))
                        row_bal2 = cur.fetchone()
                        saldo_fmt = f"Rp{(row_bal2[0] if row_bal2 else 0):,}".replace(",", ".")
                        amount_fmt = f"Rp{amount:,}".replace(",", ".")
                    except Exception as fetch_err:
                        if "closed" in str(fetch_err).lower():
                            print("⚠️ Database closed during fetch, reconnecting...")
                            conn, cur = reconnect_db()
                            cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (user_id,))
                            row_bal2 = cur.fetchone()
                            saldo_fmt = f"Rp{(row_bal2[0] if row_bal2 else 0):,}".replace(",", ".")
                            amount_fmt = f"Rp{amount:,}".replace(",", ".")
                        else:
                            saldo_fmt = f"Rp{amount:,}".replace(",", ".")
                            amount_fmt = f"Rp{amount:,}".replace(",", ".")

                    if topic_msg_id:
                        try:
                            deposit_key = "DepositLogs"
                            if deposit_key in slug_channel_map:
                                dep_chat_id, dep_topic_id = slug_channel_map[deposit_key]

                                topic_text_paid = f"""
✅ **DEPOSIT BERHASIL (PAID)**

👤 **User:** [{user_id}](tg://user?id={user_id})
📄 **Transaction ID:** `{transaction_id}`
💰 **Nominal:** `{amount_fmt}`
⏱️ **Status:** SUCCESS
🕒 **Waktu:** `{now_str}`
💳 **New Balance:** `{saldo_fmt}`

**__-- MARKETPLACE BY: @WINEDASH --__**
                                """.strip()

                                try:
                                    await bot.edit_message(dep_chat_id, topic_msg_id, topic_text_paid)
                                except Exception as e:
                                    if "Content of the message was not modified" in str(e):
                                        print(f"ℹ️ Topic deposit {row_id} sudah text PAID, skip edit.")
                                    else:
                                        print(f"⚠️ Gagal edit topic_msg_id PAID {topic_msg_id}: {e}")
                            else:
                                print("ℹ️ slug_channel_map tidak punya key 'deposit' saat PAID, skip edit topic.")
                        except Exception as e:
                            print(f"⚠️ Error edit topic_msg_id PAID untuk tx={transaction_id}: {e}")

                    try:
                        msg_user = f"""
✅ **DEPOSIT BERHASIL (PAID)**

📄 **Transaction ID:** `{transaction_id}`
💰 **Nominal:** `{amount_fmt}`
⏰ **Waktu:** {now_str}
💳 **Saldo anda:** `{saldo_fmt}`

^^**__Terimakasih, Deposit berhasil dan saldo anda sudah ditambahkan, klik tombol dibawah ini untuk cek saldo.__**^^
                        """.strip()

                        buttons = [
                            [Button.inline("💸 CEK SALDO", data="status")]
                        ]

                        await bot.send_message(user_id, msg_user, buttons=buttons)
                    except Exception as e:
                        print(f"⚠️ Gagal kirim notif deposit PAID ke {user_id}: {e}")

                # ============ STATUS EXPIRED DARI API ============
                elif status_api == "expired":
                    try:
                        cur.execute("""
                            UPDATE deposit_qris
                            SET status='expired', last_check=?
                            WHERE id=?
                        """, (now_ts, row_id))
                        conn.commit()
                    except Exception as update_err:
                        if "closed" in str(update_err).lower():
                            print("⚠️ Database closed during expired update, reconnecting...")
                            conn, cur = reconnect_db()
                            cur.execute("""
                                UPDATE deposit_qris
                                SET status='expired', last_check=?
                                WHERE id=?
                            """, (now_ts, row_id))
                            conn.commit()
                        else:
                            raise update_err

                    if message_id and chat_id:
                        try:
                            await bot.delete_messages(chat_id, message_id)
                        except Exception as e:
                            print(f"⚠️ Gagal hapus pesan QRIS expired(API) tx={transaction_id}: {e}")

                    if topic_msg_id:
                        try:
                            deposit_key = "DepositLogs"
                            if deposit_key in slug_channel_map:
                                dep_chat_id, dep_topic_id = slug_channel_map[deposit_key]

                                amount_fmt = f"Rp{amount:,}".replace(",", ".")
                                topic_text_expired_api = f"""
🚫 **DEPOSIT EXPIRED TIMEOUT**

👤 **User:** [{user_id}](tg://user?id={user_id})
📄 **Transaction ID:** `{transaction_id}`
💰 **Nominal:** `{amount_fmt}`
⏱️ **Status:** `EXPIRED`

^^__Deposit ini telah expired, karena pengguna tidak melakukan transfer setelah 5 menit!__^^
                                """.strip()

                                try:
                                    await bot.edit_message(dep_chat_id, topic_msg_id, topic_text_expired_api)
                                except Exception as e:
                                    if "Content of the message was not modified" in str(e):
                                        print(f"ℹ️ Topic deposit {row_id} sudah text EXPIRED(API), skip edit.")
                                    else:
                                        print(f"⚠️ Gagal edit topic_msg_id expired(API) {topic_msg_id}: {e}")
                            else:
                                print("ℹ️ slug_channel_map tidak punya key 'deposit' saat expired(API), skip edit topic.")
                        except Exception as e:
                            print(f"⚠️ Error edit topic_msg_id expired(API) untuk tx={transaction_id}: {e}")

                # ============ STATUS LAIN ============
                else:
                    try:
                        cur.execute(
                            "UPDATE deposit_qris SET last_check=? WHERE id=?",
                            (now_ts, row_id)
                        )
                        conn.commit()
                    except Exception as update_err:
                        if "closed" in str(update_err).lower():
                            print("⚠️ Database closed during last_check update, reconnecting...")
                            conn, cur = reconnect_db()
                            cur.execute(
                                "UPDATE deposit_qris SET last_check=? WHERE id=?",
                                (now_ts, row_id)
                            )
                            conn.commit()
                        else:
                            raise update_err
                    continue

            await asyncio.sleep(1)

        except Exception as e:
            print(f"❌ Error di monitor_deposit_qris: {e}")
            if "closed" in str(e).lower() or "cannot operate" in str(e).lower():
                print("🔄 Mencoba reconnect database...")
                try:
                    conn, cur = reconnect_db()
                except Exception as reconnect_err:
                    print(f"❌ Gagal reconnect database: {reconnect_err}")
            await asyncio.sleep(5)

async def monitor_ticket_session(session_id: int):
    try:
        while True:
            now_ts = int(time.time())

            cur.execute("""
                SELECT keyword_text, expire_at, max_users
                FROM ticket_sessions
                WHERE id=?
            """, (session_id,))
            row = cur.fetchone()

            if not row:
                print(f"ℹ️ ticket_session {session_id} sudah tidak ada di DB.")
                return

            keyword_text, expire_at, max_users = row

            # Hitung jumlah claim
            cur.execute("""
                SELECT COUNT(*) FROM ticket_claims
                WHERE session_id=?
            """, (session_id,))
            claimed = cur.fetchone()[0] or 0

            # Jika kuota penuh, kita bisa anggap sesi "selesai"
            if claimed >= max_users:
                print(f"✅ ticket_session {session_id} kuota penuh ({claimed}/{max_users}), auto-expired.")
                # Tidak perlu hapus row, cukup biarkan expire_at bekerja.
                return

            # Jika waktu habis, stop monitor
            if now_ts >= expire_at:
                print(f"⏰ ticket_session {session_id} waktu habis.")
                return

            await asyncio.sleep(5)
    except Exception as e:
        print(f"❌ Error monitor_ticket_session({session_id}): {e}")

def get_user_balance(user_id: int) -> int:
    cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    return int(row[0]) if row and row[0] is not None else 0

def add_user_balance(user_id: int, amount: int):
    cur.execute("""
        INSERT INTO user_balance (user_id, balance)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET balance = balance + excluded.balance
    """, (user_id, amount))
    conn.commit()

def normalize_slug(query: str):
    if not query:
        return None

    query = query.strip()

    # Tangkap slug dari berbagai bentuk URL
    m = re.search(r"(?:https?://t\.me/(?:nft/)?|t\.me/(?:nft/)?)([A-Za-z0-9\-_]+)", query, re.IGNORECASE)
    if m:
        return m.group(1).strip()

    # Tangkap dari teks biasa
    query = query.replace(" ", "").replace("#", "-")
    return query.strip()

def normalize_slug(input_text: str) -> str:
    match = re.search(r"(?:https?://)?t\.me/nft/([A-Za-z0-9_-]+)", input_text, re.IGNORECASE)
    if match:
        return match.group(1)

    clean = input_text.strip().lower()
    clean = re.sub(r"[^\w\s#-]", "", clean) 
    clean = clean.replace(" ", "")
    clean = clean.replace("#", "-")
    return clean

def parse_duration(text: str):
    text = text.strip().lower()
    match = re.match(r"(\d+)\s*(detik|menit|jam|hari|minggu|bulan|tahun)", text)
    if not match:
        # tidak cocok → return 0 (supaya tidak error)
        return 0

    jumlah, satuan = match.groups()
    jumlah = int(jumlah)

    if satuan == "detik":
        return jumlah
    elif satuan == "menit":
        return jumlah * 60
    elif satuan == "jam":
        return jumlah * 3600
    elif satuan == "hari":
        return jumlah * 86400
    elif satuan == "minggu":
        return jumlah * 604800
    elif satuan == "bulan":
        return jumlah * 2592000
    elif satuan == "tahun":
        return jumlah * 31536000
    return 0

async def monitor_owner():
    print("🕵️ Memulai monitor perpindahan owner gift (API Telegram)...")
    while True:
        try:
            cur.execute("""
                SELECT slug, api_owner_id, user_id, status_tfo, is_sold, is_listed
                FROM gifts
                WHERE slug IS NOT NULL
            """)
            gifts = cur.fetchall()

            for slug, db_api_owner_id, gift_owner, status_tfo, is_sold, is_listed in gifts:
                try:
                    if is_sold == 1 or is_listed == 0:
                        continue

                    if status_tfo == "is_sold":
                        continue

                    result = await userbot(functions.payments.GetUniqueStarGiftRequest(slug=slug))
                    gift = result.gift

                    if gift.owner_id and isinstance(gift.owner_id, types.PeerUser):
                        api_owner_id = gift.owner_id.user_id
                    else:
                        continue

                    if api_owner_id != db_api_owner_id:
                        cur.execute("UPDATE gifts SET api_owner_id=? WHERE slug=?", (api_owner_id, slug))
                        conn.commit()

                        display_name = slug.split("-")[0]
                        notif_text = f"""
🆕 **__INFORMASI GIFT ANDA BERPINDAH OWNER!__**

🎁 **Gift:** [{display_name}](https://t.me/nft/{slug})
👤 **Owner Baru (API):** [{api_owner_id}](tg://user?id={api_owner_id})

^^__Gift ini berpindah owner di luar market.  
Jika gift ini memang sudah dijual, ubah status menjadi__ **🚫 SOLD OUT** __agar data tetap akurat.__^^
                        """

                        buttons = [
                            [Button.inline("❌ SOLD OUT", data=f"sold_{slug}")]
                        ]

                        if gift_owner:
                            try:
                                await bot.send_message(gift_owner, notif_text, buttons=buttons)
                                print(f"🔔 Notifikasi dikirim ke {gift_owner} untuk gift {slug}")
                            except Exception as e:
                                print(f"⚠️ Gagal kirim notif ke {gift_owner}: {e}")

                    await asyncio.sleep(0.5)

                except Exception as e:
                    print(f"⚠️ Gagal cek gift {slug}: {e}")
                    await asyncio.sleep(1)

            await asyncio.sleep(1)

        except Exception as e:
            print(f"❌ Monitor owner error: {e}")
            await asyncio.sleep(5)

async def fetch_preview_from_webpagebot(slug: str):
    try:
        url = f"https://t.me/nft/{slug}"
        sent = await userbot.send_message("webpagebot", url)
        await asyncio.sleep(2)

        preview_msg = await userbot.get_messages("webpagebot", ids=sent.id)

        if preview_msg.web_preview and preview_msg.web_preview.photo:
            photo = preview_msg.web_preview.photo
            os.makedirs("previews", exist_ok=True)
            file_path = f"previews/{slug}.jpg"
            await userbot.download_media(photo, file_path)
            print(f"📸 Preview berhasil diambil untuk {slug}")
            return file_path
        else:
            print(f"⚠️ Tidak ada web_preview.photo untuk {slug}")
    except Exception as e:
        print(f"⚠️ Gagal ambil preview untuk {slug}: {e}")
    return None

def get_effective_user_id(sender_id):
    cur.execute("SELECT target_id FROM impersonations WHERE owner_id=?", (sender_id,))
    row = cur.fetchone()
    if row:
        return row[0]
    return sender_id

def format_slug_display(slug: str) -> str:
    parts = slug.split("-")
    name = parts[0]
    number = parts[1] if len(parts) > 1 else ""
    display_name = "".join([" " + c if c.isupper() else c for c in name]).strip()
    return f"{display_name} #{number}" if number else display_name

async def monitor_nego():
    while True:
        now = int(time.time())
        cur.execute("SELECT id, slug, user_id, created_at FROM nego_history")
        rows = cur.fetchall()
        for r in rows:
            nego_id, slug, user_id, created_at = r
            if now - created_at >= 3600:
                cur.execute("DELETE FROM nego_history WHERE id=?", (nego_id,))
                conn.commit()
                print(f"⌛ Nego {slug} dari user {user_id} otomatis expired (12 jam).")
        await asyncio.sleep(60)

async def resume_monitor_tfo():
    cur.execute("""
        SELECT slug, buyer_id, owner_id, user_id
        FROM gifts
        WHERE status_tfo='pending_tfo'
    """)
    rows = cur.fetchall()
    for slug, buyer_id, owner_id, user_id in rows:
        actual_owner = owner_id or user_id
        if buyer_id:
            asyncio.create_task(monitor_tfo(slug, buyer_id, actual_owner, None))
            print(f"♻️ Resume monitor_tfo untuk slug={slug}, buyer={buyer_id}, owner={actual_owner}")

async def monitor_tfo(slug: str, buyer_id: int, old_owner: int, pending_msg_id: int):
    slug_lower = slug.lower()
    print(f"🕵️ monitor_tfo start slug={slug} buyer={buyer_id} old_owner={old_owner}")
    
    if buyer_id is None:
        cur.execute("SELECT buyer_id FROM gifts WHERE LOWER(slug)=?", (slug_lower,))
        row = cur.fetchone()
        if row:
            buyer_id = row[0]

    start_time = datetime.now()

    while True:
        await asyncio.sleep(5)
        try:
            cur.execute("""
                SELECT id, owner_id, status_tfo,
                       model, model_rarity,
                       background, background_rarity,
                       symbol, symbol_rarity,
                       price, msg_id, pending_tfo_at, slug,
                       user_id   -- ⬅️ kita ambil juga user_id (kalau owner_id NULL)
                FROM gifts 
                WHERE LOWER(slug)=?
            """, (slug_lower,))
            row = cur.fetchone()

            if not row:
                print(f"⚠️ Gift {slug} hilang dari DB saat monitor_tfo")
                return

            (gift_id,
             db_owner_id,
             status_tfo,
             model,
             model_rarity,
             background,
             background_rarity,
             symbol,
             symbol_rarity,
             price,
             msg_id_db,
             pending_tfo_at,
             slug_db,
             user_id_db) = row

            owner_marketplace_id = db_owner_id or user_id_db

            if msg_id_db:
                pending_msg_id = msg_id_db

            if status_tfo not in ("pending_tfo", "success_tfo"):
                print(f"ℹ️ monitor_tfo slug={slug} berhenti, status_tfo={status_tfo}")
                return
              
            api_owner_id = None

            now_dt = datetime.now()
            if pending_tfo_at:
                elapsed_hours = (now_dt - datetime.fromtimestamp(pending_tfo_at)).total_seconds() / 3600
                start_dt = datetime.fromtimestamp(pending_tfo_at)
            else:
                elapsed_hours = (now_dt - start_time).total_seconds() / 3600
                start_dt = start_time

            tz = pytz.timezone("Asia/Jakarta")
            start_dt_local = start_dt.astimezone(tz) if start_dt.tzinfo else tz.localize(start_dt)
            now_dt_local = now_dt.astimezone(tz) if now_dt.tzinfo else tz.localize(now_dt)

            start_str = start_dt_local.strftime("%d-%m-%Y %H:%M:%S")
            now_str = now_dt_local.strftime("%d-%m-%Y %H:%M:%S")

            if elapsed_hours >= 12 and status_tfo == "pending_tfo":
                print(f"⌛ Gift {slug} tidak di-TFO dalam 12 jam — REFUND & UNADD.")

                harga = price or 0

                cur.execute("""
                    SELECT buyer_id, owner_id, user_id FROM gifts WHERE LOWER(slug)=?
                """, (slug_lower,))
                row = cur.fetchone()
                if row:
                    buyer_db, owner_id_db, user_id_db = row
                    buyer_id = buyer_db
                    owner_id = owner_id_db or user_id_db

                cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (buyer_id,))
                row_bal = cur.fetchone()
                buyer_balance = row_bal[0] if row_bal else 0
                new_balance = buyer_balance + harga

                if row_bal is None:
                    cur.execute(
                        "INSERT INTO user_balance (user_id, balance) VALUES (?, ?)",
                        (buyer_id, new_balance)
                    )
                else:
                    cur.execute(
                        "UPDATE user_balance SET balance=? WHERE user_id=?",
                        (new_balance, buyer_id)
                    )
                conn.commit()

                cur.execute("""
                    UPDATE gifts
                    SET user_id=NULL,
                        buyer_id=NULL,
                        status_tfo=NULL,
                        is_listed=0,
                        is_sold=0
                    WHERE id=?
                """, (gift_id,))
                conn.commit()

                try:
                    cur.execute("DELETE FROM pending_transfers WHERE slug=?", (slug_db,))
                    conn.commit()
                except Exception as e:
                    print(f"⚠️ Gagal hapus dari pending_transfers: {e}")

                slug_link = slug_db
                slug_text = slug_db.replace("-", " #")
                gift_link = f"https://t.me/nft/{slug_link}"

                harga_fmt = f"Rp{(harga or 0):,}".replace(",", ".")
                new_balance_fmt = f"Rp{new_balance:,}".replace(",", ".")

                try:
                    buyer = await bot.get_entity(buyer_id)
                    buyer_username = f"@{buyer.username}" if buyer.username else f"[{buyer.id}](tg://user?id={buyer.id})"
                    buyer_mention = f"[{buyer.first_name}](tg://user?id={buyer.id})"
                except Exception:
                    buyer_username = f"`{buyer_id}`"
                    buyer_mention = f"`{buyer_id}`"

                try:
                    owner_ent = await bot.get_entity(old_owner)
                    owner_username = f"@{owner_ent.username}" if owner_ent.username else f"[{owner_ent.id}](tg://user?id={owner_ent.id})"
                    owner_mention = f"[{owner_ent.first_name}](tg://user?id={owner_ent.id})"
                except Exception:
                    owner_username = f"`{old_owner}`"
                    owner_mention = f"`{old_owner}`"

                text_buyer = f"""
[⌛]({gift_link}) **__TRANSACTION EXPIRED TFO TIMEOUT__**

🎁 **Gift:** {slug_text}
✨ **Model:** {model or '-'} ({model_rarity or '-'})
🖼️ **Background:** {background or '-'} ({background_rarity or '-'})
👾 **Symbol:** {symbol or '-'} ({symbol_rarity or '-'})
💸 **Price:** {harga_fmt}
📅 **Time buy:** `{start_str}`
📅 **Time now:** `{now_str}`
💳 **New Balance:** `{new_balance_fmt}`

^^⚠️ Owner gift tidak melakukan TFO dalam waktu 12 jam. Transaksi otomatis dibatalkan dan saldo kamu sudah dikembalikan ke akun marketplace.^^
                """.strip()

                text_owner = f"""
[⚠️]({gift_link}) **__TFO GIFT TIMEOUT & GIFT DI-UNADD!__**

🎁 **Gift:** {slug_text}
✨ **Model:** {model or '-'} ({model_rarity or '-'})
🖼️ **Background:** {background or '-'} ({background_rarity or '-'})
👾 **Symbol:** {symbol or '-'} ({symbol_rarity or '-'})
💸 **Price:** {harga_fmt}
📅 **Time buy:** `{start_str}`
📅 **Time now:** `{now_str}`

%%__Anda tidak melakukan TFO dalam waktu 12 jam. Transaksi dibatalkan, saldo buyer dikembalikan dan gift sudah otomatis di-UNADD (tidak lagi tercatat sebagai titipan), jika anda ingin menitipkan gift kembali maka segera hubungi admin.__%%
                """.strip()

                text_admin = f"""
🚨 **GIFT TIMEOUT TFO TO BUYER**

[🎁 Gift]({gift_link}): {slug_text}
✨ **Model:** {model or '-'} ({model_rarity or '-'})
🖼️ **Background:** {background or '-'} ({background_rarity or '-'})
👾 **Symbol:** {symbol or '-'} ({symbol_rarity or '-'})
💸 **Price:** {harga_fmt}

**BUYER GIFT**
🆔 `{buyer_id}`
👤 {buyer_mention}
🪪 {buyer_username}

**OWNER GIFT**
🆔 `{old_owner}`
👤 {owner_mention}
🪪 {owner_username}

📅 **Time buy:** `{start_str}`
📅 **Time now:** `{now_str}`

^^__Gift telah di unadd dari titipan WINEDASH karena terkena pelanggaran peraturan WINEDASH, gift sudah berhasil di un-add dari list titipan!__^^
                """.strip()

                await delete_all_tfo_messages(slug)

                try:
                    if pending_msg_id:
                        await bot.delete_messages(CHANNEL_PENDING, pending_msg_id)
                except Exception as e:
                    print(f"⚠️ Gagal hapus pesan pending: {e}")

                try:
                    await bot.send_message(buyer_id, text_buyer)
                except Exception as e:
                    print(f"⚠️ Gagal kirim notif ke buyer {buyer_id}: {e}")

                try:
                    await bot.send_message(old_owner, text_owner)
                except Exception as e:
                    print(f"⚠️ Gagal kirim notif ke owner {old_owner}: {e}")

                try:
                    await bot.send_message(GROUP_ADMIN, text_admin)
                except Exception as e:
                    print(f"⚠️ Gagal kirim notif ke group admin: {e}")
                    
                try:
                    await bot.send_message(CHANNEL_PENDING, text_admin)
                except Exception as e:
                    print(f"⚠️ Gagal kirim notif ke channel pending: {e}")
                return

            if status_tfo == "pending_tfo":
                try:
                    result_api = await userbot(functions.payments.GetUniqueStarGiftRequest(slug=slug))
                    gift_api = result_api.gift
                
                    if gift_api.owner_id and isinstance(gift_api.owner_id, types.PeerUser):
                        api_owner_id = gift_api.owner_id.user_id
            
                except Exception as e:
                    print(f"⚠️ Gagal cek owner API untuk {slug}: {e}")
                    continue
            
            if api_owner_id == buyer_id and status_tfo == "pending_tfo":
                cur.execute("""
                    UPDATE gifts
                    SET status_tfo='success_tfo',
                        api_owner_id=?
                    WHERE id=?
                """, (api_owner_id, gift_id))
                conn.commit()
            
                print(f"✅ API CONFIRM → {slug} ditandai success_tfo")
                continue

            if status_tfo == "success_tfo":
                print(f"🚀 EXECUTE TFO FROM DB for {slug}")

                base_price = price or 0
            
                if base_price > 0 and owner_marketplace_id:
                    cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (owner_marketplace_id,))
                    row_owner_bal = cur.fetchone()
                    owner_balance = row_owner_bal[0] if row_owner_bal else 0
            
                    new_owner_balance = owner_balance + base_price
            
                    if row_owner_bal is None:
                        cur.execute(
                            "INSERT INTO user_balance (user_id, balance) VALUES (?, ?)",
                            (owner_marketplace_id, new_owner_balance)
                        )
                    else:
                        cur.execute(
                            "UPDATE user_balance SET balance=? WHERE user_id=?",
                            (new_owner_balance, owner_marketplace_id)
                        )
                    conn.commit()
            
                    print(f"💰 Saldo owner {owner_marketplace_id} +{base_price} (harga asli)")
                    await process_referral_bonus(buyer_id, base_price)
            
                cur.execute("""
                    UPDATE gifts
                    SET status_tfo='done_tfo',
                        is_sold=1,
                        is_listed=0
                    WHERE id=?
                """, (gift_id,))
                conn.commit()
                
                print(f"✅ Gift {slug} berhasil TFO ke buyer {buyer_id}")
            
                await delete_all_tfo_messages(slug)

                cur.execute("""
                    SELECT slug, model, model_rarity, background, background_rarity, 
                           symbol, symbol_rarity, price 
                    FROM gifts WHERE id=?
                """, (gift_id,))
                gift = cur.fetchone()
                if gift:
                    (slug_db2, model2, model_r2, background2, background_r2,
                     symbol2, symbol_r2, price2) = gift

                    slug_link2 = slug_db2
                    slug_text2 = slug_db2.replace("-", " #")
                    gift_link2 = f"https://t.me/nft/{slug_link2}"

                    try:
                        buyer2 = await bot.get_entity(buyer_id)
                        buyer_username2 = f"@{buyer2.username}" if buyer2.username else f"[{buyer2.id}](tg://user?id={buyer2.id})"
                    except Exception:
                        buyer_username2 = f"`{buyer_id}`"

                    try:
                        owner2 = await bot.get_entity(owner_marketplace_id)
                        owner_username2 = f"@{owner2.username}" if owner2.username else f"[{owner2.id}](tg://user?id={owner2.id})"
                    except Exception:
                        owner_username2 = f"`{owner_marketplace_id}`"

                    harga_fmt2 = f"Rp{(price2 or 0):,}".replace(",", ".")
                    owner_balance_fmt = None

                    try:
                        cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (owner_marketplace_id,))
                        row_owner_bal2 = cur.fetchone()
                        if row_owner_bal2:
                            owner_balance_fmt = f"Rp{row_owner_bal2[0]:,}".replace(",", ".")
                    except Exception:
                        owner_balance_fmt = None

                    text_buyer = f"""
[✅]({gift_link2}) **__SUCCESSFULLY TRANSFER OWNERSHIP!__**

🎁 **Gift:** {slug_text2}
✨ **Model:** {model2 or '-'} ({model_r2 or '-'})
🖼️ **Backdrop:** {background2 or '-'} ({background_r2 or '-'})
👾 **Symbol:** {symbol2 or '-'} ({symbol_r2 or '-'})
💸 **Price:** {harga_fmt2}

^^**__Gift sudah ada di akun anda, transaksi pembelian selesai dan Terimakasih sudah menggunakan jasa kami!__**^^
                    """.strip()

                    text_owner = f"""
[💰]({gift_link2}) **__GIFT BERHASIL DI TFO & BALANCE DITAMBAHKAN!__**

🎁 **Gift:** {slug_text2}
💸 **Price:** {harga_fmt2}
🧾 **Status:** __SUCCESS__
{f"💳 **New Balance:** `{owner_balance_fmt}`" if owner_balance_fmt else ""}

^^**__Gift berhasil di TFO ke buyer, dan balance sudah kami tambahkan ke akun anda. Terimakasih sudah menggunakan jasa kami!__**^^
                    """.strip()

                    text_channel = f"""
🎁 **GIFT SOLD OUT!**

^^🔖 **Gift:** [{slug_text2}]({gift_link2})
✨ **Model:** {model2 or '-'} ({model_r2 or '-'})
🖼️ **Backdrop:** {background2 or '-'} ({background_r2 or '-'})
👾 **Symbol:** {symbol2 or '-'} ({symbol_r2 or '-'})^^

💰 **PRICE:** {harga_fmt2}
                    """.strip()

                    try:
                        if "GiftSoldOut" in slug_channel_map:
                            topic_chat_id, topic_msg_id = slug_channel_map["GiftSoldOut"]

                            topic_text = f"""
[🚫]({gift_link2}) **GIFT SOLD OUT BY @WINEDASH**

^^🎁 **Gift:** {slug_text2}
✨ **Model:** {model2 or '-'} ({model_r2 or '-'})
🖼️ **Backdrop:** {background2 or '-'} ({background_r2 or '-'})
👾 **Symbol:** {symbol2 or '-'} ({symbol_r2 or '-'})
👤 **Buyer:** {buyer_username2}
👤 **Seller:** {owner_username2}^^

💸 **Price:** {harga_fmt2}
                            """.strip()

                            await bot.send_message(
                                topic_chat_id,
                                topic_text,
                                reply_to=topic_msg_id
                            )
                            print(f"📣 Notif GiftSoldOut dikirim ke topic untuk {slug_db2}")
                        else:
                            print("ℹ️ Key 'GiftSoldOut' tidak ditemukan di slug_channel_map, skip notif topic.")
                    except Exception as e:
                        print(f"⚠️ Gagal kirim notif GiftSoldOut ke topic: {e}")

                    try:
                        if pending_msg_id:
                            await bot.delete_messages(CHANNEL_PENDING, pending_msg_id)
                    except Exception as e:
                        print(f"⚠️ Gagal hapus pesan pending: {e}")

                    try:
                        await bot.send_message(CHANNEL_PENDING, text_channel, link_preview=True)
                    except Exception as e:
                        print(f"⚠️ Gagal kirim notif channel: {e}")

                    try:
                        await bot.send_message(buyer_id, text_buyer, link_preview=False)
                    except Exception as e:
                        print(f"⚠️ Gagal kirim ke buyer {buyer_id}: {e}")

                    try:
                        await bot.send_message(owner_marketplace_id, text_owner, link_preview=False)
                    except Exception as e:
                        print(f"⚠️ Gagal kirim ke owner {owner_marketplace_id}: {e}")

                return

        except Exception as e:
            print(f"❌ Error monitor_tfo {slug}: {e}")
            return

async def get_topic_entry_msg_id(chat_id: int, topic_id: int) -> int:
    try:
        res = await bot.get_messages(chat_id, ids=topic_id)
        if res:
            return res.id
    except Exception as e:
        print(f"⚠️ Gagal ambil entry msg_id untuk topic {topic_id} di {chat_id}: {e}")
    return None


def format_rarity(rarity):
    if rarity is None:
        return "N/A"
    percentage = rarity / 10
    return f"{int(percentage)}%" if percentage.is_integer() else f"{percentage:.1f}%"

def slug_to_slugbuy(slug: str) -> str:
    if "-" in slug:
        parts = slug.split("-")
        return parts[0] + "_" + parts[1]
    return slug.replace("-", "_")

def slugbuy_to_slug(slugbuy: str) -> str:
    """
    Ubah slug_buy dari JellyBunny_123 → JellyBunny-123
    """
    if "_" in slugbuy:
        parts = slugbuy.split("_")
        return parts[0] + "-" + parts[1]
    return slugbuy.replace("_", "-")

async def fetch_gift_data(slug):
    try:
        result = await userbot(functions.payments.GetUniqueStarGiftRequest(slug=slug))
        gift = result.gift

        model, model_rarity = None, None
        background, background_rarity = None, None
        symbol, symbol_rarity = None, None
        original_details = "No Minus"

        for attr in gift.attributes:
            if isinstance(attr, StarGiftAttributeModel):
                model = attr.name
                model_rarity = format_rarity(getattr(attr, "rarity_permille", None))
            elif isinstance(attr, StarGiftAttributeBackdrop):
                background = attr.name
                background_rarity = format_rarity(getattr(attr, "rarity_permille", None))
            elif isinstance(attr, StarGiftAttributePattern):
                symbol = attr.name
                symbol_rarity = format_rarity(getattr(attr, "rarity_permille", None))
            elif isinstance(attr, StarGiftAttributeOriginalDetails):
                original_details = "Minus"

        availability_issued = getattr(gift, "availability_issued", 0)
        availability_total = getattr(gift, "availability_total", "N/A")

        return {
            "slug": slug,
            "model": model,
            "model_rarity": model_rarity,
            "background": background,
            "background_rarity": background_rarity,
            "symbol": symbol,
            "symbol_rarity": symbol_rarity,
            "original_details": original_details,
            "availability_issued": availability_issued,
            "availability_total": availability_total
        }

    except Exception as e:
        logging.error(f"❌ Gagal ambil data gift {slug}: {e}")
        return None

async def get_ton_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=idr,usd,rub"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                data = await resp.json()
                ton_data = data.get("the-open-network", {})
                idr = ton_data.get("idr", 0)
                usd = ton_data.get("usd", 0)
                rub = ton_data.get("rub", 0)
                return idr, usd, rub
        except Exception as e:
            print(f"⚠️ Gagal mengambil harga TON: {e}")
            return 0, 0, 0

# Handle perintah /coingecko {ton}
@userbot.on(events.NewMessage(pattern=r'^/coingecko\s+([\d.]+)'))
async def coingecko_price_handler(event):
    try:
        ton_amount = float(event.pattern_match.group(1))

        idr_price, usd_price, rub_price = await get_ton_price()

        if idr_price == 0 and usd_price == 0 and rub_price == 0:
            return await event.reply("⚠️ Gagal mengambil harga TON dari CoinGecko.")

        # Kalikan harga dengan jumlah TON
        total_idr = idr_price * ton_amount
        total_usd = usd_price * ton_amount
        total_rub = rub_price * ton_amount

        msg = (f"💰 Harga untuk {ton_amount} TON:\n"
               f"- Rp {total_idr:,.0f}\n"
               f"- $ {total_usd:,.2f}\n"
               f"- ₽ {total_rub:,.2f}")

        await event.reply(msg)

    except Exception as e:
        print(f"⚠️ Error pada handle /coingecko: {e}")
        await event.reply("❌ Terjadi kesalahan saat memproses perintah.")

@bot.on(events.NewMessage(pattern=r"^/info\s+(.+)"))
async def impersonate_user(event):
    if event.sender_id not in OWNER_ID:
        return await event.reply("🚫 Anda tidak memiliki izin untuk menggunakan perintah ini.")

    arg = event.pattern_match.group(1).strip()

    target_id = None
    target_username = None

    if arg.startswith("@"):
        username = arg[1:]
        cur.execute("SELECT user_id FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        if row:
            target_id = row[0]
            target_username = username
    else:
        try:
            target_id = int(arg)
            cur.execute("SELECT username FROM users WHERE user_id=?", (target_id,))
            row = cur.fetchone()
            if row:
                target_username = row[0]
        except:
            return await event.reply("❌ Format user_id tidak valid.")

    if not target_id:
        return await event.reply("❌ User tidak ditemukan di database.")

    cur.execute("""
        INSERT OR REPLACE INTO impersonations (owner_id, target_id)
        VALUES (?, ?)
    """, (event.sender_id, target_id))
    conn.commit()

    await event.reply(
        f"✅ Sekarang kamu impersonasi sebagai user **{target_username or target_id}**.\n"
        f"Semua perintah akan berjalan seolah-olah dari user ini."
    )

@bot.on(events.NewMessage(pattern=r"^/keluar\s+(.+)"))
async def keluar_impersonasi(event):
    if event.sender_id not in OWNER_ID:
        return

    arg = event.pattern_match.group(1).strip()

    target_id = None
    if arg.startswith("@"):
        username = arg[1:]
        cur.execute("SELECT user_id FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        if row:
            target_id = row[0]
    else:
        try:
            target_id = int(arg)
        except:
            return await event.reply("❌ Format user_id tidak valid.")

    cur.execute("DELETE FROM impersonations WHERE owner_id=? AND target_id=?", (event.sender_id, target_id))
    conn.commit()

    await event.reply(f"🚪 Keluar dari impersonasi user {arg}. Kembali sebagai OWNER.")

@bot.on(events.NewMessage(pattern=r"^/chat (\d+)$"))
async def chat_forward_handler(event):
    try:
        target_id = int(event.pattern_match.group(1))
        reply = await event.get_reply_message()

        if not reply:
            return await event.reply("⚠️ Harus membalas pesan yang ingin dikirim!\n\nContoh:\n`/chat 7998861975` (reply ke pesan)")

        fwd = await reply.forward_to(target_id)

        # Konfirmasi sukses
        await event.reply(f"✅ Pesan berhasil diteruskan ke pengguna dengan ID `{target_id}`.", link_preview=False)

    except Exception as e:
        await event.reply(f"❌ Gagal meneruskan pesan:\n`{e}`")

@bot.on(events.NewMessage(pattern=r"^/print\s+(.+)$"))
async def cmd_print_nft(event):
    text = event.pattern_match.group(1).strip()

    match = GIFT_LINK_PATTERN.match(text)
    if match:
        slug = match.group(1)
        try:
            result = await userbot(functions.payments.GetUniqueStarGiftRequest(slug=slug))
            gift = getattr(result, "gift", None)
            if not gift:
                return await event.reply("❌ Gift tidak ditemukan.")
            gift_address = getattr(gift, "gift_address", None)
            if not gift_address:
                return await event.reply("🚫 Gift tidak memiliki gift_address.")
            target = gift_address
        except Exception as e:
            return await event.reply(f"❌ Gagal ambil gift address:\n`{e}`")
    else:
        target = text

    async with aiohttp.ClientSession() as session:
        nft_url = f"https://tonapi.io/v2/nfts/{target}"
        async with session.get(nft_url) as resp:
            if resp.status != 200:
                return await event.reply(f"❌ Gagal ambil data dari TonAPI ({resp.status})")
            nft_data = await resp.json()

    owner = nft_data.get("owner") or {}
    is_wallet = owner.get("is_wallet", True)
    owner_address = owner.get("address", "Tidak diketahui")

    if is_wallet:
        msg = (
            "✅ **Gift ini berada di blockchain pengguna yang melakukan contract!**\n"
            "**-- Masih dipegang oleh pemilik aslinya. --**\n\n"
            f"💼 **Wallet Pemilik Asli:**\nhttps://tonscan.org/address/{owner_address}"
        )
    else:
        msg = (
            "❌ **Gift ini sedang berada di blockchain lain atau profil pengguna lain.**\n"
            "**-- Sudah tidak dipegang oleh pemilik aslinya. --**\n\n"
            f"💼 **Wallet Pemilik Saat Ini:**\nhttps://tonscan.org/address/{owner_address}"
        )

    await event.reply(msg, parse_mode="md")
    await logs.send_message(CHLOGS, f"{user_id} menggunakan perintah `/print {text}`")

@bot.on(events.NewMessage(pattern=r"^/scan$", from_users=OWNER_ID))
async def scan_all_gift_links(event):
    try:
        await event.respond("🔍 Sedang memindai seluruh pesan di channel... Mohon tunggu beberapa saat.")

        channel_id = CHAT_SCAN_ID
        entity = await userbot.get_entity(PeerChannel(channel_id))

        offset_id = 0
        total_found = 0
        total_new = 0

        while True:
            history = await userbot(GetHistoryRequest(
                peer=entity,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=100,
                max_id=0,
                min_id=0,
                hash=0
            ))

            messages = history.messages
            if not messages:
                break

            for msg in messages:
                if not msg.message:
                    continue

                matches = LINK_PATTERN.findall(msg.message)
                if not matches:
                    continue

                for slug in matches:
                    total_found += 1

                    cur.execute("SELECT 1 FROM gift_scanned WHERE slug=?", (slug,))
                    if cur.fetchone():
                        continue

                    text_content = msg.message.strip() if msg.message else ""
                    cur.execute(
                        "INSERT INTO gift_scanned (slug, message_id, text) VALUES (?, ?, ?)",
                        (slug, msg.id, text_content)
                    )
                    conn.commit()
                    total_new += 1

            offset_id = messages[-1].id

        await event.respond(f"""
✅ **Scan selesai!**
📦 Total gift ditemukan: `{total_found}`
🆕 Tersimpan baru: `{total_new}`
💬 Dari chat: `{channel_id}`
        """)

    except Exception as e:
        print(f"⚠️ Error di /scan: {e}")
        await event.respond(f"⚠️ Gagal melakukan scan.\n**Error:** `{e}`")

@bot.on(events.NewMessage(pattern=r"^/cek(?:\s+(.+))?$"))
async def cek_gift(event):
    user_id = event.sender_id
    query = event.pattern_match.group(1)

    if not query:
        await event.reply("❌ Gunakan format: `/cek <slug atau link gift>`", parse_mode="markdown")
        return

    slug = normalize_slug(query)
    if not slug:
        await event.reply("⚠️ Tidak dapat mengenali slug dari input kamu.", parse_mode="markdown")
        await logs.send_message(CHLOGS, f"{user_id} menggunakan perintah `/cek {query}`")
        return

    try:
        cur.execute("SELECT message_id, text FROM gift_scanned WHERE slug=?", (slug,))
        row = cur.fetchone()

        if not row:
            await event.reply(f"⚠️ Gift https://t.me/nft/{slug} tidak kotor!")
            return

        msg_id, text_content = row
        channel_link = f"https://t.me/c/{str(CHAT_SCAN_ID)[4:]}/{msg_id}"

        buttons = [[Button.url("🔗 LIHAT DI CHANNEL", channel_link)]]
        await event.reply(f"**🔴 GIFT INI HASIL PENIPUAN!**\n\n{text_content}", buttons=buttons, link_preview=False)
        await logs.send_message(CHLOGS, f"{user_id} menggunakan perintah `/cek {query}`")

    except Exception as e:
        print(f"⚠️ Error di /cek: {e}")
        await event.reply(f"⚠️ Terjadi kesalahan: `{e}`", parse_mode="markdown")

@bot.on(events.NewMessage(pattern=r"^/cari$", from_users=OWNER_ID))
async def cari_gift_penipu(event):
    """
    /cari
    Ambil semua slug gift penipu dari tabel gift_scanned (hasil /scan),
    lalu untuk tiap slug: cari di GROUP CHANNEL_CARI apakah slug itu pernah dipromosikan.
    Kalau ketemu, balikin list link ke pesan-pesan di group tersebut.
    """
    try:
        await event.respond("🔍 Sedang mencari gift penipu yang dipromosikan di GROUP_CARI berdasarkan slug di database...")

        # 1. Ambil semua slug penipu dari database
        cur.execute("SELECT slug FROM gift_scanned")
        rows = cur.fetchall()
        if not rows:
            await event.respond("⚠️ Belum ada data gift penipu di database (tabel gift_scanned kosong).")
            return

        bad_slugs = sorted({row[0] for row in rows})  # set → list terurut biar rapi
        if not bad_slugs:
            await event.respond("⚠️ Tidak ada slug gift penipu yang tersimpan.")
            return

        # 2. Ambil entity GROUP_CARI
        try:
            entity = await userbot.get_entity(CHANNEL_CARI)
        except Exception as e:
            await event.respond(
                "❌ userbot **tidak bisa get_entity GROUP_CARI**.\n"
                "Pastikan userbot sudah JOIN group tersebut dan CHANNEL_CARI benar.\n\n"
                f"Error: `{e}`"
            )
            return

        group_short_id = str(CHANNEL_CARI)[4:]  # untuk t.me/c/xxxx
        found_links = []  # simpan (slug, msg_id)

        # 3. Untuk SETIAP slug, cari di GROUP_CARI
        for slug in bad_slugs:
            query_text = f"https://t.me/nft/{slug}"

            try:
                search = await userbot(SearchRequest(
                    peer=entity,
                    q=query_text,
                    filter=InputMessagesFilterEmpty(),
                    min_date=None,
                    max_date=None,
                    offset_id=0,
                    add_offset=0,
                    limit=50,   # kalau ada banyak, ambil sampai 50 pesan per slug
                    max_id=0,
                    min_id=0,
                    hash=0
                ))
            except Exception as e:
                # Kalau cari slug ini error, skip tapi log
                print(f"⚠️ Error search slug {slug} di GROUP_CARI: {e}")
                continue

            for msg in search.messages:
                found_links.append((slug, msg.id))

        # 4. Susun hasil
        if not found_links:
            await event.respond("✅ Tidak ditemukan gift penipu (berdasarkan slug di DB) yang sedang dipromosikan di GROUP_CARI.")
            return

        # Buat list link dengan format:
        # TOTAL: X
        # LIST: [1](link1), [2](link2), ...
        links = []
        for idx, (slug, mid) in enumerate(found_links, start=1):
            url = f"https://t.me/c/{group_short_id}/{mid}"
            # Bisa ditambah info slug di teks kalau mau
            links.append(f"[{idx} - `{slug}`]({url})")

        reply_text = (
            "✅ **BERHASIL MENEMUKAN GIFT PENIPU DI GROUP_CARI!**\n\n"
            f"TOTAL PESAN: `{len(found_links)}`\n"
            f"LIST: {', '.join(links)}"
        )

        await event.respond(reply_text, link_preview=False)

    except Exception as e:
        print(f"⚠️ Error di /cari: {e}")
        await event.respond(f"⚠️ Gagal melakukan pencarian di GROUP_CARI.\n**Error:** `{e}`")

@bot.on(events.NewMessage(pattern=r"^/bc$"))
async def broadcast(event):
    if event.sender_id != 7998861975:
        return await event.reply("❌ Kamu tidak diizinkan menggunakan perintah ini.")

    if not event.is_reply:
        return await event.reply("❗ Balas pesan yang ingin dikirim ke semua pengguna dengan perintah /bc")

    replied_msg = await event.get_reply_message()

    cur.execute("SELECT user_id FROM users")
    rows = cur.fetchall()

    if not rows:
        return await event.reply("❌ Tidak ada pengguna yang terdaftar di database.")

    user_ids = [row[0] for row in rows]

    sent = 0
    failed = 0
    total = len(user_ids)

    status = await event.reply(f"📣 Memulai broadcast ke {total} pengguna...\n\n🔄 Loading ………… 0%\n💬 Send: [0/{total}]")

    for index, uid in enumerate(user_ids, start=1):
        try:
            await replied_msg.forward_to(uid)
            sent += 1
        except Exception as e:
            print(f"[ERROR] Gagal kirim ke {uid}: {e}")
            failed += 1

        if sent % 50 == 0 or index == total:
            percent = int((sent / total) * 100)

            bar_length = 20
            filled = int(bar_length * percent / 100)
            bar = "I" * filled + "·" * (bar_length - filled)

            try:
                await status.edit(
                    f"🔄 Loading {bar}…….. {percent}%\n"
                    f"💬 Send: [{sent}/{total}]\n\n"
                    f"👥 Total: {total}\n🟢 Sukses: {sent}\n🔴 Gagal: {failed}"
                )
            except:
                pass

        await asyncio.sleep(0.5)

    try:
        await status.edit(
            f"✅ **Broadcast selesai!**\n\n"
            f"👥 Total: {total}\n🟢 Terkirim: {sent}\n🔴 Gagal: {failed}\n\n"
            f"🎯 Selesai 100%!"
        )
    except:
        pass

@bot.on(events.NewMessage(pattern=r"^/save$"))
async def cmd_save_offer_item(event):
    user_id = event.sender_id

    if user_id not in OWNER_ID and user_id not in ADMIN_ID:
        await event.reply("🚫 Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    if not event.is_reply:
        return await event.reply("⚠️ Gunakan /save dengan cara **reply** ke pesan format offer.")

    reply = await event.get_reply_message()
    raw = (reply.raw_text or "").strip()

    m_offer = RE_OFFER_ID.search(raw)
    if not m_offer:
        return await event.reply("🚫 Tidak menemukan `offer_id`.\nPastikan format: `Format offer #OfferID`.")
    offer_id = m_offer.group(1).strip()

    cur.execute("""
        SELECT end_at, status
        FROM gift_offer
        WHERE offer_id=?
    """, (offer_id,))
    row = cur.fetchone()
    if not row:
        return await event.reply(f"🚫 `offer_id` `{offer_id}` tidak ditemukan di database gift_offer.")

    end_at, status = row
    now_ts = int(time.time())
    if now_ts >= end_at or status != "active":
        return await event.reply(f"⚠️ Offer `{offer_id}` sudah **expired** atau tidak aktif.")

    cur.execute("""
        SELECT COUNT(*) FROM gift_offer_items
        WHERE offer_id = ?
    """, (offer_id,))
    cnt = cur.fetchone()[0] or 0
    if cnt >= 10:
        return await event.reply(
            f"⚠️ Offer `{offer_id}` sudah memiliki 10 data gift.\n"
            f"Tidak bisa menambah lagi."
        )

    m_user = RE_USERNAME.search(raw)
    if not m_user:
        return await event.reply("🚫 Tidak menemukan `Username:`.\nContoh: `• Username: @ftamous`.")
    owner_username = m_user.group(1).strip()

    m_link = RE_LINK.search(raw)
    if not m_link:
        return await event.reply("🚫 Tidak menemukan `Link gift:`.\nContoh: `• Link gift: https://t.me/nft/JellyBunny-123`.")
    link_gift = m_link.group(1).strip()

    slug = None
    m_slug = re.search(r"/nft/([A-Za-z0-9_-]+)", link_gift)
    if m_slug:
        slug = m_slug.group(1).strip()

    if not slug:
        return await event.reply(
            "🚫 Link gift tidak mengandung `/nft/{slug}` yang valid.\n"
            "Contoh: `https://t.me/nft/JellyBunny-123`."
        )

    m_bid = RE_START_BID.search(raw)
    if not m_bid:
        return await event.reply(
            "🚫 Tidak menemukan `Start bid:`.\n"
            "Contoh: `• Start bid: 10.000`."
        )
    start_bid_str = m_bid.group(1).strip()

    try:
        start_bid = parse_dot_price(start_bid_str)
    except Exception:
        return await event.reply(
            "🚫 Format `Start bid` tidak valid.\n"
            "Wajib pakai titik, contoh: `10.000` atau `100.000`."
        )

    try:
        cur.execute("""
            INSERT INTO gift_offer_items (offer_id, owner_username, slug, start_bid, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (offer_id, owner_username, slug, start_bid, now_ts))
        conn.commit()
    except Exception as e:
        print(f"❌ Error insert gift_offer_items: {e}")
        return await event.reply("❌ Gagal menyimpan data gift offer ke database.")

    start_bid_fmt = f"Rp{start_bid:,}".replace(",", ".")

    msg = f"""
✅ **GIFT OFFER `{offer_id}` (`{cnt+1}/10`)**
    """.strip()

    await event.reply(msg, parse_mode="markdown")

@bot.on(events.NewMessage(pattern=r"^/sendoffer\s+([A-Za-z0-9]+)$"))
async def cmd_sendoffer(event):
    user_id = event.sender_id

    if user_id not in OWNER_ID and user_id not in ADMIN_ID:
        return await event.reply("🚫 Anda tidak memiliki izin untuk mengirim gift offer.")

    offer_id = event.pattern_match.group(1).strip()

    cur.execute("""
        SELECT mode, end_at, status
        FROM gift_offer
        WHERE offer_id=?
    """, (offer_id,))
    row = cur.fetchone()

    if not row:
        return await event.reply(f"🚫 Offer ID `{offer_id}` tidak ditemukan di database `gift_offer`.")

    mode, end_at, status = row
    now_ts = int(time.time())

    if status != "active":
        return await event.reply(
            f"⚠️ Offer `{offer_id}` tidak berstatus **active** (status sekarang: `{status}`)."
        )

    cur.execute("""
        SELECT owner_username, slug, start_bid
        FROM gift_offer_items
        WHERE offer_id=?
        ORDER BY id ASC
    """, (offer_id,))
    items = cur.fetchall()

    if not items:
        return await event.reply(
            f"⚠️ Belum ada gift yang disimpan untuk Offer `{offer_id}`.\n"
            f"Gunakan `/save` (reply ke format) untuk menambah gift."
        )

    if mode == "oc":
        header_title = "🎁 ON OFFER CANCEL"
        mode_label = "OFFER CANCEL"
    elif mode == "onc":
        header_title = "🎁 ON OFFER NO CANCEL"
        mode_label = "OFFER NO CANCEL"
    else:
        header_title = "🎁 ON OFFER"
        mode_label = "OFFER"

    tz = pytz.timezone("Asia/Jakarta")
    dt_end = datetime.fromtimestamp(end_at, tz)
    end_str = dt_end.strftime("%d.%m.%Y %H:%M:%S")

    index = 1
    for owner_username, slug, start_bid in items:
        if not owner_username.startswith("@"):
            owner_username_fmt = f"@{owner_username}"
        else:
            owner_username_fmt = owner_username

        start_bid_fmt = f"Rp{start_bid:,}".replace(",", ".")
        link = f"https://t.me/nft/{slug}"

        text = f"""
{header_title}

🆔 Offer ID: `{offer_id}`
📛 Mode: **{mode_label}**
⏰ End offer: `{end_str}`

👤 Owner: {owner_username_fmt}
🎁 Gift: [{slug}]({link})
💰 Start bid: `{start_bid_fmt}`

({index}/{len(items)})
        """.strip()

        try:
            result = await userbot(functions.payments.GetUniqueStarGiftRequest(slug=slug))
            gift = result.gift

            model_doc = None
            bg_doc = None
            mime_type = None

            for a in gift.attributes:
                if isinstance(a, StarGiftAttributeModel) and hasattr(a, "document"):
                    model_doc = a.document
                elif isinstance(a, StarGiftAttributeBackdrop) and hasattr(a, "document"):
                    bg_doc = a.document

            mime_type = getattr(model_doc, "mime_type", None) if model_doc else None

            if not model_doc:
                print(f"⚠️ Gift {slug} tidak punya model document, kirim teks saja.")
                await bot.send_message(
                    CHANNEL_OFFER,
                    text,
                    link_preview=False,
                    parse_mode="markdown"
                )

            elif mime_type in ["image/png", "image/jpeg"]:
                model_io = BytesIO()
                await bot.download_media(model_doc, file=model_io)
                model_io.seek(0)
                model_img = Image.open(model_io).convert("RGBA")

                if bg_doc:
                    bg_io = BytesIO()
                    await bot.download_media(bg_doc, file=bg_io)
                    bg_io.seek(0)
                    bg_img = Image.open(bg_io).convert("RGBA").resize(model_img.size)
                    final_img = Image.alpha_composite(bg_img, model_img)
                else:
                    final_img = model_img

                final_img = final_img.convert("RGB")
                nft_path = f"offer_{offer_id}_{slug}.jpg"
                final_img.save(nft_path, "JPEG")

                await bot.send_file(
                    CHANNEL_OFFER,
                    nft_path,
                    caption=text,
                    parse_mode="markdown"
                )
                print(f"✅ Gambar NFT dikirim untuk offer {offer_id} gift {slug}")

            elif mime_type == "application/x-tgsticker":
                nft_path = f"offer_{offer_id}_{slug}.tgs"
                await bot.download_media(model_doc, file=nft_path)
                await bot.send_file(
                    CHANNEL_OFFER,
                    nft_path,
                    caption=text,
                    parse_mode="markdown",
                    force_document=True
                )
                print(f"✅ Sticker NFT (.tgs) dikirim untuk offer {offer_id} gift {slug}")

            else:
                await bot.send_message(
                    CHANNEL_OFFER,
                    text,
                    link_preview=False,
                    parse_mode="markdown"
                )
                print(f"⚠️ Gift {slug} mime {mime_type}, kirim teks saja.")

        except Exception as e:
            print(f"⚠️ Gagal kirim media NFT untuk offer {offer_id} gift {slug}: {e}")
            await bot.send_message(
                CHANNEL_OFFER,
                text,
                link_preview=False,
                parse_mode="markdown"
            )

        index += 1

    try:
        cur.execute("""
            UPDATE gift_offer
            SET status = 'expired'
            WHERE offer_id = ?
        """, (offer_id,))
        conn.commit()
    except Exception as e:
        print(f"❌ Error update status gift_offer ke expired: {e}")
        return await event.reply(
            f"✅ Offer `{offer_id}` berhasil dikirim ke channel,\n"
            f"tetapi gagal mengubah status menjadi `expired` di database."
        )

    await event.reply(
        f"✅ Offer `{offer_id}` berhasil dikirim ke channel (total {len(items)} gift) dan status telah diubah menjadi `expired`.",
        parse_mode="markdown"
    )

@bot.on(events.NewMessage(pattern=r"^/onoffer\s+(oc|onc)\s+(\d{2}\.\d{2}\.\d{4})\s+(\d{2}:\d{2})$"))
async def cmd_onoffer(event):
    user_id = event.sender_id

    if user_id not in OWNER_ID and user_id not in ADMIN_ID:
        await event.reply("🚫 Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    mode = event.pattern_match.group(1).lower()   # 'oc' atau 'onc'
    date_str = event.pattern_match.group(2)       # dd.mm.yyyy
    time_str = event.pattern_match.group(3)       # HH:MM

    # Parse time_end jadi datetime Asia/Jakarta
    try:
        tz = pytz.timezone("Asia/Jakarta")
        dt_str = f"{date_str} {time_str}"         # "28.11.2025 20:00"
        end_dt = datetime.strptime(dt_str, "%d.%m.%Y %H:%M")
        end_dt = tz.localize(end_dt)
        end_ts = int(end_dt.timestamp())
    except Exception as e:
        print(f"⚠️ Gagal parse time_end /onoffer: {e}")
        return await event.reply(
            "🚫 Format waktu salah.\nGunakan format: `/onoffer oc 28.11.2025 20:00`",
            parse_mode="markdown"
        )

    now_dt = datetime.now(tz)
    now_ts = int(now_dt.timestamp())

    if end_ts <= now_ts:
        return await event.reply("🚫 Waktu end_time harus lebih besar dari waktu saat ini.")

    # Generate offer_id
    offer_id = generate_offer_id(15)

    # Simpan ke database
    try:
        cur.execute("""
            INSERT INTO gift_offer (offer_id, mode, created_by, created_at, end_at, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            offer_id,
            mode,
            user_id,
            now_ts,
            end_ts,
            "active"
        ))
        conn.commit()
    except Exception as e:
        print(f"❌ Error insert gift_offer: {e}")
        return await event.reply("❌ Gagal membuat OFFER, coba lagi sebentar.")

    end_str = end_dt.strftime("%d.%m.%Y %H:%M:%S")

    msg = f"""
✅ **OFFER AKTIF**

🆔 Offer ID: `{offer_id}`
🪪 Mode: `{mode.upper()}`
📅 End time: `{end_str}` (WIB)

__Offer ini akan otomatis dianggap *expired* setelah waktu end time terlewati.__
    """.strip()

    await event.reply(msg, parse_mode="markdown")

@bot.on(events.NewMessage(pattern=r"^/uptiket\s+(.+)$"))
async def cmd_uptiket(event):
    user_id = event.sender_id
    if user_id not in OWNER_ID and user_id not in ADMIN_ID:
        await event.reply("🚫 Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    keyword_text = event.pattern_match.group(1).strip()
    if not keyword_text:
        return await event.reply(
            "⚠️ Format salah.\nContoh: `/uptiket Aku Mau tiket, aldi ganteng ❤️‍🔥❤️‍🔥`",
            parse_mode="markdown"
        )

    tz = pytz.timezone("Asia/Jakarta")
    now_dt = datetime.now(tz)
    now_ts = int(now_dt.timestamp())

    expire_dt = now_dt + timedelta(minutes=TICKET_DURATION_MIN)
    expire_ts = int(expire_dt.timestamp())
    expire_str = expire_dt.strftime("%d-%m-%Y %H:%M:%S")

    # Cek apakah keyword_text sudah pernah dipakai (unik per teks)
    cur.execute("""
        SELECT id, expire_at FROM ticket_sessions
        WHERE keyword_text=?
    """, (keyword_text,))
    row = cur.fetchone()
    if row:
        sess_id, expire_at_old = row
        # Jika masih aktif, tolak
        if expire_at_old > now_ts:
            old_expire = datetime.fromtimestamp(expire_at_old, tz).strftime("%d-%m-%Y %H:%M:%S")
            return await event.reply(
                f"⚠️ Teks uptiket ini masih aktif sampai `{old_expire}`.\n"
                f"Tunggu expired dulu atau gunakan teks lain.",
                parse_mode="markdown"
            )
        else:
            # Sudah expired → boleh di-overwrite
            cur.execute("DELETE FROM ticket_sessions WHERE id=?", (sess_id,))
            cur.execute("DELETE FROM ticket_claims WHERE session_id=?", (sess_id,))
            conn.commit()

    # Simpan sesi baru
    cur.execute("""
        INSERT INTO ticket_sessions (keyword_text, created_by, created_at, expire_at, max_users)
        VALUES (?, ?, ?, ?, ?)
    """, (keyword_text, user_id, now_ts, expire_ts, MAX_TICKET_USERS))
    conn.commit()

    sess_id = cur.lastrowid

    # Notifikasi ke CHANNEL_OFFER
    text = f"""
🎟 **TIKET PROMO BARU!**

Keyword: `{keyword_text}`

Cara klaim:
> Kirim *persis* teks di atas ke bot ini (tanpa /slash).

⏰ Berlaku sampai: `{expire_str}`  
👥 Maksimal: `{MAX_TICKET_USERS}` user tercepat yang memenuhi syarat.

__Pastikan saldo kamu minimal Rp3.000 di balance untuk bisa mendapatkan tiket.__
    """.strip()

    try:
        await bot.send_message(CHANNEL_OFFER, text)
    except Exception as e:
        print(f"⚠️ Gagal kirim info uptiket ke CHANNEL_OFFER: {e}")

    await event.reply(
        f"✅ Sesi tiket dibuat.\n"
        f"Keyword: `{keyword_text}`\n"
        f"Expired: `{expire_str}`\n"
        f"Max user: `{MAX_TICKET_USERS}`",
        parse_mode="markdown"
    )

    # Opsional: jalankan monitor (kalau mau logic tambahan saat expired)
    asyncio.create_task(monitor_ticket_session(sess_id))
    
@bot.on(events.NewMessage)
async def handle_ticket_claim(event):
    user_id = event.sender_id
    text = (event.raw_text or "").strip()

    # Lewati command
    if text.startswith("/"):
        return

    if not text:
        return

    now_ts = int(time.time())

    # Cari sesi tiket yang keyword_text persis sama dan belum expired
    cur.execute("""
        SELECT id, expire_at, max_users
        FROM ticket_sessions
        WHERE keyword_text=? 
        ORDER BY id DESC 
        LIMIT 1
    """, (text,))
    row = cur.fetchone()

    if not row:
        # Bukan teks uptiket aktif → biarkan handler lain tangani atau diam
        return

    sess_id, expire_at, max_users = row

    # Cek expired
    if now_ts > expire_at:
        return await event.reply(
            "⏰ Maaf, tiket ini sudah *expired*.",
            parse_mode="markdown"
        )

    # Hitung berapa user yang sudah klaim
    cur.execute("""
        SELECT COUNT(*) FROM ticket_claims
        WHERE session_id=?
    """, (sess_id,))
    claimed_count = cur.fetchone()[0] or 0

    if claimed_count >= max_users:
        return await event.reply(
            f"⚠️ Kuota tiket sudah penuh ({max_users} user).",
            parse_mode="markdown"
        )

    # Cek apakah user sudah pernah klaim di sesi ini
    cur.execute("""
        SELECT 1 FROM ticket_claims
        WHERE session_id=? AND user_id=?
    """, (sess_id, user_id))
    exists = cur.fetchone()
    if exists:
        return await event.reply(
            "ℹ️ Kamu sudah mendapatkan tiket untuk sesi ini.",
            parse_mode="markdown"
        )

    # Cek saldo minimal 3.000
    saldo = get_user_balance(user_id)
    if saldo < 3000:
        return await event.reply(
            "🚫 Saldo kamu kurang dari `Rp3.000`, tidak dapat klaim tiket.",
            parse_mode="markdown"
        )

    # Insert claim (sementara, sebelum potong saldo kita hitung posisi lagi biar aman)
    try:
        cur.execute("""
            INSERT INTO ticket_claims (session_id, user_id, claimed_at)
            VALUES (?, ?, ?)
        """, (sess_id, user_id, now_ts))
        conn.commit()
    except Exception as e:
        print(f"⚠️ Gagal insert ticket_claims: {e}")
        return await event.reply("❌ Terjadi error saat klaim tiket, coba lagi sebentar.")

    # Hitung ulang posisi user (perlu supaya pastikan dia tidak lewat batas)
    cur.execute("""
        SELECT COUNT(*) FROM ticket_claims
        WHERE session_id=?
    """, (sess_id,))
    new_count = cur.fetchone()[0] or 0

    if new_count > max_users:
        # Kalau tiba-tiba lewat (race condition) → hapus lagi dan tolak
        cur.execute("""
            DELETE FROM ticket_claims
            WHERE session_id=? AND user_id=?
        """, (sess_id, user_id))
        conn.commit()
        return await event.reply(
            f"⚠️ Kuota tiket sudah penuh ({max_users} user).",
            parse_mode="markdown"
        )

    try:
        add_user_balance(user_id, -3000)
    except Exception as e:
        print(f"⚠️ Gagal potong saldo user {user_id}: {e}")
        cur.execute("""
            DELETE FROM ticket_claims
            WHERE session_id=? AND user_id=?
        """, (sess_id, user_id))
        conn.commit()
        return await event.reply("❌ Gagal memproses saldo kamu, klaim tiket dibatalkan.")

    await event.reply(
        f"✅ Kamu berhasil mendapatkan tiket!\n"
        f"Posisi kamu: `{new_count}/{max_users}`\n"
        f"Saldo dipotong: `Rp3.000`.",
        parse_mode="markdown"
    )

@bot.on(events.NewMessage(pattern=r'^/cek(?:@[\w_]+)?$'))
async def cek_stars_balance(event):
    msg = await event.reply("🔍 Cek saldo Stars userbot dulu...")

    try:
        status = await userbot(functions.payments.GetStarsTransactionsRequest(
            peer='me',
            offset='0',
            limit=0
        ))

        balance_raw = getattr(status.balance, "amount", 0)
        currency = getattr(status.balance, "currency", "⭐")

        balance_fmt = "{:,}".format(int(balance_raw)).replace(",", ".")

        text = (
            "💳 **Saldo Stars Userbot**\n\n"
            f"• Balance: **{balance_fmt} {currency}**\n"
        )

        await msg.edit(text)

    except Exception as e:
        print("Error cek stars balance:", e)
        await msg.edit("❌ Gagal cek saldo Stars userbot.\nCoba lagi nanti.")

@userbot.on(events.NewMessage(
    pattern=r"^/remove\s+(\S+)$"
))
async def remove_gift_handler(event):
    slug = event.pattern_match.group(1)

    # =========================
    # CEK JUMLAH DATA
    # =========================
    cur.execute("""
        SELECT COUNT(*)
        FROM unique_gifts
        WHERE slug = ?
    """, (slug,))
    count = cur.fetchone()[0]

    if count == 0:
        return await event.reply(
            "❌ Tidak ada data gift dengan slug tersebut."
        )

    # =========================
    # HAPUS SEMUA DATA SLUG
    # =========================
    cur.execute("""
        DELETE FROM unique_gifts
        WHERE slug = ?
    """, (slug,))
    conn.commit()

    # =========================
    # RESPON
    # =========================
    await event.reply(
        "🗑 **DATA GIFT DIHAPUS**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"Slug  : `{slug}`\n"
        f"Total : **{count} data**\n"
        "━━━━━━━━━━━━━━━━━━",
        link_preview=False
    )

    print(f"[REMOVE] slug={slug} | deleted={count}")

@userbot.on(events.NewMessage(
    pattern=r"^/tfo\s+(\S+)\s+(@\w+|\d+)$"
))
async def tfo_handler(event):
    slug = event.pattern_match.group(1)
    target_raw = event.pattern_match.group(2)

    cur.execute("""
        SELECT id, msg_id, title
        FROM unique_gifts
        WHERE slug = ?
        ORDER BY received_at DESC
        LIMIT 1
    """, (slug,))
    row = cur.fetchone()

    if not row:
        return await event.reply(
            "❌ Gift tidak ditemukan atau sudah ditransfer."
        )

    row_id, msg_id, title = row

    try:
        target = (
            await userbot.get_entity(int(target_raw))
            if target_raw.isdigit()
            else await userbot.get_entity(target_raw)
        )
    except Exception as e:
        return await event.reply(f"❌ Target invalid\n`{e}`")

    try:
        print(f"""
[TFO START]
Slug   : {slug}
Msg ID : {msg_id}
Title  : {title}
Target : {target_raw}
""")

        await transfer_unique_gift(
            userbot=userbot,
            target=target,
            msg_id=msg_id
        )

        cur.execute(
            "DELETE FROM unique_gifts WHERE id = ?",
            (row_id,)
        )
        conn.commit()

        await event.reply(
            "✅ **NFT berhasil dikirim!**\n"
            f"🎁 **{title}**\n"
            f"➡️ {target_raw}",
            link_preview=False
        )

    except Exception as e:
        await event.reply(
            "❌ Gagal transfer.\n"
            "⚠️ Gift kemungkinan sudah tidak ada di Saved Gifts.\n\n"
            f"`{e}`"
        )

@userbot.on(events.Raw(UpdateNewMessage))
async def gift_handler(event):
    msg = event.message
    if not msg or not msg.action:
        return

    action = msg.action
    peer = msg.peer_id
    peer_id = get_peer_id(peer)

    try:
        print(action)
        print("DICT:", action.to_dict())
    except Exception:
        pass

    if not isinstance(action, types.MessageActionStarGiftUnique):
        return

    gift = action.gift
    if not gift:
        return

    slug = getattr(gift, "slug", None)
    gift_internal_id = getattr(gift, "id", None)
    title = getattr(gift, "title", "Unknown Gift")
    stars = getattr(gift, "value_amount", 0)

    if not slug:
        print("❌ SLUG NULL, SKIP")
        return

    try:
        me = await userbot.get_me()
        offset = ""
        found_in_profile = False

        while True:
            res = await userbot(functions.payments.GetSavedStarGiftsRequest(
                peer=me,
                offset=offset,
                limit=100,
                exclude_unsaved=False,
                exclude_saved=False,
                exclude_unlimited=False,
                exclude_unique=False,
                sort_by_value=False,
                exclude_upgradable=False,
                exclude_unupgradable=False
            ))

            for saved in res.gifts:
                g = saved.gift
                if getattr(g, "slug", None) == slug:
                    found_in_profile = True
                    break

            if found_in_profile or not getattr(res, "next_offset", None):
                break

            offset = res.next_offset

        if not found_in_profile:
            print(f"🚫 GIFT {slug} TIDAK ADA DI PROFIL ME → SKIP & CLEAN DB")

            cur.execute(
                "DELETE FROM unique_gifts WHERE slug = ?",
                (slug,)
            )
            conn.commit()
            return

    except Exception as e:
        print(f"❌ Gagal cek profil me: {e}")
        return

    sender_id = None
    if msg.from_id:
        sender_id = get_peer_id(msg.from_id)
    elif getattr(gift, "owner_id", None):
        sender_id = get_peer_id(gift.owner_id)

    model = None
    background = None
    symbol = None

    for attr in gift.attributes or []:
        if isinstance(attr, types.StarGiftAttributeModel):
            model = attr.name
        elif isinstance(attr, types.StarGiftAttributeBackdrop):
            background = attr.name
        elif isinstance(attr, types.StarGiftAttributePattern):
            symbol = attr.name

    msg_id = msg.id

    cur.execute("""
        INSERT INTO unique_gifts (
            msg_id,
            slug,
            gift_id,
            title,
            stars,
            model,
            background,
            symbol,
            peer_id,
            sender_id,
            received_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        msg_id,
        slug,
        gift_internal_id,
        title,
        stars,
        model,
        background,
        symbol,
        peer_id,
        sender_id,
        int(time.time())
    ))
    conn.commit()

    print(f"""
🎁 UNIQUE STAR GIFT RECEIVED (VALID)
━━━━━━━━━━━━━━━━━━━━━━━━━━
Slug       : {slug}
Title      : {title}
Stars      : {stars}
Gift ID    : {gift_internal_id}
Msg ID     : {msg_id}
Model      : {model}
Pattern    : {symbol}
Background : {background}
Peer ID    : {peer_id}
Sender ID  : {sender_id}
━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

    text = f"""
🎁 UNIQUE STAR GIFT RECEIVED
━━━━━━━━━━━━━━━━━━━━━━━━━━
Slug       : `{slug}`
Title      : **{title}**
Stars      : {stars}
Gift ID    : {gift_internal_id}
Msg ID     : {msg_id}
Model      : {model}
Pattern    : {symbol}
Background : {background}
Peer ID    : {peer_id}
Sender ID  : {sender_id}
━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    await userbot.send_message(
        peer,
        text,
        link_preview=False
    )

@bot.on(events.NewMessage(pattern=r"^/unban$"))
async def unban_all_channel(event):
    chat = await event.get_chat()

    if not event.is_channel:
        return await event.reply("❌ Perintah ini hanya untuk CHANNEL atau SUPERGROUP.")

    try:
        participant = await bot(GetParticipantRequest(event.chat_id, event.sender_id))
        user_is_admin = bool(
            getattr(participant.participant, "admin_rights", None) or 
            getattr(participant.participant, "rank", None)
        )
    except UserNotParticipantError:
        user_is_admin = False

    bot_participant = await bot(GetParticipantRequest(event.chat_id, 'me'))
    if not bot_participant.participant.admin_rights or not bot_participant.participant.admin_rights.ban_users:
        return await event.reply("❌ Bot tidak punya izin unban di channel ini.")

    count = 0
    
    async for banned in bot.iter_participants(event.chat_id, filter=ChannelParticipantsKicked):
        try:
            await bot(EditBannedRequest(
                event.chat_id,
                banned.id,
                ChatBannedRights(
                    view_messages=False,
                    until_date=None
                )
            ))
            count += 1
        except Exception as e:
            print(f"Gagal unban {banned.id}: {e}")

    await event.delete()

    msg = await bot.send_message(event.chat_id, f"✅ Selesai membuka blokir {count} pengguna.")
    await asyncio.sleep(8)
    await msg.delete()

@userbot.on(events.NewMessage(pattern=r"^/profil(?:\s+(.+))?$"))
async def profil_handler(event):
    import io, os, uuid, math, subprocess
    from PIL import Image, ImageDraw, ImageFont

    args = event.pattern_match.group(1)
    if not args:
        return await event.reply("❌ Format salah.\nGunakan:\n`/profil @username`")
    username = args.strip()

    # get entity
    try:
        target = await userbot.get_entity(username)
    except Exception:
        return await event.reply("❌ Username tidak ditemukan.")

    # fetch saved gifts
    gifts = []
    offset = ""
    try:
        while True:
            res = await userbot(functions.payments.GetSavedStarGiftsRequest(
                peer=target,
                offset=offset,
                limit=100,
                exclude_unsaved=False,
                exclude_saved=False,
                exclude_unlimited=False,
                exclude_unique=False,
                sort_by_value=False,
                exclude_upgradable=False,
                exclude_unupgradable=False
            ))
            gifts.extend(res.gifts)
            if not getattr(res, "next_offset", None):
                break
            offset = res.next_offset
    except Exception as e:
        return await event.reply(f"❌ Gagal mengambil profil gift:\n`{e}`")

    if not gifts:
        return await event.reply(f"📭 `{username}` belum memiliki gift yang tersimpan.")

    await event.reply(
        f"🎁 **Profil Gift @{target.username}**\n"
        f"📦 Total Gift: **{len(gifts)}**\n"
        f"📸 Menyusun grid (3 per baris)..."
    )

    # helper to get usable PIL image
    async def get_gift_image(saved):
        gift = saved.gift
        doc = getattr(gift, "sticker", None) or getattr(gift, "document", None)

        # 1) gift.photo
        try:
            if hasattr(gift, "photo") and gift.photo and getattr(gift.photo, "sizes", None):
                largest = max(
                    gift.photo.sizes,
                    key=lambda s: (getattr(s, "w", 0) or 0) * (getattr(s, "h", 0) or 0)
                )
                b = await userbot.download_file(largest.location)
                return Image.open(io.BytesIO(b)).convert("RGBA")
        except:
            pass

        # 2) thumbs
        try:
            if doc is not None and getattr(doc, "thumbs", None):
                for t in doc.thumbs:
                    if hasattr(t, "bytes") and t.bytes:
                        try:
                            return Image.open(io.BytesIO(t.bytes)).convert("RGBA")
                        except:
                            pass
                    if hasattr(t, "location"):
                        try:
                            b = await userbot.download_file(t.location)
                            return Image.open(io.BytesIO(b)).convert("RGBA")
                        except:
                            pass
        except:
            pass

        # 3) download thumbnail
        try:
            data = await userbot.download_media(doc, thumb=-1)
            if data:
                if isinstance(data, (bytes, bytearray)):
                    return Image.open(io.BytesIO(data)).convert("RGBA")
                if isinstance(data, str) and os.path.exists(data):
                    img = Image.open(data).convert("RGBA")
                    os.remove(data)
                    return img
        except:
            pass

        # 4) full file
        try:
            tmp_in = f"/tmp/{uuid.uuid4().hex}"
            path = await userbot.download_media(doc, file=tmp_in)

            if isinstance(path, str) and os.path.exists(path):
                ext = os.path.splitext(path)[1].lower()

                if ext in (".png", ".jpg", ".jpeg", ".webp"):
                    img = Image.open(path).convert("RGBA")
                    os.remove(path)
                    return img

                if ext in (".webm", ".mp4", ".mov", ".mkv"):
                    tmp_out = f"/tmp/{uuid.uuid4().hex}.png"
                    subprocess.run(
                        ["ffmpeg", "-y", "-i", path, "-vframes", "1", tmp_out],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                    if os.path.exists(tmp_out):
                        img = Image.open(tmp_out).convert("RGBA")
                        os.remove(path); os.remove(tmp_out)
                        return img
                    os.remove(path)

                tmp_out = f"/tmp/{uuid.uuid4().hex}.png"
                subprocess.run(
                    ["ffmpeg", "-y", "-i", path, "-vframes", "1", tmp_out],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                if os.path.exists(tmp_out):
                    img = Image.open(tmp_out).convert("RGBA")
                    os.remove(path); os.remove(tmp_out)
                    return img

                os.remove(path)

            if isinstance(path, (bytes, bytearray)):
                return Image.open(io.BytesIO(path)).convert("RGBA")

        except:
            pass

        return None

    # group by gift.id
    counted = {}
    for saved in gifts:
        gid = getattr(saved.gift, "id", None)
        if gid is None:
            continue
        counted.setdefault(gid, {"saved": saved, "count": 0})
        counted[gid]["count"] += 1

    groups = list(counted.values())
    if not groups:
        return await event.reply("❌ Gagal membuat gambar gift. Tidak ada gift yang bisa diproses.")

    # collect thumbnails
    thumbnails = []
    for g in groups:
        saved = g["saved"]
        count = g["count"]
        img = await get_gift_image(saved)
        if img:
            thumbnails.append((img, count, saved.gift))

    if not thumbnails:
        return await event.reply("❌ Gagal membuat gambar gift. Tidak ada thumbnail yang berhasil didownload.")

    # === RENDER GRID ===

    # rounded rect helper
    def round_rect(draw, xy, radius, fill):
        x1, y1, x2, y2 = xy
        draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill)

    COLS = 3
    BOX = 360
    BOX_H = 360
    GAP = 28
    rows = math.ceil(len(thumbnails) / COLS)

    bg_color = (0, 0, 0)
    box_bg = (28, 28, 29)

    canvas_w = GAP + COLS * (BOX + GAP)
    canvas_h = GAP + rows * (BOX_H + GAP)

    canvas = Image.new("RGB", (canvas_w, canvas_h), bg_color)
    draw = ImageDraw.Draw(canvas)

    # font
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30
        )
    except:
        font = ImageFont.load_default()

    corner_radius = 45  # kotak rounded

    for idx, (img, count, gift_obj) in enumerate(thumbnails):
        col = idx % COLS
        row = idx // COLS

        x = GAP + col * (BOX + GAP)
        y = GAP + row * (BOX_H + GAP)

        round_rect(draw, (x, y, x + BOX, y + BOX_H), radius=corner_radius, fill=box_bg)

        img_h_space = BOX_H - 85
        img_w_space = BOX - 55
        
        w_ratio = img_w_space / img.width
        h_ratio = img_h_space / img.height
        
        ratio = min(w_ratio, h_ratio) * 0.95
        
        new_w = int(img.width * ratio)
        new_h = int(img.height * ratio)
        
        im_resized = img.resize((new_w, new_h), Image.LANCZOS)
        
        px = x + (BOX - new_w) // 2
        py = y + 22 + (img_h_space - new_h) // 2

        canvas.paste(im_resized, (px, py), im_resized)

        # bottom text
        name = getattr(gift_obj, "title", None) or "Gift"
        text = f"{name}  x{count}"

        tb = draw.textbbox((0, 0), text, font=font)
        tw = tb[2] - tb[0]
        th = tb[3] - tb[1]

        tx = x + 25
        ty = y + BOX_H - 55

        # background rounded rect for text
        round_rect(
            draw,
            (tx - 10, ty - 10, tx + tw + 10, ty + th + 12),
            radius=20,
            fill=(0, 0, 0, 190)
        )

        draw.text((tx, ty), text, font=font, fill=(255, 255, 255))

    # output final image
    out = io.BytesIO()
    canvas.save(out, format="JPEG", quality=92)
    out.seek(0)
    out.name = f"profile_{target.id}.jpg"

    await userbot.send_file(
        event.chat_id,
        out,
        caption=(
            f"🎁 Profil Gift @{target.username}\n"
            f"👤 User ID: `{target.id}`\n"
            f"📦 Total Gift: **{len(gifts)}**"
        ),
        force_document=False
    )

@bot.on(events.NewMessage(pattern=r"^/cektfo$"))
async def cektfo_handler(event):
    try:
        cur.execute("""
            SELECT slug, buyer_id, owner_id, user_id
            FROM gifts
            WHERE status_tfo='pending_tfo'
        """)
        rows = cur.fetchall()

        if not rows:
            await event.reply("ℹ️ Tidak ada gift yang sedang pending TFO saat ini.")
            return

        buttons = []
        messages = []

        for slug, buyer_id, owner_id, user_id in rows:
            actual_owner = owner_id or user_id

            cur.execute(
                "SELECT msg_id, chat_id FROM tfo_messages WHERE slug=?",
                (slug.lower(),)
            )
            tfo_msgs = cur.fetchall()
            msg_info = ", ".join(
                [f"{msg_id}@{chat_id}" for msg_id, chat_id in tfo_msgs]
            ) if tfo_msgs else "tidak ada msg"

            messages.append(
                f"- `{slug}` | buyer={buyer_id} | owner={actual_owner} | msg_id={msg_info}"
            )

            buttons.append([
                Button.inline(
                    text=f"⚡ FORCE {slug}",
                    data=f"force_tfo:{slug}".encode()
                )
            ])

        response = "\n".join(messages)
        await event.reply(
            f"📡 **Gift Pending TFO**:\n\n{response}",
            buttons=buttons
        )

    except Exception as e:
        await event.reply(f"❌ Terjadi error saat mengambil data TFO: {e}")
        print(f"❌ Error /cektfo: {e}")

@bot.on(events.CallbackQuery(pattern=b"force_tfo:"))
async def force_tfo_callback(event):
    slug = event.data.decode().split(":", 1)[1]
    slug_lower = slug.lower()

    await event.answer("⚡ Memaksa status TFO menjadi SUCCESS...", alert=False)

    try:
        cur.execute("""
            SELECT id, buyer_id
            FROM gifts
            WHERE LOWER(slug)=? AND status_tfo='pending_tfo'
        """, (slug_lower,))
        row = cur.fetchone()

        if not row or not row[1]:
            return await event.answer(
                "❌ Gift tidak valid / bukan pending TFO",
                alert=True
            )

        gift_id, buyer_id = row

        # 🔥 INTI FORCE TFO
        cur.execute("""
            UPDATE gifts
            SET status_tfo='success_tfo',
                api_owner_id=?
            WHERE id=?
        """, (buyer_id, gift_id))
        conn.commit()

        await event.edit(
            f"⚡ **FORCE TFO SUCCESS FLAGGED**\n\n"
            f"🎁 Gift `{slug}` ditandai sebagai **success_tfo**.\n"
            f"🤖 `monitor_tfo()` akan melanjutkan proses otomatis."
        )

    except Exception as e:
        print(f"❌ Error force_tfo {slug}: {e}")
        await event.answer("❌ Gagal force TFO", alert=True)

@bot.on(events.NewMessage)
async def on_any_message(event):
    global LAST_PING
    LAST_PING = time.time()

async def await_download_photo(entity, bot, as_bytes=True):
    if not hasattr(entity, 'photo') or entity.photo is None:
        return None
    try:
        if as_bytes:
            return await bot.download_profile_photo(entity, file=bytes)
        else:
            import tempfile
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            await bot.download_profile_photo(entity, file=tmp.name)
            tmp.close()
            return tmp.name
    except:
        return None

def split_text_to_pages(text, max_len=1000):
    lines = text.split("\n")
    pages = []
    current = ""
    for line in lines:
        if len(current) + len(line) + 1 > max_len:
            pages.append(current)
            current = ""
        current += line + "\n"
    if current:
        pages.append(current)
    return pages

@bot.on(events.NewMessage(pattern=r"^/get\s+(.+)$"))
async def get_user_handler(event):
    input_arg = event.pattern_match.group(1).strip()
    msg = await event.reply("🔎 Mengambil data user…")

    try:
        # Resolve entity
        try:
            entity = await bot.get_entity(input_arg)
        except Exception:
            return await msg.edit("❌ User tidak ditemukan atau input tidak valid.")

        # Get full user
        full = await bot(functions.users.GetFullUserRequest(id=entity))
        user = full.users[0]
        full_user = full.full_user

        # Safe get attribute
        def get_attr(obj, attr, default="—"):
            return getattr(obj, attr, default)

        # ===== BASIC INFO =====
        info = {
            "id": user.id,
            "access_hash": get_attr(user, "access_hash"),
            "first_name": get_attr(user, "first_name"),
            "last_name": get_attr(user, "last_name"),
            "username": f"@{user.username}" if user.username else "—",
            "phone": get_attr(user, "phone"),
            "lang_code": get_attr(user, "lang_code"),
            "emoji_status": get_attr(user, "emoji_status"),
        }

        # ===== FLAGS =====
        flags_list = [
            "is_self", "contact", "mutual_contact", "deleted", "bot",
            "bot_chat_history", "bot_nochats", "verified", "restricted", "min",
            "bot_inline_geo", "support", "scam", "apply_min_photo", "fake",
            "bot_attach_menu", "premium", "attach_menu_enabled", "bot_can_edit",
            "close_friend", "stories_hidden", "stories_unavailable",
            "contact_require_premium", "bot_business", "bot_has_main_app",
            "bot_forum_view"
        ]
        flags = {f: getattr(user, f, False) for f in flags_list}

        # ===== ADDITIONAL INFO =====
        extra = {
            "bot_info_version": get_attr(user, "bot_info_version"),
            "restriction_reason": get_attr(user, "restriction_reason", []),
            "bot_inline_placeholder": get_attr(user, "bot_inline_placeholder"),
            "usernames": get_attr(user, "usernames", []),
            "stories_max_id": get_attr(user, "stories_max_id"),
            "color": get_attr(user, "color"),
            "profile_color": get_attr(user, "profile_color"),
            "bot_active_users": get_attr(user, "bot_active_users"),
            "bot_verification_icon": get_attr(user, "bot_verification_icon"),
            "send_paid_messages_stars": get_attr(user, "send_paid_messages_stars"),
        }

        # ===== STATUS =====
        status = user.status
        if isinstance(status, types.UserStatusOnline):
            last_seen = "Online"
        elif isinstance(status, types.UserStatusRecently):
            last_seen = "Recently"
        elif isinstance(status, types.UserStatusLastWeek):
            last_seen = "Last week"
        elif isinstance(status, types.UserStatusLastMonth):
            last_seen = "Last month"
        elif isinstance(status, types.UserStatusOffline):
            last_seen = f"Offline ({status.was_online})"
        else:
            last_seen = "Hidden / Unknown"

        # ===== ABOUT / BIO =====
        about = get_attr(full_user, "about")

        # ===== FORMAT TEKS =====
        text = "**USER INFO (Full)**\n\n"
        for k, v in info.items():
            text += f"• **{k.capitalize()}**: `{v}`\n"
        text += "\n⚑ **Flags**:\n"
        for k, v in flags.items():
            text += f"• {k}: `{v}`\n"
        text += "\n📝 **Additional Info**:\n"
        for k, v in extra.items():
            text += f"• {k}: `{v}`\n"
        text += f"\n📝 **About/Bio**: {about}\n"
        text += f"⏱ **Last Seen / Status**: {last_seen}\n"

        # ===== SPLIT KE HALAMAN =====
        pages = split_text_to_pages(text, max_len=800)
        current_page = 0

        # Tombol inline
        buttons = []
        if len(pages) > 1:
            buttons = [[Button.inline("◀️", b"prev"), Button.inline("▶️", b"next")]]

        # Kirim file sebagai “Unamed” (bukan photo)
        sent = await bot.send_file(
            event.chat_id,
            file=bytes(" ", "utf-8"),  # kosong tapi tetap file
            caption=pages[current_page],
            file_name="Unamed",
            buttons=buttons
        )

        # Simpan state
        PAGES_STATE[sent.id] = {"pages": pages, "current": current_page, "buttons": buttons}

        await msg.delete()

    except Exception as e:
        await msg.edit(f"❌ Error: {e}")


@bot.on(events.CallbackQuery)
async def callback_query_handler(event):
    # Ambil message_id dengan aman
    try:
        message_id = event.message.id
    except AttributeError:
        # fallback untuk beberapa versi Telethon
        message_id = getattr(event, "message_id", None)
        if message_id is None:
            return await event.answer("⚠️ Tidak bisa ambil message_id", alert=True)

    if message_id not in PAGES_STATE:
        return

    data = event.data
    state = PAGES_STATE[message_id]

    if data == b"next":
        state["current"] = (state["current"] + 1) % len(state["pages"])
    elif data == b"prev":
        state["current"] = (state["current"] - 1) % len(state["pages"])
    else:
        return await event.answer()  # ignore unknown

    # Edit message
    try:
        await event.edit(state["pages"][state["current"]], buttons=state["buttons"])
    except Exception as e:
        # fallback: kalau edit gagal, kirim alert
        await event.answer(f"⚠️ Tidak bisa update halaman: {e}", alert=True)
    else:
        await event.answer()  # hide loading

@bot.on(events.NewMessage(pattern=r"^/bg\s+(https?://t\.me/nft/[\w-]+)$"))
async def bg_command(event):
    try:
        url = event.pattern_match.group(1)
        slug = url.split("/")[-1]  # ToyBear-372

        # Ambil data gift via API unik, seperti di /add
        data = await fetch_gift_data(slug)
        if not data:
            return await event.respond(f"❌ Gift `{slug}` tidak ditemukan via API unik.")

        background_name = data.get("background")
        if not background_name:
            return await event.respond(f"❌ Gift `{slug}` tidak memiliki background.")

        # Ambil semua backdrops dari peek.tg
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://peek.tg/api/nft/gifts/all/backdrops?sort=asc")
            resp.raise_for_status()
            backdrops = resp.json()

        # Cari backdrop yang cocok
        matched = next((b for b in backdrops if b["name"].lower() == background_name.lower()), None)
        if not matched:
            return await event.respond(f"❌ Background `{background_name}` tidak ditemukan di peek.tg.")

        # URL gambar medium
        backdrop_id = matched["_id"]
        preview_url = f"https://peek.tg/api/nft/gifts/backdrops/{backdrop_id}.medium.jpg"

        await event.respond(
            f"🎨 Preview background untuk [{slug}](https://t.me/nft/{slug}) ({background_name}):",
            file=preview_url,
            link_preview=False
        )

    except Exception as e:
        print(f"⚠️ Error /bg: {e}")
        await event.respond("❌ Gagal mengambil preview background.")

@bot.on(events.NewMessage(pattern="^/start$"))
async def start(event):
    try:
        sender = await event.get_sender()
        user_id = sender.id

        main_buttons = [
            [Button.inline("💬 HUBUNGI ADMIN", data="admin")],
            [Button.inline("🎮 GAMES", data="games"),
             Button.inline("⭐ STARS & GIFT️", data="stars")],
            [Button.inline("🎁 INVENTORY", data="inventory"),
             Button.inline("👤 PROFIL", data="status")],
            [Button.inline("🔎 SEARCH GIFT", data="search"),
             Button.inline("🏷️ PRICE GIFT", data="pricegift")],
            [Button.inline("💻 QUESTION & BANTUAN", data="bantuan")]
        ]

        if isinstance(sender, types.Channel):
            chat = await event.get_chat()
            chat_id = event.chat_id
            title = getattr(chat, "title", "Channel Tanpa Nama")
            msg = f"""
📢 **Bot Marketplace Gift Aktif di Channel Ini**

🆔 Channel ID: `{chat_id}`
🏷️ Nama Channel: **{title}**

Bot siap menerima perintah dari channel ini (jika diizinkan).
"""
            await event.respond(msg, buttons=main_buttons)
            await logs.send_message(CHLOGS, f"{user_id} start bot via channel.")
            return

        try:
            await bot.get_permissions(CHANNEL_SUBSCRIBE, user_id)
            is_subscribed = True
        except errors.UserNotParticipantError:
            is_subscribed = False
        except errors.ChannelPrivateError:
            is_subscribed = False
        except Exception as e:
            print(f"⚠️ Error cek subscribe: {e}")
            is_subscribed = False

        if not is_subscribed:
            join_buttons = [
                [Button.url("📢 SUBSCRIBE CHANNEL", f"https://t.me/{CHANNEL_SUBSCRIBE.strip('@')}")],
                [Button.url("✅ SUDAH SUBSCRIBE", "https://t.me/marketaldibot?start=")]
            ]
            await event.respond(
                f"""
⚠️ **__Silahkan bergabung ke channel dibawah ini sebelum menggunakan bot!__**
                """,
                buttons=join_buttons
            )
            await logs.send_message(CHLOGS, f"{user_id} start bot, belum subs.")
            return

        fullname = getattr(sender, "first_name", "") or ""
        mention = f"[{fullname}](tg://user?id={user_id})"
        username = sender.username or ""

        tz = pytz.timezone("Asia/Jakarta")
        now = datetime.now(tz).strftime("%d.%m.%Y %H:%M:%S")

        cur.execute("SELECT first_start FROM users WHERE user_id=?", (user_id,))
        row = cur.fetchone()

        if row is None:
            cur.execute("""
                INSERT INTO users (user_id, fullname, username, first_start, last_start)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, fullname, username, now, now))
        else:
            first_start = row[0]
            if not first_start:
                cur.execute("""
                    UPDATE users SET fullname=?, username=?, first_start=?, last_start=? WHERE user_id=?
                """, (fullname, username, now, now, user_id))
            else:
                cur.execute("""
                    UPDATE users SET fullname=?, username=?, last_start=? WHERE user_id=?
                """, (fullname, username, now, user_id))
        conn.commit()

        msg = f"""
🎉 **Hallo {mention}, selamat datang di market gift {CHANNEL_SUBSCRIBE}!**

🆔 ID: `{user_id}`
🪪 USERNAME: @{username if username else '❌ Tidak ada'}
👤 NAME: {mention}

**__Silahkan klik tombol dibawah ini untuk menggunakan fitur-fitur bot!__**
        """

        await event.respond(msg, buttons=main_buttons)
        await logs.send_message(CHLOGS, f"{user_id} start bot.")

    except Exception as e:
        print(f"⚠️ Error di /start: {e}")
        await event.respond(f"⚠️ Terjadi kesalahan:\n`{e}`")

@bot.on(events.CallbackQuery(pattern=b"pricegift"))
async def pricegift(event):
    user_id = event.sender_id
    
    msg = f"""
📊 **STATISTIK HARGA SEMUA GIFT (GLOBAL)**

**__Anda dapat mencari harga gift berdasarkan pencarian yang tersedia di bot, seperti harga semua gift, hanya gift tertentu, gift turun, gift rugi, gift berdasarkan waktu dan lainnya...__**
    """
    
    buttons = [
      [Button.inline("📊 ALL GIFTS", data="price:allgifts"),
       Button.inline("🏦 MARKET CAP", data="price:marketcap")],
      [Button.inline("🔎 CERTAIN GIFT", data="price:certain")],
      [Button.inline("🔙 KEMBALI", data="back_gift")]
    ]
    
    await event.delete()
    await event.respond(msg, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=b"price:allgifts"))
async def price_allgifts_callback(event):
    await event.answer("⏳ Mengambil data market...", alert=False)
    me = await userbot.get_me()
    user_id = event.sender_id

    # ===== TP USER (SESSION MILIK USER) =====
    cur.execute("SELECT selection FROM tp_sessions WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    selection = row[0] if row else "24j"
    query_time = tp_mapping.get(selection, "24h")

    direction = get_tp_direction(user_id)
    sort_mode = get_tp_sort(user_id)
    order_mode = get_tp_order(user_id)
    price_mode = get_tp_price_mode(user_id)

    # ===== AMBIL DATA GLOBAL (USER_ID = 0) =====
    cur.execute("""
        SELECT title, percent, ton, rupiah, usd, rub
        FROM gift_search
        WHERE user_id = ? AND tp = ?
        ORDER BY timestamp DESC
    """, (GLOBAL_USER_ID, selection))
    rows = cur.fetchall()

    print(f"📦 DB FETCH price:allgifts | GLOBAL_USER_ID tp={selection}")
    for r in rows[:5]:
        print("   ↳", r)

    results_parsed = []
    sortable = []

    # ===== TAMPILKAN DATA DARI DATABASE =====
    if rows:
        for title, percent, ton, rupiah, usd, rub in rows:
            percent = percent or "0%"

            try:
                p = float(percent.replace("%", ""))
            except:
                p = 0.0

            # ===== FILTER ARAH =====
            if direction == "up" and p <= 0:
                continue
            if direction == "down" and p >= 0:
                continue

            sortable.append({
                "title": title,
                "percent": p,
                "percent_raw": percent,
                "ton": ton,
                "rupiah": rupiah or 0,
                "usd": usd or 0,
                "price": (
                    ton if price_mode == "ton" else
                    rupiah if price_mode == "idr" else
                    usd if price_mode == "usd" else 0
                )
            })

    # ===== JIKA DATABASE GLOBAL BENAR-BENAR KOSONG =====
    else:
        print("⚠️ DB GLOBAL kosong → ambil inline (TANPA SIMPAN)")
        inline_query = f"All Gifts {query_time}"
        results = await userbot.inline_query("peektgbot", inline_query)

        await results[0].click(me.id)
        await asyncio.sleep(1)

        raw_text = None
        async for msg in userbot.iter_messages(me.id, limit=8):
            if msg.text and "Details ⬇️" in msg.text:
                raw_text = msg.text
                break

        if not raw_text:
            return await event.respond("❌ Gagal mengambil data market.")

        details = raw_text.split("Details ⬇️", 1)[1]
        lines = details.splitlines()

        pattern = re.compile(
            r"^(.+?)\s+([+-]?\d+(?:\.\d+)?%)?\s+—\s+([\d.]+)\s+TON$"
        )

        for line in lines:
            m = pattern.match(line.strip())
            if not m:
                continue

            title, percent, ton = m.groups()
            percent = percent or "0%"

            try:
                p = float(percent.replace("%", ""))
            except:
                p = 0.0

            if direction == "up" and p <= 0:
                continue
            if direction == "down" and p >= 0:
                continue

            sortable.append({
                "title": title,
                "percent": p,
                "percent_raw": percent,
                "ton": ton,
                "rupiah": 0,
                "usd": 0,
                "price": ton
            })

    # ===== FIX ORDER MODE (FINAL & KONSISTEN) =====
    if sort_mode == "abjad":
        if order_mode == "lowhight":
            reverse = True
        elif order_mode == "hightlow":
            reverse = False
        else:
            reverse = False

    elif sort_mode == "percent":
        if direction == "down":
            if order_mode == "lowhight":
                reverse = True
            elif order_mode == "hightlow":
                reverse = False
            else:
                reverse = True
        else:
            if order_mode == "lowhight":
                reverse = False
            elif order_mode == "hightlow":
                reverse = True
            else:
                reverse = True

    else:
        if order_mode == "lowhight":
            reverse = False
        elif order_mode == "hightlow":
            reverse = True
        else:
            reverse = True

    if sort_mode == "price":
        sortable.sort(key=lambda x: x["price"], reverse=reverse)
    elif sort_mode == "percent":
        sortable.sort(key=lambda x: x["percent"], reverse=reverse)
    elif sort_mode == "abjad":
        sortable.sort(key=lambda x: x["title"].lower(), reverse=reverse)

    for x in sortable:
        if price_mode == "ton":
            price_text = f'{x["ton"]} TON'
        elif price_mode == "idr":
            price_text = format_currency(x["rupiah"], "idr")
        elif price_mode == "usd":
            try:
                usd_val = float(x["usd"])
                price_text = f'${usd_val:.2f}'
            except:
                price_text = '$0.00'

        results_parsed.append(
            f'**{x["title"]}** {x["percent_raw"]} — {price_text}'
        )

    if not results_parsed:
        return await event.respond("❌ Tidak ada data gift.")

    text = f"""
📊 **ALL GIFTS MARKET (DETAILS)**

^^{"\n".join(results_parsed)}^^
    """

    buttons = [
        [Button.inline("🖼 MEDIA STATISTIC️", data="tp:media")],
        [Button.inline(("◉ TON" if price_mode == "ton" else "TON"), data="tp:priceton"),
         Button.inline(("◉ IDR" if price_mode == "idr" else "IDR"), data="tp:priceidr"),
         Button.inline(("◉ USD" if price_mode == "usd" else "USD"), data="tp:priceusd")],
        [Button.inline(("◉ Up" if direction == "up" else "Up"), data="tp:up"),
         Button.inline(("◉ Up & Down" if direction == "updown" else "Up & Down"), data="tp:updown"),
         Button.inline(("◉ Down" if direction == "down" else "Down"), data="tp:down")],
        [Button.inline(("◉ By Price" if sort_mode == "price" else "By Price"), data="tp:onprice"),
         Button.inline(("◉ By Percent" if sort_mode == "percent" else "By Percent"), data="tp:percent"),
         Button.inline(("◉ By Alphabet" if sort_mode == "abjad" else "By Alphabet"), data="tp:abjad")],
        [Button.inline(("◉ Low to Hight" if order_mode == "lowhight" else "Low to Hight"), data="tp:lowhight"),
         Button.inline(("◉ Hight to Low" if order_mode == "hightlow" else "Hight to Low"), data="tp:hightlow")],
        [Button.inline("🔙 KEMBALI", data="pricegift")]
    ]

    await event.edit(text, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=b"tp:priceton"))
async def tp_priceton_callback(event):
    user_id = event.sender_id

    cur.execute("""
        INSERT INTO tp_sessions (user_id, price_mode)
        VALUES (?, 'ton')
        ON CONFLICT(user_id) DO UPDATE SET price_mode='ton'
    """, (user_id,))
    conn.commit()

    await event.answer("✅ Price: TON", alert=False)
    await price_allgifts_callback(event)

@bot.on(events.CallbackQuery(pattern=b"tp:priceidr"))
async def tp_priceidr_callback(event):
    user_id = event.sender_id

    cur.execute("""
        INSERT INTO tp_sessions (user_id, price_mode)
        VALUES (?, 'idr')
        ON CONFLICT(user_id) DO UPDATE SET price_mode='idr'
    """, (user_id,))
    conn.commit()

    await event.answer("✅ Price: IDR", alert=False)
    await price_allgifts_callback(event)

@bot.on(events.CallbackQuery(pattern=b"tp:priceusd"))
async def tp_priceusd_callback(event):
    user_id = event.sender_id

    cur.execute("""
        INSERT INTO tp_sessions (user_id, price_mode)
        VALUES (?, 'usd')
        ON CONFLICT(user_id) DO UPDATE SET price_mode='usd'
    """, (user_id,))
    conn.commit()

    await event.answer("✅ Price: USD", alert=False)
    await price_allgifts_callback(event)

@bot.on(events.CallbackQuery(pattern=b"tp:lowhight"))
async def tp_lowhight_callback(event):
    user_id = event.sender_id

    cur.execute("""
        INSERT INTO tp_sessions (user_id, order_mode)
        VALUES (?, 'lowhight')
        ON CONFLICT(user_id) DO UPDATE SET order_mode='lowhight'
    """, (user_id,))
    conn.commit()

    await event.answer("✅ Low → High", alert=False)

    # Trigger refresh ALL GIFTS
    await event.client.send_event(
        event.chat_id,
        events.CallbackQuery(
            chat_id=event.chat_id,
            msg_id=event.message.id,
            data=b"price:allgifts"
        )
    )
    
@bot.on(events.CallbackQuery(pattern=b"tp:hightlow"))
async def tp_hightlow_callback(event):
    user_id = event.sender_id

    cur.execute("""
        INSERT INTO tp_sessions (user_id, order_mode)
        VALUES (?, 'hightlow')
        ON CONFLICT(user_id) DO UPDATE SET order_mode='hightlow'
    """, (user_id,))
    conn.commit()

    await event.answer("✅ High → Low", alert=False)

    # Trigger refresh ALL GIFTS
    await event.client.send_event(
        event.chat_id,
        events.CallbackQuery(
            chat_id=event.chat_id,
            msg_id=event.message.id,
            data=b"price:allgifts"
        )
    )

@bot.on(events.CallbackQuery(pattern=b"tp:percent"))
async def tp_percent_callback(event):
    user_id = event.sender_id

    cur.execute("""
        INSERT INTO tp_sessions (user_id, sort)
        VALUES (?, 'percent')
        ON CONFLICT(user_id) DO UPDATE SET sort='percent'
    """, (user_id,))
    conn.commit()

    await event.answer("✅ Sort by Percent", alert=False)

    # LANGSUNG REFRESH VIEW
    await event.client.send_event(
        event.chat_id,
        events.CallbackQuery(
            chat_id=event.chat_id,
            msg_id=event.message.id,
            data=b"price:allgifts"
        )
    )

@bot.on(events.CallbackQuery(pattern=b"tp:onprice"))
async def tp_onprice_callback(event):
    user_id = event.sender_id

    cur.execute("""
        INSERT INTO tp_sessions (user_id, sort)
        VALUES (?, 'price')
        ON CONFLICT(user_id) DO UPDATE SET sort='price'
    """, (user_id,))
    conn.commit()

    await event.answer("✅ Sort by Price", alert=False)

    await event.client.send_event(
        event.chat_id,
        events.CallbackQuery(
            chat_id=event.chat_id,
            msg_id=event.message.id,
            data=b"price:allgifts"
        )
    )

@bot.on(events.CallbackQuery(pattern=b"tp:abjad"))
async def tp_abjad_callback(event):
    user_id = event.sender_id

    cur.execute("""
        INSERT INTO tp_sessions (user_id, sort)
        VALUES (?, 'abjad')
        ON CONFLICT(user_id) DO UPDATE SET sort='abjad'
    """, (user_id,))
    conn.commit()

    await event.answer("✅ Sort by Alphabet", alert=False)

    await event.client.send_event(
        event.chat_id,
        events.CallbackQuery(
            chat_id=event.chat_id,
            msg_id=event.message.id,
            data=b"price:allgifts"
        )
    )

@bot.on(events.CallbackQuery(pattern=b"tp:up"))
async def tp_up_callback(event):
    set_tp_direction(event.sender_id, "up")
    await price_allgifts_callback(event)
    
@bot.on(events.CallbackQuery(pattern=b"tp:down"))
async def tp_down_callback(event):
    set_tp_direction(event.sender_id, "down")
    await price_allgifts_callback(event)
    
@bot.on(events.CallbackQuery(pattern=b"tp:updown"))
async def tp_updown_callback(event):
    set_tp_direction(event.sender_id, "updown")
    await price_allgifts_callback(event)

@bot.on(events.CallbackQuery(pattern=b"tp:media"))
async def tp_media_callback(event):
    await event.answer("⏳ Membuat media gift...", alert=False)
    user_id = event.sender_id

    # ===== SESSION USER =====
    cur.execute("SELECT selection FROM tp_sessions WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    selection = row[0] if row else "24j"

    direction = get_tp_direction(user_id)
    price_mode = get_tp_price_mode(user_id)

    # ===== AMBIL DATA =====
    cur.execute("""
        SELECT title, percent, ton, rupiah, usd
        FROM gift_search
        WHERE user_id=? AND tp=?
    """, (GLOBAL_USER_ID, selection))
    rows = cur.fetchall()

    if not rows:
        return await event.answer("❌ Data market belum tersedia.", alert=True)

    parsed = []
    for title, percent, ton, rupiah, usd in rows:
        percent = percent or "0%"
        try:
            p = float(percent.replace("%", ""))
        except:
            continue

        if direction == "up" and p <= 0:
            continue
        if direction == "down" and p >= 0:
            continue

        parsed.append({
            "title": title,
            "percent": p,
            "ton": ton,
            "rupiah": rupiah,
            "usd": usd
        })

    if not parsed:
        return await event.answer("❌ Tidak ada data sesuai filter.", alert=True)

    parsed.sort(key=lambda x: x["percent"])
    bottom_15 = parsed[:5]
    top_15 = parsed[-5:][::-1]

    def format_price(x):
        if price_mode == "ton":
            return f'{x["ton"]} TON'
        if price_mode == "idr":
            return format_currency(x["rupiah"], "idr")
        if price_mode == "usd":
            try:
                return f'${float(x["usd"]):.2f}'
            except:
                return '$0.00'
        return "-"

    # ===== GRID IMAGE =====
    grid = await create_pricegift_grid(GLOBAL_USER_ID, selection)
    if not grid:
        grid = await create_pricegift_grid(user_id, selection)
    if not grid:
        return await event.answer("❌ Gagal membuat media grid.", alert=True)

    # ===== UPLOAD IMAGE =====
    image_url = await upload_to_imgbb(grid)
    if not image_url:
        return await event.answer("❌ Gagal upload grid ke imgbb.", alert=True)

    # ===== TEXT (URL DISAMARKAN, PREVIEW AKTIF) =====
    text = f"[‎]({image_url})📊 **TOP 30 GIFTS MARKET**\n\n"
    text += "🟢 **TOP 15 GAINERS**\n"
    for x in top_15:
        text += f'➕ **{x["title"]}** `{x["percent"]:+.2f}%` — {format_price(x)}\n'

    text += "\n🔴 **TOP 15 LOSERS**\n"
    for x in bottom_15:
        text += f'➖ **{x["title"]}** `{x["percent"]:+.2f}%` — {format_price(x)}\n'

    text += "\n**-- STATISTIC BY: @WINEDASH --**"

    parsed_text, entities = markdown.parse(text)

    message = await event.get_message()

    # ===== SEND MESSAGE (RESMI & AMAN) =====
    await event.client(
        functions.messages.SendMessageRequest(
            peer=message.chat_id,
            message=parsed_text,
            entities=entities,
            invert_media=True,
            no_webpage=False,
            reply_markup=types.ReplyInlineMarkup(
                rows=[
                    types.KeyboardButtonRow(
                        buttons=[
                            types.KeyboardButtonCallback(
                                text="🗑️ DELETE",
                                data=b"delmedia"
                            )
                        ]
                    )
                ]
            )
        )
    )

    await message.delete()
    
@bot.on(events.CallbackQuery(pattern=b"delmedia"))
async def delmedia(event):
    user_id = event.sender_id

    # 1️⃣ hapus pesan lama (media)
    try:
        await event.delete()
    except:
        pass

    # 2️⃣ kirim message baru (text only)
    msg_self = await event.respond("🔎 Memuat...")

    # 3️⃣ FakeEvent TERIKAT ke msg_self
    class FakeEvent:
        def __init__(self, original_event, new_msg):
            self.original_event = original_event
            self.message = new_msg
            self.chat_id = new_msg.chat_id
            self.sender_id = original_event.sender_id
            self.data = b"price:allgifts"

        async def answer(self, *args, **kwargs):
            return await self.original_event.answer(*args, **kwargs)

        async def edit(self, *args, **kwargs):
            return await self.message.edit(*args, **kwargs)

        async def respond(self, *args, **kwargs):
            return await self.original_event.respond(*args, **kwargs)

        async def delete(self):
            return await self.message.delete()

    # 4️⃣ panggil ulang ALL GIFTS → EDIT msg_self
    await price_allgifts_callback(FakeEvent(event, msg_self))

@bot.on(events.NewMessage(pattern=r"^/pushstringify$"))
async def handle_push_stringify(event):

    user_id_exec = event.sender_id
    if user_id_exec not in OWNER_ID and user_id_exec not in ADMIN_ID:
        return await event.reply("🚫 Tidak punya izin")

    status = await event.reply("🔄 Mengambil data gift dari Telegram...")

    await export_stringify_json_files()

    await status.edit("📤 Push stringify ke GitHub...")

    push_json_stringify_to_github()

    await status.edit("✅ Semua stringify FULL DATA berhasil dipush!")

@bot.on(events.NewMessage(pattern=r"^/result$"))
async def handle_result_unique(event):
    if not event.is_reply:
        return await event.reply(
            "🥺 Reply pesan yang ada link gift nya dulu ya"
        )

    reply_msg = await event.get_reply_message()
    links = GIFT_LINK_PATTERN.findall(reply_msg.raw_text or "")

    if not links:
        return await event.reply("❌ Ga ada link gift di pesan itu")

    status = await event.reply("🔎 Mengambil stringify...")

    sent = 0

    for slug in links:
        try:
            result = await userbot(
                functions.payments.GetUniqueStarGiftRequest(slug=slug)
            )

            text = result.stringify()

            path = f"/tmp/{slug}.txt"
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)

            await event.reply(file=path)
            os.remove(path)

            sent += 1

        except Exception as e:
            await event.reply(f"❌ `{slug}` gagal:\n`{e}`")

    await status.edit(f"✅ Selesai — {sent} gift berhasil di stringify")

@bot.on(events.NewMessage(pattern=r"^/upload$"))
async def upload_gifts_handler(event):
    status = await event.reply("⏳ Mengambil katalog StarGift...")

    def flatten_rgba(img, bg_color=(222, 239, 233)):
        """Ubah RGBA menjadi RGB dengan background hijau #DEEFE9"""
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, bg_color)
            bg.paste(img, mask=img.split()[3])
            return bg
        return img.convert("RGB")

    # =========================
    # 1️⃣ ambil katalog StarGift
    # =========================
    try:
        res = await userbot(functions.payments.GetStarGiftsRequest(hash=0))
        gifts = res.gifts or []
    except Exception as e:
        return await status.edit(f"❌ Gagal ambil katalog:\n`{e}`")

    # =========================
    # 📝 SIMPAN RESULT.STRINGIFY KE TXT
    # =========================
    try:
        txt_path = "/tmp/stargifts_result.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(res.stringify())
    except Exception as e:
        print(f"⚠️ Gagal simpan stringify: {e}")
        txt_path = None

    # =========================
    # 2️⃣ filter gift valid
    # =========================
    valid = [g for g in gifts if getattr(g, "id", None) and getattr(g, "title", None)]

    if not valid:
        return await status.edit("❌ Tidak ada StarGift bertitle.")

    # =========================
    # 3️⃣ urutkan A–Z
    # =========================
    valid.sort(key=lambda g: g.title.lower())

    await status.edit(f"💾 Menyimpan {len(valid)} gift ke database...")

    saved = 0
    skipped = 0
    now = int(time.time())

    for gift in valid:
        try:
            gift_id = gift.id
            title = gift.title

            # =========================
            # ambil image mentah HD
            # =========================
            img = await get_raw_gift_image(userbot, gift)
            if not img:
                skipped += 1
                continue

            img = flatten_rgba(img)

            # =========================
            # simpan file sementara DB
            # =========================
            image_path = f"/tmp/uploaded_gift_{gift_id}.jpg"
            img.save(image_path, "JPEG", quality=95)

            # =========================
            # simpan/update database
            # =========================
            cur.execute("""
                INSERT INTO uploaded_gifts (gift_id, title, image_path, saved_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(gift_id) DO UPDATE SET
                    title=excluded.title,
                    image_path=excluded.image_path,
                    saved_at=excluded.saved_at
            """, (gift_id, title, image_path, now))
            conn.commit()

            saved += 1

        except Exception as e:
            print(f"[UPLOAD ERROR] {gift.title} -> {e}")
            skipped += 1

    # =========================
    # 🔄 SYNC PNG KE FOLDER WEBSITE
    # =========================
    try:
        await sync_stargift_png()
    except Exception as e:
        print(f"⚠️ Sync PNG gagal: {e}")

    # =========================
    # RESPON AKHIR + KIRIM TXT
    # =========================
    caption = (
        "✅ **UPLOAD SELESAI**\n\n"
        f"💾 Disimpan/Update: **{saved}** gift\n"
        f"⏭️ Dilewati (gagal download): **{skipped}** gift\n"
        "🖼️ PNG folder sudah disinkronkan."
    )

    if txt_path and os.path.exists(txt_path):
        await event.respond(caption, file=txt_path)
        await status.delete()
    else:
        await status.edit(caption)

@bot.on(events.NewMessage(pattern=r"^/view\s+(.+)$"))
async def view_gift_handler(event):
    query = event.pattern_match.group(1).strip()

    if not query:
        return await event.reply("❌ Gunakan:\n`/view <title>`")

    cur.execute("""
        SELECT gift_id, title, image_path
        FROM uploaded_gifts
        WHERE LOWER(title) LIKE ?
        ORDER BY title ASC
        LIMIT 1
    """, (f"%{query.lower()}%",))

    row = cur.fetchone()

    if not row:
        return await event.reply("❌ Gift tidak ditemukan di database.")

    gift_id, title, image_path = row

    if not image_path or not os.path.exists(image_path):
        return await event.reply("❌ File gambar gift tidak ditemukan.")

    await bot.send_file(
        event.chat_id,
        image_path,
        caption=f"{title} - {gift_id}",
        force_document=False
    )

@userbot.on(events.NewMessage(pattern=r"^/panggil\s+(.+)$"))
async def panggil_inline(event):
    query_text = event.pattern_match.group(1).strip()
    if not query_text:
        return await event.reply("❌ Query tidak boleh kosong.")

    try:
        # 1️⃣ Panggil inline query (TANPA @)
        results = await userbot.inline_query(
            "peektgbot",
            query_text
        )

        if not results:
            return await event.reply("❌ Tidak ada hasil inline.")

        # 2️⃣ Hapus command biar rapi
        await event.delete()

        # 3️⃣ Klik hasil inline pertama
        await results[0].click(
            event.chat_id,
            reply_to=event.id
        )

    except Exception as e:
        await event.reply(f"❌ Error inline query:\n`{e}`")

@bot.on(events.NewMessage(pattern=r"^/uniqueid$"))
async def uniqueid_handler(event):
    if event.sender_id not in OWNER_ID:
        return

    if not event.is_reply:
        return await event.reply(
            "❌ Reply ke pesan berisi slug NFT unique\n\n"
            "Contoh:\n"
            "`https://t.me/nft/JellyBunny-123`"
        )

    reply = await event.get_reply_message()
    text = reply.raw_text or ""

    # ambil slug LENGKAP
    slugs = re.findall(
        r"https?://t\.me/nft/([A-Za-z0-9_]+-\d+)",
        text
    )

    if not slugs:
        return await event.reply("❌ Tidak ditemukan slug NFT unique.")

    result_ok = []
    result_fail = []

    for slug in slugs:
        try:
            res = await userbot(
                functions.payments.GetUniqueStarGiftRequest(
                    slug=slug
                )
            )

            gift_id = res.gift.id
            gift_name = slug.rsplit("-", 1)[0]

            result_ok.append(f"{gift_name} - {gift_id}")

        except Exception as e:
            result_fail.append(f"{slug} ❌")

    msg = "🎁 **UNIQUE GIFT ID**\n\n"

    if result_ok:
        msg += "\n".join(result_ok)

    if result_fail:
        msg += "\n\n⚠️ **Gagal:**\n" + "\n".join(result_fail)

    await event.reply(msg)

@bot.on(events.NewMessage(pattern=r"^/stringify$"))
async def stringify_handler(event):
    import tempfile, os
    from telethon import functions

    status = await event.reply("⏳ Mengambil result.stringify() ...")

    try:
        # AMBIL RESULT LANGSUNG
        result = await userbot(
            functions.payments.GetStarGiftsRequest(hash=0)
        )

        text = result.stringify()

        # TULIS KE FILE
        fd, path = tempfile.mkstemp(
            prefix="result_",
            suffix=".txt"
        )
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)

        await bot.send_file(
            event.chat_id,
            path,
            caption="📄 result.stringify()"
        )

        os.remove(path)
        await status.delete()

    except Exception as e:
        await status.edit(f"❌ ERROR:\n`{e}`")

@bot.on(events.NewMessage(pattern=r"^/uniqueid$"))
async def uniqueid_handler(event):
    if event.sender_id not in OWNER_ID:
        return

    if not event.is_reply:
        return await event.reply(
            "❌ Reply ke pesan berisi slug NFT unique\n\n"
            "Contoh:\n"
            "`https://t.me/nft/JellyBunny-123`"
        )

    reply = await event.get_reply_message()
    text = reply.raw_text or ""

    # ambil slug LENGKAP
    slugs = re.findall(
        r"https?://t\.me/nft/([A-Za-z0-9_]+-\d+)",
        text
    )

    if not slugs:
        return await event.reply("❌ Tidak ditemukan slug NFT unique.")

    result_ok = []
    result_fail = []

    for slug in slugs:
        try:
            res = await userbot(
                functions.payments.GetUniqueStarGiftRequest(
                    slug=slug
                )
            )

            gift_id = res.gift.id
            gift_name = slug.rsplit("-", 1)[0]

            result_ok.append(f"{gift_name} - {gift_id}")

        except Exception as e:
            result_fail.append(f"{slug} ❌")

    msg = "🎁 **UNIQUE GIFT ID**\n\n"

    if result_ok:
        msg += "\n".join(result_ok)

    if result_fail:
        msg += "\n\n⚠️ **Gagal:**\n" + "\n".join(result_fail)

    await event.reply(msg)

@bot.on(events.NewMessage(pattern=r"^/stringify$"))
async def stringify_handler(event):
    import tempfile, os
    from telethon import functions

    status = await event.reply("⏳ Mengambil result.stringify() ...")

    try:
        # AMBIL RESULT LANGSUNG
        result = await userbot(
            functions.payments.GetStarGiftsRequest(hash=0)
        )

        text = result.stringify()

        # TULIS KE FILE
        fd, path = tempfile.mkstemp(
            prefix="result_",
            suffix=".txt"
        )
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)

        await bot.send_file(
            event.chat_id,
            path,
            caption="📄 result.stringify()"
        )

        os.remove(path)
        await status.delete()

    except Exception as e:
        await status.edit(f"❌ ERROR:\n`{e}`")

@bot.on(events.NewMessage(pattern=r"^/panel$"))
async def mines_panel(event):
    if event.sender_id not in OWNER_ID:
        return await event.reply("🚫 Perintah ini khusus OWNER.")

    cur.execute("""
        SELECT COUNT(DISTINCT user_id)
        FROM mines_history
    """)
    total_users = cur.fetchone()[0] or 0

    cur.execute("""
        SELECT COUNT(*)
        FROM mines_history
    """)
    total_games = cur.fetchone()[0] or 0

    def count_level(level):
        cur.execute("""
            SELECT COUNT(*)
            FROM mines_history
            WHERE level=?
        """, (level,))
        return cur.fetchone()[0] or 0

    easy   = count_level("easy")
    normal = count_level("normal")
    hard   = count_level("hard")
    devil  = count_level("devil")

    cur.execute("""
        SELECT
            COALESCE(SUM(bet), 0)    AS total_bet,
            COALESCE(SUM(payout), 0) AS total_payout
        FROM mines_history
    """)
    total_bet, total_payout = cur.fetchone()

    bandar_net = total_bet - total_payout

    if bandar_net > 0:
        bandar_status = f"🟢 **BANDAR UNTUNG** `Rp{bandar_net:,}`"
    elif bandar_net < 0:
        bandar_status = f"🔴 **BANDAR RUGI** `Rp{abs(bandar_net):,}`"
    else:
        bandar_status = "⚪ **BANDAR IMPAS**"

    msg = f"""
📊 **PANEL STATISTIK MINES GAME**

👥 **User Pernah Main** : `{total_users}`
🎮 **Total Game**       : `{total_games}`

🎯 **Mode Digunakan**
• EASY   : `{easy}`
• NORMAL : `{normal}`
• HARD   : `{hard}`
• DEVIL  : `{devil}`

💰 **Money Management (REAL)**
• Total Bet Masuk : `Rp{total_bet:,}`
• Total Dibayar  : `Rp{total_payout:,}`
• Net Bandar     : `Rp{bandar_net:,}`

{bandar_status}
""".replace(",", ".")

    await event.reply(msg)

@bot.on(events.NewMessage(pattern=r"^/resetmines$"))
async def reset_mines_handler(event):
    if event.sender_id not in OWNER_ID:
        return await event.reply("🚫 Perintah ini khusus OWNER.")

    try:
        cur.execute("DELETE FROM mines_history")
        conn.commit()

        await event.reply(
            "🧨 **RESET MINES BERHASIL**\n\n"
            "✅ Semua data `mines_history` telah dihapus.\n"
            "📊 Panel statistik kembali ke 0."
        )

    except Exception as e:
        await event.reply(f"❌ Gagal reset mines:\n`{e}`")

@bot.on(events.NewMessage(pattern=r"^/voucher\s+(\d+)\s*-\s*(\d+)$"))
async def create_voucher(event):
    user_id = event.sender_id
    if user_id not in OWNER_ID:
        return await event.reply("🚫 Perintah ini khusus OWNER.")

    total_claims = int(event.pattern_match.group(1))
    wicash_amount = int(event.pattern_match.group(2))

    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=25))

    cur.execute("""
        INSERT INTO vouchers (code, total_claims, wicash_amount, created_at)
        VALUES (?, ?, ?, ?)
    """, (code, total_claims, wicash_amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    
    msg = f"""
🎟️ **VOUCHER DIBUAT!**

**Voucher:** `{code}`
**Total:** {total_claims}
**$Wicash per-voucher:** {wicash_amount}

**Lanjut untuk kirim voucher?**
    """
    
    buttons=[
      [Button.inline("✅ KONFIRMASI", data=f"voucher_confirm:{code}"),
       Button.inline("❌ BATALKAN", data=f"voucher_cancel:{code}")]
    ]
    
    await event.reply(msg, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=b"^voucher_confirm:(.+)$"))
async def voucher_confirm(event):
    code = event.pattern_match.group(1).decode()

    cur.execute("UPDATE vouchers SET status='active' WHERE code=?", (code,))
    conn.commit()

    await event.edit(f"✅ **Voucher `{code}` aktif. Siap diklaim!**")

    # ambil user aktif 1-30 hari berdasarkan last_start format "%d.%m.%Y %H:%M:%S"
    cur.execute("SELECT user_id, last_start FROM users WHERE last_start IS NOT NULL")
    rows = cur.fetchall()
    users = []
    now = datetime.now()
    for uid, last_start in rows:
        try:
            last_dt = datetime.strptime(last_start, "%d.%m.%Y %H:%M:%S")
            delta_days = (now - last_dt).days
            if 1 <= delta_days <= 30:
                users.append(uid)
        except:
            continue

    await event.respond(f"📢 **Voucher akan dibroadcast ke {len(users)} user aktif**")

    msg_users = f"""
🎁 **New Voucher Added!**

**Voucher code:** `{code}`

^^**__Simpan Voucher Code diatas ini, Belum dapat di klaim, anda dapat klaim voucher ini setelah mendapatkan informasi di @winedash, Stay tuned to monitor in channel!__**^^
    """
    
    buttons = [
      [Button.url("🔊 VIEW CHANNEL", "https://t.me/winedash")]
    ]

    for uid in users:
        try:
            await bot.send_message(
                uid,
                msg_users,
                buttons=buttons
            )
        except Exception as e:
            print(f"❌ Gagal kirim voucher ke {uid}: {e}")

    # simpan session voucher aktif
    vdata = cur.execute(
        "SELECT total_claims, wicash_amount FROM vouchers WHERE code=?", (code,)
    ).fetchone()
    user_claim[code] = {
        "total_claims": vdata[0],
        "claimed_count": 0,
        "wicash_amount": vdata[1],
        "active": True
    }

    msg_channel = f"""
⏰ **WAKTUNYA KLAIM VOUCHER!**

• Bot sudah mengirim voucher code ke seluruh users.
• Salin voucher code kalian yang dikirim oleh bot dan siapkan untuk diklaim.
• Klik tombol dibawah ini untuk mengirim voucher code dan kalian akan mendapatkan reward.

🔎 **Voucher hanya dapat diklaim oleh beberapa pengguna tercepat.**
    """
    
    buttons_voucher = [
      [Button.url("🎟️ KLAIM VOUCHER DISINI", url="https://t.me/marketaldibot?start=claim_voucher")]
    ]
      
    await bot.send_message(CHANNEL_PENDING, msg_channel, buttons=buttons_voucher)

@bot.on(events.CallbackQuery(pattern=b"^voucher_cancel:(.+)$"))
async def voucher_cancel(event):
    code = event.pattern_match.group(1).decode()
    cur.execute("DELETE FROM vouchers WHERE code=?", (code,))
    conn.commit()
    await event.edit(f"❌ Voucher `{code}` dibatalkan.")

@bot.on(events.NewMessage(pattern=r"^/start claim_voucher$"))
async def start_claim_voucher(event):
    user_id = event.sender_id

    active_vouchers = [c for c,d in user_claim.items() if d["active"]]
    if not active_vouchers:
        return await event.reply("❌ Tidak ada voucher aktif saat ini.")

    await event.reply(
        "📩 **Voucher aktif tersedia!**\n\n"
        "Silakan kirim kode voucher yang kamu dapatkan untuk diklaim.\n\n"
        "^^**NOTED:** Voucher hanya bisa diklaim oleh beberapa pengguna yang tercepat.**^^"
    )

@bot.on(events.NewMessage(pattern=r"^[A-Z0-9]{25}$"))
async def input_voucher_code(event):
    user_id = event.sender_id
    code = event.raw_text.strip().upper()

    if code not in user_claim or not user_claim[code]["active"]:
        return await event.reply("❌ Voucher tidak valid atau sudah habis.")

    vdata = user_claim[code]

    if vdata["claimed_count"] >= vdata["total_claims"]:
        vdata["active"] = False
        cur.execute("UPDATE vouchers SET status='finished' WHERE code=?", (code,))
        conn.commit()
        return await event.reply("🥲 **Ups! Voucher telah habis diklaim oleh pengguna lain.**")

    cur.execute("SELECT 1 FROM voucher_claims WHERE voucher_code=? AND user_id=?", (code, user_id))
    if cur.fetchone():
        return await event.reply("⚠️ **Kamu sudah mengklaim voucher ini.**")

    cur.execute("""
        INSERT INTO voucher_claims (voucher_code, user_id, claimed_at)
        VALUES (?, ?, ?)
    """, (code, user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    cur.execute("SELECT wicash FROM wicash_wallet WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if row is None:
        cur.execute("INSERT INTO wicash_wallet (user_id, wicash) VALUES (?, ?)", (user_id, 0))
        wicash = 0
    else:
        wicash = row[0] or 0
    new_wicash = wicash + vdata["wicash_amount"]
    cur.execute("UPDATE wicash_wallet SET wicash=? WHERE user_id=?", (new_wicash, user_id))
    conn.commit()

    vdata["claimed_count"] += 1
    if vdata["claimed_count"] >= vdata["total_claims"]:
        vdata["active"] = False
        cur.execute("UPDATE vouchers SET status='finished' WHERE code=?", (code,))
        conn.commit()

    for owner in OWNER_ID:
        try:
            await bot.send_message(7998861975, f"📩 **User {user_id} telah mengklaim voucher `{code}`!**")
        except:
            pass

    msg_klaim = f"""
✅ **SUCCESSFULLY CLAIM VOUCHER!**

__Anda berhasil klaim voucher, total {vdata['wicash_amount']} $Wicash telah ditambahkan ke akun anda!__
    """
    buttons_klaim = [
      [Button.inline("💣 PLAY MINES BOMB", data="game_mines")]
    ]
    
    await event.reply(msg_klaim, buttons=buttons_klaim, message_effect_id=5046509860389126442)

@bot.on(events.CallbackQuery(data=b"gms"))
async def soon_games(event):
    user_id = get_effective_user_id(event.sender_id)
    
    await event.answer("📩 SOON..", alert=True)

@bot.on(events.CallbackQuery(pattern=b"games"))
async def games(event):
    user_id = get_effective_user_id(event.sender_id)
    
    msg = f"""
🎮 **__ANDA BERALIH KE GAMES MODE!__**
    """
    
    buttons = [
      [Button.inline("💣 MINES BOMB", data="game_mines"),
       Button.inline("🔙 KEMBALI", data="back_gift")]
      ]
      
    await event.edit(msg, buttons=buttons)

@bot.on(events.CallbackQuery(data=b"mines_play"))
async def mines_play(event):
    user_id = get_effective_user_id(event.sender_id)

    cur.execute("""
        SELECT level, bombs, boxes, multiplier_step, bet,
               current_multiplier, opened_boxes, status, bet_source,
               predict_msg_id
        FROM mines_games
        WHERE user_id=?
    """, (user_id,))
    row = cur.fetchone()

    if not row:
        return await event.answer("❌ Game belum disiapkan", alert=True)

    (level, bombs, boxes, step, bet,
     mult, opened, status, bet_source,
     predict_msg_id) = row

    if not level or not bet or bet <= 0:
        return await event.answer("❌ Level atau Bet belum diatur", alert=True)

    PER_ROW = {
        "easy": 3,
        "normal": 4,
        "hard": 6,
        "devil": 6
    }.get(level, 4)

    if status != "playing":

        if bet_source == "wicash":
            cur.execute("SELECT wicash FROM wicash_wallet WHERE user_id=?", (user_id,))
            saldo = cur.fetchone()[0] or 0
            if saldo < bet:
                return await event.answer("❌ WICASH tidak mencukupi", alert=True)

            cur.execute(
                "UPDATE wicash_wallet SET wicash = wicash - ? WHERE user_id=?",
                (bet, user_id)
            )
        else:
            cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (user_id,))
            saldo = cur.fetchone()[0] or 0
            if saldo < bet:
                return await event.answer("❌ Saldo tidak mencukupi", alert=True)

            cur.execute(
                "UPDATE user_balance SET balance = balance - ? WHERE user_id=?",
                (bet, user_id)
            )

        # ===== GENERATE BOMB =====
        bomb_positions = sorted(random.sample(range(boxes), bombs))

        cur.execute("""
            INSERT OR REPLACE INTO mines_sessions
            (user_id, bomb_positions, opened_positions)
            VALUES (?, ?, ?)
        """, (user_id, json.dumps(bomb_positions), json.dumps({})))

        cur.execute("""
            UPDATE mines_games SET
                status='playing',
                current_multiplier=0,
                opened_boxes=0,
                created_at=?,
                predict_msg_id=NULL
            WHERE user_id=?
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))

        conn.commit()
        mult = 0
        opened = 0

        pred_buttons = []
        idx = 0
        while idx < boxes:
            row_btn = []
            for _ in range(PER_ROW):
                if idx >= boxes:
                    break
                emoji = "💣" if idx in bomb_positions else "✅"
                row_btn.append(Button.url(emoji, url="https://t.me/marketaldibot"))
                idx += 1
            pred_buttons.append(row_btn)

        try:
            user = await bot.get_entity(user_id)
            username = f"@{user.username}" if user.username else "-"
            mention = f"[{user.first_name}](tg://user?id={user_id})"
        except:
            username = "-"
            mention = "-"

        pred_msg = await bot.send_message(
            CHANNEL_MINES,
            f"""
🧨 **PREDIKSI MINES GAME**

👤 User ID : `{user_id}`
🔗 Username : {username}
👀 Mention : {mention}
🎯 Level : {level.upper()}
💣 Bomb : {bombs}
📦 Box : {boxes}
            """,
            buttons=pred_buttons,
            parse_mode="markdown"
        )

        # ===== SIMPAN msg.id =====
        cur.execute("""
            UPDATE mines_games
            SET predict_msg_id=?
            WHERE user_id=?
        """, (pred_msg.id, user_id))
        conn.commit()

    # =======================
    # AMBIL SESSION
    # =======================
    cur.execute("""
        SELECT bomb_positions, opened_positions
        FROM mines_sessions
        WHERE user_id=?
    """, (user_id,))
    bombs_json, opened_json = cur.fetchone()

    bomb_positions = set(json.loads(bombs_json))
    opened_positions = json.loads(opened_json or "{}")

    # =======================
    # RENDER GRID USER
    # =======================
    buttons = []
    idx = 0

    while idx < boxes:
        row_btn = []
        for _ in range(PER_ROW):
            if idx >= boxes:
                break

            if str(idx) in opened_positions:
                row_btn.append(
                    Button.inline(
                        f"x{opened_positions[str(idx)]:.2f}",
                        data=b"noop"
                    )
                )
            else:
                row_btn.append(
                    Button.inline("⬛", data=f"mines_open:{idx}")
                )
            idx += 1
        buttons.append(row_btn)

    buttons.append([
        Button.inline("💰 CASH OUT", data="mines_cashout")
    ])

    potential = int(bet * mult)

    msg = f"""
💣 **MINES GAME – {level.upper()}**

🎯 Bet: Rp{bet:,}
📈 Multiplier: x{mult:.2f}
💵 Potensi: Rp{potential:,}
⬛ Dibuka: {len(opened_positions)}/{boxes - bombs}

Klik kotak dan hindari bomb!
""".replace(",", ".")

    try:
        await event.edit(msg, buttons=buttons)
    except:
        await event.respond(msg, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=b"^mines_open:(\d+)$"))
async def mines_open(event):
    user_id = event.sender_id
    idx = int(event.pattern_match.group(1).decode())

    cur.execute("""
        SELECT g.level, g.bet, g.bombs, g.boxes, g.multiplier_step,
               g.current_multiplier, g.opened_boxes, g.predict_msg_id,
               s.bomb_positions, s.opened_positions
        FROM mines_games g
        JOIN mines_sessions s ON g.user_id=s.user_id
        WHERE g.user_id=?
    """, (user_id,))
    row = cur.fetchone()

    if not row:
        return await event.answer("❌ Game tidak ditemukan", alert=True)

    (
        level, bet, bombs, boxes, step,
        mult, opened, predict_msg_id,
        bombs_json, opened_json
    ) = row

    bomb_positions = set(json.loads(bombs_json))
    opened_positions = json.loads(opened_json or "{}")

    if str(idx) in opened_positions:
        return await event.answer("Kotak sudah dibuka")

    # ==============================
    # FORCE BOMB (PINDAH POSISI)
    # ==============================
    force_bomb = should_force_bomb(bet, mult, step)

    if force_bomb and idx not in bomb_positions:
        movable = list(bomb_positions - {int(k) for k in opened_positions.keys()})
        if movable:
            old_bomb = movable[0]
            bomb_positions.remove(old_bomb)
            bomb_positions.add(idx)

            cur.execute("""
                UPDATE mines_sessions
                SET bomb_positions=?
                WHERE user_id=?
            """, (json.dumps(list(bomb_positions)), user_id))
            conn.commit()

            # edit prediksi di CHANNEL_MINES
            await edit_predict_buttons(
                user_id=user_id,
                boxes=boxes,
                per_row=get_per_row(level),
                bomb_positions=bomb_positions
            )

    if idx in bomb_positions:
    
        # 💰 bandar untung
        add_bandar_profit(bet)
    
        # 🧾 simpan history
        save_mines_history(
            user_id=user_id,
            level=level,
            bet=bet,
            payout=0
        )
    
        # 📊 update stats
        cur.execute("INSERT OR IGNORE INTO mines_stats (user_id) VALUES (?)", (user_id,))
        cur.execute("""
            UPDATE mines_stats
            SET total_games = total_games + 1,
                total_lose  = total_lose + 1
            WHERE user_id=?
        """, (user_id,))
    
        # 🔁 akhiri game
        cur.execute("""
            UPDATE mines_games
            SET status='finished',
                current_multiplier=0,
                opened_boxes=0
            WHERE user_id=?
        """, (user_id,))
        conn.commit()
    
        # ==============================
        # 📤 FORWARD PREDIKSI KE USER
        # ==============================
        if predict_msg_id:
            try:
                await bot.forward_messages(
                    entity=user_id,
                    messages=predict_msg_id,
                    from_peer=CHANNEL_MINES
                )
            except Exception as e:
                print(f"❌ Gagal forward prediksi ke {user_id}: {e}")
    
        # ==============================
        # ❌ TAMPILKAN HASIL
        # ==============================
        return await event.edit(
            "💥 **BOOM! Kamu kena bomb!**\n\n"
            "❌ **LOSE — Bet hangus**\n\n"
            "📩 *Prediksi telah dikirim ke chat kamu*",
            buttons=[[Button.inline("🔁 MAIN LAGI", data="game_mines")]]
        )

    # ==============================
    # ✅ AMAN
    # ==============================
    new_mult = mult + step
    opened_positions[str(idx)] = round(new_mult, 2)
    opened += 1

    cur.execute("""
        UPDATE mines_games
        SET opened_boxes=?, current_multiplier=?
        WHERE user_id=?
    """, (opened, new_mult, user_id))

    cur.execute("""
        UPDATE mines_sessions
        SET opened_positions=?
        WHERE user_id=?
    """, (json.dumps(opened_positions), user_id))

    conn.commit()
    await mines_play(event)

@bot.on(events.CallbackQuery(data=b"mines_cashout"))
async def mines_cashout(event):
    user_id = event.sender_id

    cur.execute("""
        SELECT level, bet, current_multiplier, bet_source
        FROM mines_games
        WHERE user_id=?
    """, (user_id,))
    row = cur.fetchone()

    if not row:
        return await event.answer("❌ Game tidak ditemukan", alert=True)

    level, bet, mult, bet_source = row
    payout = int(bet * mult)
    profit = payout - bet

    # bayar user
    if bet_source == "wicash":
        cur.execute("UPDATE wicash_wallet SET wicash = wicash + ? WHERE user_id=?", (payout, user_id))
    else:
        cur.execute("UPDATE user_balance SET balance = balance + ? WHERE user_id=?", (payout, user_id))

    add_bandar_profit(-profit)

    save_mines_history(
        user_id=user_id,
        level=level,
        bet=bet,
        payout=payout
    )

    cur.execute("INSERT OR IGNORE INTO mines_stats (user_id) VALUES (?)", (user_id,))
    cur.execute("""
        UPDATE mines_stats
        SET total_games = total_games + 1,
            total_win = total_win + 1,
            highest_multiplier = MAX(highest_multiplier, ?),
            total_profit = total_profit + ?
        WHERE user_id=?
    """, (mult, profit, user_id))

    cur.execute("""
        UPDATE mines_games
        SET status='finished',
            current_multiplier=0,
            opened_boxes=0,
            cashout_multiplier=?,
            result='WIN'
        WHERE user_id=?
    """, (mult, user_id))

    conn.commit()

    await event.edit(
        f"""
💰 **CASH OUT BERHASIL**

🎯 Level : {level.upper()}
🎲 Bet   : Rp{bet:,}
📈 Multi : x{mult:.2f}
💵 Payout: Rp{payout:,}
        """.replace(",", "."),
        buttons=[[Button.inline("🔁 MAIN LAGI", data="game_mines")]]
    )

@bot.on(events.CallbackQuery(pattern=b"game_mines"))
async def game_mines(event):
    user_id = get_effective_user_id(event.sender_id)

    if user_id in mines_bet_sessions:
        del mines_bet_sessions[user_id]

    cur.execute("""
        SELECT level, bombs, boxes, multiplier_step, bet
        FROM mines_games
        WHERE user_id=?
    """, (user_id,))
    row = cur.fetchone()

    if row:
        level, bombs, boxes, step, bet = row
    else:
        level = bombs = boxes = step = bet = None

    cur.execute("""
        SELECT wicash
        FROM wicash_wallet
        WHERE user_id=?
    """, (user_id,))
    r = cur.fetchone()
    wicash = r[0] if r else 0

    level_txt = level.upper() if level else "-"
    bomb_txt = bombs if bombs else "-"
    box_txt = boxes if boxes else "-"
    step_txt = f"x{step}" if step else "-"
    bet_txt = f"Rp{bet:,}".replace(",", ".") if bet and bet > 0 else "-"
    wicash_txt = f"Rp{wicash:,}".replace(",", ".")

    msg = f"""
**==== MINES GAME BOT MENU ====**

🎯 **Level :** {level_txt}
💣 **Bomb :** {bomb_txt}
⬛ **Kotak :** {box_txt}
📈 **Perkalian :** {step_txt}
💰 **Place Bet:** {bet_txt}

^^__Silakan place bet dan pilih level, sebelum memulai permainan diharapkan perhatikan perlengkapan game yang akan digunakan seperti jumlah bomb, jumlah kotak, perkalian dan level.__^^
    """

    def lv_btn(name, key):
        return Button.inline(
            f"✅ {name}" if level == key else name,
            data=f"lvmines_{key}"
        )

    buttons = [
        [lv_btn("EASY", "easy"), lv_btn("NORMAL", "normal")],
        [lv_btn("HARD", "hard"), lv_btn("DEVIL", "devil")],
        [Button.inline("💰 PLACE BET", data="mines_pb"),
         Button.inline("🏁 PLAY GAME", data="mines_play")],
        [Button.inline("❔ PENJELASAN", data="mines_penjelasan"),
         Button.inline("📊 MY STATUS", data="mines_status")],
        [Button.inline("🔙 KEMBALI", data="games")]
    ]

    try:
        await event.edit(msg, buttons=buttons)
    except:
        await event.respond(msg, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=b"mines_penjelasan"))
async def mines_penjelasan(event):
    user_id = get_effective_user_id(event.sender_id)
    
    msg = f"""
💣 **Mines Bomb** __adalah permainan tebak kotak di mana pemain harus membuka kotak aman dan menghindari bom. Setiap permainan menggunakan taruhan dari pengguna, sehingga terdapat risiko kalah maupun peluang menang.__

🎯 **Mekanisme Permainan**
^^	•	Sebelum permainan dimulai, bot secara otomatis dan acak menentukan posisi bom.
	•	Posisi bom tersebut bersifat tetap selama satu sesi permainan dan tidak berubah di tengah permainan.
	•	Setiap kotak yang dibuka akan dicek berdasarkan posisi / prediksi bom yang telah ditentukan di awal.
	• Jika pengguna membuka bomb maka permainan selesai, pengguna dianggap kalah dan taruhan di hanguskan.
	• Jika pengguna mengambil keuntungan / cash out, otomatis pengguna di anggap menang jika pengguna mengambil keputusan cashout diatas nominal taruhan dan pengguna akan mendapatkan $WICASH.^^
	
🪙 **Wicash sistem & rules**
^^  • $Wicash adalah saldo permainan / earning dari game yang di menangkan, berapapun pengguna melakukan cashout maka bot akan memberikan $wicash kepada pengguna tersebut.
  • $Wicash hanya dapat digunakan untuk membeli gift, secara umumnya $wicash adalah tiket yang dapat diambil keuntungan secara nyata dalam bentuk NFT Gift Telegram.
  • Anda hanya dapat membeli NFT Gift Telegram menggunakan $wicash pada marketplace WINEDASH, lebih tepatnya anda membeli gift titipan seller lain di WINEDASH.^^

⚖️ **Sistem Fair Play**
^^	•	Bot tidak memiliki kemampuan atau mekanisme untuk membuat pemain kalah secara sengaja.
	•	Tidak ada pengaturan tersembunyi, manipulasi hasil, atau intervensi manual dari developer.
	•	Semua hasil permainan murni berdasarkan keberuntungan dan keputusan pemain.^^

❗ **Risiko Pengguna**
^^	•	Jika pemain mengalami kekalahan, hal tersebut bukan disebabkan oleh kecurangan bot, melainkan akibat pilihan kotak yang mengenai bom.
	•	Pemain bertanggung jawab penuh atas setiap keputusan yang diambil selama permainan.^^

✅ **Dengan sistem ini, Mines Bomb berjalan secara adil, transparan, dan konsisten, di mana setiap pemain memiliki peluang yang sama tanpa campur tangan pihak mana pun.**
    """
    
    buttons = [
      [Button.inline("🔙 KEMBALI", data="game_mines")]
    ]
    
    await event.edit(msg, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=b"mines_status"))
async def mines_status(event):
    user_id = get_effective_user_id(event.sender_id)

    try:
        user = await bot.get_entity(user_id)
        if user.username:
            username = f"@{user.username}"
        elif getattr(user, "usernames", None):
            username = f"@{user.usernames[0].username}"
        else:
            username = "-"

        mention = f"[{user.first_name}](tg://user?id={user_id})"
        fullname = f"{user.first_name or ''} {user.last_name or ''}".strip()

    except:
        username = "-"
        mention = "-"
        fullname = "-"

    cur.execute("""
        SELECT
            COUNT(*) AS total_game,
            SUM(CASE WHEN payout > bet THEN 1 ELSE 0 END) AS total_win,
            SUM(CASE WHEN payout = 0 THEN 1 ELSE 0 END) AS total_lose
        FROM mines_history
        WHERE user_id=?
    """, (user_id,))
    r = cur.fetchone()

    total_games = r[0] or 0
    total_win   = r[1] or 0
    total_lose  = r[2] or 0

    def level_count(lv):
        cur.execute("""
            SELECT COUNT(*)
            FROM mines_history
            WHERE user_id=? AND level=?
        """, (user_id, lv))
        return cur.fetchone()[0] or 0

    easy_cnt   = level_count("easy")
    normal_cnt = level_count("normal")
    hard_cnt   = level_count("hard")
    devil_cnt  = level_count("devil")

    cur.execute("""
        SELECT
            MIN(bet),
            MAX(bet),
            MAX(profit),
            SUM(profit)
        FROM mines_history
        WHERE user_id=?
    """, (user_id,))
    min_bet, max_bet, highest_profit, total_profit = cur.fetchone()

    min_bet = min_bet or 0
    max_bet = max_bet or 0
    highest_profit = highest_profit or 0
    total_profit = total_profit or 0

    cur.execute("""
        SELECT highest_multiplier
        FROM mines_stats
        WHERE user_id=?
    """, (user_id,))
    r = cur.fetchone()
    highest_multiplier = r[0] if r and r[0] else 0

    cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (user_id,))
    r = cur.fetchone()
    saldo = r[0] if r else 0

    cur.execute("SELECT wicash FROM wicash_wallet WHERE user_id=?", (user_id,))
    r = cur.fetchone()
    wicash = r[0] if r else 0

    cur.execute("""
        SELECT created_at
        FROM mines_history
        WHERE user_id=?
        ORDER BY created_at DESC
        LIMIT 1
    """, (user_id,))
    r = cur.fetchone()

    if r and r[0]:
        tz = pytz.timezone("Asia/Jakarta")
        last_play = datetime.strptime(r[0], "%Y-%m-%d %H:%M:%S")
        last_play = pytz.utc.localize(last_play).astimezone(tz)
        last_play_txt = last_play.strftime("%d %B %Y • %H:%M WIB")
    else:
        last_play_txt = "-"

    if total_profit > 0:
        profit_txt = f"**Total profit:** Rp{total_profit:,}"
    elif total_profit < 0:
        profit_txt = f"**Total rugi:** Rp{abs(total_profit):,}"
    else:
        profit_txt = "**Pendapatan:** -"

    msg = f"""
📊 **MINES PLAYER STATUS**

┏━━━━━━━━━━
 👤 **USER INFO**
 • **ID:** `{user_id}`
 • **Username:** {username}
 • **Mention:** {mention}
 • **Nama:** {fullname}
┗━━━━━━━━━━
┏━━━━━━━━━━
  🎮 **STATISTIK GAME**
 • **Total Game:** {total_games}x
 • **Win:** {total_win}x
 • **Lose:** {total_lose}x
┗━━━━━━━━━━
┏━━━━━━━━━━
  🎯 **LEVEL DIMAINKAN**
 • **EASY:** {easy_cnt}x
 • **NORMAL:** {normal_cnt}x
 • **HARD:** {hard_cnt}x
 • **DEVIL:** {devil_cnt}x
┗━━━━━━━━━━
┏━━━━━━━━━━
  💰 **KEUANGAN**
 • **Saldo:** `Rp{saldo:,}`
 • **Wicash:** `Rp{wicash:,}`
 • **Bet Terendah:** `Rp{min_bet:,}`
 • **Bet Tertinggi:** `Rp{max_bet:,}`
┗━━━━━━━━━━
┏━━━━━━━━━━
  📈 **PERFORMA GAME**
 • **Multiplier Tertinggi:** `x{highest_multiplier}`
 • **Profit Tertinggi:** `Rp{highest_profit:,}`
 • {profit_txt}
┗━━━━━━━━━━

⏰ **LAST PLAYING GAME!**
__{last_play_txt}__
    """.replace(",", ".")

    await event.edit(
        msg,
        buttons=[[Button.inline("🔙 KEMBALI", data="game_mines")]],
        parse_mode="markdown"
    )

@bot.on(events.CallbackQuery(data=b"mines_pb"))
async def mines_pb(event):
    user_id = event.sender_id

    if user_id in mines_bet_sessions:
        del mines_bet_sessions[user_id]

    cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (user_id,))
    saldo = cur.fetchone()
    saldo = saldo[0] if saldo else 0

    cur.execute("SELECT wicash FROM wicash_wallet WHERE user_id=?", (user_id,))
    wicash = cur.fetchone()
    wicash = wicash[0] if wicash else 0

    # bet sekarang
    cur.execute("""
        SELECT bet, last_bet, bet_source
        FROM mines_games WHERE user_id=?
    """, (user_id,))
    r = cur.fetchone()

    bet = r[0] if r and r[0] else 0
    last_bet = r[1] if r and r[1] else 0
    bet_source = r[2] if r and r[2] else "saldo"

    saldo_fmt = f"Rp{saldo:,}".replace(",", ".")
    wicash_fmt = f"Rp{wicash:,}".replace(",", ".")
    bet_fmt = f"Rp{bet:,}".replace(",", ".") if bet else "-"

    use_saldo_txt = "✅ USE SALDO" if bet_source == "saldo" else "USE SALDO"
    use_wicash_txt = "✅ USE WICASH" if bet_source == "wicash" else "USE WICASH"

    msg = f"""
💰 **PLACE BET – MINES GAME**

💳 **Saldo:** {saldo_fmt}
💎 **Wicash:** {wicash_fmt}
➕ **{bet_source.upper()} bet:** {bet_fmt}

^^__Silakan pasang bet / taruhan anda, dan dipastikan anda memilih sumber dengan sesuai seperti saldo / wicash yang ingin anda gunakan sebagai taruhannya.__^^
"""

    buttons = [
        [Button.inline("-5.000", "mines_bet:-5000"), Button.inline("+5.000", "mines_bet:+5000")],
        [Button.inline("-10.000", "mines_bet:-10000"), Button.inline("+10.000", "mines_bet:+10000")],
        [Button.inline("-25.000", "mines_bet:-25000"), Button.inline("+25.000", "mines_bet:+25000")],
        [Button.inline("-100.000", "mines_bet:-100000"), Button.inline("+100.000", "mines_bet:+100000")],
        [Button.inline("📉 MIN BET", "mines_bet:min"), Button.inline("📈 MAX BET", "mines_bet:max")],
        [
            Button.inline(use_saldo_txt, "mines_bet:use_saldo"),
            Button.inline(use_wicash_txt, "mines_bet:use_wicash")
        ],
        [Button.inline("✍️ MANUAL BET", "mines_bet:manual")],
        [
            Button.inline("🔙 KEMBALI", "game_mines"),
            Button.inline("✅ CONFIRM", "mines_bet:confirm")
        ]
    ]

    await event.edit(msg, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=b"^mines_bet:(.+)$"))
async def mines_bet_adjust(event):
    user_id = event.sender_id
    action = event.pattern_match.group(1).decode()

    cur.execute("""
        SELECT bet, last_bet, bet_source
        FROM mines_games WHERE user_id=?
    """, (user_id,))
    r = cur.fetchone()

    bet = r[0] if r and r[0] else 0
    last_bet = r[1] if r and r[1] else 0
    bet_source = r[2] if r and r[2] else "saldo"

    # =====================
    # SWITCH SOURCE (INI FIX UTAMA)
    # =====================
    if action == "use_saldo":
        cur.execute("UPDATE mines_games SET bet_source='saldo' WHERE user_id=?", (user_id,))
        conn.commit()
        return await mines_pb(event)

    if action == "use_wicash":
        cur.execute("UPDATE mines_games SET bet_source='wicash' WHERE user_id=?", (user_id,))
        conn.commit()
        return await mines_pb(event)

    # =====================
    # AMBIL SALDO SESUAI SOURCE
    # =====================
    if bet_source == "wicash":
        cur.execute("SELECT wicash FROM wicash_wallet WHERE user_id=?", (user_id,))
        source_label = "WICASH"
    else:
        cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (user_id,))
        source_label = "SALDO"

    saldo = cur.fetchone()
    saldo = saldo[0] if saldo else 0

    # =====================
    # ACTION LAIN
    # =====================
    if action == "max":
        bet = min(saldo, MAX_BET)

    elif action == "min":
        bet = MIN_BET

    elif action == "last":
        bet = min(last_bet, saldo)

    elif action == "manual":
        mines_bet_sessions[user_id] = {"source": bet_source}
        msg_manual = f"""
➕ **__Silakan kirim angka jumlah bet yang ingin digunakan.__**

**Contoh:**
^^__10000 bukan 10.000
5000 bukan 5.000__^^

^^Klik 🚫 BATALKAN jika ingin dibatalkan.^^
        """
        buttons = [
          [Button.inline("🚫 BATALKAN", data="mines_pb")]
        ]
        
        await event.delete()
        await event.respond(msg_manual, buttons=buttons)
        return

    elif action == "confirm":
        if bet < MIN_BET or bet > saldo:
            return await event.answer("❌ Bet tidak valid", alert=True)

        cur.execute("""
            UPDATE mines_games SET bet=?, last_bet=?, status='ready'
            WHERE user_id=?
        """, (bet, bet, user_id))
        conn.commit()
        return await game_mines(event)

    else:
        try:
            bet += int(action)
        except:
            return

    bet = max(MIN_BET, min(bet, MAX_BET))
    if bet > saldo:
        return await event.answer(f"❌ {source_label} tidak mencukupi", alert=True)

    cur.execute("""
        UPDATE mines_games SET bet=?, last_bet=?
        WHERE user_id=?
    """, (bet, bet, user_id))
    conn.commit()

    await event.answer(f"✅ Bet: Rp{bet:,}".replace(",", "."))
    await mines_pb(event)

@bot.on(events.NewMessage)
async def mines_bet_manual_input(event):
    user_id = event.sender_id

    if user_id not in mines_bet_sessions:
        return

    del mines_bet_sessions[user_id]

    # =======================
    # PARSE INPUT
    # =======================
    try:
        bet = int(event.raw_text.replace(".", "").replace(",", "").strip())
    except:
        return await event.reply("❌ **Input tidak valid**")

    # =======================
    # AMBIL BET SOURCE
    # =======================
    cur.execute("""
        SELECT bet_source
        FROM mines_games
        WHERE user_id=?
    """, (user_id,))
    r = cur.fetchone()
    bet_source = r[0] if r and r[0] else "saldo"

    # =======================
    # AMBIL SALDO SESUAI SOURCE
    # =======================
    if bet_source == "wicash":
        cur.execute(
            "SELECT wicash FROM wicash_wallet WHERE user_id=?",
            (user_id,)
        )
    else:
        cur.execute(
            "SELECT balance FROM user_balance WHERE user_id=?",
            (user_id,)
        )

    s = cur.fetchone()
    saldo = s[0] if s and s[0] else 0

    # =======================
    # VALIDASI
    # =======================
    if bet < MIN_BET or bet > MAX_BET:
        return await event.reply(
            "❌ __Nominal di luar batas!__\n\n"
            f"Minimal: Rp{MIN_BET:,}\n"
            f"Maksimal: Rp{MAX_BET:,}".replace(",", ".")
        )

    if bet > saldo:
        sumber = "WICASH" if bet_source == "wicash" else "SALDO"
        return await event.reply(
            f"❌ **{sumber} tidak mencukupi!**"
        )

    # =======================
    # SIMPAN BET
    # =======================
    cur.execute("""
        UPDATE mines_games SET
            bet=?,
            last_bet=?,
            status='ready'
        WHERE user_id=?
    """, (bet, bet, user_id))
    conn.commit()

    sumber_txt = "WICASH" if bet_source == "wicash" else "SALDO"

    msg = f"""
✅ **Bet berhasil diset**

🎯 Nominal : Rp{bet:,}
💰 Sumber  : {sumber_txt}
    """.replace(",", ".")

    buttons = [
        [Button.inline("🔙 KEMBALI", data="game_mines")]
    ]

    await event.reply(msg, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=b"^lvmines_(easy|normal|hard|devil)$"))
async def select_mines_level(event):
    user_id = get_effective_user_id(event.sender_id)
    level = event.pattern_match.group(1).decode()

    config = MINES_LEVELS[level]

    cur.execute("""
        INSERT INTO mines_games
        (user_id, level, bombs, boxes, multiplier_step, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            level=excluded.level,
            bombs=excluded.bombs,
            boxes=excluded.boxes,
            multiplier_step=excluded.multiplier_step
    """, (
        user_id,
        level,
        config["bombs"],
        config["tiles"],
        config["inc"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()

    await game_mines(event)

@bot.on(events.CallbackQuery(pattern=b"inventory"))
async def inventory(event):
    user_id = get_effective_user_id(event.sender_id)
    
    text = """
**__Silakan klikt tombol dibawah ini sesuai dengan yang ingin anda gunakan fiturnya!__**

^^🎁 **GIFTS:** Untuk mengatur gift anda yang di titipkan ke winedash.
🧾 **ACC/CHANNEL:** Untuk mengatur akun / channel include gift limited.^^
    """
    
    buttons = [
      [Button.inline("🎁 GIFTS JASTIP", data="gift"),
       Button.inline("🧾 GIFT LIMITED", data="limitedgift")],
      [Button.inline("⌚ GIFT RENTAL️", data="rent")],
      [Button.inline("🔙 KEMBALI", data="back_gift")]
    ]
    
    await event.edit(text, buttons=buttons)

def clear_limited_session():
    if hasattr(bot, "_wait_limited_owner"):
        delattr(bot, "_wait_limited_owner")

    for k in list(state.keys()):
        if state[k].get("mode") in ("delete_limited",):
            state.pop(k, None)
            
@bot.on(events.CallbackQuery(data="limitedgift"))
async def limitedgift(event):
    sender = await event.get_sender()
    user_id = sender.id
    fullname = getattr(sender, "first_name", "") or ""
    mention = f"[{fullname}](tg://user?id={user_id})"
    username = sender.username or ""
    tz = pytz.timezone("Asia/Jakarta")
    now = datetime.now(tz).strftime("%d.%m.%Y %H:%M:%S")
    
    clear_limited_session()
    
    text = f"""
🛠️ **PENGATURAN GIFT LIMITED**

**Username:** @{username}
**User ID:** `{user_id}`
**Name:** {mention}
**Time:** __{now}__
**Saved:** 
    """
    
    buttons = [
      [Button.inline("➕ ADDED", data="add_limited"),
       Button.inline("📦 LIST", data="list_limited")],
      [Button.inline("🔙 KEMBALI", data="inventory")]
    ]
    
    await event.delete()
    await event.respond(text, buttons=buttons)

@bot.on(events.CallbackQuery(data="list_limited"))
async def list_limited(event):
    user_id = event.sender_id

    if hasattr(bot, "_wait_limited_owner"):
        delattr(bot, "_wait_limited_owner")

    state.pop(user_id, None)

    cur.execute("""
        SELECT owner_peer_id, username, name
        FROM limited_profiles
        WHERE is_active = 1
          AND requested_by = ?
        ORDER BY last_updated DESC
    """, (user_id,))
    rows = cur.fetchall()

    if not rows:
        return await event.answer(
            "📭 Belum ada akun / channel limited yang tersimpan.",
            alert=True
        )

    buttons, row_btn = [], []

    for i, (peer_id, username, name) in enumerate(rows, 1):
        label = f"{i}. @{username}" if username else f"{i}. {peer_id}"
        row_btn.append(Button.inline(label, data=f"limited_detail:{peer_id}"))

        if len(row_btn) == 3:
            buttons.append(row_btn)
            row_btn = []

    if row_btn:
        buttons.append(row_btn)

    buttons.append([
        Button.inline("🗑️ DELETE", data="delete_limited"),
        Button.inline("🚮 DELETE ALL", data="delete_limited_all")
    ])
    buttons.append([Button.inline("🔙 KEMBALI", data="limitedgift")])

    await event.delete()
    await event.respond(
        "📦 **DAFTAR AKUN / CHANNEL GIFT LIMITED**\n\n"
        "__Pilih akun untuk melihat detail atau hapus data.__",
        buttons=buttons
    )

@bot.on(events.CallbackQuery(data="delete_limited"))
async def delete_limited(event):
    user_id = event.sender_id

    cur.execute("""
        SELECT peer_id, username
        FROM limited_owners
        ORDER BY added_at DESC
    """)
    rows = cur.fetchall()

    if not rows:
        return await event.answer("📭 Tidak ada data.", alert=True)

    state[user_id] = {
        "mode": "delete_limited",
        "selected": set()
    }

    await render_delete_limited(event, rows)
    
@bot.on(events.CallbackQuery(pattern=r"toggle_delete_limited:(\d+)"))
async def toggle_delete_limited(event):
    user_id = event.sender_id
    peer_id = int(event.pattern_match.group(1))

    if user_id not in state or state[user_id].get("mode") != "delete_limited":
        return await event.answer("⚠️ Mode tidak aktif.", alert=True)

    selected = state[user_id]["selected"]

    if peer_id in selected:
        selected.remove(peer_id)
    else:
        selected.add(peer_id)

    cur.execute("""
        SELECT peer_id, username
        FROM limited_owners
        ORDER BY added_at DESC
    """)
    rows = cur.fetchall()

    await render_delete_limited(event, rows)
    
@bot.on(events.CallbackQuery(data="confirm_delete_limited"))
async def confirm_delete_limited(event):
    user_id = event.sender_id
    selected = state.get(user_id, {}).get("selected")

    if not selected:
        return await event.answer("⚠️ Tidak ada yang dipilih.", alert=True)

    for peer_id in selected:
        cur.execute("DELETE FROM limited_owners WHERE peer_id = ?", (peer_id,))
        cur.execute("DELETE FROM limited_profiles WHERE owner_peer_id = ?", (peer_id,))

    conn.commit()
    state.pop(user_id, None)

    await event.answer("✅ Data terpilih berhasil dihapus.", alert=True)
    await list_limited(event)
    
@bot.on(events.CallbackQuery(data="delete_limited_all"))
async def delete_limited_all(event):
    clear_limited_session()

    cur.execute("DELETE FROM limited_owners")
    cur.execute("DELETE FROM limited_profiles")
    cur.execute("DELETE FROM limited_gifts")
    conn.commit()

    await event.answer("🚮 Semua data limited berhasil dihapus.", alert=True)
    await event.edit(
        "🚮 **SEMUA DATA GIFT LIMITED TELAH DIHAPUS**",
        buttons=[[Button.inline("🔙 KEMBALI", data="limitedgift")]]
    )

@bot.on(events.CallbackQuery(pattern=r"limited_detail:(\d+)"))
async def limited_detail(event):
    owner_peer_id = int(event.pattern_match.group(1))
    await send_limited_detail(event, owner_peer_id)

@bot.on(events.CallbackQuery(pattern=r"^refresh_limited:(\d+)$"))
async def refresh_limited(event):
    owner_peer_id = int(event.pattern_match.group(1))
    user_id = event.sender_id

    cur.execute("""
        SELECT requested_by
        FROM limited_profiles
        WHERE owner_peer_id = ?
          AND is_active = 1
    """, (owner_peer_id,))
    row = cur.fetchone()

    if not row:
        return await event.answer("❌ Data limited tidak ditemukan.", alert=True)

    requested_by = row[0]
    if requested_by != user_id:
        return await event.answer("🚫 Data ini bukan milik anda.", alert=True)

    await event.edit("🔄 **__Wait, bot sedang memperbarui...__**")

    try:
        peer = await userbot.get_entity(owner_peer_id)
    except Exception:
        return await event.answer("❌ Gagal mengambil data akun / channel.", alert=True)

    name = peer.title if hasattr(peer, "title") else getattr(peer, "first_name", "")
    peer_type = "channel" if hasattr(peer, "title") else "user"

    if getattr(peer, "username", None):
        username = peer.username
    elif getattr(peer, "usernames", None):
        username = peer.usernames[0].username if peer.usernames else None
    else:
        username = None

    saved_gifts_all = await fetch_saved_gifts(peer)
    if not saved_gifts_all:
        return await event.answer("📭 Tidak ada gift terdeteksi.", alert=True)

    saved_gifts = []
    gifts_json = []

    for saved in saved_gifts_all:
        g = saved.gift
        stars = getattr(g, "stars", 0)

        if stars == 0:
            continue

        gifts_json.append({
            "gift_id": getattr(g, "id", "N/A"),
            "title": getattr(g, "title", "N/A"),
            "stars": stars,
            "limited": getattr(g, "limited", False),
            "upgradable": getattr(g, "upgradable", False),
            "symbol": getattr(g, "symbol", "🎁")
        })
        saved_gifts.append(saved)

    if not gifts_json:
        return await event.answer("📭 Tidak ada gift valid untuk disimpan.", alert=True)

    try:
        image_bytes = await render_profile_image(peer, saved_gifts)
    except Exception as e:
        return await event.answer(f"❌ Gagal render image\n{e}", alert=True)

    image_path = f"/tmp/limited_{owner_peer_id}.jpg"
    with open(image_path, "wb") as f:
        f.write(image_bytes.getbuffer())

    cur.execute("""
        UPDATE limited_profiles SET
            name = ?,
            username = ?,
            type = ?,
            image_path = ?,
            gift_total = ?,
            gifts_json = ?,
            last_updated = ?
        WHERE owner_peer_id = ?
          AND requested_by = ?
    """, (
        name,
        username,
        peer_type,
        image_path,
        len(saved_gifts),
        json.dumps(gifts_json, ensure_ascii=False),
        int(time.time()),
        owner_peer_id,
        requested_by
    ))
    conn.commit()

    await send_limited_detail(event, owner_peer_id)

@bot.on(events.CallbackQuery(pattern=r"view_limited:(\d+):(\d+)"))
async def view_limited(event):
    owner_peer_id = int(event.pattern_match.group(1))
    page = int(event.pattern_match.group(2))

    cur.execute("""
        SELECT gifts_json
        FROM limited_profiles
        WHERE owner_peer_id = ? AND is_active = 1
    """, (owner_peer_id,))
    row = cur.fetchone()
    if not row:
        return await event.answer("❌ Owner tidak ditemukan.", alert=True)

    try:
        gifts = json.loads(row[0])
    except:
        gifts = []

    if not gifts:
        return await event.answer("❌ Tidak ada gift.", alert=True)

    # group dan urutkan
    grouped = {}
    for g in gifts:
        key = (g.get("symbol","🎁"), g.get("stars",0), g.get("limited",False), g.get("gift_id","N/A"))
        grouped.setdefault(key, 0)
        grouped[key] += 1

    grouped_list = []
    for (symbol, stars, limited, gid), count in grouped.items():
        grouped_list.append({
            "symbol": symbol,
            "stars": stars,
            "limited": limited,
            "gift_id": gid,
            "count": count
        })

    grouped_list.sort(key=lambda x: (x["limited"], x["stars"]))

    # pagination
    total_pages = (len(grouped_list) - 1) // GIFTS_PER_PAGE + 1
    start = page * GIFTS_PER_PAGE
    end = start + GIFTS_PER_PAGE
    page_items = grouped_list[start:end]

    text_lines = []
    for idx, g in enumerate(page_items, start + 1):
        symbol = g["symbol"]
        stars = g["stars"]
        limited = g["limited"]
        count = g["count"]
        gid = g["gift_id"]
        status = "Unlimited" if not limited else "Limited"
        line = f"{idx}. {symbol}{stars}⭐️ (x{count}) {status} [`{gid}`]"
        text_lines.append(line)

    text = "^^\n" + "\n".join(text_lines) + "\n^^"

    buttons = []
    nav = []
    if page > 0:
        nav.append(Button.inline("⬅️", data=f"view_limited:{owner_peer_id}:{page-1}"))
    if page < total_pages - 1:
        nav.append(Button.inline("➡️", data=f"view_limited:{owner_peer_id}:{page+1}"))
    if nav:
        buttons.append(nav)
    buttons.append([Button.inline("🔙 KEMBALI", data=f"limited_detail:{owner_peer_id}")])

    await event.edit(text, buttons=buttons)
    
@bot.on(events.CallbackQuery(data="add_limited"))
async def add_limited(event):
    user_id = event.sender_id
    
    msg = """
➕ **__Silakan kirim input username akun / channel yang ingin ditambahkan!__**

^^**NOTED:** Bot hanya dapat mendeteksi gift di akun / channel jika tidak di sembunyikan, contoh input: `@ftamous atau @winedash`^^
    """
    
    buttons = [
      [Button.inline("🚫 BATALKAN", data="limitedgift")]
    ]
    
    await event.answer()
    await event.delete()
    await event.respond(msg, buttons=buttons)

    bot._wait_limited_owner = {
        "from_id": event.sender_id,
        "chat_id": event.chat_id
    }

@bot.on(events.NewMessage)
async def limited_owner_input(event):
    state = getattr(bot, "_wait_limited_owner", None)
    if not state or event.sender_id != state["from_id"]:
        return

    delattr(bot, "_wait_limited_owner")

    username = event.raw_text.strip()
    if not username.startswith("@"):
        return await event.reply(
            "😐 **__Invalid input, silakan input ulang harus `@username`__**"
        )

    try:
        target = await userbot.get_entity(username)
    except Exception:
        return await event.reply("❌ Username tidak ditemukan.")

    if not isinstance(target, (types.User, types.Channel)):
        return await event.reply("❌ Hanya akun user / channel.")

    if isinstance(target, types.Channel) and target.megagroup:
        return await event.reply("❌ Group tidak didukung.")

    owner_peer_id = target.id
    is_channel = isinstance(target, types.Channel)

    cur.execute(
        "SELECT 1 FROM limited_profiles WHERE owner_peer_id = ? AND is_active = 1",
        (owner_peer_id,)
    )
    if cur.fetchone():
        return await event.reply(
            "⚠️ **Akun / channel ini sudah terdaftar sebagai limited owner.**"
        )

    btn_gagal = [[Button.inline("➕ ADDED", data="add_limited")]]

    if is_channel:
        bot_id = (await bot.get_me()).id

        requester_is_admin = False
        async for admin in userbot.iter_participants(
            target,
            filter=ChannelParticipantsAdmins
        ):
            if admin.id == event.sender_id:
                requester_is_admin = True
                break

        if not requester_is_admin:
            return await event.reply(
                "🚫 **__Anda bukan owner / administrator channel tersebut!__**",
                buttons=btn_gagal
            )

        bot_is_admin = False
        async for admin in userbot.iter_participants(
            target,
            filter=ChannelParticipantsAdmins
        ):
            if admin.id == bot_id:
                bot_is_admin = True
                break

        if not bot_is_admin:
            return await event.reply(
                "🚫 **__Bot harus menjadi admin channel terlebih dahulu!__**",
                buttons=btn_gagal
            )

        now = int(time.time())
        name = target.title
        username_val = target.username

        cur.execute("""
            INSERT INTO limited_profiles
            (owner_peer_id, requested_by, name, username, type,
             saved_at, last_updated, is_active)
            VALUES (?, ?, ?, ?, 'channel', ?, ?, 1)
            ON CONFLICT(owner_peer_id) DO UPDATE SET
                requested_by = excluded.requested_by,
                name = excluded.name,
                username = excluded.username,
                last_updated = excluded.last_updated,
                is_active = 1
        """, (
            owner_peer_id,
            event.sender_id,
            name,
            username_val,
            now,
            now
        ))
        conn.commit()

        msg = (
            "📩 **NOTIFIKASI**\n\n"
            "✅ Channel ini **berhasil ditambahkan** ke "
            "**MARKETPLACE @WINEDASH** sebagai:\n"
            "__channel include gift limited__."
        )
        
        btn_back = [
          [Button.inline("🔙 KEMBALI", data="limitedgift")]
        ]

        await bot.send_message(owner_peer_id, msg)
        await event.reply(
            "✅ **Channel berhasil ditambahkan dan disimpan ke penyimpanan bot.**",
            buttons=btn_back
        )
        return

    cur.execute(
        "SELECT 1 FROM pending_limited_requests WHERE owner_peer_id = ?",
        (owner_peer_id,)
    )
    if cur.fetchone():
        btn = [[Button.inline("🚫 CANCEL PENDING", data=f"cancel_add:{owner_peer_id}")]]
        return await event.reply(
            "⏳ **Akun ini masih pending konfirmasi.**",
            buttons=btn
        )

    cur.execute("""
        INSERT INTO pending_limited_requests
        (owner_peer_id, requested_by, requested_at)
        VALUES (?, ?, ?)
    """, (
        owner_peer_id,
        event.sender_id,
        int(time.time())
    ))
    conn.commit()

    msg = """
📩 **__NOTIFIKASI KONFIRMASI__**

__Akun anda mendapatkan permintaan added dari marketplace @winedash untuk disimpan sebagai akun include gift limited, Jika tindakan ini tidak anda kenali segera batalkan dan kirim laporan, Terimakasih!__
    """

    buttons = [
        [
            Button.inline("✅ KONFIRMASI", data=f"confirm_limited:{owner_peer_id}"),
            Button.inline("🚫 BATALKAN", data=f"cancel_limited:{owner_peer_id}")
        ]
    ]
    
    cancel_pending = [
      [Button.inline("🚫 CANCEL PENDING", data=f"cancel_add:{owner_peer_id}")]
    ]

    await bot.send_message(target.id, msg, buttons=buttons)

    await event.reply("🔎 **Bot berhasil mengirim notifikasi ke akun yang ingin anda tambahkan, Jika anda pemilik akun tersebut silakan lakukan tindakan konfirmasi sendiri akun tersebut!**",
      buttons=cancel_pending
    )

@bot.on(events.CallbackQuery(pattern=r"^confirm_limited:(\d+)$"))
async def confirm_limited(event):
    owner_peer_id = int(event.pattern_match.group(1))
    sender = await event.get_sender()

    try:
        peer = await userbot.get_entity(owner_peer_id)
    except Exception:
        return await event.answer("❌ Entity tidak ditemukan.", alert=True)

    # =========================
    # 🚫 BLOK CHANNEL TOTAL
    # =========================
    if isinstance(peer, types.Channel):
        return await event.answer(
            "ℹ️ Channel tidak memerlukan konfirmasi.",
            alert=True
        )

    # =========================
    # VALIDASI USER SAJA
    # =========================
    if sender.id != owner_peer_id:
        return await event.answer(
            "🤒 Konfirmasi ini bukan untuk anda.",
            alert=True
        )

    # =========================
    # LOADING
    # =========================
    msg_self = await event.edit("🔎 **Memuat...**")

    # =========================
    # CEK PENDING
    # =========================
    cur.execute(
        "SELECT requested_by FROM pending_limited_requests WHERE owner_peer_id = ?",
        (owner_peer_id,)
    )
    row = cur.fetchone()
    if not row:
        return await event.answer("😰 Request sudah dibatalkan.", alert=True)

    requested_by = row[0]

    # =========================
    # DATA DASAR USER
    # =========================
    name = peer.first_name or ""
    peer_type = "user"
    username = peer.username

    # =========================
    # AMBIL GIFT
    # =========================
    saved_gifts_all = await fetch_saved_gifts(peer)
    if not saved_gifts_all:
        return await event.answer("📭 Tidak ada gift.", alert=True)

    saved_gifts = []
    gifts_json = []

    for saved in saved_gifts_all:
        g = saved.gift
        stars = getattr(g, "stars", 0)
        if stars == 0:
            continue

        gifts_json.append({
            "gift_id": getattr(g, "id", "N/A"),
            "title": getattr(g, "title", "N/A"),
            "stars": stars,
            "limited": getattr(g, "limited", False),
            "upgradable": getattr(g, "upgradable", False),
            "symbol": getattr(g, "symbol", "🎁")
        })
        saved_gifts.append(saved)

    if not gifts_json:
        return await event.answer("📭 Tidak ada gift valid.", alert=True)

    # =========================
    # RENDER IMAGE
    # =========================
    try:
        image_bytes = await render_profile_image(peer, saved_gifts)
    except Exception as e:
        return await event.answer(f"❌ Gagal render image\n{e}", alert=True)

    image_path = f"/tmp/limited_{owner_peer_id}.jpg"
    with open(image_path, "wb") as f:
        f.write(image_bytes.getbuffer())

    # =========================
    # SIMPAN KE DATABASE
    # =========================
    now = int(time.time())
    cur.execute("""
        INSERT INTO limited_profiles
        (owner_peer_id, requested_by, name, username, type,
         image_path, gift_total, gifts_json,
         saved_at, last_updated, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        ON CONFLICT(owner_peer_id) DO UPDATE SET
            requested_by = excluded.requested_by,
            name = excluded.name,
            username = excluded.username,
            type = excluded.type,
            image_path = excluded.image_path,
            gift_total = excluded.gift_total,
            gifts_json = excluded.gifts_json,
            last_updated = excluded.last_updated,
            is_active = 1
    """, (
        owner_peer_id,
        requested_by,
        name,
        username,
        peer_type,
        image_path,
        len(saved_gifts),
        json.dumps(gifts_json, ensure_ascii=False),
        now,
        now
    ))
    conn.commit()

    # =========================
    # HAPUS PENDING
    # =========================
    cur.execute(
        "DELETE FROM pending_limited_requests WHERE owner_peer_id = ?",
        (owner_peer_id,)
    )
    conn.commit()

    # =========================
    # NOTIFIKASI REQUESTER
    # =========================
    await bot.send_file(
        requested_by,
        image_path,
        caption=(
            "✅ **LIMITED OWNER DIKONFIRMASI**\n\n"
            f"👤 `{owner_peer_id}`\n"
            f"📦 Total Gift: **{len(saved_gifts)}**"
        ),
        buttons=[
            [Button.inline("📋 LIHAT LIST", data=f"view_limited:{owner_peer_id}:0")]
        ]
    )

    await msg_self.edit("✅ **__Berhasil Dikonfirmasi!__**")

@bot.on(events.CallbackQuery(pattern=r"^cancel_add:(\d+)$"))
async def cancel_add(event):
    owner_peer_id = int(event.pattern_match.group(1))
    requester_id = event.sender_id

    cur.execute("""
        SELECT requested_by FROM pending_limited_requests
        WHERE owner_peer_id = ?
    """, (owner_peer_id,))
    row = cur.fetchone()

    if not row:
        return await event.answer(
            "⚠️ Request sudah tidak tersedia atau telah diproses.",
            alert=True
        )

    if row[0] != requester_id:
        return await event.answer(
            "🤒 Anda tidak berhak membatalkan request ini.",
            alert=True
        )

    cur.execute(
        "DELETE FROM pending_limited_requests WHERE owner_peer_id = ?",
        (owner_peer_id,)
    )
    conn.commit()

    await event.answer("🚫 Request berhasil dibatalkan.", alert=True)
    await event.delete()

@bot.on(events.CallbackQuery(pattern=r"^confirm_limited:(\d+)$"))
async def confirm_limited(event):
    owner_peer_id = int(event.pattern_match.group(1))
    sender = await event.get_sender()

    try:
        peer = await userbot.get_entity(owner_peer_id)
    except Exception:
        return await event.answer("❌ Entity tidak ditemukan.", alert=True)

    is_channel = isinstance(peer, types.Channel)

    if not is_channel:
        if sender.id != owner_peer_id:
            return await event.answer("🤒 Bukan untuk anda!", alert=True)

    else:
        try:
            participant = await userbot.get_participant(peer, sender.id)
        except Exception:
            return await event.answer("🚫 Anda bukan admin channel ini.", alert=True)

        if not isinstance(
            participant,
            (ChannelParticipantCreator, ChannelParticipantAdmin)
        ):
            return await event.answer("🚫 Hanya admin / owner channel yang dapat konfirmasi.", alert=True)

    # =========================
    # LOADING
    # =========================
    msg_self = await event.edit("🔎 **Memuat...**")

    # =========================
    # CEK PENDING
    # =========================
    cur.execute(
        "SELECT requested_by FROM pending_limited_requests WHERE owner_peer_id = ?",
        (owner_peer_id,)
    )
    row = cur.fetchone()
    if not row:
        return await event.answer("😰 Request dibatalkan.", alert=True)

    requested_by = row[0]

    # =========================
    # AMBIL NAMA & USERNAME
    # =========================
    name = peer.title if is_channel else getattr(peer, "first_name", "")
    peer_type = "channel" if is_channel else "user"

    if getattr(peer, "username", None):
        username = peer.username
    elif getattr(peer, "usernames", None) and peer.usernames:
        username = peer.usernames[0].username
    else:
        username = None

    # =========================
    # AMBIL GIFT
    # =========================
    saved_gifts_all = await fetch_saved_gifts(peer)
    if not saved_gifts_all:
        return await event.answer("📭 Tidak ada gift.", alert=True)

    saved_gifts = []
    gifts_json = []

    for saved in saved_gifts_all:
        g = saved.gift
        stars = getattr(g, "stars", 0)

        if stars == 0:
            continue

        gifts_json.append({
            "gift_id": getattr(g, "id", "N/A"),
            "title": getattr(g, "title", "N/A"),
            "stars": stars,
            "limited": getattr(g, "limited", False),
            "upgradable": getattr(g, "upgradable", False),
            "symbol": getattr(g, "symbol", "🎁")
        })
        saved_gifts.append(saved)

    if not gifts_json:
        return await event.answer("📭 Tidak ada gift valid.", alert=True)

    try:
        image_bytes = await render_profile_image(peer, saved_gifts)
    except Exception as e:
        return await event.answer(f"❌ Gagal render image\n{e}", alert=True)

    image_path = f"/tmp/limited_{owner_peer_id}.jpg"
    with open(image_path, "wb") as f:
        f.write(image_bytes.getbuffer())

    now = int(time.time())
    cur.execute("""
        INSERT INTO limited_profiles
        (owner_peer_id, requested_by, name, username, type,
         image_path, gift_total, gifts_json,
         saved_at, last_updated, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        ON CONFLICT(owner_peer_id) DO UPDATE SET
            requested_by = excluded.requested_by,
            name = excluded.name,
            username = excluded.username,
            type = excluded.type,
            image_path = excluded.image_path,
            gift_total = excluded.gift_total,
            gifts_json = excluded.gifts_json,
            last_updated = excluded.last_updated,
            is_active = 1
    """, (
        owner_peer_id,
        requested_by,
        name,
        username,
        peer_type,
        image_path,
        len(saved_gifts),
        json.dumps(gifts_json, ensure_ascii=False),
        now,
        now
    ))
    conn.commit()

    cur.execute(
        "DELETE FROM pending_limited_requests WHERE owner_peer_id = ?",
        (owner_peer_id,)
    )
    conn.commit()

    # =========================
    # NOTIFIKASI REQUESTER
    # =========================
    await bot.send_file(
        requested_by,
        image_path,
        caption=(
            f"✅ **LIMITED OWNER DIKONFIRMASI**\n\n"
            f"👤 `{owner_peer_id}`\n"
            f"📦 Total Gift: **{len(saved_gifts)}**"
        ),
        buttons=[
            [Button.inline("📋 LIHAT LIST", data=f"view_limited:{owner_peer_id}:0")]
        ]
    )

    await msg_self.edit("✅ **__Berhasil Dikonfirmasi!__**")

@bot.on(events.CallbackQuery(data="cancel_limited"))
async def cancel_limited(event):
    await event.edit("❌ Permintaan dibatalkan.")

@bot.on(events.NewMessage(pattern=r"^/start ref_(\d+)$"))
async def start_ref(event):
    try:
        sender = await event.get_sender()
        user_id = sender.id
        ref_id = int(event.pattern_match.group(1))

        if ref_id == user_id:
            msg = f"""
🗳️ **LINK REFERRAL SYSTEM**

^^__- Kamu akan mendapatkan 1% dari total harga asli gift yang di beli oleh referral kamu.
- Bagikan kepada teman anda atau pengguna lain di telegram.
- Referral yang anda dapatkan adalah 1% dari total harga asli gift bukan harga marketplace.
- Jika buyer tidak memiliki referral maka semua fee marketplace akan didapatkan kepada admins.
- Fee 1% anda dapatkan dan 1% diberikan kepada admin market, sesuai dengan berdasarkan fee market yaitu 2%.__^^
            """
            await event.respond(msg)
            return

        cur.execute("SELECT referred_by FROM user_referral WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        already_ref = row and row[0] is not None

        if not already_ref:
            cur.execute("""
                INSERT OR IGNORE INTO user_referral (user_id, total_ref)
                VALUES (?, 0)
            """, (ref_id,))

            cur.execute("""
                INSERT INTO user_referral (user_id, referred_by, total_ref)
                VALUES (?, ?, 0)
                ON CONFLICT(user_id) DO UPDATE SET referred_by=excluded.referred_by
                WHERE referred_by IS NULL
            """, (user_id, ref_id))

            cur.execute("""
                UPDATE user_referral
                SET total_ref = total_ref + 1
                WHERE user_id = ?
            """, (ref_id,))

            conn.commit()

            await logs.send_message(
                CHLOGS,
                f"📥 Referral baru!\n• User: {user_id}\n• Dari: {ref_id}"
            )

        return await start(event)

    except Exception as e:
        print(f"Error start_ref: {e}")
        await event.respond(f"⚠️ Terjadi kesalahan di referral:\n`{e}`")

@bot.on(events.CallbackQuery(pattern=b"^stars$"))
async def cb_stars(event):
    await show_stars_menu(event, is_callback=True)

async def show_stars_menu(event, is_callback: bool = False):
    if isinstance(event, events.CallbackQuery.Event):
        user = await event.get_sender()
    else:
        user = await event.get_sender()

    user_id = user.id
    fullname = user.first_name or ""
    mention = f"[{fullname}](tg://user?id={user_id})"
    username = user.username or (user.usernames[0].username if getattr(user, "usernames", None) else None)

    cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    balance = row[0] if row else 0
    saldo_fmt = f"Rp{balance:,}".replace(",", ".")

    msg = f"""
💫 **MENU GIFT STARS**

**User ID:** `{user_id}`
**Username:** @{username}
**Name:** {mention}
**Saldo:** {saldo_fmt}

__Klik tombol di bawah ini untuk pengaturan pembelian gift stars.__
    """

    buttons = [
        [Button.inline("⭐️ BUY GIFT", data=b"buying_stars"),
         Button.inline("📊 STATUS", data=b"status_stars")],
        [Button.inline("🔙 KEMBALI", data="back_gift")]
    ]

    if is_callback:
        await event.edit(msg, buttons=buttons)
    else:
        await event.respond(msg, buttons=buttons)
    
@bot.on(events.CallbackQuery(pattern=b"^buying_stars$"))
async def buy_stars(event):
    user = await event.get_sender()
    user_id = user.id
    fullname = user.first_name or ""
    mention = f"[{fullname}](tg://user?id={user_id})"
    username = user.username or (user.usernames[0].username if getattr(user, "usernames", None) else None)

    if user_id in user_state:
        del user_state[user_id]

    cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    balance = row[0] if row else 0
    saldo_fmt = f"Rp{balance:,}".replace(",", ".")

    order = get_or_create_stars_order(user_id)

    gift_key = order["gift_type"]
    cfg = GIFT_STARS_CATALOG.get(gift_key) or {}
    price_rp = cfg.get("price_rp", 0)
    price_fmt = f"Rp{price_rp:,}".replace(",", ".") if price_rp else "-"
    gift_display = gift_key if gift_key else "-"

    qty = order["qty"] or 1
    note_text = order["note"] or "-"
    send_to_text = order["send_to"] or "-"
    send_mode = order["send_mode"] or "Unhide"
    send_from = order["send_from"] or "-"

    total_price_rp = order.get("total_price_rp") or (price_rp * qty)
    total_price_fmt = f"Rp{total_price_rp:,}".replace(",", ".")

    if send_mode == "Hide":
        hide_btn_text = "👀 UN HIDE"
    else:
        hide_btn_text = "📵 HIDE"

    msg = f"""
💫 **Pengaturan pembelian Gift Stars**

^^**User ID:** `{user_id}`
**Username:** @{username}
**Name:** {mention}
**Saldo:** {saldo_fmt}^^

**Gift:** `{gift_display} ({price_fmt})`
**Jumlah:** `{qty}`
**Noted:** `{note_text}`
**Send to:** `{send_to_text}`
**Send mode:** `{send_mode}`
**Send from:** `{send_from}`
**Total price:** `{total_price_fmt}`

⭐️ __Silakan atur gift, jumlah, noted, tujuan, mode & pengirim sebelum klik BUY NOW.__
    """

    buttons = [
      [Button.inline("🧸 SELECT GIFT", data=b"pilih_stars"),
       Button.inline("🔢 JUMLAH", data=b"jumlah_stars")],
      [Button.inline("📝 NOTED", data=b"noted_stars"),
       Button.inline("👤 SEND TO", data=b"send_stars")],
      [Button.inline(hide_btn_text, data=b"hide_stars"),
       Button.inline("💌 SEND FROM", data=b"from_stars")],
      [Button.inline("💳 DEPOSIT SALDO", data="deposit")],
      [Button.inline("🔙 KEMBALI", data=b"stars"),
       Button.inline("✅ BUY NOW", data=b"beli_stars")]
    ]

    await event.edit(msg, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=b"^hide_stars$"))
async def cb_hide_stars(event):
    user = await event.get_sender()
    user_id = user.id

    order = get_or_create_stars_order(user_id)
    current_mode = order["send_mode"] or "Unhide"

    if current_mode == "Unhide":
        new_mode = "Hide"
        info = "Mode pengirim di-set ke 📵 Hide."
        new_button_text = "👀 UN HIDE"
    else:
        new_mode = "Unhide"
        info = "Mode pengirim di-set ke 👀 Unhide."
        new_button_text = "📵 HIDE"

    update_stars_order(user_id, send_mode=new_mode)
    print(f"[DEBUG] toggle hide_stars: user_id={user_id}, from={current_mode} to={new_mode}")

    await event.answer(info, alert=True)
    await buy_stars(event)

@bot.on(events.CallbackQuery(pattern=b"^from_stars$"))
async def cb_from_stars(event):
    user = await event.get_sender()
    user_id = user.id

    rows = []
    row = []
    for name in GIFT_SENDER_BOTS.keys():
        label = f"🤖 {name}"
        data = f"from_pick:{name}".encode()
        row.append(Button.inline(label, data=data))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    rows.append([Button.inline("⬅️ KEMBALI", data=b"buying_stars")])

    text = (
        "💌 *Pilih userbot pengirim Gift*\n\n"
        "Silakan pilih salah satu userbot di bawah sebagai pengirim gift stars."
    )

    await event.edit(text, buttons=rows)
    
@bot.on(events.CallbackQuery(pattern=b"^from_pick:(.+)$"))
async def cb_from_pick(event):
    user = await event.get_sender()
    user_id = user.id

    raw = event.pattern_match.group(1)
    if isinstance(raw, bytes):
        raw = raw.decode()
    bot_name = raw.strip()

    if bot_name not in GIFT_SENDER_BOTS:
        await event.answer("Userbot tidak dikenal.", alert=True)
        return

    # simpan ke DB
    update_stars_order(user_id, send_from=bot_name)

    await event.answer(f"Pengirim di-set ke {bot_name}.", alert=True)
    # kembali ke menu utama buying_stars
    await buy_stars(event)

@bot.on(events.CallbackQuery(pattern=b"^pilih_stars$"))
async def cb_pilih_stars(event):
    user = await event.get_sender()
    user_id = user.id

    buttons = []
    row = []
    for key in GIFT_STARS_CATALOG.keys():
        text_btn = format_gift_name(key)
        row.append(Button.inline(text_btn, data=f"sel_gift:{key}".encode()))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append([Button.inline("🔙 KEMBALI", data=b"buying_stars")])

    text = f"""
🧸 **__Silakan pilih gift yang ingin anda beli, klik tombol dibawah ini!__**
    """

    await event.edit(text, buttons=buttons, parse_mode="markdown")
    
@bot.on(events.CallbackQuery(pattern=b"^sel_gift:(.+)$"))
async def cb_gift_selected(event):
    user = await event.get_sender()
    user_id = user.id

    m = event.pattern_match.group(1)
    if isinstance(m, bytes):
        m = m.decode()

    gift_key = m.lower()

    cfg = GIFT_STARS_CATALOG.get(gift_key)
    if not cfg:
        await event.answer("Gift tidak dikenal.", alert=True)
        return

    # Simpan ke DB
    update_stars_order(
        user_id,
        gift_type=gift_key,
        gift_id=cfg["gift_id"],
        price_rp=cfg["price_rp"]
    )

    await event.answer(f"Gift di-set ke {format_gift_name(gift_key)}", alert=True)

    # Refresh tampilan menu BUY
    await buy_stars(event)

@bot.on(events.CallbackQuery(pattern=b"^jumlah_stars$"))
async def cb_jumlah_stars(event):
    user = await event.get_sender()
    user_id = user.id

    text = """
🔢 **__Silakan kirim jumlah gift yang ingin anda beli!__**
    """
    
    buttons = [
      [Button.inline("🔙 KEMBALI", data="buying_stars")]
    ]
    
    await event.respond(text, buttons=buttons)
    await event.delete()

    user_state[user_id] = {"mode": "set_qty"}


@bot.on(events.CallbackQuery(pattern=b"^noted_stars$"))
async def cb_noted_stars(event):
    user = await event.get_sender()
    user_id = user.id

    text = """
📝 **__Silakan kirim text untuk noted gift yang akan dikirim ke user, kirim "-" jika anda ingin membeli tanpa noted.__**
    """
    
    buttons = [
      [Button.inline("🔙 KEMBALI", data="buying_stars")]
    ]
    
    await event.respond(text, buttons=buttons)
    await event.delete()

    user_state[user_id] = {"mode": "set_note"}

@bot.on(events.CallbackQuery(pattern=b"^send_stars$"))
async def cb_send_stars(event):
    user = await event.get_sender()
    user_id = user.id

    text = f"""
👤 **__Silakan kirim username / ID user penerima gift yang anda beli.__**
    """
    
    buttons = [
        [Button.inline("🔙 KEMBALI", data=b"buying_stars")]
    ]
    
    await event.respond(text, buttons=buttons)
    await event.delete()
    
    user_state[event.sender_id] = {"mode": "set_send_to"}
    
@bot.on(events.NewMessage)
async def handle_stars_input(event):
    if event.is_group or event.is_channel:
        return

    user = await event.get_sender()
    user_id = user.id
    text = (event.raw_text or "").strip()

    state = user_state.get(user_id)
    if not state:
        return

    mode = state.get("mode")

    if mode == "set_qty":
        try:
            qty = int(text)
            if qty <= 0:
                raise ValueError
        except ValueError:
            await event.reply("❌ Jumlah tidak valid. Kirim angka > 0.")
            return
        update_stars_order(user_id, qty=qty)
        
        buttons = [
          [Button.inline("🔙 KEMBALI", data="buying_stars")]
        ]
        
        await event.reply(f"✅ Jumlah gift di-set ke: `{qty}`", buttons=buttons)
        user_state.pop(user_id, None)
        return

    if mode == "set_note":
        if text == "-":
            note = ""
        else:
            note = text
        update_stars_order(user_id, note=note)
        
        buttons = [
          [Button.inline("🔙 KEMBALI", data="buying_stars")]
        ]
        
        await event.reply("✅ Noted berhasil di-set.", buttons=buttons)
        user_state.pop(user_id, None)
        return

    if mode == "set_send_to":
        raw = text.strip()
        if not raw:
            await event.reply("❌ Format kosong. Contoh: `123456789, @user2`")
            return
    
        # izinkan campuran: ID angka dan @username
        parts = [p.strip() for p in raw.split(",") if p.strip()]
    
        cleaned_parts = []
        invalid_parts = []
    
        for p in parts:
            # kalau pure angka -> simpan apa adanya
            if p.isdigit():
                cleaned_parts.append(p)
                continue
    
            # kalau diawali @ -> simpan apa adanya (jangan diresolve ke ID)
            if p.startswith("@"):
                if len(p) > 1:
                    cleaned_parts.append(p)
                else:
                    invalid_parts.append(p)
                continue
    
            # kalau bukan angka & bukan @username → anggap invalid
            invalid_parts.append(p)
    
        if not cleaned_parts:
            msg = "❌ Tidak ada target yang valid."
            if invalid_parts:
                msg += "\nGagal parsing: `" + ", ".join(invalid_parts) + "`"
            await event.reply(msg)
            return
    
        send_to_str = ",".join(cleaned_parts)
        update_stars_order(user_id, send_to=send_to_str)
    
        # hapus state
        user_state.pop(user_id, None)
    
        msg = (
            "✅ **Send To berhasil di-set.**\n\n"
            f"Tujuan:\n`{send_to_str}`\n\n"
            "__Kamu bisa menggunakan campuran ID dan @username.__"
        )
        buttons = [
            [Button.inline("🔙 KEMBALI", data=b"buying_stars")]
        ]
        await event.reply(msg, buttons=buttons, parse_mode="markdown")
    
        return
      
@bot.on(events.CallbackQuery(pattern=b"^beli_stars$"))
async def cb_beli_stars(event):
    user = await event.get_sender()
    user_id = user.id

    order = get_or_create_stars_order(user_id)

    gift_type  = order["gift_type"]
    gift_id    = order["gift_id"]
    price_rp   = order["price_rp"]
    qty        = order["qty"] or 1
    send_to    = order["send_to"] or ""
    note       = order["note"] or ""
    send_mode  = order["send_mode"] or "Unhide"
    send_from  = order["send_from"] or ""

    # DEBUG penting
    print(f"[DEBUG] cb_beli_stars user_id={user_id}, send_mode={send_mode}, send_from={send_from}")

    # Validasi gift
    if not gift_type or not gift_id or not price_rp:
        await event.answer("Pilih gift dulu.", alert=True)
        return

    # Validasi send_to
    if not send_to.strip():
        await event.answer("Set 'send to' dulu.", alert=True)
        return

    # Validasi send_from
    if not send_from or send_from not in GIFT_SENDER_BOTS:
        await event.answer("Pilih 'SEND FROM' dulu.", alert=True)
        return

    total_price_rp = price_rp * qty

    cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    balance = row[0] if row else 0
    
    balance_fmt = f"Rp{balance:,}".replace(",", ".")
    totalprice_fmt = f"Rp{total_price_rp:,}".replace(",", ".")

    if balance < total_price_rp:
        msg = f"""
💵 **Saldo anda tidak mencukupi untuk melakukan tindakan pembelian gift tersebut!**

Saldo: {balance_fmt}
Price: {totalprice_fmt}

__Silakan lakukan deposit terlebih dahulu, klik tombol dibawah ini!__
        """
        
        buttons = [
          [Button.inline("💳 DEPOSIT", data="deposit"),
           Button.inline("🔙 KEMBALI", data="buying_stars")]
        ]
        
        await event.edit(msg, buttons=buttons)
        return

    # Pilih userbot sesuai send_from
    userbot_client = GIFT_SENDER_BOTS.get(send_from)
    if not userbot_client or not userbot_client.is_connected():
        await event.answer(f"Userbot '{send_from}' tidak aktif / tidak terdaftar.", alert=True)
        return

    # optional: cek saldo stars userbot
    stars_balance, stars_currency = await get_userbot_stars_balance(userbot_client)
    print(f"[{user_id}] Stars balance {send_from}: {stars_balance} {stars_currency}")

    # Potong saldo balance (Rp) di DB
    new_balance = balance - total_price_rp
    cur.execute("UPDATE user_balance SET balance=? WHERE user_id=?", (new_balance, user_id))
    conn.commit()

    # Build list target (ID / username string)
    print(f"[DEBUG] raw send_to from DB: {repr(send_to)}")
    send_to_list = [x.strip() for x in send_to.split(",") if x.strip()]
    print(f"[DEBUG] parsed send_to_list: {send_to_list}")

    await event.edit("⏳ Memproses pembelian gift...")

    # DI SINI KUNCI:
    hide_sender = (send_mode == "Hide")
    print(f"[DEBUG] calling send_stars_gift hide_sender={hide_sender} (send_mode={send_mode})")

    total_sent, failed_targets = await send_stars_gift(
        userbot_client=userbot_client,
        gift_id=gift_id,
        qty=qty,
        send_to_list=send_to_list,
        note=note,
        hide_sender=hide_sender
    )

    # Simpan status terakhir
    status_text = f"Sent {total_sent}/{qty} gift(s), total_price_rp={total_price_rp}, mode={send_mode}, from={send_from}"
    if failed_targets:
        status_text += f", failed: {','.join(failed_targets)}"

    update_stars_order(
        user_id,
        total_price_rp=total_price_rp,
        last_status=status_text
    )

    total_price_fmt = f"Rp{total_price_rp:,}".replace(",", ".")
    new_balance_fmt = f"Rp{new_balance:,}".replace(",", ".")

    failed_info = ""
    if failed_targets:
        failed_info = "\n\n❌ Gagal kirim ke: " + ", ".join(failed_targets)

    msg_done = (
        f"✅ **Pembelian Gift Stars selesai**\n\n"
        f"Gift: `{format_gift_name(gift_type)}`\n"
        f"Qty: `{qty}`\n"
        f"Mode: `{send_mode}`\n"
        f"From: `{send_from}`\n"
        f"Total Bayar: {total_price_fmt}\n"
        f"Saldo sisa: {new_balance_fmt}\n"
        f"Gift terkirim: {total_sent}/{qty}"
        f"{failed_info}"
    )

    await event.edit(msg_done)
    
@bot.on(events.CallbackQuery(pattern=b"^status_stars$"))
async def cb_status_stars(event):
    user = await event.get_sender()
    user_id = user.id

    order = get_or_create_stars_order(user_id)

    # saldo Rp
    cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    balance = row[0] if row else 0
    saldo_fmt = f"Rp{balance:,}".replace(",", ".")

    userbot = userbot.get("me")
    if userbot:
        stars_balance, stars_currency = await get_userbot_stars_balance(userbot)
    else:
        stars_balance, stars_currency = (0, "")

    gift_text = format_gift_name(order["gift_type"])
    qty_text = order["qty"]
    note_text = order["note"] or "-"
    send_to_text = order["send_to"] or "-"
    total_price_rp = order["total_price_rp"] or 0
    total_price_fmt = f"Rp{total_price_rp:,}".replace(",", ".")

    msg = f"""
📊 **STATUS GIFT STARS**

Saldo Bot: {saldo_fmt}
Saldo Stars Userbot: `{stars_balance} {stars_currency}`

Gift: `{gift_text}`
Qty: `{qty_text}`
Noted: `{note_text}`
Send to: `{send_to_text}`
Total price terakhir: `{total_price_fmt}`

Last status: `{order['last_status'] or '-'}`
    """

    buttons = [[Button.inline("🔙 KEMBALI", data=b"stars")]]
    await event.edit(msg, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=b"^withdraw$"))
async def withdraw_callback(event):
    user_id = event.sender_id

    try:
        await event.answer()
    except:
        pass

    cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    balance = row[0] if row else 0

    if balance <= 0:
        return await event.answer(
            "🚫 Saldo kamu kosong, tidak bisa melakukan withdraw!", alert=True
        )

    saldo_fmt = f"Rp{balance:,}".replace(",", ".")

    withdraw_sessions[user_id] = {
        "step": "amount",
        "amount": None,
        "withdraw_id": None,
    }

    msg = f"""
📤 **WITHDRAW BALANCE**

__Silakan kirim input angka untuk jumlah withdraw yang anda inginkan!__

^^Klik 🚫 BATALKAN untuk dibatalkan.^^
"""

    buttons = [
        [Button.inline("🚫 BATALKAN", data=b"back_gift")]
    ]

    await event.respond(msg, buttons=buttons)
    await event.delete()
    await logs.send_message(CHLOGS, f"{user_id} menekan tombol 📤 WITHDRAW")
    
@bot.on(events.NewMessage)
async def handle_withdraw_and_others(event):
    user_id = event.sender_id

    if event.is_group or event.is_channel:
        return

    raw = (event.raw_text or "").strip()

    if user_id not in withdraw_sessions:
        return

    session = withdraw_sessions[user_id]
    step = session.get("step")

    if step == "amount":
        text = raw.replace(" ", "")
        if not text.isdigit():
            return await event.reply(
                "__Nominal input salah, kirim angka tanpa spasi atau titik, contoh: `1000` untuk jumlah 1.000__"
            )

        amount = int(text)

        if amount <= 0:
            return await event.reply("⚠️ Nominal withdraw harus lebih dari 0.")
        
        cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        balance = row[0] if row else 0

        if balance <= 0:
            withdraw_sessions.pop(user_id, None)
            return await event.reply(
                "🚫 **Saldo kamu kosong, tidak bisa melakukan withdraw.**"
            )

        if amount > balance:
            saldo_fmt = f"Rp{balance:,}".replace(",", ".")
            return await event.reply(
                f"🚫 **Saldo tidak mencukupi untuk withdraw {amount}, saldo anda: {saldo_fmt}.**\n"
            )

        session["step"] = "account"
        session["amount"] = amount

        amount_fmt = f"Rp{amount:,}".replace(",", ".")

        msg = f"""
⏳ **Jumlah withdraw `{amount_fmt}`**

__Silakan kirim format data rekening anda, rekening ini disimpan untuk admin melakukan transfer permintaan withdraw anda, kirim input format rekening seperti dibawah ini!__

**Contoh:**
`DANA - 081234567890 - ALDI KENZ`
`BCA - 1234567890 - ALDI KENZ`

^^Format: [bank] - [nomor] - [nama], harap gunakan spasi untuk setiap strip (-) seperti contoh diatas supaya bot mendeteksi!^^
        """
        
        buttons = [
          [Button.inline("🚫 BATALKAN", data="back_gift")]
        ]
        
        await event.reply(msg, buttons=buttons)
        await logs.send_message(CHLOGS, f"{user_id} input jumlah wothdraw {amount_fmt}")
        return

    elif step == "account":
        account_info = raw

        parts = [p.strip() for p in account_info.split("-")]
        if len(parts) < 3:
            return await event.reply(
                "⚠️ **Format rekening tidak valid.**\n"
                "Gunakan format:\n"
                "`DANA - 081234567890 - ALDI KENZ`"
            )

        rekening = parts[0]
        nomor = parts[1]
        nama = "-".join(parts[2:]).strip()

        if not rekening or not nomor or not nama:
            return await event.reply(
                "⚠️ **Format rekening tidak valid.**\n"
                "Gunakan format:\n"
                "`DANA - 081234567890 - ALDI KENZ`"
            )

        amount = session.get("amount") or 0

        cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        balance = row[0] if row else 0

        if amount <= 0 or balance < amount:
            withdraw_sessions.pop(user_id, None)
            saldo_fmt = f"Rp{balance:,}".replace(",", ".")
            return await event.reply(
                f"🚫 **Saldo tidak mencukupi / nominal invalid.**\n"
                f"💳 Saldo sekarang: `{saldo_fmt}`"
            )

        withdraw_id = generate_withdraw_id(25)

        now_ts = int(time.time())

        new_balance = balance - amount
        cur.execute(
            "UPDATE user_balance SET balance=? WHERE user_id=?",
            (new_balance, user_id)
        )
        conn.commit()

        cur.execute("""
            INSERT INTO withdraw_requests (
                withdraw_id, user_id, amount, account_info,
                status, created_at, updated_at, topic_msg_id, extra
            )
            VALUES (?, ?, ?, ?, 'pending', ?, ?, NULL, NULL)
        """, (
            withdraw_id,
            user_id,
            amount,
            account_info,
            now_ts,
            now_ts
        ))
        conn.commit()

        withdraw_sessions.pop(user_id, None)

        amount_fmt = f"Rp{amount:,}".replace(",", ".")
        saldo_fmt = f"Rp{new_balance:,}".replace(",", ".")

        msg_user = f"""
📤 **REQUEST WITHDRAW PENDING!**

🆔 Withdraw ID: `{withdraw_id}`
💰 Nominal: `{amount_fmt}`
🏦 Rekening: `{account_info}`

Status saat ini: `PENDING`
💳 **Saldo kamu sekarang:** `{saldo_fmt}`

^^__Tunggu admin memproses withdraw kamu. Bot otomatis akan mengirim notifikasi setelah diproses.__^^
        """.strip()

        await event.reply(msg_user)
        await logs.send_message(CHLOGS, f"{user_id} input nomor rekening untuk withdraw.")

        try:
            if "WithdrawLogs" in slug_channel_map:
                topic_chat_id, topic_msg_id = slug_channel_map["WithdrawLogs"]

                try:
                    user_ent = await bot.get_entity(user_id)
                    user_username = f"@{user_ent.username}" if user_ent.username else f"[{user_ent.id}](tg://user?id={user_ent.id})"
                    user_name = (user_ent.first_name or "") + " " + (user_ent.last_name or "")
                    user_name = user_name.strip() or str(user_id)
                except Exception:
                    user_username = f"`{user_id}`"
                    user_name = str(user_id)

                created_dt = datetime.fromtimestamp(now_ts, TZ_JAKARTA)
                created_str = created_dt.strftime("%d-%m-%Y %H:%M:%S")

                topic_text = f"""
📤 **NEW WITHDRAW REQUEST**

**Withdraw ID:** `{withdraw_id}`
**User:** {user_username} (`{user_id}`)
**Name:** `{user_name}`
**Nominal:** `{amount_fmt}`
**Status:** `PENDING`

⏰ **WAKTU:** `{created_str}`
                """.strip()
                
                buttons = [
                  [Button.url("💰 PROSES", f"https://t.me/marketaldibot?start=wd_{withdraw_id}"),
                   Button.inline("🚫 REJECT", data=f"rejectwd_{withdraw_id}")]
                  ]

                sent_topic = await bot.send_message(
                    topic_chat_id,
                    topic_text,
                    buttons=buttons,
                    reply_to=topic_msg_id
                )

                cur.execute("""
                    UPDATE withdraw_requests
                    SET topic_msg_id=?, updated_at=?
                    WHERE withdraw_id=?
                """, (sent_topic.id, int(time.time()), withdraw_id))
                conn.commit()
            else:
                print("ℹ️ Key 'WithdrawLogs' tidak ada di slug_channel_map, skip notif topic.")
        except Exception as e:
            print(f"⚠️ Gagal kirim notif WithdrawLogs ke topic: {e}")

@bot.on(events.CallbackQuery(pattern=b"^rejectwd_(.+)$"))
async def reject_withdraw(event):
    admin_id = event.sender_id

    # Cek hak akses
    if admin_id not in OWNER_SALDO:
        try:
            await event.answer("🚫 Kamu tidak punya akses untuk reject withdraw.", alert=True)
            await logs.send_message(CHLOGS, f"{user_id} mencoba menekan tombol 🚫 REJECT withdraw di topic logs.")
        except:
            pass
        return

    withdraw_id = event.pattern_match.group(1).decode().strip()

    cur.execute("""
        SELECT id, user_id, amount, status, topic_msg_id
        FROM withdraw_requests
        WHERE withdraw_id=?
    """, (withdraw_id,))
    row = cur.fetchone()

    if not row:
        try:
            await event.answer("⚠️ Withdraw ID tidak ditemukan.", alert=True)
        except:
            pass
        return

    row_id, user_id, amount, status_row, topic_msg_id = row

    if status_row != "pending":
        try:
            await event.answer(f"⚠️ Withdraw status bukan PENDING (sekarang: {status_row}).", alert=True)
        except:
            pass
        return

    now_ts = int(time.time())

    cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (user_id,))
    row_bal = cur.fetchone()
    balance = row_bal[0] if row_bal else 0
    new_balance = balance + amount

    if row_bal is None:
        cur.execute(
            "INSERT INTO user_balance (user_id, balance) VALUES (?, ?)",
            (user_id, new_balance)
        )
    else:
        cur.execute(
            "UPDATE user_balance SET balance=? WHERE user_id=?",
            (new_balance, user_id)
        )
    conn.commit()

    cur.execute("""
        UPDATE withdraw_requests
        SET status='rejected', updated_at=?
        WHERE id=?
    """, (now_ts, row_id))
    conn.commit()

    amount_fmt = f"Rp{amount:,}".replace(",", ".")
    new_balance_fmt = f"Rp{new_balance:,}".replace(",", ".")

    try:
        msg_user = f"""
🚫 **WITHDRAW ANDA DITOLAK**

🆔 Withdraw ID: `{withdraw_id}`
💰 Nominal: `{amount_fmt}`

^^Withdraw anda ditolak oleh admin, jika ini sebuah kesalahan segera hubungi admin dan saldo anda berhasil di kembalikan!^^
        """.strip()
        await bot.send_message(user_id, msg_user)
    except Exception as e:
        print(f"⚠️ Gagal kirim notif reject ke user {user_id}: {e}")

    try:
        await event.answer("✅ Withdraw berhasil direject & saldo dikembalikan.", alert=True)
        await event.delete()
    except:
        pass
      
@bot.on(events.NewMessage(pattern=r"^/start\s+wd_(.+)$"))
async def start_withdraw_proof(event):
    admin_id = event.sender_id

    if admin_id not in OWNER_SALDO:
        await event.reply("🚫 Kamu tidak punya akses untuk memproses withdraw.")
        await logs.send_message(CHLOGS, f"{user_id} mencoba start params untuk 💰 PROSES withdraw.")
        return

    withdraw_id = event.pattern_match.group(1).strip()

    cur.execute("""
        SELECT id, user_id, amount, status, account_info
        FROM withdraw_requests
        WHERE withdraw_id=?
    """, (withdraw_id,))
    row = cur.fetchone()

    if not row:
        return await event.reply("⚠️ Withdraw ID tidak ditemukan.")

    _row_id, user_id, amount, status_row, account_info = row

    if status_row != "pending":
        return await event.reply(f"⚠️ Withdraw ini tidak dalam status PENDING (sekarang: `{status_row}`).")

    withdraw_proof_sessions[admin_id] = {
        "withdraw_id": withdraw_id,
        "user_id": user_id,
        "amount": amount,
        "account_info": account_info,
    }

    amount_fmt = f"Rp{amount:,}".replace(",", ".")

    msg = f"""
📤 **PROSES WITHDRAW USER**

🆔 Withdraw ID: `{withdraw_id}`
👤 User ID: `{user_id}`
💰 Nominal: `{amount_fmt}`
🏦 Rekening: `{account_info}`

__Silakan kirim foto bukti transfer disini, bot akan forward ke user dan sebagai bukti!__
    """.strip()
    
    buttons = [
      [Button.inline("🚫 BATALKAN", data="back_gift")]]

    await event.reply(msg, buttons=buttons)
    
@bot.on(events.NewMessage(func=lambda e: e.sender_id in withdraw_proof_sessions and e.photo))
async def handle_withdraw_proof_photo(event):
    admin_id = event.sender_id
    session = withdraw_proof_sessions.get(admin_id)
    if not session:
        return

    withdraw_id = session["withdraw_id"]

    cur.execute("""
        SELECT id, user_id, amount, status
        FROM withdraw_requests
        WHERE withdraw_id=?
    """, (withdraw_id,))
    row = cur.fetchone()

    if not row:
        withdraw_proof_sessions.pop(admin_id, None)
        return await event.reply("⚠️ Withdraw ID tidak ditemukan (mungkin sudah dihapus).")

    row_id, user_id, amount, status_row = row

    if status_row != "pending":
        withdraw_proof_sessions.pop(admin_id, None)
        return await event.reply(f"⚠️ Withdraw ini tidak lagi PENDING (status: `{status_row}`).")

    extra = {
        "proof_msg_id": event.id,
        "proof_admin_id": admin_id,
    }

    cur.execute("""
        UPDATE withdraw_requests
        SET extra=?, updated_at=?
        WHERE id=?
    """, (json.dumps(extra), int(time.time()), row_id))
    conn.commit()

    amount_fmt = f"Rp{amount:,}".replace(",", ".")

    caption = f"""
📤 **BUKTI TRANSFER WITHDRAW TERSIMPAN**

🆔 Withdraw ID: `{withdraw_id}`
👤 User ID: `{user_id}`
💰 Nominal: `{amount_fmt}`

__Klik tombol di bawah ini untuk **CONFIRM WITHDRAW**.__
    """.strip()

    buttons = [
        [Button.inline("✅ CONFIRM WITHDRAW", data=f"confirmwd_{withdraw_id}")]
    ]

    await event.reply(caption, buttons=buttons)
    
@bot.on(events.CallbackQuery(pattern=b"^confirmwd_(.+)$"))
async def confirm_withdraw(event):
    admin_id = event.sender_id

    if admin_id not in OWNER_SALDO:
        try:
            await event.answer("🚫 Kamu tidak punya akses untuk confirm withdraw.", alert=True)
            await logs.send_message(CHLOGS, f"{user_id} mencoba menekan tombol ✅ PROSES WITHDRAW khusus admin.")
        except:
            pass
        return

    withdraw_id = event.pattern_match.group(1).decode().strip()

    cur.execute("""
        SELECT id, user_id, amount, status, topic_msg_id, user_msg_id, extra
        FROM withdraw_requests
        WHERE withdraw_id=?
    """, (withdraw_id,))
    row = cur.fetchone()

    if not row:
        try:
            await event.answer("⚠️ Withdraw ID tidak ditemukan.", alert=True)
        except:
            pass
        return

    row_id, user_id, amount, status_row, topic_msg_id, user_msg_id, extra_json = row

    if status_row != "pending":
        try:
            await event.answer(f"⚠️ Withdraw ini tidak lagi PENDING (status: {status_row}).", alert=True)
        except:
            pass
        return

    extra = {}
    if extra_json:
        try:
            extra = json.loads(extra_json)
        except Exception:
            extra = {}

    proof_msg_id = extra.get("proof_msg_id")
    proof_admin_id = extra.get("proof_admin_id")

    now_ts = int(time.time())
    now_wib_str = datetime.fromtimestamp(now_ts, TZ_JAKARTA).strftime("%d-%m-%Y %H:%M:%S")

    cur.execute("""
        UPDATE withdraw_requests
        SET status='paid', updated_at=?
        WHERE id=?
    """, (now_ts, row_id))
    conn.commit()

    amount_fmt = f"Rp{amount:,}".replace(",", ".")

    try:
        if "WithdrawLogs" in slug_channel_map and topic_msg_id:
            topic_chat_id, topic_root_msg_id = slug_channel_map["WithdrawLogs"]

            cur.execute("""
                SELECT withdraw_id, user_id, amount, account_info, status, created_at, updated_at
                FROM withdraw_requests
                WHERE id=?
            """, (row_id,))
            wd = cur.fetchone()

            if not wd:
                print("⚠️ Withdraw tidak ditemukan saat update WithdrawLogs.")
                return

            (wd_withdraw_id,
             wd_user_id,
             wd_amount,
             wd_account_info,
             wd_status,
             wd_created_at,
             wd_updated_at) = wd

            amount_fmt = f"Rp{wd_amount:,}".replace(",", ".")

            created_str = datetime.fromtimestamp(wd_created_at, TZ_JAKARTA).strftime("%d-%m-%Y %H:%M:%S")
            updated_str = datetime.fromtimestamp(wd_updated_at, TZ_JAKARTA).strftime("%d-%m-%Y %H:%M:%S")

            try:
                user_ent = await bot.get_entity(wd_user_id)
                user_username = f"@{user_ent.username}" if user_ent.username else f"[{user_ent.id}](tg://user?id={user_ent.id})"
                user_name = (user_ent.first_name or "") + " " + (user_ent.last_name or "")
                user_name = user_name.strip() or str(wd_user_id)
            except Exception:
                user_username = f"`{wd_user_id}`"
                user_name = str(wd_user_id)

            caption_topic = f"""
📤 **WITHDRAW REQUEST (SUCCESS)**

🆔 **Withdraw ID:** `{wd_withdraw_id}`
👤 **User:** {user_username} (`{wd_user_id}`)
👥 **Name:** `{user_name}`
💰 **Nominal:** `{amount_fmt}`
✅ **STATUS:** `SUCCESSFULLY`
💻 **Admin:** `{admin_id}`
⏰ **Request time:** `{created_str} WIB`
⏰ **Success time:** `{updated_str} WIB`

**__-- MARKETPLACE BY: @WINEDASH --__**
            """.strip()

            if proof_msg_id and proof_admin_id:
                try:
                    proof_msg = await bot.get_messages(proof_admin_id, ids=proof_msg_id)
                    media = proof_msg.media

                    await bot.edit_message(
                        topic_chat_id,
                        topic_msg_id,
                        file=media,
                        text=caption_topic
                    )
                except Exception as e:
                    print(f"⚠️ Gagal edit WithdrawLogs dengan foto: {e}")
                    try:
                        await bot.edit_message(topic_chat_id, topic_msg_id, caption_topic)
                    except Exception as e2:
                        print(f"⚠️ Gagal edit teks WithdrawLogs: {e2}")
            else:
                await bot.edit_message(topic_chat_id, topic_msg_id, caption_topic)
    except Exception as e:
        print(f"⚠️ Error update WithdrawLogs (confirm): {e}")

    try:
        if user_msg_id:
            try:
                user_msg = await bot.get_messages(user_id, ids=user_msg_id)
                old_text_user = user_msg.message or ""
            except Exception:
                old_text_user = ""

            success_info = (
                f"\n\n✅ **STATUS WITHDRAW:** `BERHASIL DIBAYAR`\n"
                f"⏰ Updated At: `{now_wib_str} WIB`"
            )

            new_text_user = (old_text_user + success_info).strip()

            await bot.edit_message(
                user_id,
                user_msg_id,
                new_text_user
            )
    except Exception as e:
        print(f"⚠️ Gagal edit pesan pending user: {e}")

    try:
        proof_caption = f"""
✅ **WITHDRAW BERHASIL DIBAYAR!**

🆔 Withdraw ID: `{withdraw_id}`
💰 Nominal: `{amount_fmt}`

^^Terimakasih telah menggunakan layanan marketplace kami, foto diatas adalah bukti transfer admin!^^
        """.strip()

        if proof_msg_id and proof_admin_id:
            try:
                await bot.forward_messages(
                    user_id,
                    messages=proof_msg_id,
                    from_peer=proof_admin_id
                )
                await bot.send_message(user_id, proof_caption)
            except Exception as e:
                print(f"⚠️ Gagal forward bukti ke user: {e}")
                await bot.send_message(user_id, proof_caption)
        else:
            await bot.send_message(user_id, proof_caption)
    except Exception as e:
        print(f"⚠️ Gagal kirim info sukses ke user: {e}")

    try:
        await event.answer("✅ Withdraw dikonfirmasi berhasil (PAID).", alert=True)
        await event.delete()
    except:
        pass

@bot.on(events.CallbackQuery(pattern=b"^rdeposit_(.+)$"))
async def rdeposit_callback(event):
    user_id = event.sender_id
    transaction_id = event.pattern_match.group(1).decode().strip()

    cur.execute("""
        SELECT amount, status
        FROM deposit_qris
        WHERE transaction_id=? AND user_id=?
    """, (transaction_id, user_id))
    row = cur.fetchone()

    if not row:
        return await event.answer("⚠️ Deposit tidak ditemukan untuk akun ini.", alert=True)

    amount, status_row = row
    if status_row != "expired":
        return await event.answer("⚠️ Deposit ini belum / tidak berstatus EXPIRED.", alert=True)

    deposit_report_session[user_id] = {
        "transaction_id": transaction_id,
        "media": None,
        "caption": ""
    }

    text = f"""
📮 **LAPORAN DEPOSIT EXPIRED**

Silakan kirim **screenshot bukti transfer / pembayaran** disertai **caption (teks)** dalam **1x kirim**.

**Transaction ID:** `{transaction_id}`

⚠️ Kirim sekarang dalam bentuk:
- Foto + caption (teks laporan)
    """.strip()

    await event.answer()
    await event.respond(text)
    await logs.send_message(CHLOGS, f"{user_id} menekan tombol laporan deposit expired.")

@bot.on(events.NewMessage)
async def handle_deposit_report_input(event):
    user_id = event.sender_id

    if user_id not in deposit_report_session:
        return

    if not event.media:
        return await event.reply("⚠️ Kirim bukti dalam bentuk **foto + caption teks** dalam satu kali kirim.")
    if not (event.raw_text or "").strip():
        return await event.reply("⚠️ Tambahkan **caption teks** di foto laporan deposit Anda.")

    data = deposit_report_session[user_id]
    transaction_id = data["transaction_id"]

    deposit_report_session[user_id]["media"] = event.message
    deposit_report_session[user_id]["caption"] = (event.raw_text or "").strip()

    buttons = [
        [Button.inline("✅ KONFIRMASI LAPORAN", data=f"user_confirm_rdeposit_{user_id}".encode())],
        [Button.inline("🚫 BATALKAN LAPORAN", data=f"user_cancel_rdeposit_{user_id}".encode())]
    ]

    msg = f"""
📮 **KONFIRMASI LAPORAN DEPOSIT EXPIRED**

**Transaction ID:** `{transaction_id}`

Pastikan bukti & caption yang Anda kirim sudah benar.
Tekan tombol **KONFIRMASI LAPORAN** untuk mengirim ke admin,
atau **BATALKAN LAPORAN** untuk membatalkan.
    """.strip()

    await event.reply(msg, buttons=buttons)
    await logs.send_message(CHLOGS, f"{user_id} mengirim input laporan deposit expired")

@bot.on(events.CallbackQuery(pattern=b"^user_cancel_rdeposit_(\d+)$"))
async def user_cancel_rdeposit(event):
    user_id_btn = int(event.pattern_match.group(1).decode())
    if event.sender_id != user_id_btn:
        return await event.answer("⚠️ Ini bukan laporan milik Anda.", alert=True)

    deposit_report_session.pop(user_id_btn, None)

    try:
        await event.edit("❌ Laporan deposit telah dibatalkan.")
    except Exception:
        pass

    await event.answer("Laporan deposit dibatalkan.", alert=True)
    await logs.send_message(CHLOGS, f"{user_id} membatalkan laporan deposit expired")

@bot.on(events.CallbackQuery(pattern=b"^user_confirm_rdeposit_(\d+)$"))
async def user_confirm_rdeposit(event):
    user_id = int(event.pattern_match.group(1).decode())
    if event.sender_id != user_id:
        return await event.answer("⚠️ Ini bukan laporan milik Anda.", alert=True)

    data = deposit_report_session.get(user_id)
    if not data:
        return await event.answer("⚠️ Tidak ada laporan deposit untuk dikonfirmasi.", alert=True)

    transaction_id = data["transaction_id"]
    media_file = data["media"]
    caption_user = data["caption"]

    session_id = make_rdeposit_session_id(user_id, transaction_id)
    admin_rdeposit_session[session_id] = {
        "transaction_id": transaction_id,
        "user_id": user_id,
        "media": media_file,
        "caption": caption_user,
    }

    buttons = [
        [
            Button.inline("✅ KONFIRMASI (ADMIN)", data=f"admin_confirm_rdeposit_{session_id}".encode()),
            Button.inline("🚫 BATALKAN (ADMIN)", data=f"admin_cancel_rdeposit_{session_id}".encode()),
        ]
    ]

    caption = f"""
❗️ **LAPORAN DEPOSIT EXPIRED USER!**

**Transaction ID: `{transaction_id}`**
**User ID:** [{user_id}](tg://user?id={user_id})

%%{caption_user}%%
    """.strip()

    try:
        await bot.send_file(
            GROUP_ADMIN,
            media_file,
            caption=caption,
            buttons=buttons
        )
        try:
            await event.delete()
        except Exception:
            pass

        await event.respond("✅ **__Laporan deposit Anda telah dikirim dan menunggu konfirmasi admin!__**")
        await logs.send_message(CHLOGS, f"{user_id} mengonfirmasi laporan deposit expired.")
    except Exception as e:
        print(f"⚠️ Gagal forward laporan deposit {transaction_id}: {e}")
        await event.answer("❌ Gagal kirim laporan deposit ke admin.", alert=True)

    deposit_report_session.pop(user_id, None)

@bot.on(events.CallbackQuery(pattern=b"^admin_confirm_rdeposit_(.+)$"))
async def admin_confirm_rdeposit(event):
    admin_id = event.sender_id

    if admin_id not in OWNER_SALDO:
        return await event.answer("⚠️ Kamu tidak berhak mengkonfirmasi saldo.", alert=True)

    session_id = event.pattern_match.group(1).decode()
    data = admin_rdeposit_session.get(session_id)
    if not data:
        return await event.answer("⚠️ Data laporan tidak ditemukan / sudah kadaluwarsa.", alert=True)

    transaction_id = data["transaction_id"]
    user_id = data["user_id"]

    cur.execute("SELECT amount FROM deposit_qris WHERE transaction_id=? AND user_id=?", (transaction_id, user_id))
    row = cur.fetchone()
    if not row:
        return await event.answer("⚠️ Deposit tidak ditemukan.", alert=True)
    amount = row[0]

    now_ts = int(time.time())
    cur.execute("""
        UPDATE deposit_qris
        SET status='paid', paid_at=?, last_check=?
        WHERE transaction_id=? AND user_id=?
    """, (now_ts, now_ts, transaction_id, user_id))
    conn.commit()

    cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (user_id,))
    row_bal = cur.fetchone()
    if row_bal:
        new_balance = (row_bal[0] or 0) + amount
        cur.execute("UPDATE user_balance SET balance=? WHERE user_id=?", (new_balance, user_id))
    else:
        cur.execute("INSERT INTO user_balance (user_id, balance) VALUES (?, ?)", (user_id, amount))
    conn.commit()

    try:
        amount_fmt = f"Rp{amount:,}".replace(",", ".")

        msg = f"""
✅ **LAPORAN DI KONFIRMASI ADMIN!**

**Transaction ID: `{transaction_id}`**
**Saldo anda:** `{amount_fmt}`

^^Terimakasih atas laporan anda dan telah memberikan kepercayaan kepada admin WINEDASH, Kami mengucapkan banyak permintaan maaf apabila kendala ini benar-benar membuat anda kecewa... 🙏🏻^^
        """.strip()

        await bot.send_message(user_id, msg)
        try:
            await event.edit(f"✅ Deposit `{transaction_id}` telah dikonfirmasi oleh admin.")
        except Exception:
            pass
    except Exception as e:
        print(f"⚠️ Gagal notif user {user_id}: {e}")

    admin_rdeposit_session.pop(session_id, None)


@bot.on(events.CallbackQuery(pattern=b"^admin_cancel_rdeposit_(.+)$"))
async def admin_cancel_rdeposit(event):
    admin_id = event.sender_id

    if admin_id not in OWNER_SALDO:
        return await event.answer("⚠️ Kamu tidak berhak membatalkan laporan.", alert=True)

    session_id = event.pattern_match.group(1).decode()
    data = admin_rdeposit_session.get(session_id)
    if not data:
        return await event.answer("⚠️ Data laporan tidak ditemukan / sudah kadaluwarsa.", alert=True)

    transaction_id = data["transaction_id"]
    user_id = data["user_id"]

    cur.execute(
        "UPDATE deposit_qris SET last_check=? WHERE transaction_id=? AND user_id=?",
        (int(time.time()), transaction_id, user_id)
    )
    conn.commit()

    try:
        msg = f"""
❗️ **LAPORAN DEPOSIT EXPIRED DITOLAK!**

**Transaction ID: `{transaction_id}`**
%%Segera hubungi admin jika tindakan ini membuat pertanyaan dari diri anda sendiri, Saya harap anda melakukan laporan sekali lagi terlebih dahulu sebelum menghubungi admin.%%
        """.strip()
        await bot.send_message(user_id, msg)
        try:
            await event.edit(f"❌ Deposit `{transaction_id}` ditolak oleh admin.")
        except Exception:
            pass
    except Exception as e:
        print(f"⚠️ Gagal notif user {user_id}: {e}")

    admin_rdeposit_session.pop(session_id, None)

@bot.on(events.CallbackQuery(pattern=b"^deposit$"))
async def deposit_menu(event):
    user_id = event.sender_id

    try:
        await event.answer()
    except:
        pass

    deposit_sessions[user_id] = True

    msg = f"""
💳 **DEPOSIT SALDO**

__Silakan kirim angka untuk jumlah deposit anda, contoh: 10000 (maka deposit anda adalah 10.000), anda tidak perlu mengirim bukti screenshot setelah deposit karena bot ini menggunakan qris otomatis.__

^^• Klik 🚫 BATALKAN untuk dibatalkan.^^
"""

    buttons = [
      [Button.inline("🚫 BATALKAN", data="back_gift")]
    ]

    await event.respond(msg, buttons=buttons)
    await event.delete()
    await logs.send_message(CHLOGS, f"{user_id} menekan tombol 💳 DEPOSIT")

@bot.on(events.NewMessage)
async def handle_deposit_input(event):
    user_id = event.sender_id

    if user_id not in deposit_sessions:
        return

    if event.is_group or event.is_channel:
        return
    if event.raw_text.startswith("/"):
        return

    text = (event.raw_text or "").strip().replace(" ", "")
    if not text.isdigit():
        return await event.reply(
            "⚠️ **Nominal deposit harus berupa angka tanpa titik/koma.**\n"
            "Contoh:\n`10000`\n`25000`\n`100000`"
        )

    amount = int(text)

    if amount > 10_000_000:
        return await event.reply("⚠️ **Maksimal deposit adalah 10.000.000**.\nSilakan kirim nominal lagi.")

    cur.execute("""
        SELECT COUNT(*) FROM deposit_qris 
        WHERE user_id=? AND status='pending'
    """, (user_id,))
    pending_count = cur.fetchone()[0]
    if pending_count >= 3:
        deposit_sessions.pop(user_id, None)
        return await event.reply(
            "🚫 __Tidak dapat membuat permintaan deposit kembali, anda sedang memiliki status deposit yang pending, tunggu hingga expired untuk melakukan deposit ulang!__"
        )

    loading = await event.respond("⏳ Sedang generate QRIS deposit...")

    try:
        result = generate_qris_v2(amount)
        if not result["success"]:
            deposit_sessions.pop(user_id, None)
            await loading.edit(f"❌ Gagal generate QRIS.\nError: `{result['error']}`")
            return

        data = result["data"]
        qr_string = data.get("qr_string")
        if not qr_string:
            deposit_sessions.pop(user_id, None)
            await loading.edit("❌ Respon Cashify tidak mengandung `qr_string`.")
            return

        transaction_id = data.get("transactionId")
        if not transaction_id:
            deposit_sessions.pop(user_id, None)
            await loading.edit("❌ Respon Cashify tidak mengandung `transactionId`.")
            return

        total_amount_raw = data.get("totalAmount", amount)
        if isinstance(total_amount_raw, str):
            total_amount_raw = total_amount_raw.replace(".", "").replace(",", "")
        try:
            total_amount = int(total_amount_raw)
        except:
            total_amount = amount

        now_ts = int(time.time())
        expired_ts = now_ts + 5 * 60

        qr_url = build_qr_image_url(qr_string)
        harga_fmt = f"Rp{total_amount:,}".replace(",", ".")

        caption = f"""
🧾 **DEPOSIT SALDO (PENDING)**

🆔 User ID: `{user_id}`
📄 Transaction ID: `{transaction_id}`
💰 Nominal Deposit: `{harga_fmt}`
⏰ Expired: `after 5 minutes`

^^**__Silakan scan QRIS di atas, jangan ubah nominal saat membayar. Jika terjadi sebuah kesalahan segera hubungi admin dan simpan bukti screenshot transfer anda!__**^^
        """.strip()

        msg_bayar = await bot.send_file(
            event.chat_id,
            file=qr_url,
            caption=caption,
        )

        await loading.delete()
        await logs.send_message(CHLOGS, f"{user_id} mengirim input jumlah deposit {harga_fmt}")
        deposit_sessions.pop(user_id, None)
        topic_msg_id = None

        try:
            deposit_key = "DepositLogs"

            if deposit_key in slug_channel_map:
                dep_chat_id, dep_topic_id = slug_channel_map[deposit_key]

                reply_to_dep = await get_topic_entry_msg_id(dep_chat_id, dep_topic_id)

                if reply_to_dep:
                    notif_topic_text = f"""
💳 **PENDING DEPOSIT BARU**

🧑‍💻 User: [`{user_id}`](tg://user?id={user_id})
📄 Transaction ID: `{transaction_id}`
💰 Nominal: `{harga_fmt}`
⏱️ Status: `PENDING`

^^Deposit ini masih menunggu pembayaran via QRIS.^^
                    """.strip()

                    notif_msg = await bot.send_message(
                        dep_chat_id,
                        notif_topic_text,
                        reply_to=reply_to_dep
                    )
                    topic_msg_id = notif_msg.id
                else:
                    print("⚠️ Gagal ambil reply_to topic untuk deposit, notif topic tidak dikirim.")
            else:
                print("ℹ️ slug_channel_map tidak punya key 'deposit', notif topic di-skip.")

        except Exception as e:
            print(f"⚠️ Gagal kirim notif deposit ke topic: {e}")
            topic_msg_id = None

        cur.execute("""
            INSERT INTO deposit_qris (
                user_id, transaction_id, amount, status, created_at, expired_at, last_check,
                message_id, chat_id, topic_msg_id
            )
            VALUES (?, ?, ?, 'pending', ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            transaction_id,
            total_amount,
            now_ts,
            expired_ts,
            now_ts,
            msg_bayar.id,
            event.chat_id,
            topic_msg_id
        ))
        conn.commit()

        async def auto_delete_after_expired(m):
            await asyncio.sleep(5 * 60)
            try:
                await m.delete()
            except:
                pass

        asyncio.create_task(auto_delete_after_expired(msg_bayar))

    except Exception as e:
        print("❌ Error di handle_deposit_input:", repr(e))
        deposit_sessions.pop(user_id, None)
        try:
            await loading.edit(f"⚠️ Terjadi kesalahan saat generate QRIS:\n`{e}`")
        except:
            pass

@bot.on(events.NewMessage(pattern=r"^([+\-#%])saldo\b"))
async def owner_saldo_handler(event):
    sender_id = event.sender_id
    if sender_id not in OWNER_ID:
        return

    text = (event.raw_text or "").strip()
    parts = text.split()

    op = parts[0][0]

    if op in ["+", "-"]:
        if len(parts) < 3:
            return await event.reply(
                "❌ Format salah.\n\n"
                "**Tambah saldo:**\n`+saldo <user_id/username> <jumlah>`\n"
                "**Kurangi saldo:**\n`-saldo <user_id/username> <jumlah>`\n"
                "**Reset saldo:**\n`#saldo <user_id/username>`\n"
                "**Cek saldo:**\n`%saldo <user_id/username>`"
            )
        raw_user = parts[1]
        raw_amount = parts[2]

    elif op in ["#", "%"]:
        if len(parts) < 2:
            return await event.reply(
                "❌ Format salah.\n\n"
                "**Reset saldo:**\n`#saldo <user_id/username>`\n"
                "**Cek saldo:**\n`%saldo <user_id/username>`"
            )
        raw_user = parts[1]
        raw_amount = None

    target_id = await _resolve_target_user(bot, raw_user)
    if not target_id:
        return await event.reply(f"❌ Tidak bisa menemukan user: `{raw_user}`")

    cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (target_id,))
    row = cur.fetchone()
    current_balance = row[0] if row else 0

    # =========================
    # 🔍 CEK SALDO (%saldo)
    # =========================
    if op == "%":
        balance_fmt = f"Rp{current_balance:,}".replace(",", ".")

        try:
            ent = await bot.get_entity(target_id)
            uname = f"@{ent.username}" if getattr(ent, "username", None) else "-"
            mention = f"[{getattr(ent, 'first_name', 'User')}](tg://user?id={target_id})"
        except Exception:
            uname = "-"
            mention = f"`{target_id}`"

        msg = f"""
💰 **CEK SALDO USER**

👤 User: {mention}
🆔 ID: `{target_id}`
🏷️ Username: {uname}

📊 **Saldo saat ini:** `{balance_fmt}`
        """.strip()

        await event.reply(msg)
        return

    # =========================
    # ➕ / ➖ TAMBAH / KURANGI
    # =========================
    if op in ["+", "-"]:
        if not raw_amount.isdigit():
            return await event.reply("❌ Jumlah saldo harus berupa angka (contoh: `10000`).")

        delta = int(raw_amount)
        if delta <= 0:
            return await event.reply("❌ Jumlah harus lebih besar dari 0.")

        if op == "+":
            new_balance = current_balance + delta
            action = "MENAMBAHKAN"
            sign = "+"
        else:
            new_balance = max(0, current_balance - delta)
            action = "MENGURANGI"
            sign = "-"

        if row is None:
            cur.execute(
                "INSERT INTO user_balance (user_id, balance) VALUES (?, ?)",
                (target_id, new_balance)
            )
        else:
            cur.execute(
                "UPDATE user_balance SET balance=? WHERE user_id=?",
                (new_balance, target_id)
            )
        conn.commit()

        current_fmt = f"Rp{current_balance:,}".replace(",", ".")
        delta_fmt = f"Rp{delta:,}".replace(",", ".")
        new_fmt = f"Rp{new_balance:,}".replace(",", ".")

        try:
            ent = await bot.get_entity(target_id)
            uname = f"@{ent.username}" if getattr(ent, "username", None) else "-"
            mention = f"[{getattr(ent, 'first_name', 'User')}](tg://user?id={target_id})"
        except Exception:
            uname = "-"
            mention = f"`{target_id}`"

        msg = f"""
🛠️ **ADMIN SALDO — {action} SALDO USER**

👤 User: {mention}
🆔 ID: `{target_id}`
🏷️ Username: {uname}

💰 Saldo awal: `{current_fmt}`
{sign} Perubahan: `{delta_fmt}`
📊 Saldo baru: `{new_fmt}`
        """.strip()
        
        msg_target = f"""
💰 **__Admin {action} saldo anda!__**

**Saldo awal:** ~~{current_fmt}~~ {sign}{delta_fmt}
**Saldo baru:** {new_fmt}
        """

        await event.reply(msg)
        await bot.send_message(target_id, msg_target)
        return

    # =========================
    # ♻️ RESET SALDO (#saldo)
    # =========================
    elif op == "#":
        new_balance = 0

        if row is None:
            cur.execute(
                "INSERT INTO user_balance (user_id, balance) VALUES (?, ?)",
                (target_id, new_balance)
            )
        else:
            cur.execute(
                "UPDATE user_balance SET balance=? WHERE user_id=?",
                (new_balance, target_id)
            )
        conn.commit()

        current_fmt = f"Rp{current_balance:,}".replace(",", ".")
        new_fmt = f"Rp{new_balance:,}".replace(",", ".")

        try:
            ent = await bot.get_entity(target_id)
            uname = f"@{ent.username}" if getattr(ent, "username", None) else "-"
            mention = f"[{getattr(ent, 'first_name', 'User')}](tg://user?id={target_id})"
        except Exception:
            uname = "-"
            mention = f"`{target_id}`"

        msg = f"""
🛠️ **ADMIN SALDO — RESET SALDO USER**

👤 User: {mention}
🆔 ID: `{target_id}`
🏷️ Username: {uname}

💰 Saldo sebelumnya: `{current_fmt}`
📊 Saldo baru: `{new_fmt}`

✅ Saldo user telah di-reset menjadi 0.
        """.strip()
        
        msg_reset = f"""
🔄 **SALDO ANDA DI RESET OLEH ADMIN!**

__Jika ini sebuah kesalahan, segera hubungi admin!__

💰 **Saldo:** ~~{current_fmt}~~ **{new_fmt}**
        """

        await event.reply(msg)
        await bot.send_message(target_id, msg_reset)
        export_user_to_json(target_id)
        push_user_json_to_github(target_id)
        return

@bot.on(events.CallbackQuery(data=b"rent"))
async def handle_rent(event):
    user_id = event.sender_id
    
    buttons = [
      [Button.inline("🗑️ DELETE RENT", data="del_rent"),
      Button.inline("⌚️ ADD RENT", data="add_rent")],
      [Button.inline("🎁 INVENTORY", data="my_rent"),
      Button.inline("📊 STATUS RENT", data="status_rent")],
      [Button.inline("🔎 SEARCH RENT", data="search_rent"),
      Button.inline("🔙 KEMBALI", data="back_gift")],
      [Button.inline("💻 QUESTION & BANTUAN", data="bantuan")]
    ]
    
    msg = f"""
⌚️ **__Hallo... {user_id} anda membuka menu RENTAL GIFT, silahkan klik tombol dibawah ini!__**
    """
    
    await event.edit(msg, buttons=buttons)
    await logs.send_message(CHLOGS, f"{user_id} menekan tombol ⌚ GIFT RENT️")

@bot.on(events.CallbackQuery(data=b"del_rent"))
async def del_rent(event):
    user_id = event.sender_id

    cur.execute("SELECT slug, model FROM gift_rent WHERE user_id=?", (user_id,))
    gifts = cur.fetchall()

    if not gifts:
        return await event.answer("❌ Kamu belum punya gift rental yang tersimpan.", alert=True)

    selected_gifts[user_id] = set()

    buttons = []
    row = []
    for i, (slug, model) in enumerate(gifts, start=1):
        label = f"{slug}"
        row.append(Button.inline(label, data=f"selgift_{slug}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append([
        Button.inline("🗑️ DELETE", data="confirm_delete_selected"),
        Button.inline("🗑️ DELETE ALL", data="confirm_delete_all")
    ])
    buttons.append([Button.inline("🔙 KEMBALI", data="rent")])

    msg = f"""
🗑️ **HAPUS GIFT RENTAL**

Pilih gift yang ingin kamu hapus dengan menekan tombol di bawah.
Klik ulang untuk membatalkan pilihan ✅.

Setelah memilih, tekan **DELETE** untuk menghapus yang dipilih
atau **DELETE ALL** untuk menghapus semua gift.
    """
    await event.edit(msg.strip(), buttons=buttons)
    await logs.send_message(CHLOGS, f"{user_id} menekan tombol 🗑️ DELETE RENT")

@bot.on(events.CallbackQuery(pattern=b"^selgift_(.+)$"))
async def select_gift_toggle(event):
    user_id = event.sender_id
    slug = event.pattern_match.group(1).decode()

    cur.execute("SELECT slug, model FROM gift_rent WHERE user_id=?", (user_id,))
    gifts = cur.fetchall()

    if user_id not in selected_gifts:
        selected_gifts[user_id] = set()

    selected = selected_gifts[user_id]

    if slug in selected:
        selected.remove(slug)
    else:
        selected.add(slug)

    buttons = []
    row = []
    for i, (s_slug, model) in enumerate(gifts, start=1):
        label = f"{s_slug}"
        if s_slug in selected:
            label = f"✅ {label}"
        row.append(Button.inline(label, data=f"selgift_{s_slug}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append([
        Button.inline("🗑️ DELETE", data="confirm_delete_selected"),
        Button.inline("🗑️ DELETE ALL", data="confirm_delete_all")
    ])
    buttons.append([Button.inline("🔙 KEMBALI", data="rent")])

    msg = f"""
🗑️ **HAPUS GIFT RENTAL**

✅ Gift terpilih: {len(selected)}

Klik ulang tombol untuk membatalkan pilihan.
Tekan **DELETE** untuk menghapus yang dipilih
atau **DELETE ALL** untuk menghapus semuanya.
    """

    await event.edit(msg.strip(), buttons=buttons)

@bot.on(events.CallbackQuery(data=b"confirm_delete_selected"))
async def confirm_delete_selected(event):
    user_id = event.sender_id
    selected = selected_gifts.get(user_id, set())

    if not selected:
        return await event.answer("❌ Belum ada gift yang dipilih.", alert=True)

    msg = f"""
⚠️ **KONFIRMASI PENGHAPUSAN**

Kamu akan menghapus **{len(selected)} gift** dari daftar rental.
Apakah kamu yakin?
    """
    buttons = [
        [Button.inline("✅ YA, HAPUS", data="do_delete_selected"),
         Button.inline("❌ BATAL", data="del_rent")]
    ]
    await event.edit(msg.strip(), buttons=buttons)


@bot.on(events.CallbackQuery(data=b"do_delete_selected"))
async def do_delete_selected(event):
    user_id = event.sender_id
    selected = selected_gifts.get(user_id, set())

    if not selected:
        return await event.answer("❌ Tidak ada gift yang dipilih.", alert=True)

    deleted_count = 0
    failed_count = 0

    for slug in selected:
        cur.execute("SELECT channel_msg_id FROM gift_rent WHERE user_id=? AND slug=?", (user_id, slug))
        row = cur.fetchone()
        channel_msg_id = row[0] if row else None

        if channel_msg_id:
            try:
                await bot.delete_messages(CHANNEL_RENTAL, channel_msg_id)
            except Exception as e:
                print(f"⚠️ Gagal hapus postingan channel untuk {slug}: {e}")
                failed_count += 1

        cur.execute("DELETE FROM gift_rent WHERE user_id=? AND slug=?", (user_id, slug))
        conn.commit()
        deleted_count += 1

    selected_gifts[user_id] = set()

    msg = f"✅ **Berhasil menghapus {deleted_count} gift rental.**"
    if failed_count > 0:
        msg += f"\n⚠️ {failed_count} postingan gagal dihapus dari channel."

    buttons = [[Button.inline("🔙 KEMBALI", data="rent")]]
    await event.edit(msg.strip(), buttons=buttons)

@bot.on(events.CallbackQuery(data=b"confirm_delete_all"))
async def confirm_delete_all(event):
    user_id = event.sender_id

    cur.execute("SELECT COUNT(*), GROUP_CONCAT(channel_msg_id) FROM gift_rent WHERE user_id=?", (user_id,))
    count_row = cur.fetchone()
    total = count_row[0] or 0

    if total == 0:
        return await event.answer("❌ Tidak ada data untuk dihapus.", alert=True)

    msg = f"""
⚠️ **KONFIRMASI HAPUS SEMUA**

Kamu akan menghapus **SEMUA ({total}) gift rental** yang kamu simpan.
Tindakan ini tidak bisa dibatalkan!

Apakah kamu yakin ingin melanjutkan?
    """
    buttons = [
        [Button.inline("✅ YA, HAPUS SEMUA", data="do_delete_all"),
         Button.inline("❌ BATAL", data="del_rent")]
    ]
    await event.edit(msg.strip(), buttons=buttons)


@bot.on(events.CallbackQuery(data=b"do_delete_all"))
async def do_delete_all(event):
    user_id = event.sender_id

    # Ambil semua channel_msg_id sebelum hapus
    cur.execute("SELECT channel_msg_id, slug FROM gift_rent WHERE user_id=?", (user_id,))
    rows = cur.fetchall()

    deleted_count = 0
    failed_count = 0

    for channel_msg_id, slug in rows:
        if channel_msg_id:
            try:
                await bot.delete_messages(CHANNEL_RENTAL, channel_msg_id)
            except Exception as e:
                print(f"⚠️ Gagal hapus postingan channel untuk {slug}: {e}")
                failed_count += 1
        deleted_count += 1

    # Hapus semua dari DB
    cur.execute("DELETE FROM gift_rent WHERE user_id=?", (user_id,))
    conn.commit()
    selected_gifts[user_id] = set()

    msg = f"✅ **Semua gift rental ({deleted_count}) berhasil dihapus.**"
    if failed_count > 0:
        msg += f"\n⚠️ {failed_count} postingan gagal dihapus dari channel."

    buttons = [[Button.inline("🔙 KEMBALI", data="rent")]]
    await event.edit(msg.strip(), buttons=buttons)

@bot.on(events.CallbackQuery(data=b"my_rent"))
async def my_rent_list(event):
    user_id = get_effective_user_id(event.sender_id)

    try:
        # Ambil semua gift rental milik user
        cur.execute("SELECT slug FROM gift_rent WHERE user_id=?", (user_id,))
        rows = cur.fetchall()

        if not rows:
            return await event.answer("📭 Kamu belum memiliki gift rental yang aktif!", alert=True)

        buttons = []
        seen_slugs = set()
        row_buttons = []

        for (slug,) in rows:
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)

            # Format tombol: nama + nomor
            parts = slug.split("-")
            name = parts[0]
            number = parts[1] if len(parts) > 1 else ""
            display = f"{name} #{number}"

            # Tambahkan tombol inline untuk tiap gift
            row_buttons.append(Button.inline(display, data=f"rentgift_{slug}"))

            # 2 tombol per baris
            if len(row_buttons) == 2:
                buttons.append(row_buttons)
                row_buttons = []

        if row_buttons:
            buttons.append(row_buttons)

        # Tombol kembali
        buttons.append([Button.inline("🔙 KEMBALI", data="rent")])

        msg = "🎁 **__Daftar Gift Rental Kamu__**\n\nKlik gift di bawah ini untuk melihat detail atau mengelolanya."

        try:
            await event.edit(msg, buttons=buttons)
        except:
            await event.respond(msg, buttons=buttons)

    except Exception as e:
        print(f"⚠️ Error di my_rent_list: {e}")
        await event.answer("⚠️ Terjadi kesalahan saat menampilkan daftar rental.", alert=True)

@bot.on(events.CallbackQuery(pattern=b"^rentgift_(.+)$"))
async def rentgift_detail(event):
    slug = event.pattern_match.group(1).decode()
    viewer_id = get_effective_user_id(event.sender_id)

    try:
        # === Ambil data gift dari DB ===
        cur.execute("""
            SELECT model, background, symbol, rarity, price, status, created_at, gift_address,
                   owner_address, channel_msg_id
            FROM gift_rent
            WHERE slug=? AND user_id=?
        """, (slug, viewer_id))
        row = cur.fetchone()

        if not row:
            return await event.answer("❌ Gift rental tidak ditemukan atau bukan milikmu.", alert=True)

        model, background, symbol, rarity, price, status, created_at, gift_address, owner_address, channel_msg_id = row

        # === Ambil detail gift dari Telegram ===
        result = await userbot(functions.payments.GetUniqueStarGiftRequest(slug=slug))
        gift = getattr(result, "gift", None)
        if not gift:
            raise Exception("Gift object tidak ditemukan di hasil RPC.")

        # Ambil atribut dari gift
        model_rarity = background_rarity = symbol_rarity = None
        for attr in getattr(gift, "attributes", []):
            if isinstance(attr, StarGiftAttributeModel):
                model = model or attr.name
                model_rarity = format_rarity(getattr(attr, "rarity_permille", None))
            elif isinstance(attr, StarGiftAttributeBackdrop):
                background = background or attr.name
                background_rarity = format_rarity(getattr(attr, "rarity_permille", None))
            elif isinstance(attr, StarGiftAttributePattern):
                symbol = symbol or attr.name
                symbol_rarity = format_rarity(getattr(attr, "rarity_permille", None))

        rarity = rarity or model_rarity or background_rarity or symbol_rarity

        # === Ambil gift_address ===
        if not gift_address:
            gift_address = getattr(gift, "gift_address", None)

        # === Ambil owner address via TonAPI ===
        ton_owner_address = None
        if gift_address:
            async with aiohttp.ClientSession() as session_http:
                nft_url = f"https://tonapi.io/v2/nfts/{gift_address}"
                async with session_http.get(nft_url) as resp:
                    if resp.status == 200:
                        nft_data = await resp.json()
                        owner_info = nft_data.get("owner", {})
                        ton_owner_address = owner_info.get("address")

        owner_address = ton_owner_address or getattr(result, "owner_address", None) or owner_address
        image_url = getattr(gift, "photo", None)
        availability_issued = getattr(gift, "availability_issued", 0)
        availability_total = getattr(gift, "availability_total", 0)

        # === Ambil daftar harga dari tabel gift_rent_prices ===
        cur.execute("""
            SELECT duration_text, price FROM gift_rent_prices
            WHERE slug=? ORDER BY id
        """, (slug,))
        prices = cur.fetchall()

        if prices:
            price_lines = []
            for dur, pval in prices:
                price_display = f"Rp{pval:,}" if str(pval).isdigit() else str(pval)
                price_lines.append(f"• {dur} → {price_display}")
            display_price_list = "\n".join(price_lines)
        else:
            display_price_list = "__Owner belum memasang harga!__"

        # === Simpan update ke DB (model, symbol, dll) ===
        cur.execute("""
            UPDATE gift_rent
            SET model=?, background=?, symbol=?, rarity=?, gift_address=?, owner_address=?, status=?, price=?
            WHERE slug=? AND user_id=?
        """, (model, background, symbol, rarity, gift_address, owner_address, status, price, slug, viewer_id))
        conn.commit()

        # Format waktu
        jakarta_tz = pytz.timezone("Asia/Jakarta")
        waktu_jakarta = datetime.fromtimestamp(created_at, jakarta_tz)
        waktu_str = waktu_jakarta.strftime("%d %b %Y • %H:%M WIB")

        # Format display
        display_price = f"Rp{price or 0:,}"
        status_text = status or "unknown"
        addr_display = f"[OPEN](https://tonviewer.com/{gift_address})" if gift_address else "❌ Tidak tersedia"
        owner_display = f"[OPEN](https://tonviewer.com/{owner_address})" if owner_address else "❌ Tidak tersedia"

        # === Pesan utama ===
        msg = f"""
**__DETAIL DATA GIFT RENTAL [{slug}](https://t.me/nft/{slug})__**

^^✨ **Model:** {model or '❌ None'} ({model_rarity or '-'})
🖼️ **Background:** {background or '❌ None'} ({background_rarity or '-'})
👾 **Symbol:** {symbol or '❌ None'} ({symbol_rarity or '-'})
🔢 **Availability:** {availability_issued}/{availability_total}
📊 **Status:** {status_text}
🕓 **Ditambahkan:** {waktu_str}^^

🔹 **Gift Address:** {addr_display}
👤 **Owner Address:** {owner_display}
📦 **Price List:**
{display_price_list}
        """

        # === Tombol-tombol utama ===
        buttons = [
            [
                Button.inline("⏰ TIME & PRICE", data=f"rentprice_{slug}"),
                Button.inline("📊 STATUS", data=f"rentstatus_{slug}")
            ],
            [
                Button.inline("🏪 ADD STORE", data=f"storerent_{slug}"),
                Button.inline("🚫 UNADD RENT", data=f"rentunadd_{slug}")
            ],
            [
                Button.inline("🛒 IN RENT", data=f"inrent_{slug}"),
                Button.inline("🏷️ UNLISTED", data=f"unlistrent_{slug}")
            ]
        ]

        # === Jika belum pernah diposting ===
        if not channel_msg_id:
            buttons.append([
                Button.inline("🛍️ POST GIFT", data=f"postgift_{slug}")
            ])
            buttons.append([
                Button.inline("🔙 KEMBALI", data="rent")
            ])
        else:
            post_link = f"https://t.me/sewagifts/{channel_msg_id}"
            buttons.append([
                Button.url("🛍️ VIEW POST", url=post_link)
            ])
            buttons.append([
                Button.inline("🔙 KEMBALI", data="rent")
            ])

        # === Tampilkan pesan ===
        if image_url:
            await event.edit(file=image_url, text=msg.strip(), buttons=buttons)
        else:
            await event.edit(msg.strip(), buttons=buttons)

    except Exception as e:
        print(f"⚠️ Error di rentgift_detail: {e}")
        await event.answer("⚠️ Terjadi kesalahan saat membuka detail rental.", alert=True)

@bot.on(events.CallbackQuery(pattern=b"^storerent_(.+)$"))
async def storerent_callback(event):
    slug = event.pattern_match.group(1).decode()
    user_id = event.sender_id

    # Simpan state agar tahu user ini sedang input teks store
    pending_store_input[user_id] = slug

    await event.edit(
        f"🏪 **Tambahkan teks dan link store kamu untuk gift `{slug}`.**\n\n"
        "Contoh:\n"
        "`Cek gift lainnya di store aku guys!! - https://t.me/channelstore/123`\n\n"
        "Link **wajib** diawali dengan `https://t.me/`",
        buttons=[[Button.inline("❌ BATALKAN", data=f"rentgift_{slug}")]]
    )
    
@bot.on(events.NewMessage)
async def handle_store_input(event):
    user_id = event.sender_id

    # Jika user sedang dalam mode input store
    if user_id in pending_store_input:
        slug = pending_store_input[user_id]
        text = event.raw_text.strip()

        # Validasi input harus mengandung link t.me
        if not re.search(r"https://t\.me/[^\s]+", text):
            await event.reply("❌ Format tidak valid. Harus berisi link yang diawali `https://t.me/`.")
            return

        try:
            # Simpan ke database
            cur.execute("""
                INSERT OR REPLACE INTO gift_rent_store (slug, user_id, store_text, created_at)
                VALUES (?, ?, ?, ?)
            """, (slug, user_id, text, int(time.time())))
            conn.commit()

            # Hapus dari daftar pending
            del pending_store_input[user_id]

            # === Ambil data gift untuk update postingan ===
            cur.execute("""
                SELECT model, background, symbol, rarity, price, gift_address, username, channel_msg_id
                FROM gift_rent
                WHERE slug=? AND user_id=?
            """, (slug, user_id))
            row = cur.fetchone()
            if not row:
                return await event.reply("❌ Gift tidak ditemukan atau bukan milikmu.")

            model, background, symbol, rarity, price_val, gift_address, username, channel_msg_id = row

            # Ambil text store baru
            cur.execute("SELECT store_text FROM gift_rent_store WHERE slug=?", (slug,))
            store_row = cur.fetchone()
            channel_store = f"\n\n{store_row[0]}" if store_row and store_row[0] else ""

            # === Ambil daftar harga rental ===
            cur.execute("""
                SELECT duration_text, price
                FROM gift_rent_prices
                WHERE slug=?
                ORDER BY id
            """, (slug,))
            prices = cur.fetchall()

            if prices:
                price_lines = []
                for dur, pval in prices:
                    price_display = f"Rp{pval:,}" if str(pval).isdigit() else str(pval)
                    price_lines.append(f"• {dur} → {price_display}")
                display_price = "\n".join(price_lines)
            else:
                display_price = "__Owner belum memasang harga!__"

            tonviewer_link = f"https://tonviewer.com/{gift_address}" if gift_address else None
            ton_line = f"[OPEN]({tonviewer_link})" if tonviewer_link else "❌ Tidak tersedia"
            contact_line = f"📞 **CONTACT:** @{username}" if username else "📞 **CONTACT:** (username tidak tersedia)"

            # === CAPTION BARU (seperti postgift_callback) ===
            caption = f"""
⌚️ **__GIFT AVAILABLE FOR RENTAL!__**

- [{slug}](https://t.me/nft/{slug})

^^✨ **Model:** {model or '-'}
🖼️ **Background:** {background or '-'}
👾 **Symbol:** {symbol or '-'}
🔎 **__Scan tonviewer:__** {ton_line}
{contact_line}^^

💸 **__PRICE LIST__**
{display_price}

{channel_store}
            """.strip()

            # === Update caption di channel rental (jika sudah pernah diposting) ===
            if channel_msg_id:
                try:
                    await bot.edit_message(CHANNEL_RENTAL, channel_msg_id, caption)
                    await event.reply(f"✅ Store berhasil disimpan dan postingan `{slug}` diperbarui di channel!")
                except Exception as e:
                    print(f"⚠️ Gagal update postingan di channel: {e}")
                    await event.reply("✅ Store tersimpan, tapi gagal memperbarui postingan di channel.")
            else:
                await event.reply(f"✅ Store berhasil disimpan untuk gift `{slug}` (belum pernah diposting).")

            # === Kirim ulang menu pengaturan ===
            buttons = [
                [Button.inline("💸 HARGA RENTAL", data=f"rentprice_{slug}")],
                [Button.inline("🏪 ADD STORE", data=f"storerent_{slug}")],
                [Button.inline("🔙 KEMBALI", data=f"rentgift_{slug}")]
            ]
            await event.reply(
                f"🎁 Detail gift `{slug}` diperbarui.\n\nKamu bisa mengatur ulang store atau harga di bawah ini:",
                buttons=buttons
            )

        except Exception as e:
            print(f"⚠️ Error di handle_store_input: {e}")
            await event.reply("⚠️ Gagal menyimpan store ke database.")

# === UNADD RENT HANDLER ===
@bot.on(events.CallbackQuery(pattern=b"^rentunadd_(.+)$"))
async def rent_unadd(event):
    slug = event.pattern_match.group(1).decode()
    user_id = event.sender_id

    try:
        # === Cek apakah gift ada di database dan milik user ini ===
        cur.execute("""
            SELECT channel_msg_id
            FROM gift_rent
            WHERE slug=? AND user_id=?
        """, (slug, user_id))
        row = cur.fetchone()

        if not row:
            return await event.answer("❌ Gift rental tidak ditemukan atau bukan milikmu.", alert=True)

        channel_msg_id = row[0]

        # === Konfirmasi ke user sebelum hapus ===
        confirm_buttons = [
            [
                Button.inline("✅ YA, HAPUS", data=f"do_rentunadd_{slug}"),
                Button.inline("❌ BATAL", data=f"rentgift_{slug}")
            ]
        ]
        await event.edit(
            f"⚠️ Apakah kamu yakin ingin **menghapus gift `{slug}` dari daftar rental**?\n\n"
            "Tindakan ini juga akan **menghapus postingan dari channel rental** (jika ada).",
            buttons=confirm_buttons
        )

    except Exception as e:
        print(f"⚠️ Error di rent_unadd: {e}")
        await event.answer("⚠️ Gagal memproses UNADD RENT.", alert=True)


# === Eksekusi penghapusan ===
@bot.on(events.CallbackQuery(pattern=b"^do_rentunadd_(.+)$"))
async def do_rent_unadd(event):
    slug = event.pattern_match.group(1).decode()
    user_id = event.sender_id

    try:
        # === Ambil data dulu untuk ambil message_id dan memastikan kepemilikan ===
        cur.execute("""
            SELECT channel_msg_id
            FROM gift_rent
            WHERE slug=? AND user_id=?
        """, (slug, user_id))
        row = cur.fetchone()

        if not row:
            return await event.answer("❌ Data gift tidak ditemukan.", alert=True)

        channel_msg_id = row[0]

        # === Hapus postingan dari channel jika ada ===
        if channel_msg_id:
            try:
                await bot.delete_messages(CHANNEL_RENTAL, channel_msg_id)
                print(f"🗑️ Postingan gift {slug} dihapus dari channel rental.")
            except Exception as e:
                print(f"⚠️ Gagal hapus pesan di channel untuk {slug}: {e}")

        # === Hapus data dari database gift_rent & gift_rent_prices ===
        cur.execute("DELETE FROM gift_rent_prices WHERE slug=?", (slug,))
        cur.execute("DELETE FROM gift_rent WHERE slug=? AND user_id=?", (slug, user_id))
        conn.commit()

        await event.edit(f"✅ Gift `{slug}` berhasil dihapus dari daftar rental dan postingan channel dihapus.")
        await bot.send_message(user_id, f"🗑️ Gift `{slug}` kamu telah **dihapus sepenuhnya dari sistem rental.**")

    except Exception as e:
        print(f"⚠️ Error di do_rent_unadd: {e}")
        await event.answer("⚠️ Gagal menghapus gift rental.", alert=True)

@bot.on(events.CallbackQuery(pattern=b"^postgift_(.+)$"))
async def postgift_callback(event):
    slug = event.pattern_match.group(1).decode()
    user_id = event.sender_id

    try:
        # === Ambil data gift dari database ===
        cur.execute("""
            SELECT model, background, symbol, rarity, price, gift_address, username
            FROM gift_rent
            WHERE slug=? AND user_id=?
        """, (slug, user_id))
        row = cur.fetchone()
        if not row:
            return await event.answer("❌ Gift tidak ditemukan atau bukan milikmu.", alert=True)

        model, background, symbol, rarity, price_val, gift_address, username = row

        # === Ambil detail gift dari Telegram ===
        result = await userbot(functions.payments.GetUniqueStarGiftRequest(slug=slug))
        gift = getattr(result, "gift", None)
        if not gift:
            raise Exception("Gift object tidak ditemukan dari hasil RPC.")

        # Ambil rarity dari atribut gift
        model_rarity = background_rarity = symbol_rarity = None
        for attr in getattr(gift, "attributes", []):
            if isinstance(attr, StarGiftAttributeModel):
                model = model or attr.name
                model_rarity = format_rarity(getattr(attr, "rarity_permille", None))
            elif isinstance(attr, StarGiftAttributeBackdrop):
                background = background or attr.name
                background_rarity = format_rarity(getattr(attr, "rarity_permille", None))
            elif isinstance(attr, StarGiftAttributePattern):
                symbol = symbol or attr.name
                symbol_rarity = format_rarity(getattr(attr, "rarity_permille", None))

        cur.execute("SELECT store_text FROM gift_rent_store WHERE slug=?", (slug,))
        store_row = cur.fetchone()

        if store_row and store_row[0]:
            text_store = store_row[0]
            if " - http" in text_store:
                parts = text_store.split(" - ", 1)
                if len(parts) == 2:
                    desc, link = parts
                    channel_store = f"[{desc.strip()}]({link.strip()})"
                else:
                    channel_store = text_store
            else:
                channel_store = text_store
        else:
            channel_store = ""

        # === Ambil daftar harga rental ===
        cur.execute("""
            SELECT duration_text, price
            FROM gift_rent_prices
            WHERE slug=?
            ORDER BY id
        """, (slug,))
        prices = cur.fetchall()

        if prices:
            price_lines = []
            for dur, pval in prices:
                if isinstance(pval, int):
                    price_display = f"Rp{pval:,}"
                else:
                    price_display = str(pval).strip()
                price_lines.append(f"• {dur} → {price_display}")
            display_price = "\n".join(price_lines)
        else:
            display_price = "__Owner belum memasang harga!__"

        # === Buat link tonviewer ===
        tonviewer_link = f"https://tonviewer.com/{gift_address}" if gift_address else None
        ton_line = f"[OPEN]({tonviewer_link})" if tonviewer_link else "❌ Tidak tersedia"

        contact_line = f"📞 **Contact:** @{username}" if username else "📞 **CONTACT:** (username tidak tersedia)"

        caption = f"""
⌚️ **__GIFT AVAILABLE FOR RENTAL!__**

- [{slug}](https://t.me/nft/{slug})

^^✨ **Model:** {model or '-'} ({model_rarity or '-'})
🖼️ **Background:** {background or '-'} ({background_rarity or '-'})
👾 **Symbol:** {symbol or '-'} ({symbol_rarity or '-'})
🔎 **Scan tonviewer:** {ton_line}
{contact_line}^^

💸 **__PRICE LIST__**
{display_price}

**__- Ads: {channel_store}__**
        """.strip()

        sent = await bot.send_message(CHANNEL_RENTAL, caption)
        cur.execute(
            "UPDATE gift_rent SET channel_msg_id=? WHERE slug=? AND user_id=?",
            (sent.id, slug, user_id)
        )
        conn.commit()

        await event.answer("✅ Gift berhasil diposting ke channel rental!", alert=True)
        await rentgift_detail(event)

    except Exception as e:
        print(f"⚠️ Error di postgift_callback: {e}")
        await event.answer("⚠️ Gagal memposting gift ke channel.", alert=True)

@bot.on(events.CallbackQuery(pattern=b"^rentprice_(.+)$"))
async def rentprice_menu(event):
    slug = event.pattern_match.group(1).decode()
    viewer_id = get_effective_user_id(event.sender_id)

    try:
        # Pastikan gift milik user
        cur.execute("SELECT id FROM gift_rent WHERE slug=? AND user_id=?", (slug, viewer_id))
        if not cur.fetchone():
            return await event.answer("🚫 Gift ini bukan milikmu!", alert=True)

        # Ambil semua daftar harga untuk slug ini
        cur.execute("""
            SELECT id, duration_text, price, created_at
            FROM gift_rent_prices
            WHERE slug=?
            ORDER BY id
        """, (slug,))
        rows = cur.fetchall()

        if rows:
            lines = []
            for r in rows:
                row_id, duration_text, price_val, created_at = r

                # Jika price disimpan sebagai integer -> format ribuan
                price_display = None
                if isinstance(price_val, int):
                    price_display = f"Rp{price_val:,}"
                else:
                    # coba konversi string yang berisi angka saja
                    try:
                        # hapus karakter non-digit lalu parse (jika ada digit)
                        digits = re.sub(r"[^\d]", "", str(price_val) or "")
                        if digits:
                            price_int = int(digits)
                            if str(price_val).strip().isdigit():
                                price_display = f"Rp{price_int:,}"
                            else:
                                price_display = str(price_val)
                        else:
                            price_display = str(price_val)
                    except Exception:
                        price_display = str(price_val)

                try:
                    created_str = ""
                    if created_at:
                        tz = pytz.timezone("Asia/Jakarta")
                        created_dt = datetime.fromtimestamp(int(created_at), tz)
                        created_str = f" • {created_dt.strftime('%d %b %Y %H:%M')}"
                    lines.append(f"• {duration_text} → {price_display}")
                except Exception:
                    lines.append(f"• {duration_text} → {price_display}")

            price_list = "\n".join(lines)
        else:
            price_list = "__Owner belum memasang harga!__"

        msg = f"""
💸 **PRICE LIST UNTUK RENT GIFT**
📦 Slug: `{slug}`

{price_list}
        """.strip()

        buttons = [
            [Button.inline("💸 ADD PRICE", data=f"addprice_{slug}")],
            [Button.inline("🗑️ DELETE PRICE", data=f"delprice_{slug}")],
            [Button.inline("🔙 KEMBALI", data=f"rentgift_{slug}")]
        ]

        # edit pesan callback (jika bisa), kalau gagal coba respond
        try:
            await event.edit(msg, buttons=buttons)
        except Exception:
            await event.respond(msg, buttons=buttons)

    except Exception as e:
        print(f"⚠️ Error di rentprice_menu: {e}")
        await event.answer("⚠️ Terjadi kesalahan membuka harga.", alert=True)

@bot.on(events.CallbackQuery(pattern=b"^delprice_(.+)$"))
async def delprice_menu(event):
    slug = event.pattern_match.group(1).decode()
    user_id = event.sender_id

    try:
        # pastikan gift milik user
        cur.execute("SELECT id FROM gift_rent WHERE slug=? AND user_id=?", (slug, user_id))
        if not cur.fetchone():
            return await event.answer("🚫 Gift ini bukan milikmu!", alert=True)

        # ambil daftar harga
        cur.execute("SELECT id, duration_text, price FROM gift_rent_prices WHERE slug=?", (slug,))
        prices = cur.fetchall()

        if not prices:
            return await event.answer("❌ Tidak ada harga yang tersimpan untuk gift ini.", alert=True)

        # simpan state awal user
        selected_prices[user_id] = set()

        # buat tombol daftar harga
        buttons = []
        row = []
        for i, (pid, durasi, price) in enumerate(prices, start=1):
            # pastikan format harga aman (karena TEXT)
            if isinstance(price, int):
                price_text = f"Rp{price:,}"
            else:
                price_text = str(price)
            label = f"{durasi} → {price_text}"
            row.append(Button.inline(label, data=f"selprice_{pid}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)

        # tombol aksi
        buttons.append([
            Button.inline("🗑️ DELETE", data=f"confirm_delprice_selected_{slug}"),
            Button.inline("🗑️ DELETE ALL", data=f"confirm_delprice_all_{slug}")
        ])
        buttons.append([Button.inline("🔙 KEMBALI", data=f"rentprice_{slug}")])

        msg = f"""
🗑️ **HAPUS HARGA RENTAL**

📦 Slug: `{slug}`

Pilih harga yang ingin kamu hapus dengan menekan tombol di bawah.
Klik ulang untuk membatalkan pilihan ✅.

Setelah memilih, tekan **DELETE** untuk menghapus yang dipilih
atau **DELETE ALL** untuk menghapus semua harga.
        """
        await event.edit(msg.strip(), buttons=buttons)

    except Exception as e:
        print(f"⚠️ Error di delprice_menu: {e}")
        await event.answer("⚠️ Gagal membuka daftar harga.", alert=True)

# === Toggle pilihan harga ===
@bot.on(events.CallbackQuery(pattern=b"^selprice_(\\d+)$"))
async def toggle_price_selection(event):
    user_id = event.sender_id
    price_id = int(event.pattern_match.group(1).decode())

    try:
        # ambil slug dari data
        cur.execute("SELECT slug FROM gift_rent_prices WHERE id=?", (price_id,))
        row = cur.fetchone()
        if not row:
            return await event.answer("❌ Data tidak ditemukan.", alert=True)
        slug = row[0]

        # ambil daftar semua harga
        cur.execute("SELECT id, duration_text, price FROM gift_rent_prices WHERE slug=?", (slug,))
        prices = cur.fetchall()

        if user_id not in selected_prices:
            selected_prices[user_id] = set()

        selected = selected_prices[user_id]

        # toggle pilihan
        if price_id in selected:
            selected.remove(price_id)
        else:
            selected.add(price_id)

        # buat ulang tombol dengan tanda ✅
        buttons = []
        row_btn = []
        for i, (pid, durasi, price) in enumerate(prices, start=1):
            # hindari format numeric, karena price adalah TEXT
            price_str = f"{price}" if isinstance(price, str) else str(price)
            label = f"{durasi} → {price_str}"
            if pid in selected:
                label = f"✅ {label}"
            row_btn.append(Button.inline(label, data=f"selprice_{pid}"))
            if len(row_btn) == 2:
                buttons.append(row_btn)
                row_btn = []
        if row_btn:
            buttons.append(row_btn)

        # tombol aksi
        buttons.append([
            Button.inline("🗑️ DELETE", data=f"confirm_delprice_selected_{slug}"),
            Button.inline("🗑️ DELETE ALL", data=f"confirm_delprice_all_{slug}")
        ])
        buttons.append([Button.inline("🔙 KEMBALI", data=f"rentprice_{slug}")])

        msg = f"""
🗑️ **HAPUS HARGA RENTAL**

📦 Slug: `{slug}`
✅ Harga terpilih: {len(selected)}

Klik ulang untuk membatalkan pilihan.
Tekan **DELETE** untuk menghapus yang dipilih
atau **DELETE ALL** untuk menghapus semuanya.
        """
        await event.edit(msg.strip(), buttons=buttons)

    except Exception as e:
        print(f"⚠️ Error di toggle_price_selection: {e}")
        await event.answer("⚠️ Gagal memperbarui tampilan.", alert=True)


# === Konfirmasi hapus terpilih ===
@bot.on(events.CallbackQuery(pattern=b"^confirm_delprice_selected_(.+)$"))
async def confirm_delprice_selected(event):
    slug = event.pattern_match.group(1).decode()
    user_id = event.sender_id
    selected = selected_prices.get(user_id, set())

    try:
        if not selected:
            return await event.answer("__Owner belum memasang harga!__", alert=True)

        msg = f"""
⚠️ **KONFIRMASI PENGHAPUSAN**

Kamu akan menghapus **{len(selected)} harga** untuk gift `{slug}`.
Apakah kamu yakin?
        """
        buttons = [
            [Button.inline("✅ YA, HAPUS", data=f"do_delprice_selected_{slug}"),
             Button.inline("❌ BATAL", data=f"delprice_{slug}")]
        ]
        await event.edit(msg.strip(), buttons=buttons)

    except Exception as e:
        print(f"⚠️ Error di confirm_delprice_selected: {e}")
        await event.answer("⚠️ Gagal memproses konfirmasi.", alert=True)


# === Eksekusi hapus terpilih ===
@bot.on(events.CallbackQuery(pattern=b"^do_delprice_selected_(.+)$"))
async def do_delprice_selected(event):
    slug = event.pattern_match.group(1).decode()
    user_id = event.sender_id
    selected = selected_prices.get(user_id, set())

    try:
        if not selected:
            return await event.answer("❌ Tidak ada harga yang dipilih.", alert=True)

        cur.executemany("DELETE FROM gift_rent_prices WHERE id=?", [(pid,) for pid in selected])
        conn.commit()

        count = len(selected)
        selected_prices[user_id] = set()

        await event.edit(
            f"✅ **Berhasil menghapus {count} harga rental untuk `{slug}`.**",
            buttons=[[Button.inline("🔙 KEMBALI", data=f"rentprice_{slug}")]]
        )

    except Exception as e:
        print(f"⚠️ Error di do_delprice_selected: {e}")
        await event.answer("⚠️ Gagal menghapus data.", alert=True)


# === Konfirmasi hapus semua ===
@bot.on(events.CallbackQuery(pattern=b"^confirm_delprice_all_(.+)$"))
async def confirm_delprice_all(event):
    slug = event.pattern_match.group(1).decode()
    user_id = event.sender_id

    try:
        cur.execute("SELECT COUNT(*) FROM gift_rent_prices WHERE slug=?", (slug,))
        total = cur.fetchone()[0] or 0

        if total == 0:
            return await event.answer("❌ Tidak ada data untuk dihapus.", alert=True)

        msg = f"""
⚠️ **KONFIRMASI HAPUS SEMUA**

Kamu akan menghapus **SEMUA ({total}) harga** untuk gift `{slug}`.
Tindakan ini tidak bisa dibatalkan!

Apakah kamu yakin ingin melanjutkan?
        """
        buttons = [
            [Button.inline("✅ YA, HAPUS SEMUA", data=f"do_delprice_all_{slug}"),
             Button.inline("❌ BATAL", data=f"delprice_{slug}")]
        ]
        await event.edit(msg.strip(), buttons=buttons)

    except Exception as e:
        print(f"⚠️ Error di confirm_delprice_all: {e}")
        await event.answer("⚠️ Gagal menampilkan konfirmasi.", alert=True)

# === Eksekusi hapus semua harga ===
@bot.on(events.CallbackQuery(pattern=b"^do_delprice_all_(.+)$"))
async def do_delprice_all(event):
    from telethon.tl import functions, types
    from io import BytesIO

    slug = event.pattern_match.group(1).decode()
    user_id = event.sender_id

    try:
        # === Hapus semua data harga dari tabel ===
        cur.execute("DELETE FROM gift_rent_prices WHERE slug=?", (slug,))
        conn.commit()

        # Bersihkan cache harga user jika ada
        if user_id in selected_prices:
            selected_prices[user_id].clear()

        # === Ambil data gift utama untuk update postingan channel ===
        cur.execute("""
            SELECT model, background, symbol, rarity, gift_address, channel_msg_id, username
            FROM gift_rent WHERE slug=?
        """, (slug,))
        gift_row = cur.fetchone()
        if not gift_row:
            return await event.edit(
                f"⚠️ Gift `{slug}` tidak ditemukan di database.",
                buttons=[[Button.inline("🔙 KEMBALI", data=f"rentprice_{slug}")]]
            )

        model, background, symbol, rarity, gift_address, channel_msg_id, username_db = gift_row

        # === Ambil OWNER asli dari API Telegram ===
        owner_display = None
        try:
            result = await userbot(functions.payments.GetUniqueStarGiftRequest(slug=slug))
            gift = result.gift
            if gift and gift.owner_id and isinstance(gift.owner_id, types.PeerUser):
                owner_entity = await userbot.get_entity(gift.owner_id.user_id)
                if getattr(owner_entity, "username", None):
                    owner_display = f"@{owner_entity.username}"
                else:
                    fullname = (owner_entity.first_name or "") + " " + (owner_entity.last_name or "")
                    owner_display = fullname.strip() if fullname.strip() else f"[{owner_entity.id}](tg://user?id={owner_entity.id})"
        except Exception as e:
            print(f"⚠️ Gagal ambil owner API untuk {slug}: {e}")

        # fallback jika gagal ambil owner dari API
        contact_line = f"📞 **CONTACT:** {owner_display}" if owner_display else (
            f"📞 **CONTACT:** @{username_db}" if username_db else "📞 **CONTACT:** (username tidak tersedia)"
        )

        # === Update caption postingan di channel (hapus daftar harga) ===
        if channel_msg_id and channel_msg_id != 0:
            try:
                tonviewer_link = f"https://tonviewer.com/{gift_address}" if gift_address else None
                ton_line = f"[OPEN]({tonviewer_link})" if tonviewer_link else "❌ Tidak tersedia"
                rarity_safe = rarity or "-"

                caption = f"""
⌚️ **__GIFT AVAILABLE FOR RENTAL__**

[{slug}](https://t.me/nft/{slug})

^^✨ **Model:** {model or '-'} ({rarity_safe})
🖼️ **Background:** {background or '-'} ({rarity_safe})
👾 **Symbol:** {symbol or '-'} ({rarity_safe})
🔎 **__Scan tonviewer:__** {ton_line}
{contact_line}^^

💸 **__PRICE DURASI__**
__Owner belum memasang harga!__
                """.strip()

                await bot.edit_message(CHANNEL_RENTAL, channel_msg_id, caption)
                print(f"🗑️ Semua harga untuk {slug} dihapus & postingan channel diperbarui (owner API: {owner_display})")
            except Exception as e:
                print(f"⚠️ Gagal update postingan channel setelah hapus semua harga: {e}")

        # === Konfirmasi ke user ===
        msg = f"""
✅ **Semua harga rental untuk `{slug}` berhasil dihapus.**
💬 Postingan channel juga telah diperbarui.
👤 **Owner:** {owner_display or 'Tidak diketahui'}
        """
        buttons = [[Button.inline("🔙 KEMBALI", data=f"rentprice_{slug}")]]
        await event.edit(msg.strip(), buttons=buttons)

    except Exception as e:
        print(f"⚠️ Error di do_delprice_all: {e}")
        await event.answer("⚠️ Gagal menghapus semua data.", alert=True)
        
@bot.on(events.CallbackQuery(pattern=b"^addprice_(.+)$"))
async def add_price_request(event):
    slug = event.pattern_match.group(1).decode()
    viewer_id = get_effective_user_id(event.sender_id)

    # Cegah sesi ganda
    if viewer_id in active_price_sessions:
        return await event.answer("⚠️ Kamu sedang mengisi harga lain. Batalkan dulu sebelum mulai baru.", alert=True)

    try:
        await event.delete()

        msg_text = f"""
🕒 **Silahkan kirim input waktu dan harga untuk gift https://t.me/nft/{slug}**

**FORMAT WAKTU:** 
__jam, hari, minggu, bulan dan tahun.__

**__• CONTOH MISALNYA:__**
^^`1 hari - 5k` ✅
`7 hari - 30.000` ✅
`1 minggu - Rp30.000 / 1 TON` ✅

`1 day - Blabla...` 🚫
`1 week-Blabla...` 🚫
`<1 minggu> - <30.000>` 🚫^^

**format yang benar: `<durasi> - <harga>`**.
^^- Gunakan spasi untuk penggunaan strip perantara durasi dan harga.
- Jangan gunakan tanda kurung <> untuk input.
- Durasi wajib menggunakan bahasa indonesia, dan harga bebas di isi, misalnya: `1k bonus 1 day`^^
        """

        buttons = [[Button.inline("🚫 BATALKAN", data=f"cancelprice_{slug}")]]
        sent = await event.respond(msg_text.strip(), buttons=buttons)

        # Simpan sesi pengguna
        active_price_sessions[viewer_id] = {
            "slug": slug,
            "message_id": sent.id
        }

    except Exception as e:
        print(f"⚠️ Error di add_price_request: {e}")
        await event.answer("⚠️ Gagal membuka input harga.", alert=True)
        return

    @bot.on(events.NewMessage(from_users=viewer_id))
    async def handler_price_input(ev):
        if viewer_id not in active_price_sessions:
            return  # sesi sudah dibatalkan
    
        try:
            session = active_price_sessions[viewer_id]
            slug_sess = session["slug"]
    
            if "-" not in ev.raw_text:
                return await ev.reply("⚠️ Format salah! Gunakan format: `1 hari - 5000`")
    
            waktu_str, harga_str = map(str.strip, ev.raw_text.split("-", 1))
            harga = harga_str
            created_at = int(time.time())
    
            # parse waktu → kalau gagal, set 0
            try:
                durasi_detik = parse_duration(waktu_str)
            except Exception:
                durasi_detik = 0
    
            # === Simpan harga ke tabel ===
            cur.execute("""
                INSERT INTO gift_rent_prices (slug, duration_text, duration_seconds, price, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (slug_sess, waktu_str, durasi_detik, harga, created_at))
            conn.commit()
    
            # === Ambil info gift dari DB untuk update posting channel ===
            cur.execute("""
                SELECT model, background, symbol, rarity, gift_address, channel_msg_id, username
                FROM gift_rent WHERE slug=?
            """, (slug_sess,))
            gift_row = cur.fetchone()
            if not gift_row:
                return await ev.reply("⚠️ Gift tidak ditemukan di database.")
    
            model, background, symbol, rarity, gift_address, channel_msg_id, username = gift_row
    
            if not channel_msg_id or channel_msg_id == 0:
                buttons = [[Button.inline("🔙 KEMBALI", data=f"rentgift_{slug_sess}")]]
                await ev.reply("✅ **__Harga berhasil disimpan!__**", buttons=buttons)
            else:
                # === Ambil semua harga terbaru ===
                cur.execute("""
                    SELECT duration_text, price FROM gift_rent_prices
                    WHERE slug=? ORDER BY id
                """, (slug_sess,))
                prices = cur.fetchall()
    
                if prices:
                    price_lines = []
                    for dur, pval in prices:
                        # tampilkan string as-is kalau bukan integer
                        if isinstance(pval, int) or str(pval).isdigit():
                            price_display = f"Rp{int(pval):,}"
                        else:
                            price_display = str(pval).strip()
                        price_lines.append(f"• {dur} → {price_display}")
                    display_price = "\n".join(price_lines)
                else:
                    display_price = "__Owner belum memasang harga!__"
    
                # === Buat link tonviewer ===
                tonviewer_link = f"https://tonviewer.com/{gift_address}" if gift_address else None
                ton_line = f"[OPEN]({tonviewer_link})" if tonviewer_link else "❌ Tidak tersedia"
    
                # === Buat contact line ===
                contact_line = f"📞 **CONTACT:** @{username}" if username else "📞 **CONTACT:** (username tidak tersedia)"
    
                # === Rarity placeholder aman ===
                model_rarity = background_rarity = symbol_rarity = rarity or "-"
    
                # === Caption postingan baru ===
                caption = f"""
⌚️ **__GIFT AVAILABLE FOR RENTAL!__**
    
[{slug_sess}](https://t.me/nft/{slug_sess})
    
^^✨ **Model:** {model or '-'} ({model_rarity})
🖼️ **Background:** {background or '-'} ({background_rarity})
👾 **Symbol:** {symbol or '-'} ({symbol_rarity})
🔎 **__Scan tonviewer:__** {ton_line}
{contact_line}^^
    
💸 **__PRICE DURASI__**
{display_price}
                """.strip()
    
                try:
                    # === Edit postingan di channel ===
                    await bot.edit_message(CHANNEL_RENTAL, channel_msg_id, caption)
                    await ev.reply("✅ Harga disimpan & postingan channel berhasil diperbarui.")
                except Exception as e:
                    print(f"⚠️ Gagal mengedit postingan channel: {e}")
                    await ev.reply("⚠️ Harga disimpan, tapi gagal memperbarui postingan channel.")
    
            buttons = [[Button.inline("🔙 KEMBALI", data=f"rentgift_{slug_sess}")]]
            msg = f"""
    ✅ **__Berhasil disimpan!__**
    
    - **Gift:** https://t.me/nft/{slug_sess}
    - **Durasi:** {waktu_str}
    - **Price:** {harga}
            """
            await ev.respond(msg, buttons=buttons, link_preview=False)
    
            # === Hapus sesi ===
            if viewer_id in active_price_sessions:
                del active_price_sessions[viewer_id]
            bot.remove_event_handler(handler_price_input)
    
        except Exception as e:
            print(f"⚠️ Error di handler_price_input: {e}")
            await ev.reply("⚠️ Terjadi kesalahan saat menyimpan harga.")
            if viewer_id in active_price_sessions:
                del active_price_sessions[viewer_id]
            bot.remove_event_handler(handler_price_input)

# 🔹 Handle tombol batal input harga
@bot.on(events.CallbackQuery(pattern=b"^cancelprice_(.+)$"))
async def cancel_price_session(event):
    slug = event.pattern_match.group(1).decode()
    viewer_id = get_effective_user_id(event.sender_id)

    if viewer_id in active_price_sessions:
        del active_price_sessions[viewer_id]

    await event.edit(f"🚫 Input harga untuk `{slug}` telah dibatalkan.", buttons=[
        [Button.inline("🔙 KEMBALI", data=f"rentprice_{slug}")]
    ])

# === Handler klik DELETE PRICE ===
@bot.on(events.CallbackQuery(pattern=b"^delprice_(.+)$"))
async def handle_delete_price(event):
    slug = event.pattern_match.group(1).decode()
    user_id = event.sender_id

    cur.execute("SELECT price FROM gift_rent WHERE slug=? AND user_id=?", (slug, user_id))
    row = cur.fetchone()

    if not row or not row[0]:
        return await event.answer("❌ Tidak ada price yang disimpan.", alert=True)

    cur.execute("UPDATE gift_rent SET price=0 WHERE slug=? AND user_id=?", (slug, user_id))
    conn.commit()

    msg = f"✅ **Price untuk gift `{slug}` telah dihapus.**"
    buttons = [[Button.inline("🔙 KEMBALI", data=f"rentprice_{slug}")]]
    await event.edit(msg.strip(), buttons=buttons)

@bot.on(events.CallbackQuery(data=b"add_rent"))
async def rent_start(event):
    user_id = event.sender_id
    rent_sessions[user_id] = {"step": "awaiting_link"}

    await event.delete()
    await event.respond(
        "⌚️ **Masukkan link gift yang ingin kamu tambahkan untuk disewakan.**\n\n"
        "__Contoh:__\n`https://t.me/nft/LushBouquet-34343`\n\nKirim sekarang:",
        buttons=[[Button.inline("❌ Batal", data="cancel_rent")]],
    )


# 2️⃣ — HANDLE: input link gift dari user
@bot.on(events.NewMessage)
async def handle_rent_input(event):
    user_id = event.sender_id
    if user_id not in rent_sessions:
        return

    session = rent_sessions[user_id]
    if session.get("step") != "awaiting_link":
        return

    text = event.raw_text.strip()
    match = GIFT_LINK_PATTERN.match(text)
    if not match:
        await event.reply(
            "⚠️ Format link gift tidak valid.\n\n"
            "__Contoh yang benar:__\n`https://t.me/nft/JellyBunny-1234`"
        )
        return

    slug = match.group(1)
    slug = slug.decode() if isinstance(slug, bytes) else slug

    cur.execute("SELECT slug FROM gift_rent WHERE slug=?", (slug,))
    if cur.fetchone():
        await event.reply(f"⚠️ Gift `{slug}` sudah terdaftar di daftar rental.")
        del rent_sessions[user_id]
        return

    try:
        # Ambil data gift dari Telegram (via userbot)
        result = await userbot(functions.payments.GetUniqueStarGiftRequest(slug=slug))
        gift = getattr(result, "gift", None)
        if not gift:
            await event.reply("❌ Gift tidak ditemukan.")
            del rent_sessions[user_id]
            return

        gift_address = getattr(gift, "gift_address", None)
        owner_id = getattr(result, "owner_id", None)
        owner_address = getattr(result, "owner_address", None)

        if not gift_address:
            await event.reply(f"🚫 Gift `{slug}` tidak memiliki `gift_address` yang valid.")
            del rent_sessions[user_id]
            return

        # Ambil data dari TonAPI
        async with aiohttp.ClientSession() as session_http:
            nft_url = f"https://tonapi.io/v2/nfts/{gift_address}"
            async with session_http.get(nft_url) as resp:
                if resp.status != 200:
                    await event.reply(f"❌ Gagal ambil data dari TonAPI ({resp.status})")
                    del rent_sessions[user_id]
                    return
                nft_data = await resp.json()

        owner = nft_data.get("owner") or {}
        is_wallet = owner.get("is_wallet", True)
        owner_ton_address = owner.get("address", "Tidak diketahui")

        if not is_wallet:
            await event.reply(
                "❌ Gift ini **tidak lagi dipegang oleh pemilik aslinya!**\n\n"
                f"💼 **Wallet Saat Ini:**\nhttps://tonscan.org/address/{owner_ton_address}"
            )
            del rent_sessions[user_id]
            return

        # Cek pemilik Telegram
        owner_tg_id = None
        if isinstance(owner_id, types.PeerUser):
            owner_tg_id = owner_id.user_id

        if owner_tg_id and owner_tg_id != user_id:
            await event.reply(
                f"🚫 Kamu **bukan pemilik asli gift ini** menurut data Telegram.\n\n"
                f"👤 Pemilik Asli Telegram ID: `{owner_tg_id}`"
            )
            del rent_sessions[user_id]
            return

        # Kirim ke ADMIN untuk konfirmasi
        confirm_buttons = [
            [
                Button.inline("✅ KONFIRMASI", data=f"confirm_rent:{user_id}:{slug}"),
                Button.inline("❌ TOLAK", data=f"reject_rent:{user_id}:{slug}")
            ]
        ]

        notif_text = f"""
📩 **PERMINTAAN RENTAL BARU DARI USER**
👤 User ID: `{user_id}`
🎁 Slug: `{slug}`
📜 Gift Address: `{gift_address}`
💼 Wallet Pemilik Asli: [Lihat di Tonscan](https://tonscan.org/address/{owner_ton_address})

Mohon konfirmasi apakah gift ini layak ditambahkan ke daftar sewa.
"""

        for admin_id in OWNER_ID:
            try:
                await bot.send_message(admin_id, notif_text, buttons=confirm_buttons, link_preview=False)
            except Exception as e:
                print(f"❌ Gagal kirim notifikasi ke OWNER {admin_id}: {e}")

        await event.reply(
            "✅ **Gift kamu telah diverifikasi dan menunggu konfirmasi admin.**\n\n"
            "⏳ Harap tunggu hingga salah satu penjamin menyetujui atau menolak permintaanmu."
        )

    except errors.RPCError as e:
        await event.reply(f"❌ RPCError saat ambil data gift `{slug}`:\n`{e}`")
    except Exception as e:
        await event.reply(f"❌ Error saat verifikasi gift `{slug}`:\n`{e}`")
    finally:
        rent_sessions.pop(user_id, None)

@bot.on(events.CallbackQuery(pattern=r"^(confirm_rent|reject_rent):(\d+):(.+)$"))
async def rent_confirm_reject(event):
    try:
        action, user_id, slug = event.pattern_match.groups()
        action = action.decode() if isinstance(action, bytes) else action
        user_id = int(user_id)
        slug = slug.decode() if isinstance(slug, bytes) else slug
    except Exception as e:
        await event.answer("⚠️ Format callback tidak valid!", alert=True)
        print("⚠️ CALLBACK RAW:", event.data)
        return

    if action == "confirm_rent":
        created_at = int(time.time())

        # === Ambil info user untuk simpan username ===
        try:
            user = await bot.get_entity(user_id)
            if user.username:
                username = user.username
            elif getattr(user, "usernames", None):
                username = user.usernames[0].username
            else:
                username = None
        except Exception:
            username = None

        # === Simpan ke database ===
        cur.execute("""
            INSERT OR IGNORE INTO gift_rent (user_id, username, slug, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, username, slug, created_at))
        conn.commit()

        await event.edit(f"✅ Gift `{slug}` telah **DITERIMA** dan disimpan ke database.")
        await bot.send_message(
            user_id,
            f"🎉 Gift `{slug}` kamu telah **disetujui oleh admin** dan sekarang aktif di daftar rental!"
        )

    elif action == "reject_rent":
        await event.edit(f"❌ Gift `{slug}` telah **DITOLAK** oleh admin.")
        await bot.send_message(
            user_id,
            f"🚫 Gift `{slug}` kamu telah **ditolak oleh admin** dan tidak ditambahkan ke daftar rental."
        )

    else:
        await event.answer("⚠️ Aksi tidak dikenal.", alert=True)
        print("⚠️ ACTION TIDAK DIKENAL:", action)

@bot.on(events.CallbackQuery(data=b"cancel_rent"))
async def cancel_rent(event):
    user_id = event.sender_id
    if user_id in rent_sessions:
        del rent_sessions[user_id]
    await event.answer("❌ Sesi add rental dibatalkan!", alert=True)
    await handle_rent(event)

@bot.on(events.InlineQuery)
async def inline_gift_scan(event):
    query = event.text.strip()

    if not query or not query.startswith("#"):
        return

    query = query.lstrip("#").strip()
    if not query:
        await event.answer([], switch_pm="Ketik link gift setelah tanda #", switch_pm_param="start")
        return

    slug = normalize_slug(query)
    if not slug:
        await event.answer([], switch_pm="Slug gift tidak valid", switch_pm_param="start")
        return

    cur.execute("SELECT slug, message_id, text FROM gift_scanned WHERE slug LIKE ?", (f"%{slug}%",))
    results = cur.fetchall()

    inline_results = []

    if results:
        for idx, (slug_db, msg_id, text) in enumerate(results, start=1):
            channel_link = f"https://t.me/c/{str(CHAT_SCAN_ID)[4:]}/{msg_id}"

            inline_results.append(
                event.builder.article(
                    id=f"{slug_db}_{msg_id}_{idx}",
                    title=f"🎁 {slug_db}",
                    description=text[:100] + "..." if len(text) > 100 else text,
                    text=f"🎁 **Gift ditemukan:** `{slug_db}`\n\n{text}",
                    buttons=[Button.url("🔗 Lihat Pesan Asli", channel_link)],
                    link_preview=False
                )
            )

        await event.answer(inline_results, cache_time=0)
    else:
        await event.answer([], switch_pm="❌ Tidak ditemukan di hasil scan", switch_pm_param="start")

@bot.on(events.InlineQuery)
async def inline_search(event):
    text = event.text.strip()
    if not text:
        return

    query = text.lower()
    parts = [p.strip() for p in query.split(",") if p.strip()]
    inline_results = []

    RESULTS_PER_PAGE = 25
    user_id = event.sender_id

    # ==============================
    # FIX: helper VALIDASI SOLD KE DB
    # ==============================
    def filter_unsold_slugs(slugs):
        if not slugs:
            return set()
        placeholders = ",".join("?" * len(slugs))
        cur.execute(
            f"SELECT slug FROM gifts WHERE is_sold=0 AND slug IN ({placeholders})",
            tuple(slugs)
        )
        return {row[0] for row in cur.fetchall()}

    def format_slug_display(slug: str) -> str:
        slug_parts = slug.split("-")
        name = slug_parts[0]
        number = slug_parts[1] if len(slug_parts) > 1 else ""
        display_name = "".join(
            [" " + c if c.isupper() else c for c in name]
        ).strip()
        return f"{display_name} #{number}" if number else display_name

    # ==============================
    # SEARCH BY NUMBER
    # ==============================
    number_match = re.match(r"^#(\d+)(?:-#?(\d+))?$", query)
    if number_match:
        start_num = int(number_match.group(1))
        end_num = int(number_match.group(2)) if number_match.group(2) else start_num

        results = []
        cur.execute("""
            SELECT slug, price, model, background, symbol, msg_id
            FROM gifts
            WHERE is_listed=1 AND is_sold=0
        """)
        all_gifts = cur.fetchall()
        all_gifts.sort(key=lambda x: x[1] or 0)

        for slug, price, model, bg, symbol, msg_id in all_gifts:
            slug_parts = slug.split("-")
            if len(slug_parts) < 2:
                continue
            try:
                num = int(slug_parts[1])
            except:
                continue
            if start_num <= num <= end_num:
                results.append((slug, price, model, bg, symbol, msg_id))

        if results:
            total_pages = math.ceil(len(results) / RESULTS_PER_PAGE)
            active_inline_pages[user_id] = {
                "results": results,
                "page": 1,
                "total_pages": total_pages
            }

            page_results = results[:RESULTS_PER_PAGE]

            # ✅ FIX: VALIDASI SOLD SEKALI LAGI
            valid_slugs = filter_unsold_slugs([r[0] for r in page_results])

            lines = []
            for slug, price, model, bg, symbol, msg_id in page_results:
                if slug not in valid_slugs:
                    continue

                name_display = format_slug_display(slug)
                final_price = int((price or 0) * 1.02)
                price_fmt = "{:,}".format(final_price).replace(",", ".")
                link = (
                    f"https://t.me/market_wine/{slug_channel_map[slug][1]}/{msg_id}"
                    if slug in slug_channel_map
                    else f"https://t.me/nft/{slug}"
                )
                lines.append(f"- [{name_display}]({link}) Rp{price_fmt}")

            if lines:
                caption = (
                    "**__All gift titipan @WINEDASH\n"
                    "Cek Gift lainnya di @MARKET_WINE__**\n\n"
                    + chr(10).join(lines)
                )

                buttons = []
                if total_pages > 1:
                    buttons.append([Button.inline("➡️", data=f"inlinepage:{user_id}:2")])

                inline_results.append(
                    event.builder.article(
                        title=f"🔢 Nomor #{start_num}{f'-#{end_num}' if start_num != end_num else ''}",
                        description=f"Hasil pencarian {len(lines)} gift dari harga terendah",
                        text=caption,
                        buttons=buttons,
                        link_preview=True
                    )
                )

    # ==============================
    # SEARCH BY PRICE
    # ==============================
    price_match = re.match(r"^(\d+(?:\.\d+)?)(?:-(\d+(?:\.\d+)?))?$", query.replace(".", ""))
    if price_match:
        price_min = int(price_match.group(1))
        price_max = int(price_match.group(2)) if price_match.group(2) else price_min

        cur.execute("""
            SELECT slug, price, model, background, symbol, msg_id
            FROM gifts
            WHERE is_listed=1 AND is_sold=0 AND price BETWEEN ? AND ?
            ORDER BY price ASC
        """, (price_min, price_max))
        results = cur.fetchall()

        if results:
            total_pages = math.ceil(len(results) / RESULTS_PER_PAGE)
            active_inline_pages[user_id] = {
                "results": results,
                "page": 1,
                "total_pages": total_pages
            }

            page_results = results[:RESULTS_PER_PAGE]
            valid_slugs = filter_unsold_slugs([r[0] for r in page_results])

            lines = []
            for slug, price, model, bg, symbol, msg_id in page_results:
                if slug not in valid_slugs:
                    continue

                name_display = format_slug_display(slug)
                final_price = int((price or 0) * 1.02)
                price_fmt = "{:,}".format(final_price).replace(",", ".")
                link = (
                    f"https://t.me/market_wine/{slug_channel_map[slug][1]}/{msg_id}"
                    if slug in slug_channel_map
                    else f"https://t.me/nft/{slug}"
                )
                lines.append(f"- [{name_display}]({link}) Rp{price_fmt}")

            if lines:
                caption = (
                    "**__All gift titipan @WINEDASH\n"
                    "Cek Gift lainnya di @MARKET_WINE__**\n\n"
                    + chr(10).join(lines)
                )

                buttons = []
                if total_pages > 1:
                    buttons.append([Button.inline("➡️", data=f"inlinepage:{user_id}:2")])

                inline_results.append(
                    event.builder.article(
                        title=f"💰 Harga Rp{price_min:,} - Rp{price_max:,}",
                        description=f"Hasil pencarian {len(lines)} gift (Low to High)",
                        text=caption,
                        buttons=buttons,
                        link_preview=True
                    )
                )

    # ==============================
    # SEARCH BY TEXT (slug / model / bg / symbol)
    # ==============================
    def build_search(column):
        if not parts:
            return []

        placeholders = " OR ".join([f"{column} LIKE ?" for _ in parts])
        params = [f"%{p}%" for p in parts]
        sql = f"""
            SELECT slug, price, model, background, symbol, msg_id
            FROM gifts
            WHERE is_listed=1 AND is_sold=0 AND ({placeholders})
            ORDER BY price ASC
        """
        cur.execute(sql, tuple(params))
        return cur.fetchall()

    def make_result(title, icon, data, desc):
        if not data:
            return

        data.sort(key=lambda x: x[1] or 0)
        total_pages = math.ceil(len(data) / RESULTS_PER_PAGE)
        active_inline_pages[user_id] = {
            "results": data,
            "page": 1,
            "total_pages": total_pages
        }

        page_results = data[:RESULTS_PER_PAGE]
        valid_slugs = filter_unsold_slugs([r[0] for r in page_results])

        lines = []
        for slug, price, model, bg, symbol, msg_id in page_results:
            if slug not in valid_slugs:
                continue

            name_display = format_slug_display(slug)
            final_price = int((price or 0) * 1.02)
            price_fmt = "{:,}".format(final_price).replace(",", ".")
            link = (
                f"https://t.me/market_wine/{slug_channel_map[slug][1]}/{msg_id}"
                if slug in slug_channel_map
                else f"https://t.me/nft/{slug}"
            )
            lines.append(f"- [{name_display}]({link}) Rp{price_fmt}")

        if not lines:
            return

        caption = f"{icon} **{title}**\n\n{chr(10).join(lines)}"
        buttons = []
        if total_pages > 1:
            buttons.append([Button.inline("➡️", data=f"inlinepage:{user_id}:2")])

        inline_results.append(
            event.builder.article(
                title=f"{icon} {title}",
                description=f"Hasil {desc} (Low to High) untuk: {', '.join(parts)}",
                text=caption,
                buttons=buttons,
                link_preview=True
            )
        )

    if parts:
        make_result("All gift titipan @WINEDASH\nCek Gift lainnya di @MARKET_WINE", "🎁", build_search("slug"), "gift")
        make_result("All gift titipan @WINEDASH\nCek Gift lainnya di @MARKET_WINE", "🎨", build_search("model"), "model")
        make_result("All gift titipan @WINEDASH\nCek Gift lainnya di @MARKET_WINE", "🖼", build_search("background"), "background")
        make_result("All gift titipan @WINEDASH\nCek Gift lainnya di @MARKET_WINE", "💎", build_search("symbol"), "symbol")

    if not inline_results:
        await event.answer([], switch_pm="❌ Tidak ditemukan", switch_pm_param="start")
    else:
        await event.answer(inline_results, cache_time=0)

@bot.on(events.CallbackQuery(pattern=r"^inlinepage:(\d+):(\d+)$"))
async def inline_page_nav(event):
    target_user, page = map(int, event.pattern_match.groups())
    sender = event.sender_id

    if sender != target_user:
        return await event.answer("⚠️ Bukan hasil pencarianmu!", alert=True)

    if target_user not in active_inline_pages:
        return await event.answer("❌ Sesi pencarian sudah berakhir.", alert=True)

    session = active_inline_pages[target_user]
    results = session["results"]
    total_pages = session["total_pages"]

    RESULTS_PER_PAGE = 25
    page = max(1, min(total_pages, page))

    start = (page - 1) * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE
    page_results = results[start:end]

    def format_slug_display(slug: str) -> str:
        parts_slug = slug.split("-")
        name = parts_slug[0]
        number = parts_slug[1] if len(parts_slug) > 1 else ""
        display_name = "".join([" " + c if c.isupper() else c for c in name]).strip()
        return f"{display_name} #{number}" if number else display_name

    lines = []
    slugs_for_grid = []

    for slug, price, model, bg, symbol, msg_id in page_results:
        name_display = format_slug_display(slug)
        final_price = int((price or 0) * 1.02)
        price_fmt = "{:,}".format(final_price).replace(",", ".")
        if slug in slug_channel_map:
            topic_id, reply_id = slug_channel_map[slug]
            link = f"https://t.me/market_wine/{reply_id}/{msg_id}"
        else:
            link = f"https://t.me/nft/{slug}"
        lines.append(f"- [{name_display}]({link}) Rp{price_fmt}")
        slugs_for_grid.append((slug, final_price))  # dipakai untuk grid gambar

    caption = (
        f"🖼 **All gift titipan @WINEDASH**\n"
        f"Cek Gift lainnya di @MARKET_WINE\n\n"
        f"{chr(10).join(lines)}"
    )

    # tombol navigasi
    buttons = []
    nav = []
    if page > 1:
        nav.append(Button.inline("⬅️", data=f"inlinepage:{target_user}:{page-1}"))
    if page < total_pages:
        nav.append(Button.inline("➡️", data=f"inlinepage:{target_user}:{page+1}"))
    if nav:
        buttons.append(nav)

    msg = await event.get_message()

    # coba bangun grid gambar sesuai item di halaman ini
    grid_io = None
    try:
        grid_io = build_inline_grid_from_slugs(slugs_for_grid)
    except Exception as e:
        print(f"⚠️ Gagal build grid di inline_page_nav: {e}")
        grid_io = None

    if grid_io:
        try:
            # kirim pesan baru dengan foto + caption halaman ini
            new_msg = await msg.respond(
                file=grid_io,
                caption=caption,
                buttons=buttons,
                link_preview=False
            )
            # hapus pesan lama (halaman lama)
            await msg.delete()
        except Exception as e:
            print(f"⚠️ Gagal kirim foto di inline_page_nav, fallback edit teks: {e}")
            await event.edit(caption, buttons=buttons, link_preview=False)
    else:
        await event.edit(caption, buttons=buttons, link_preview=False)

@bot.on(events.CallbackQuery(data=b"search_confirm"))
async def search_confirm(event):
    user = await event.get_sender()
    user_id = event.sender_id
    fullname = user.first_name or ""
    mention = f"[{fullname}](tg://user?id={user_id})"

    cur.execute("SELECT gift_name FROM user_search_gifts WHERE user_id=?", (user_id,))
    selected_gifts = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT model_name FROM user_search_models WHERE user_id=?", (user_id,))
    selected_models = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT backdrop_name FROM user_search_backdrops WHERE user_id=?", (user_id,))
    selected_backdrops = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT simbol_name FROM user_search_simbols WHERE user_id=?", (user_id,))
    selected_simbols = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT price_min, price_max FROM user_search_prices WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    price_min, price_max = (row if row else (None, None))

    cur.execute("SELECT sort_by FROM user_search_sortby WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    sortby = row[0] if row else "Lasted"

    query = """
        SELECT slug, price, model, model_rarity, background, background_rarity, symbol, msg_id
        FROM gifts
        WHERE is_listed=1 AND is_sold=0
    """
    params = []

    if selected_gifts:
        slug_conditions = []
        for g in selected_gifts:
            prefix = g.replace(" ", "")
            slug_conditions.append("slug LIKE ?")
            params.append(f"{prefix}-%")
        query += " AND (" + " OR ".join(slug_conditions) + ")"

    if selected_models:
        placeholders = ",".join("?" * len(selected_models))
        query += f" AND model IN ({placeholders})"
        params.extend(selected_models)

    if selected_backdrops:
        placeholders = ",".join("?" * len(selected_backdrops))
        query += f" AND background IN ({placeholders})"
        params.extend(selected_backdrops)

    if selected_simbols:
        placeholders = ",".join("?" * len(selected_simbols))
        query += f" AND symbol IN ({placeholders})"
        params.extend(selected_simbols)

    if price_min:
        query += " AND price >= ?"
        params.append(price_min)
    if price_max:
        query += " AND price <= ?"
        params.append(price_max)

    if sortby == "Low To High":
        query += " ORDER BY price ASC"
    elif sortby == "High To Low":
        query += " ORDER BY price DESC"
    elif sortby == "ID Ascending":
        query += " ORDER BY CAST(SUBSTR(slug, INSTR(slug, '-')+1) AS INTEGER) ASC"
    elif sortby == "ID Descending":
        query += " ORDER BY CAST(SUBSTR(slug, INSTR(slug, '-')+1) AS INTEGER) DESC"
    elif sortby == "Lasted":
        query += " ORDER BY id DESC"
    else:
        query += " ORDER BY RANDOM()"

    cur.execute(query, tuple(params))
    results = cur.fetchall()

    if not results:
        return await event.respond(f"❌ Tidak ada hasil pencarian untuk {mention}.")

    unique_results = {}
    for slug, price, model, model_rarity, bg, bg_rarity, symbol, msg_id in results:
        final_price = int(int(price or 0) * 1.02)
        unique_results[slug] = (final_price, model, model_rarity, bg, bg_rarity, symbol, msg_id)

    all_results = list(unique_results.items())
    total_pages = (len(all_results) + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE

    page = 1
    start = (page - 1) * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE
    page_results = all_results[start:end]

    lines = []
    for slug, (price, model, model_rarity, bg, bg_rarity, symbol, msg_id) in page_results:
        slug_display = format_slug_display(slug)
        price_fmt = "{:,}".format(price).replace(",", ".")

        base_name = slug.split("-")[0]
        if base_name in slug_channel_map:
            topic_id, reply_id = slug_channel_map[base_name]
            gift_link = f"https://t.me/market_wine/{reply_id}/{msg_id}"
        else:
            gift_link = f"https://t.me/nft/{slug}"

        lines.append(f"- [{slug_display}]({gift_link}) Rp{price_fmt}")

    caption = f"""
🔎 **HASIL PENCARIAN** ({page}/{total_pages})

{chr(10).join(lines)}
"""

    buttons = []
    nav = []
    if page > 1:
        nav.append(Button.inline("⬅️", data=f"search_page:{page-1}"))
    if page < total_pages:
        nav.append(Button.inline("➡️", data=f"search_page:{page+1}"))

    if nav:
        buttons.append(nav)
    buttons.append([Button.inline("🚫 BATALKAN", data="delete")])

    try:
        photo_paths = []
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

        try:
            price_font = ImageFont.truetype(font_path, 35)
        except:
            price_font = ImageFont.load_default()

        def rounded(im, radius=65):
            w, h = im.size
            mask = Image.new("L", (w, h), 0)
            d = ImageDraw.Draw(mask)
            d.rounded_rectangle((0,0,w,h), radius=radius, fill=255)
            out = Image.new("RGBA", (w,h))
            out.paste(im, (0,0), mask)
            return out

        for slug, (price, *_rest) in page_results:
            cur.execute("SELECT file_path FROM gift_previews WHERE slug=?", (slug,))
            row = cur.fetchone()
            if not row:
                continue

            preview = row[0]
            if not os.path.exists(preview):
                continue

            img = Image.open(preview).convert("RGBA")
            draw = ImageDraw.Draw(img)

            price_text = f"Rp{price:,}".replace(",", ".")

            bbox = draw.textbbox((0,0), price_text, font=price_font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]

            margin = 25

            bg_box = (margin - 10, img.height - th - margin - 10,
                      margin + tw + 10, img.height - margin + 10)
            draw.rectangle(bg_box, fill=(0, 0, 0, 160))

            draw.text((margin, img.height - th - margin),
                      price_text,
                      font=price_font,
                      fill=(255, 255, 255, 255))

            img = rounded(img, radius=50)

            temp = f"/tmp/{slug}_sx.jpg"
            img.convert("RGB").save(temp, "JPEG", quality=96)
            photo_paths.append(temp)

        if photo_paths:
            imgs = [Image.open(p) for p in photo_paths]

            n = len(imgs)
            cols = math.ceil(math.sqrt(n))
            rows = math.ceil(n / cols)

            BOX = 520
            PAD = 40
            BG = (0, 0, 0)

            grid = Image.new(
                "RGB",
                ((BOX+PAD)*cols + PAD, (BOX+PAD)*rows + PAD),
                BG
            )

            i = 0
            for r in range(rows):
                for c in range(cols):
                    if i >= n:
                        break
                    im = imgs[i].resize((BOX, BOX))
                    x = PAD + c*(BOX+PAD)
                    y = PAD + r*(BOX+PAD)
                    grid.paste(im, (x, y))
                    i += 1

            buff = io.BytesIO()
            grid.save(buff, "JPEG", quality=95)
            buff.seek(0)
            buff.name = "search_grid.jpg"

            sent = await bot.send_file(
                event.chat_id,
                buff,
                caption=caption,
                buttons=buttons,
                link_preview=False
            )
            active_search_sessions[sent.id] = user_id
            await event.answer("🔎 Mencari...")

        else:
            sent = await event.respond(caption, buttons=buttons, link_preview=False)
            active_search_sessions[sent.id] = user_id

    except Exception as e:
        print("[ERROR SEARCH GRID]:", e)
        sent = await event.respond(caption, buttons=buttons, link_preview=False)
        active_search_sessions[sent.id] = user_id

@bot.on(events.CallbackQuery(pattern=b"^search_page:(\d+)$"))
async def search_page(event):
    user = await event.get_sender()
    user_id = event.sender_id
    fullname = user.first_name or ""
    mention = f"[{fullname}](tg://user?id={user_id})"

    page = int(event.pattern_match.group(1).decode())

    cur.execute("SELECT gift_name FROM user_search_gifts WHERE user_id=?", (user_id,))
    selected_gifts = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT model_name FROM user_search_models WHERE user_id=?", (user_id,))
    selected_models = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT backdrop_name FROM user_search_backdrops WHERE user_id=?", (user_id,))
    selected_backdrops = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT simbol_name FROM user_search_simbols WHERE user_id=?", (user_id,))
    selected_simbols = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT price_min, price_max FROM user_search_prices WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    price_min, price_max = (row if row else (None, None))

    cur.execute("SELECT sort_by FROM user_search_sortby WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    sortby = row[0] if row else "Lasted"

    query = """
        SELECT slug, price, model, model_rarity, background, background_rarity, symbol, msg_id
        FROM gifts
        WHERE is_listed=1 AND is_sold=0
    """
    params = []

    if selected_gifts:
        slug_conditions = []
        for g in selected_gifts:
            prefix = g.replace(" ", "")
            slug_conditions.append("slug LIKE ?")
            params.append(f"{prefix}-%")
        query += " AND (" + " OR ".join(slug_conditions) + ")"

    if selected_models:
        query += f" AND model IN ({','.join('?' * len(selected_models))})"
        params.extend(selected_models)

    if selected_backdrops:
        query += f" AND background IN ({','.join('?' * len(selected_backdrops))})"
        params.extend(selected_backdrops)

    if selected_simbols:
        query += f" AND symbol IN ({','.join('?' * len(selected_simbols))})"
        params.extend(selected_simbols)

    if price_min:
        query += " AND price >= ?"
        params.append(price_min)
    if price_max:
        query += " AND price <= ?"
        params.append(price_max)

    if sortby == "Low To High":
        query += " ORDER BY price ASC"
    elif sortby == "High To Low":
        query += " ORDER BY price DESC"
    elif sortby == "ID Ascending":
        query += " ORDER BY CAST(SUBSTR(slug, INSTR(slug, '-')+1) AS INTEGER) ASC"
    elif sortby == "ID Descending":
        query += " ORDER BY CAST(SUBSTR(slug, INSTR(slug, '-')+1) AS INTEGER) DESC"
    elif sortby == "Lasted":
        query += " ORDER BY id DESC"
    else:
        query += " ORDER BY RANDOM()"

    cur.execute(query, tuple(params))
    results = cur.fetchall()

    if not results:
        return await event.edit(f"❌ Tidak ada hasil pencarian untuk {mention}.")

    unique_results = {}
    for slug, price, model, model_rarity, bg, bg_rarity, symbol, msg_id in results:
        final_price = int(int(price or 0) * 1.02)
        unique_results[slug] = (final_price, model, model_rarity, bg, bg_rarity, symbol, msg_id)

    all_results = list(unique_results.items())
    total_pages = (len(all_results) + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE

    start = (page - 1) * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE
    page_results = all_results[start:end]

    lines = []
    for slug, (price, model, model_rarity, bg, bg_rarity, symbol, msg_id) in page_results:
        slug_display = format_slug_display(slug)
        price_fmt = "{:,}".format(price).replace(",", ".")

        base_name = slug.split("-")[0]
        if base_name in slug_channel_map:
            topic_id, reply_id = slug_channel_map[base_name]
            gift_link = f"https://t.me/market_wine/{reply_id}/{msg_id}"
        else:
            gift_link = f"https://t.me/nft/{slug}"

        lines.append(f"- [{slug_display}]({gift_link}) Rp{price_fmt}")

    caption = f"""
🔎 **HASIL PENCARIAN** ({page}/{total_pages})

{chr(10).join(lines)}
"""

    buttons = []
    nav = []
    if page > 1:
        nav.append(Button.inline("⬅️", data=f"search_page:{page-1}"))
    if page < total_pages:
        nav.append(Button.inline("➡️", data=f"search_page:{page+1}"))
    if nav:
        buttons.append(nav)
    buttons.append([Button.inline("🚫 BATALKAN", data="delete")])

    try:
        photo_paths = []
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        price_font = ImageFont.truetype(font_path, 35)

        def rounded(im, radius=65):
            w, h = im.size
            mask = Image.new("L", (w, h), 0)
            d = ImageDraw.Draw(mask)
            d.rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
            out = Image.new("RGBA", (w, h))
            out.paste(im, (0, 0), mask)
            return out

        for slug, (price, *_rest) in page_results:
            cur.execute("SELECT file_path FROM gift_previews WHERE slug=?", (slug,))
            row = cur.fetchone()
            if not row or not os.path.exists(row[0]):
                continue

            img = Image.open(row[0]).convert("RGBA")
            draw = ImageDraw.Draw(img)

            price_text = f"Rp{price:,}".replace(",", ".")
            bbox = draw.textbbox((0, 0), price_text, font=price_font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

            margin = 25
            bg_box = (margin - 10, img.height - th - margin - 10,
                      margin + tw + 10, img.height - margin + 10)
            draw.rectangle(bg_box, fill=(0, 0, 0, 160))
            draw.text((margin, img.height - th - margin),
                      price_text, font=price_font, fill=(255, 255, 255, 255))

            img = rounded(img, 50)

            temp = f"/tmp/{slug}_sx.jpg"
            img.convert("RGB").save(temp, "JPEG", quality=96)
            photo_paths.append(temp)

        if photo_paths:
            imgs = [Image.open(p) for p in photo_paths]
            n = len(imgs)
            cols = math.ceil(math.sqrt(n))
            rows = math.ceil(n / cols)
            BOX, PAD = 520, 40

            grid = Image.new("RGB",
                             ((BOX + PAD) * cols + PAD,
                              (BOX + PAD) * rows + PAD),
                             (0, 0, 0))

            i = 0
            for r in range(rows):
                for c in range(cols):
                    if i >= n:
                        break
                    im = imgs[i].resize((BOX, BOX))
                    x = PAD + c * (BOX + PAD)
                    y = PAD + r * (BOX + PAD)
                    grid.paste(im, (x, y))
                    i += 1

            buff = io.BytesIO()
            grid.save(buff, "JPEG", quality=95)
            buff.seek(0)
            buff.name = "search_grid.jpg"

            await event.edit(file=buff, text=caption, buttons=buttons, link_preview=False)
        else:
            await event.edit(caption, buttons=buttons, link_preview=False)

    except Exception as e:
        print("[ERROR SEARCH PAGE GRID]:", e)
        await event.edit(caption, buttons=buttons, link_preview=False)

@bot.on(events.CallbackQuery(data=b"delete"))
async def delete_event(event):
    try:
        user_id = event.sender_id
        message_id = event.message_id

        if message_id not in active_search_sessions:
            await event.answer("⚠️ Tidak ada sesi pencarian aktif!", alert=True)
            await event.delete()
            return

        owner_id = active_search_sessions[message_id]
        if user_id != owner_id:
            return await event.answer("⚠️ Kamu tidak bisa membatalkan pencarian ini, karena bukan kamu yang memulainya!", alert=True)

        # ✅ Hapus pesan & sesi
        await event.delete()
        del active_search_sessions[message_id]

    except Exception as e:
        print(f"⚠️ Error di delete_event: {e}")
        await event.answer("⚠️ Terjadi kesalahan saat membatalkan.", alert=True)

@bot.on(events.CallbackQuery(data="search"))
async def search(event):
    user = await event.get_sender()
    user_id = event.sender_id
    fullname = user.first_name or ""
    mention = f"[{fullname}](tg://user?id={user_id})"

    cur.execute("SELECT gift_name FROM user_search_gifts WHERE user_id=?", (user_id,))
    selected_gifts = [row[0] for row in cur.fetchall()]
    gift_text = ", ".join(selected_gifts) if selected_gifts else ""

    cur.execute("SELECT model_name FROM user_search_models WHERE user_id=?", (user_id,))
    selected_models = [row[0] for row in cur.fetchall()]
    model_text = ", ".join(selected_models) if selected_models else ""

    cur.execute("SELECT backdrop_name FROM user_search_backdrops WHERE user_id=?", (user_id,))
    selected_backdrops = [row[0] for row in cur.fetchall()]
    backdrop_text = ", ".join(selected_backdrops) if selected_backdrops else ""

    cur.execute("SELECT simbol_name FROM user_search_simbols WHERE user_id=?", (user_id,))
    selected_simbols = [row[0] for row in cur.fetchall()]
    simbol_text = ", ".join(selected_simbols) if selected_simbols else ""

    cur.execute("SELECT price_min, price_max FROM user_search_prices WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if row:
        price_min, price_max = row
        if price_min and price_max:
            price_text = f"{price_min} - {price_max}"
        elif price_min:
            price_text = f">= {price_min}"
        elif price_max:
            price_text = f"<= {price_max}"
        else:
            price_text = ""
    else:
        price_text = ""

    cur.execute("SELECT sort_by FROM user_search_sortby WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    sortby_text = row[0] if row else ""

    # --- Tombol inline ---
    buttons = [
      [Button.inline("🎁 GIFT", data="search_gift"),
      Button.inline("✨ MODEL", data="search_model")],
      [Button.inline("🖼 BACKDROP️", data="search_backdrop"),
      Button.inline("👾 SYMBOL", data="search_simbol")],
      [Button.inline("💸 PRICE", data="search_price"),
      Button.inline("🔎 SORT BY", data="search_sortby")],
      [Button.inline("🗑️ CLEAR ALL", data="search_clear"),
      Button.inline("✅ SEARCHING", data="search_confirm")],
      [Button.inline("🔙 KEMBALI", data="back_gift")]
    ]

    msg = f"""
🔎 **__Hallo... {mention} silahkan klik tombol dibawah ini untuk mengatur pencarian!__**

🎁 Gift: {gift_text}
✨ Model: {model_text}
🖼️ Backdrop: {backdrop_text}
👾 Simbol: {simbol_text}
💸 Price: {price_text}
🔎 Sort By: {sortby_text}
    """

    await event.edit(msg, buttons=buttons)

@bot.on(events.CallbackQuery(data=b"search_clear"))
async def search_clear(event):
    user = await event.get_sender()
    user_id = event.sender_id
    fullname = user.first_name or ""
    mention = f"[{fullname}](tg://user?id={user_id})"

    # Hapus semua filter pencarian user
    cur.execute("DELETE FROM user_search_gifts WHERE user_id=?", (user_id,))
    cur.execute("DELETE FROM user_search_models WHERE user_id=?", (user_id,))
    cur.execute("DELETE FROM user_search_backdrops WHERE user_id=?", (user_id,))
    cur.execute("DELETE FROM user_search_simbols WHERE user_id=?", (user_id,))
    cur.execute("DELETE FROM user_search_prices WHERE user_id=?", (user_id,))
    cur.execute("DELETE FROM user_search_sortby WHERE user_id=?", (user_id,))
    conn.commit()

    # --- Tombol inline ---
    buttons = [
      [Button.inline("🎁 GIFT", data="search_gift"),
      Button.inline("✨ MODEL", data="search_model")],
      [Button.inline("🖼 BACKDROP️", data="search_backdrop"),
      Button.inline("👾 SYMBOL", data="search_simbol")],
      [Button.inline("💸 PRICE", data="search_price"),
      Button.inline("🔎 SORT BY", data="search_sortby")],
      [Button.inline("🗑️ CLEAR ALL", data="search_clear"),
      Button.inline("✅ SEARCHING", data="search_confirm")],
      [Button.inline("🔙 KEMBALI", data="back_gift")]
    ]

    msg = f"""
🔎 **__Hallo... {mention} silahkan klik tombol dibawah ini untuk mengatur pencarian!__**

🎁 Gift: 
✨ Model: 
🖼️ Backdrop: 
👾 Simbol: 
💸 Price: 
🔎 Sort By: 
    """

    await event.edit(msg, buttons=buttons)

@bot.on(events.CallbackQuery(data="search_gift"))
async def search_gift(event):
    user = await event.get_sender()
    user_id = event.sender_id
    fullname = user.first_name or ""
    mention = f"[{fullname}](tg://user?id={user_id})"

    # Hitung jumlah gift di database (hanya yang available)
    gift_counts = {}
    cur.execute("SELECT slug FROM gifts WHERE is_listed=1 AND is_sold=0")
    all_slugs = [row[0] for row in cur.fetchall() if row[0]]

    for slug in all_slugs:
        base_slug = slug.split("-")[0]
        display_name = "".join([" " + c if c.isupper() and i > 0 else c
                                for i, c in enumerate(base_slug)]).strip()
        gift_counts[display_name] = gift_counts.get(display_name, 0) + 1

    # Ambil pilihan user dari DB
    cur.execute("SELECT gift_name FROM user_search_gifts WHERE user_id=?", (user_id,))
    selected_gifts = [row[0] for row in cur.fetchall()]

    # Buat tombol gift list
    buttons = []
    row = []
    for gift_name, count in sorted(gift_counts.items()):
        prefix = "✅ " if gift_name in selected_gifts else ""
        label = f"{prefix}{gift_name} ({count})"
        row.append(Button.inline(label, data=f"cari_gift_{gift_name.replace(' ', '_')}"))
        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    # Tambahan tombol kontrol
    buttons.append([
        Button.inline("🗑️ CLEAR ALL", data="clear_search_gift"),
        Button.inline("📌 SELECT ALL", data="select_search_gift")
    ])

    # Tombol kembali
    buttons.append([Button.inline("🔙 KEMBALI", data="search")])

    msg = f"""
🔎 **LIST GIFT SEARCHING**

**Hallo {mention}, silakan pilih gift yang ingin kamu cari!**
    """

    await event.edit(msg, buttons=buttons)

@bot.on(events.CallbackQuery(data="clear_search_gift"))
async def clear_search_gift(event):
    user_id = event.sender_id
    cur.execute("DELETE FROM user_search_gifts WHERE user_id=?", (user_id,))
    conn.commit()
    await search_gift(event)  # Refresh tampilan


@bot.on(events.CallbackQuery(data="select_search_gift"))
async def select_search_gift(event):
    user_id = event.sender_id
    cur.execute("DELETE FROM user_search_gifts WHERE user_id=?", (user_id,))

    # Ambil semua gift yang tersedia
    cur.execute("SELECT slug FROM gifts WHERE is_listed=1 AND is_sold=0")
    all_slugs = [row[0] for row in cur.fetchall() if row[0]]
    unique_names = set("".join([" " + c if c.isupper() and i > 0 else c
                               for i, c in enumerate(slug.split('-')[0])]).strip()
                       for slug in all_slugs)

    # Masukkan semuanya sebagai pilihan user
    cur.executemany("INSERT INTO user_search_gifts (user_id, gift_name) VALUES (?, ?)",
                    [(user_id, name) for name in unique_names])
    conn.commit()
    await search_gift(event)  # Refresh tampilan

@bot.on(events.CallbackQuery(pattern=b"^cari_gift_(.+)$"))
async def cari_gift(event):
    user_id = event.sender_id
    gift_raw = event.pattern_match.group(1).decode()
    gift_name = gift_raw.replace("_", " ")

    # Toggle simpan / hapus pilihan gift di DB
    cur.execute("SELECT 1 FROM user_search_gifts WHERE user_id=? AND gift_name=?", (user_id, gift_name))
    row = cur.fetchone()

    if row:
        cur.execute("DELETE FROM user_search_gifts WHERE user_id=? AND gift_name=?", (user_id, gift_name))
    else:
        cur.execute("INSERT OR IGNORE INTO user_search_gifts (user_id, gift_name) VALUES (?, ?)", (user_id, gift_name))
    conn.commit()

    # Ambil ulang pilihan user
    cur.execute("SELECT gift_name FROM user_search_gifts WHERE user_id=?", (user_id,))
    selected_gifts = [row[0] for row in cur.fetchall()]

    # Hitung ulang jumlah gift (hanya yang available)
    gift_counts = {}
    cur.execute("SELECT slug FROM gifts WHERE is_listed=1 AND is_sold=0")
    all_slugs = [row[0] for row in cur.fetchall() if row[0]]

    for slug in all_slugs:
        base_slug = slug.split("-")[0]
        display_name = "".join([" " + c if c.isupper() and i > 0 else c
                                for i, c in enumerate(base_slug)]).strip()
        gift_counts[display_name] = gift_counts.get(display_name, 0) + 1

    # Buat ulang tombol dengan tanda ✅
    buttons = []
    row_btn = []
    for gift_name, count in sorted(gift_counts.items()):
        prefix = "✅ " if gift_name in selected_gifts else ""
        label = f"{prefix}{gift_name} ({count})"
        row_btn.append(Button.inline(label, data=f"cari_gift_{gift_name.replace(' ', '_')}"))
        if len(row_btn) == 2:
            buttons.append(row_btn)
            row_btn = []
    if row_btn:
        buttons.append(row_btn)

    buttons.append([Button.inline("🔙 KEMBALI", data="search")])

    msg = f"""
🔎 **LIST GIFT SEARCHING**

**Hallo, silakan pilih gift yang ingin kamu cari!**
    """

    await event.edit(msg, buttons=buttons)

@bot.on(events.CallbackQuery(data=b"search_model"))
async def search_model(event):
    user = await event.get_sender()
    user_id = event.sender_id
    fullname = user.first_name or ""
    mention = f"[{fullname}](tg://user?id={user_id})"

    # --- Ambil gift yang dipilih user ---
    cur.execute("SELECT gift_name FROM user_search_gifts WHERE user_id=?", (user_id,))
    selected_gifts = [row[0] for row in cur.fetchall()]

    if not selected_gifts:
        return await event.answer("❌ Kamu belum memilih gift!", alert=True)

    # Ambil model sesuai gift dari tabel gifts (pakai model + model_rarity)
    models_available = {}
    for gift in selected_gifts:
        slug_prefix = gift.replace(" ", "")
        cur.execute("""
            SELECT DISTINCT model, model_rarity 
            FROM gifts 
            WHERE slug LIKE ? AND is_listed=1 AND is_sold=0
        """, (f"{slug_prefix}-%",))
        for row in cur.fetchall():
            if row[0]:  # pastikan ada model
                models_available[row[0]] = row[1] or "Unknown"

    # Ambil model yang sudah dipilih user sebelumnya
    cur.execute("SELECT model_name FROM user_search_models WHERE user_id=?", (user_id,))
    selected_models = [row[0] for row in cur.fetchall()]

    # Buat tombol daftar model + rarity (2 tombol per baris)
    buttons = []
    row = []
    for model, rarity in sorted(models_available.items()):
        prefix = "✅ " if model in selected_models else ""
        label = f"{prefix}{model} ({rarity})"
        row.append(Button.inline(label, data=f"cari_model_{model.replace(' ', '_')}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    # Tambahan tombol kontrol (CLEAR ALL & SELECT ALL)
    buttons.append([
        Button.inline("🗑️ CLEAR ALL", data="clear_search_model"),
        Button.inline("📌 SELECT ALL", data="select_search_model")
    ])

    # Tombol kembali
    buttons.append([Button.inline("🔙 KEMBALI", data="search")])

    msg = f"""
🔎 **LIST MODEL SEARCHING**

Hallo {mention}, berikut model yang tersedia dari gift pilihanmu.
Silakan pilih model yang ingin difilter:
    """
    await event.edit(msg, buttons=buttons)


# === Handler CLEAR ALL ===
@bot.on(events.CallbackQuery(data=b"clear_search_model"))
async def clear_search_model(event):
    user_id = event.sender_id
    cur.execute("DELETE FROM user_search_models WHERE user_id=?", (user_id,))
    conn.commit()
    await search_model(event)  # Refresh tampilan


# === Handler SELECT ALL ===
@bot.on(events.CallbackQuery(data=b"select_search_model"))
async def select_search_model(event):
    user_id = event.sender_id

    # Hapus dulu data lama
    cur.execute("DELETE FROM user_search_models WHERE user_id=?", (user_id,))

    # Ambil semua gift yang dipilih user
    cur.execute("SELECT gift_name FROM user_search_gifts WHERE user_id=?", (user_id,))
    selected_gifts = [row[0] for row in cur.fetchall()]

    if not selected_gifts:
        return await event.answer("❌ Kamu belum memilih gift!", alert=True)

    # Ambil semua model yang tersedia dari gift yang dipilih
    all_models = set()
    for gift in selected_gifts:
        slug_prefix = gift.replace(" ", "")
        cur.execute("""
            SELECT DISTINCT model 
            FROM gifts 
            WHERE slug LIKE ? AND is_listed=1 AND is_sold=0
        """, (f"{slug_prefix}-%",))
        for row in cur.fetchall():
            if row[0]:
                all_models.add(row[0])

    # Masukkan semua model ke DB user_search_models
    cur.executemany(
        "INSERT INTO user_search_models (user_id, model_name) VALUES (?, ?)",
        [(user_id, m) for m in all_models]
    )
    conn.commit()
    await search_model(event)  # Refresh tampilan


@bot.on(events.CallbackQuery(pattern=b"^cari_model_(.+)$"))
async def cari_model(event):
    user_id = event.sender_id
    model_raw = event.pattern_match.group(1).decode()
    model_name = model_raw.replace("_", " ")

    # Toggle simpan / hapus pilihan model
    cur.execute("SELECT 1 FROM user_search_models WHERE user_id=? AND model_name=?", (user_id, model_name))
    row = cur.fetchone()

    if row:
        cur.execute("DELETE FROM user_search_models WHERE user_id=? AND model_name=?", (user_id, model_name))
    else:
        cur.execute(
            "INSERT OR IGNORE INTO user_search_models (user_id, model_name) VALUES (?, ?)",
            (user_id, model_name)
        )
    conn.commit()

    # Ambil gift yang dipilih
    cur.execute("SELECT gift_name FROM user_search_gifts WHERE user_id=?", (user_id,))
    selected_gifts = [row[0] for row in cur.fetchall()]

    if not selected_gifts:
        return await event.answer("❌ Kamu belum memilih gift!", alert=True)

    # Ambil ulang daftar model dari tabel gifts
    models_available = {}
    for gift in selected_gifts:
        slug_prefix = gift.replace(" ", "")
        cur.execute("""
            SELECT DISTINCT model, model_rarity 
            FROM gifts 
            WHERE slug LIKE ? AND is_listed=1 AND is_sold=0
        """, (f"{slug_prefix}-%",))
        for row in cur.fetchall():
            if row[0]:
                models_available[row[0]] = row[1] or "Unknown"

    # Ambil model yang sudah dipilih user
    cur.execute("SELECT model_name FROM user_search_models WHERE user_id=?", (user_id,))
    selected_models = [row[0] for row in cur.fetchall()]

    # 🔹 Buat ulang tombol model (2 tombol per baris)
    buttons = []
    row = []
    for model, rarity in sorted(models_available.items()):
        prefix = "✅ " if model in selected_models else ""
        label = f"{prefix}{model} ({rarity})"
        row.append(Button.inline(label, data=f"cari_model_{model.replace(' ', '_')}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    # 🔹 Tambahkan tombol kontrol
    buttons.append([
        Button.inline("🗑️ CLEAR ALL", data="clear_search_model"),
        Button.inline("📌 SELECT ALL", data="select_search_model")
    ])

    # 🔹 Tombol kembali
    buttons.append([Button.inline("🔙 KEMBALI", data="search")])

    msg = """
🔎 **LIST MODEL SEARCHING**

Silakan pilih model yang ingin difilter:
    """
    await event.edit(msg, buttons=buttons)

@bot.on(events.CallbackQuery(data=b"search_backdrop"))
async def search_backdrop(event):
    user = await event.get_sender()
    user_id = event.sender_id
    fullname = user.first_name or ""
    mention = f"[{fullname}](tg://user?id={user_id})"

    # --- Ambil gift yang dipilih user ---
    cur.execute("SELECT gift_name FROM user_search_gifts WHERE user_id=?", (user_id,))
    selected_gifts = [row[0] for row in cur.fetchall()]

    if not selected_gifts:
        return await event.answer("❌ Kamu belum memilih gift!", alert=True)

    # Ambil backdrop sesuai gift dari tabel gifts (pakai background + background_rarity)
    backdrops_available = {}
    for gift in selected_gifts:
        slug_prefix = gift.replace(" ", "")
        cur.execute("""
            SELECT DISTINCT background, background_rarity 
            FROM gifts 
            WHERE slug LIKE ? AND is_listed=1 AND is_sold=0
        """, (f"{slug_prefix}-%",))
        for row in cur.fetchall():
            if row[0]:  # pastikan ada background
                backdrops_available[row[0]] = row[1] or "Unknown"

    # Ambil backdrop yang sudah dipilih user sebelumnya
    cur.execute("SELECT backdrop_name FROM user_search_backdrops WHERE user_id=?", (user_id,))
    selected_backdrops = [row[0] for row in cur.fetchall()]

    # Buat tombol daftar backdrop + rarity (2 tombol per baris)
    buttons = []
    row = []
    for backdrop, rarity in sorted(backdrops_available.items()):
        prefix = "✅ " if backdrop in selected_backdrops else ""
        label = f"{prefix}{backdrop} ({rarity})"
        row.append(Button.inline(label, data=f"cari_backdrop_{backdrop.replace(' ', '_')}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    # Tambahan tombol kontrol (CLEAR ALL & SELECT ALL)
    buttons.append([
        Button.inline("🗑️ CLEAR ALL", data="clear_search_backdrop"),
        Button.inline("📌 SELECT ALL", data="select_search_backdrop")
    ])

    # Tombol kembali
    buttons.append([Button.inline("🔙 KEMBALI", data="search")])

    msg = f"""
🔎 **LIST BACKDROP SEARCHING**

Hallo {mention}, berikut backdrop yang tersedia dari gift pilihanmu.
Silakan pilih backdrop yang ingin difilter:
    """
    await event.edit(msg, buttons=buttons)


# === Handler CLEAR ALL ===
@bot.on(events.CallbackQuery(data=b"clear_search_backdrop"))
async def clear_search_backdrop(event):
    user_id = event.sender_id
    cur.execute("DELETE FROM user_search_backdrops WHERE user_id=?", (user_id,))
    conn.commit()
    await search_backdrop(event)  # Refresh tampilan


# === Handler SELECT ALL ===
@bot.on(events.CallbackQuery(data=b"select_search_backdrop"))
async def select_search_backdrop(event):
    user_id = event.sender_id

    # Hapus dulu data lama
    cur.execute("DELETE FROM user_search_backdrops WHERE user_id=?", (user_id,))

    # Ambil semua gift yang dipilih user
    cur.execute("SELECT gift_name FROM user_search_gifts WHERE user_id=?", (user_id,))
    selected_gifts = [row[0] for row in cur.fetchall()]

    if not selected_gifts:
        return await event.answer("❌ Kamu belum memilih gift!", alert=True)

    # Ambil semua backdrop yang tersedia dari gift yang dipilih
    all_backdrops = set()
    for gift in selected_gifts:
        slug_prefix = gift.replace(" ", "")
        cur.execute("""
            SELECT DISTINCT background 
            FROM gifts 
            WHERE slug LIKE ? AND is_listed=1 AND is_sold=0
        """, (f"{slug_prefix}-%",))
        for row in cur.fetchall():
            if row[0]:
                all_backdrops.add(row[0])

    # Masukkan semua backdrop ke DB user_search_backdrops
    cur.executemany(
        "INSERT INTO user_search_backdrops (user_id, backdrop_name) VALUES (?, ?)",
        [(user_id, b) for b in all_backdrops]
    )
    conn.commit()
    await search_backdrop(event)  # Refresh tampilan


@bot.on(events.CallbackQuery(pattern=b"^cari_backdrop_(.+)$"))
async def cari_backdrop(event):
    user_id = event.sender_id
    backdrop_raw = event.pattern_match.group(1).decode()
    backdrop_name = backdrop_raw.replace("_", " ")

    # Toggle simpan / hapus pilihan backdrop
    cur.execute("SELECT 1 FROM user_search_backdrops WHERE user_id=? AND backdrop_name=?", (user_id, backdrop_name))
    row = cur.fetchone()

    if row:
        cur.execute("DELETE FROM user_search_backdrops WHERE user_id=? AND backdrop_name=?", (user_id, backdrop_name))
    else:
        cur.execute(
            "INSERT OR IGNORE INTO user_search_backdrops (user_id, backdrop_name) VALUES (?, ?)",
            (user_id, backdrop_name)
        )
    conn.commit()

    # Ambil gift yang dipilih
    cur.execute("SELECT gift_name FROM user_search_gifts WHERE user_id=?", (user_id,))
    selected_gifts = [row[0] for row in cur.fetchall()]

    if not selected_gifts:
        return await event.answer("❌ Kamu belum memilih gift!", alert=True)

    # Ambil ulang daftar backdrop dari tabel gifts
    backdrops_available = {}
    for gift in selected_gifts:
        slug_prefix = gift.replace(" ", "")
        cur.execute("""
            SELECT DISTINCT background, background_rarity 
            FROM gifts 
            WHERE slug LIKE ? AND is_listed=1 AND is_sold=0
        """, (f"{slug_prefix}-%",))
        for row in cur.fetchall():
            if row[0]:
                backdrops_available[row[0]] = row[1] or "Unknown"

    # Ambil backdrop yang sudah dipilih user
    cur.execute("SELECT backdrop_name FROM user_search_backdrops WHERE user_id=?", (user_id,))
    selected_backdrops = [row[0] for row in cur.fetchall()]

    # 🔹 Buat ulang tombol backdrop (2 tombol per baris)
    buttons = []
    row = []
    for backdrop, rarity in sorted(backdrops_available.items()):
        prefix = "✅ " if backdrop in selected_backdrops else ""
        label = f"{prefix}{backdrop} ({rarity})"
        row.append(Button.inline(label, data=f"cari_backdrop_{backdrop.replace(' ', '_')}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    # 🔹 Tambahkan tombol kontrol
    buttons.append([
        Button.inline("🗑️ CLEAR ALL", data="clear_search_backdrop"),
        Button.inline("📌 SELECT ALL", data="select_search_backdrop")
    ])

    # 🔹 Tombol kembali
    buttons.append([Button.inline("🔙 KEMBALI", data="search")])

    msg = """
🔎 **LIST BACKDROP SEARCHING**

Silakan pilih backdrop yang ingin difilter:
    """
    await event.edit(msg, buttons=buttons)

# === SEARCH SIMBOL ===
@bot.on(events.CallbackQuery(data=b"search_simbol"))
async def search_simbol(event):
    user = await event.get_sender()
    user_id = event.sender_id
    fullname = user.first_name or ""
    mention = f"[{fullname}](tg://user?id={user_id})"

    # --- Ambil gift yang dipilih user ---
    cur.execute("SELECT gift_name FROM user_search_gifts WHERE user_id=?", (user_id,))
    selected_gifts = [row[0] for row in cur.fetchall()]

    if not selected_gifts:
        return await event.answer("❌ Kamu belum memilih gift!", alert=True)

    # Ambil simbol sesuai gift dari tabel gifts (pakai symbol + symbol_rarity)
    simbols_available = {}
    for gift in selected_gifts:
        slug_prefix = gift.replace(" ", "")
        cur.execute("""
            SELECT DISTINCT symbol, symbol_rarity 
            FROM gifts 
            WHERE slug LIKE ? AND is_listed=1 AND is_sold=0
        """, (f"{slug_prefix}-%",))
        for row in cur.fetchall():
            if row[0]:
                simbols_available[row[0]] = row[1] or "Unknown"

    # Ambil simbol yang sudah dipilih user sebelumnya
    cur.execute("SELECT simbol_name FROM user_search_simbols WHERE user_id=?", (user_id,))
    selected_simbols = [row[0] for row in cur.fetchall()]

    # 🔹 Buat tombol daftar simbol (2 tombol per baris)
    buttons = []
    row = []
    for simbol, rarity in sorted(simbols_available.items()):
        prefix = "✅ " if simbol in selected_simbols else ""
        label = f"{prefix}{simbol} ({rarity})"
        row.append(Button.inline(label, data=f"cari_simbol_{simbol.replace(' ', '_')}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    # 🔹 Tambahkan tombol CLEAR ALL & SELECT ALL
    buttons.append([
        Button.inline("🗑️ CLEAR ALL", data="clear_search_simbol"),
        Button.inline("📌 SELECT ALL", data="select_search_simbol")
    ])

    # 🔹 Tombol kembali
    buttons.append([Button.inline("🔙 KEMBALI", data="search")])

    msg = f"""
🔎 **LIST SIMBOL SEARCHING**

Hallo {mention}, berikut simbol yang tersedia dari gift pilihanmu.
Silakan pilih simbol yang ingin difilter:
    """
    await event.edit(msg, buttons=buttons)


@bot.on(events.CallbackQuery(pattern=b"^cari_simbol_(.+)$"))
async def cari_simbol(event):
    user_id = event.sender_id
    simbol_raw = event.pattern_match.group(1).decode()
    simbol_name = simbol_raw.replace("_", " ")

    # Toggle simpan / hapus pilihan simbol
    cur.execute("SELECT 1 FROM user_search_simbols WHERE user_id=? AND simbol_name=?", (user_id, simbol_name))
    row = cur.fetchone()

    if row:
        cur.execute("DELETE FROM user_search_simbols WHERE user_id=? AND simbol_name=?", (user_id, simbol_name))
    else:
        cur.execute(
            "INSERT OR IGNORE INTO user_search_simbols (user_id, simbol_name) VALUES (?, ?)",
            (user_id, simbol_name)
        )
    conn.commit()

    # Ambil gift yang dipilih
    cur.execute("SELECT gift_name FROM user_search_gifts WHERE user_id=?", (user_id,))
    selected_gifts = [row[0] for row in cur.fetchall()]

    if not selected_gifts:
        return await event.answer("❌ Kamu belum memilih gift!", alert=True)

    # Ambil ulang daftar simbol dari gifts
    simbols_available = {}
    for gift in selected_gifts:
        slug_prefix = gift.replace(" ", "")
        cur.execute("""
            SELECT DISTINCT symbol, symbol_rarity 
            FROM gifts 
            WHERE slug LIKE ? AND is_listed=1 AND is_sold=0
        """, (f"{slug_prefix}-%",))
        for row in cur.fetchall():
            if row[0]:
                simbols_available[row[0]] = row[1] or "Unknown"

    # Ambil simbol yang dipilih user
    cur.execute("SELECT simbol_name FROM user_search_simbols WHERE user_id=?", (user_id,))
    selected_simbols = [row[0] for row in cur.fetchall()]

    # 🔹 Susun ulang tombol simbol (2 per baris)
    buttons = []
    row = []
    for simbol, rarity in sorted(simbols_available.items()):
        prefix = "✅ " if simbol in selected_simbols else ""
        label = f"{prefix}{simbol} ({rarity})"
        row.append(Button.inline(label, data=f"cari_simbol_{simbol.replace(' ', '_')}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    # 🔹 Tombol CLEAR ALL & SELECT ALL
    buttons.append([
        Button.inline("🗑️ CLEAR ALL", data="clear_search_simbol"),
        Button.inline("📌 SELECT ALL", data="select_search_simbol")
    ])

    # 🔹 Tombol kembali
    buttons.append([Button.inline("🔙 KEMBALI", data="search")])

    msg = """
🔎 **LIST SIMBOL SEARCHING**

Silakan pilih simbol yang ingin difilter:
    """
    await event.edit(msg, buttons=buttons)
    
@bot.on(events.CallbackQuery(data=b"clear_search_simbol"))
async def clear_search_simbol(event):
    user_id = event.sender_id
    cur.execute("DELETE FROM user_search_simbols WHERE user_id=?", (user_id,))
    conn.commit()
    await search_simbol(event)  # refresh tampilan


@bot.on(events.CallbackQuery(data=b"select_search_simbol"))
async def select_search_simbol(event):
    user_id = event.sender_id

    # Ambil gift yang dipilih
    cur.execute("SELECT gift_name FROM user_search_gifts WHERE user_id=?", (user_id,))
    selected_gifts = [row[0] for row in cur.fetchall()]
    if not selected_gifts:
        return await event.answer("❌ Kamu belum memilih gift!", alert=True)

    # Ambil semua simbol sesuai gift
    simbols = set()
    for gift in selected_gifts:
        slug_prefix = gift.replace(" ", "")
        cur.execute("""
            SELECT DISTINCT symbol
            FROM gifts
            WHERE slug LIKE ? AND is_listed=1 AND is_sold=0
        """, (f"{slug_prefix}-%",))
        for row in cur.fetchall():
            if row[0]:
                simbols.add(row[0])

    # Tambahkan semua simbol ke DB
    for simbol in simbols:
        cur.execute(
            "INSERT OR IGNORE INTO user_search_simbols (user_id, simbol_name) VALUES (?, ?)",
            (user_id, simbol)
        )
    conn.commit()
    await search_simbol(event)  # refresh tampilan

@bot.on(events.CallbackQuery(data=b"search_price"))
async def search_price(event):
    user_id = event.sender_id
    search_price_sessions[user_id] = True  # tandai user sedang input price

    buttons = [[Button.inline("❌ BATALKAN", data="batal_search_price")]]
    
    await event.edit(
        "💸 **SEARCH PRICE**\n\n"
        "Silakan kirim rentang harga yang ingin dicari.\n"
        "Format: `0 - 100.000` atau `1.000 - 90.000`\n\n"
        "Gunakan titik (`.`) sebagai pemisah ribuan.",
        buttons=buttons
    )


# === HANDLE BATAL SEARCH PRICE ===
@bot.on(events.CallbackQuery(data=b"batal_search_price"))
async def batal_search_price(event):
    user_id = event.sender_id
    if user_id in search_price_sessions:
        del search_price_sessions[user_id]

    await search(event)

# === HANDLE INPUT PRICE DARI USER ===
@bot.on(events.NewMessage)
async def input_search_price(event):
    user_id = event.sender_id

    if user_id not in search_price_sessions:
        return

    text = event.raw_text.strip()

    try:
        if "-" in text:
            parts = [p.strip().replace(".", "") for p in text.split("-")]
            if len(parts) != 2:
                raise ValueError("Format salah")
            price_min = int(parts[0]) if parts[0] else None
            price_max = int(parts[1]) if parts[1] else None
        else:
            price_min = int(text.replace(".", ""))
            price_max = None

        cur.execute("""
            INSERT OR REPLACE INTO user_search_prices (user_id, price_min, price_max)
            VALUES (?, ?, ?)
        """, (user_id, price_min, price_max))
        conn.commit()

        del search_price_sessions[user_id]
        
        buttons = [
          [Button.inline("🔙 KEMBALI", data="search")]
        ]

        await event.reply(
            f"✅ Rentang harga berhasil disimpan!\n"
            f"💸 {price_min or 0:,} - {price_max or '∞'}",
            parse_mode="md",
            buttons=buttons
        )

        dummy = type("obj", (object,), {"sender_id": user_id, "get_sender": event.get_sender, "edit": event.reply})
        await search(dummy)

    except Exception as e:
        await event.reply("❌ Format salah.\nGunakan contoh: `0 - 100.000`", parse_mode="md")

@bot.on(events.CallbackQuery(data=b"search_sortby"))
async def search_sortby(event):
    user_id = event.sender_id

    buttons = [
        [Button.inline("🕒 Lasted", data="sortby_lasted")],
        [Button.inline("💸 Low To High", data="sortby_lowhigh")],
        [Button.inline("💸 High To Low", data="sortby_highlow")],
        [Button.inline("🔢 ID Ascending", data="sortby_idasc")],
        [Button.inline("🔢 ID Descending", data="sortby_iddesc")],
        [Button.inline("❌ Batal", data="search")]
    ]

    await event.edit("🔎 **Silakan pilih urutan (Sort By):**", buttons=buttons)


# === SIMPAN PILIHAN SORTING KE DB ===
@bot.on(events.CallbackQuery(pattern=b"^sortby_(.+)$"))
async def sortby_selected(event):
    user_id = event.sender_id
    choice = event.pattern_match.group(1).decode()

    # mapping nama choice
    mapping = {
        "lasted": "Lasted",
        "lowhigh": "Low To High",
        "highlow": "High To Low",
        "idasc": "ID Ascending",
        "iddesc": "ID Descending"
    }

    sort_text = mapping.get(choice, "Lasted")

    # simpan ke DB
    cur.execute("""
        INSERT INTO user_search_sortby (user_id, sort_by)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET sort_by=excluded.sort_by
    """, (user_id, sort_text))
    conn.commit()

    await event.answer(f"✅ Sort by diatur ke {sort_text}", alert=True)

    await search(event)

@bot.on(events.CallbackQuery(data=b"status"))
async def status(event):
    try:
        user_id = event.sender_id

        cur.execute("SELECT first_start, last_start FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()

        if not row:
            await event.answer("❌ Data pengguna tidak ditemukan.", alert=True)
            return

        first_start, last_start = row
        if not first_start:
            await event.answer("❌ Data tanggal mulai tidak ada.", alert=True)
            return

        start_dt = datetime.strptime(first_start, "%d.%m.%Y %H:%M:%S")
        last_dt = datetime.strptime(last_start, "%d.%m.%Y %H:%M:%S") if last_start else None

        # Durasi
        now = datetime.now()
        delta = now - start_dt
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        durasi_str = f"{days} hari {hours} jam {minutes} menit"

        # Gift
        cur.execute("SELECT COUNT(*) FROM gifts WHERE user_id = ?", (user_id,))
        total_gift = cur.fetchone()[0] or 0

        cur.execute("SELECT COUNT(*) FROM user_sold_gifts WHERE user_id = ?", (user_id,))
        sold_gift = cur.fetchone()[0] or 0

        # Saldo
        cur.execute("SELECT balance FROM user_balance WHERE user_id = ?", (user_id,))
        row_saldo = cur.fetchone()
        saldo = row_saldo[0] if row_saldo and row_saldo[0] is not None else 0
        saldo_fmt = f"Rp{saldo:,}".replace(",", ".")

        # Tiket
        cur.execute("SELECT COUNT(*) FROM ticket_claims WHERE user_id = ?", (user_id,))
        row_tiket = cur.fetchone()
        total_tiket = row_tiket[0] if row_tiket and row_tiket[0] is not None else 0

        # Referral
        cur.execute("SELECT referred_by FROM user_referral WHERE user_id=?", (user_id,))
        r = cur.fetchone()
        referred_by = r[0] if r and r[0] else "-"

        cur.execute("SELECT total_ref FROM user_referral WHERE user_id=?", (user_id,))
        r2 = cur.fetchone()
        total_ref = r2[0] if r2 else 0

        buttons = [
          [Button.inline("💳 DEPOSIT", data="deposit"),
           Button.inline("📤 WITHDRAW", data="withdraw")],
          [Button.inline("🔙 KEMBALI", data="back_gift")]
        ]

        msg = f"""
📊 **STATUS PENGGUNA**
┏━━━━━━━━━━━━━━━━━━
📅 **Registed:** {start_dt.strftime("%d.%m.%Y %H:%M:%S")}
⏰ **Last Seen:** {last_dt.strftime("%d.%m.%Y %H:%M:%S") if last_dt else '-'}
⌛ **Aktif:** {durasi_str}
┗━━━━━━━━━━━━━━━━━━
💰 **Saldo:** {saldo_fmt}
🎁 **Gift added:** {total_gift}
🚫 **Gift Sold:** {sold_gift}
🎟️ **Tiket:** {total_tiket}
👥 **Referral:** `{total_ref} user`
📨 **Link Referral:**
^^https://t.me/marketaldibot?start=ref_{user_id}^^
"""

        await event.edit(msg, buttons=buttons, link_preview=False)

    except Exception as e:
        print(f"❌ Error status_callback: {e}")
        try:
            await event.answer("❌ Terjadi kesalahan saat mengambil data status.", alert=True)
        except:
            pass

@bot.on(events.CallbackQuery(pattern=b"^admin$"))
async def admin(event):
    user_id = event.sender_id
    contact_sessions[user_id] = True
    
    buttons = [[Button.inline("🚫 BERHENTI MENGHUBUNGI", data="stop_hub")]]
    
    await event.delete()
    await event.respond("**__Hallo... ada yang bisa dibantu? silahkan kirim pesan anda!__**", buttons=buttons)

@bot.on(events.CallbackQuery(data="stop_hub"))
async def stop_hub(event):
    user_id = event.sender_id
    if user_id in contact_sessions:
        del contact_sessions[user_id]

    await event.delete()
    await event.respond("🚫 **__Berhenti menghubungi admin!__**")

@bot.on(events.NewMessage)
async def forward_to_admin(event):
    if not event.is_private:
        return

    user_id = event.sender_id
    if user_id in contact_sessions and contact_sessions[user_id]:
        fwd = await bot.forward_messages(GROUP_ADMIN, event.message)
        forward_map[fwd.id] = user_id

@bot.on(events.NewMessage(chats=GROUP_ADMIN))
async def reply_from_admin(event):
    if event.is_reply:
        reply_msg = await event.get_reply_message()

        if reply_msg.id in forward_map:
            user_id = forward_map[reply_msg.id]

            text = event.raw_text.strip()

            if text.startswith(".") and len(text) > 1:
                cmd = text[1:]

                cur.execute("SELECT reply FROM admin_pers WHERE cmd=?", (cmd,))
                row = cur.fetchone()

                if row:
                    try:
                        selfmsg = await bot.send_message(user_id, "🔄 **Memuat...**")
                        await asyncio.sleep(2)
                        await bot.send_message(user_id, row[0])
                        await selfmsg.delete()
                    except Exception as e:
                        print("❌ Gagal kirim:", e)
                    return
                  
            try:
                await bot.send_message(user_id, event.message)
            except Exception as e:
                print("❌ Gagal kirim balasan:", e)

@bot.on(events.NewMessage(pattern=r"^/pers (\w+)$"))
async def save_pers(event):
    sender_id = event.sender_id
  
    if sender_id not in ADMIN_ID:
        return
    
    cmd = event.pattern_match.group(1)
    if not event.is_reply:
        return await event.reply("❌ Harus reply ke pesan yang ingin dijadikan pasangan perintah.")

    msg = await event.get_reply_message()
    text = msg.message or ""

    cur.execute("INSERT OR REPLACE INTO admin_pers (cmd, reply) VALUES (?,?)", (cmd, text))
    conn.commit()

    await event.reply(f"✅ Perintah **.{cmd}** berhasil disimpan.")

@bot.on(events.NewMessage(pattern=r"^/del (\w+)$"))
async def delete_pers(event):
    sender_id = event.sender_id
  
    if sender_id not in ADMIN_ID:
        return
    
    cmd = event.pattern_match.group(1)

    cur.execute("DELETE FROM admin_pers WHERE cmd=?", (cmd,))
    conn.commit()

    await event.reply(f"🗑 Perintah **.{cmd}** telah dihapus.")
    
@bot.on(events.NewMessage(pattern=r"^/listpers$"))
async def list_pers(event):
    sender_id = event.sender_id
  
    if sender_id not in ADMIN_ID:
        return

    cur.execute("SELECT cmd, reply FROM admin_pers")
    rows = cur.fetchall()

    if not rows:
        return await event.reply("📂 Tidak ada perintah yang tersimpan.")

    text = "📂 **LIST PERS ADMIN WINEDASH**\n\n"
    for cmd, rep in rows:
        rep_preview = (rep[:40] + "...") if len(rep) > 40 else rep
        text += f"**.{cmd}** ^^`{rep_preview}`^^\n"

    await event.reply(text)

@bot.on(events.NewMessage(pattern=r"^/resetpers$"))
async def reset_pers(event):
    sender_id = event.sender_id
  
    if sender_id not in ADMIN_ID:
        return

    cur.execute("DELETE FROM admin_pers")
    conn.commit()

    await event.reply("🗑 Semua perintah telah dihapus.")

@bot.on(events.NewMessage(pattern=r"^/clearpreview$"))
async def clear_preview(event):
    user_id_exec = event.sender_id
    if user_id_exec not in OWNER_ID and user_id_exec not in ADMIN_ID:
        return await event.reply("🚫 Anda tidak memiliki izin untuk menggunakan perintah ini.")

    try:
        # Ambil semua file preview dari database, tanpa filter apapun
        cur.execute("SELECT file_path FROM gift_previews")
        rows = cur.fetchall()

        deleted_files = 0
        for row in rows:
            file_path = row[0]
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)  # hapus file fisik
                    deleted_files += 1
                except Exception as e:
                    print(f"⚠️ Gagal hapus file {file_path}: {e}")

        # Hapus semua record dari tabel gift_previews
        cur.execute("DELETE FROM gift_previews")
        conn.commit()

        await event.reply(f"🗑️ Semua preview gift berhasil dihapus!\n"
                          f"📂 File yang dihapus: {deleted_files}")

    except Exception as e:
        print(f"⚠️ Error /clearpreview: {e}")
        await event.reply("❌ Terjadi kesalahan saat menghapus preview gift.")

@bot.on(events.NewMessage(pattern=r"^/addall$"))
async def add_all_previews(event):
    user_id_exec = event.sender_id
    if user_id_exec not in OWNER_ID and user_id_exec not in ADMIN_ID:
        return await event.reply("🚫 Anda tidak memiliki izin untuk menggunakan perintah ini.")

    # Ambil semua slug gift yang status LISTED saja
    cur.execute("""
        SELECT slug FROM gifts
        WHERE is_listed=1 AND is_sold=0
    """)
    slugs = [row[0] for row in cur.fetchall()]

    if not slugs:
        return await event.reply("❌ Tidak ada gift LISTED di database untuk disimpan preview-nya.")

    saved, skipped, failed = 0, 0, 0
    results_display = []

    await event.reply(
        f"📸 Sedang mengambil preview untuk {len(slugs)} gift LISTED...\n"
        f"Mohon tunggu beberapa saat ⏳"
    )

    for slug in slugs:
        try:
            # --- CEK apakah preview SUDAH ADA di database ---
            cur.execute("SELECT file_path FROM gift_previews WHERE slug=?", (slug,))
            existing = cur.fetchone()
            if existing:
                skipped += 1
                results_display.append(f"{slug} ⚙️ Sudah ada di database, dilewati.")
                continue

            # --- Buat URL preview Fragment langsung ---
            slug_preview = slug.lower()
            preview_url = f"https://nft.fragment.com/gift/{slug_preview}.medium.jpg"

            # --- Download preview menjadi file lokal ---
            save_dir = "/root/project/previews"
            os.makedirs(save_dir, exist_ok=True)
            file_path = os.path.join(save_dir, f"{slug_preview}.jpg")

            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(preview_url) as resp:
                    if resp.status == 200:
                        with open(file_path, "wb") as f:
                            f.write(await resp.read())
                        cur.execute("""
                            INSERT INTO gift_previews (slug, file_path, created_at)
                            VALUES (?, ?, ?)
                        """, (slug, file_path, int(time.time())))
                        conn.commit()

                        saved += 1
                        results_display.append(f"{slug} ✅ Preview tersimpan.")
                        print(f"📸 Preview tersimpan: {file_path}")
                    else:
                        failed += 1
                        results_display.append(f"{slug} 🚫 Preview tidak tersedia (HTTP {resp.status}).")
                        print(f"⚠️ Tidak ada preview untuk {slug}, HTTP {resp.status}")

        except Exception as e:
            failed += 1
            results_display.append(f"{slug} ❌ Error.")
            print(f"❌ Gagal ambil preview {slug}: {e}")

    # Ringkasan hasil terakhir (hanya 30 log terakhir)
    results_text = "\n".join(results_display[-30:])
    summary_msg = (
        f"📦 **HASIL /addall (LISTED ONLY)**\n\n"
        f"✅ **Preview disimpan:** {saved}\n"
        f"⚙️ **Sudah ada (skip):** {skipped}\n"
        f"🚫 **Gagal:** {failed}\n\n"
        f"🧾 **Log terakhir:**\n{results_text}"
    )

    await event.respond(summary_msg)

@bot.on(events.NewMessage(pattern=r"^/reloadusers$"))
async def reload_users_handler(event):
    if event.sender_id not in OWNER_ID:
        return

    conn, cur = get_db()

    cur.execute("SELECT user_id FROM user_balance")
    users = [row[0] for row in cur.fetchall()]

    added = updated = skipped = 0

    for uid in users:
        path = export_user_to_json(uid)

        # cek apakah file sudah tracked dan berubah
        repo_path = "/root/project/website"
        rel = f"users/json/{uid}.json"

        status = subprocess.run(
            ["git", "status", "--porcelain", rel],
            cwd=repo_path,
            capture_output=True,
            text=True
        ).stdout.strip()

        if not status:
            skipped += 1
            continue

        if status.startswith("??"):
            added += 1
        else:
            updated += 1

        push_user_json_to_github(uid)

    await event.reply(
        f"👤 **RELOAD USERS SELESAI**\n\n"
        f"➕ Added: {added}\n"
        f"🔄 Updated: {updated}\n"
        f"⏭️ Skipped: {skipped}"
    )

@bot.on(events.NewMessage(pattern=r"^/reloadstringid$"))
async def reload_string_id(event):
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    cur = conn.cursor()

    cur.execute("""
        SELECT id, gift_string_id
        FROM gifts
    """)

    rows = cur.fetchall()

    total = len(rows)
    created = 0

    msg_self = await event.reply("🎁 **Total {total} gift sedang diproses!...**")

    for gift_id, string_id in rows:

        if string_id:
            continue

        new_id = generate_gift_string_id()

        cur.execute("""
            UPDATE gifts
            SET gift_string_id = ?
            WHERE id = ?
        """, (new_id, gift_id))

        created += 1

    conn.commit()
    
    await msg_self.delete()
    await event.respond(
        f"✅ Reload selesai!\n\n"
        f"Total gifts: {total}\n"
        f"String dibuat: {created}\n"
        f"Sudah ada: {total - created}"
    )

@bot.on(events.NewMessage(pattern=r"^/viewstringid$"))
async def view_string_id(event):

    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    cur = conn.cursor()

    cur.execute("""
        SELECT slug, gift_string_id
        FROM gifts
        WHERE gift_string_id IS NOT NULL
    """)

    rows = cur.fetchall()

    if not rows:
        await event.reply("❌ Tidak ada gift string id ditemukan.")
        return

    data = []

    for slug, string_id in rows:
        data.append({
            "slug": slug,
            "gift_string_id": string_id
        })

    filename = "gift_string_ids.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    await event.reply(
        file=filename,
        message=f"📦 Total data: {len(data)} gift"
    )

@bot.on(events.NewMessage(pattern=r"^/clearjson$"))
async def clear_json(event):
    user_id_exec = event.sender_id
    if user_id_exec not in OWNER_ID and user_id_exec not in ADMIN_ID:
        await event.reply("🚫 Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    import os, json

    EXPORT_PATH = "/root/project/website/export/data.json"
    os.makedirs(os.path.dirname(EXPORT_PATH), exist_ok=True)

    # ================= LOAD JSON =================
    json_data = {}
    if os.path.exists(EXPORT_PATH):
        try:
            with open(EXPORT_PATH, "r", encoding="utf-8") as f:
                for item in json.load(f):
                    json_data[item["slug"]] = item
        except Exception as e:
            await event.reply(f"❌ Gagal membaca data.json\n{e}")
            return

    removed = 0
    added = 0

    # ================= REMOVE SOLD =================
    cur.execute("SELECT slug FROM gifts WHERE is_sold=1")
    sold_slugs = {row[0] for row in cur.fetchall()}

    for slug in list(json_data.keys()):
        if slug in sold_slugs:
            del json_data[slug]
            removed += 1

    # ================= ADD LISTED =================
    cur.execute("""
        SELECT
            slug,
            model, model_rarity,
            background, background_rarity,
            symbol, symbol_rarity,
            price
        FROM gifts
        WHERE is_listed=1 AND is_sold=0
    """)
    rows = cur.fetchall()

    for (
        slug,
        model, model_rarity,
        bg, bg_rarity,
        symbol, symbol_rarity,
        price
    ) in rows:

        gift_id = extract_gift_id(slug)
        base_name = slug.split("-")[0]

        def combine(name, rarity):
            if not name:
                return ""
            return f"{name} ({rarity})" if rarity else name

        json_data[slug] = {
            "id": gift_id,
            "name": f"{base_name} #{gift_id}",
            "slug": slug,
            "model": combine(model, model_rarity),
            "symbol": combine(symbol, symbol_rarity),
            "bg": combine(bg, bg_rarity),
            "price": int(price or 0),
            "saldo": int(price or 0),
            "posting": "https://t.me/market_wine/57/None",
            "image": f"https://aldiprem.github.io/WINEDASH-GALERY/previews/{slug}.jpg"
        }

        added += 1

    # ================= SAVE JSON =================
    with open(EXPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(list(json_data.values()), f, indent=2, ensure_ascii=False)

    # ================= PUSH =================
    try:
        push_json_to_github()
        pushed = "✅ Dipush ke GitHub"
    except Exception as e:
        pushed = f"⚠️ Gagal push GitHub: {e}"

    msg = (
        "🧹 **CLEAR JSON SELESAI**\n\n"
        f"❌ Dihapus (sold): {removed}\n"
        f"➕ Ditambahkan/updated (listed): {added}\n"
        f"📦 Total JSON sekarang: {len(json_data)} item\n\n"
        f"{pushed}"
    )

    await event.reply(msg)

@bot.on(events.NewMessage(pattern=r"^/ceksold$"))
async def ceksold_command(event):
    try:
        # Ambil semua gift yang status sold=1
        cur.execute("SELECT slug FROM gifts WHERE is_sold=1")
        rows = cur.fetchall()

        if not rows:
            return await event.respond("❌ Belum ada gift yang SOLD OUT.")

        slugs = [row[0] for row in rows]
        links = [f"https://t.me/nft/{slug}" for slug in slugs]

        # Buat konten file
        content = f"🚀 TOTAL {len(links)} GIFT SOLD OUT\n" + " ".join(links)

        # Simpan sementara sebagai file.txt
        file_path = "/tmp/ceksold.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Kirim file ke chat
        await bot.send_file(
            event.chat_id,
            file_path,
            caption=f"📄 Daftar gift SOLD OUT ({len(links)} items)"
        )

    except Exception as e:
        print(f"⚠️ Error /ceksold: {e}")
        await event.respond("❌ Terjadi kesalahan saat mengambil data sold gift.")

@bot.on(events.NewMessage(pattern=r"^/sold(?:\s+(.+))?$"))
async def sold_command(event):
    user_id = get_effective_user_id(event.sender_id)
    slugs = []

    # ============================
    # 1️⃣ Ambil link dari teks biasa
    # ============================
    text_links = event.pattern_match.group(1)
    if text_links:
        for link in text_links.strip().split():
            match = re.search(r"t\.me/(?:nft|market_wine)/([\w-]+)", link)
            if match:
                slugs.append(match.group(1))
            else:
                await event.respond(f"❌ Link tidak valid: {link}")

    # ============================
    # 2️⃣ Ambil link dari file reply
    # ============================
    if event.is_reply:
        reply = await event.get_reply_message()
        if reply and reply.file:
            try:
                file_path = await reply.download_media(bytes)
                content = file_path.decode("utf-8")  # asumsi file teks
                for link in re.findall(r"t\.me/(?:nft|market_wine)/([\w-]+)", content):
                    slugs.append(link)
            except Exception as e:
                print(f"⚠️ Error baca file: {e}")
                await event.respond("❌ Gagal membaca file, pastikan formatnya .txt dan berisi link valid.")
                return

    if not slugs:
        return await event.respond("❌ Tidak ada slug valid ditemukan.")

    # ============================
    # Proses setiap slug
    # ============================
    for slug in slugs:
        # Ambil msg_id dari database
        cur.execute("SELECT msg_id FROM gifts WHERE slug=?", (slug,))
        row = cur.fetchone()
        if not row:
            await event.respond(f"❌ Gift tidak ditemukan: {slug}")
            continue
        msg_id = row[0]

        # Edit pesan di channel jika ada
        slug_prefix = slug.split("-")[0]
        if slug_prefix in slug_channel_map:
            chat_id, topic_id = slug_channel_map[slug_prefix]
            try:
                await bot.edit_message(chat_id, msg_id, f"🚫 **__[SOLD OUT!](https://t.me/nft/{slug})__**")
            except Exception as e:
                if "Content of the message was not modified" in str(e):
                    print(f"ℹ️ Pesan gift {slug} sudah SOLD OUT, skip edit.")
                else:
                    print(f"⚠️ Gagal edit pesan {slug}: {e}")

        # Update status sold di database
        try:
            cur.execute("""
                UPDATE gifts
                SET is_listed=0, is_sold=1
                WHERE slug=?
            """, (slug,))
            conn.commit()
            print(f"✅ Gift {slug} berhasil diubah menjadi SOLD OUT")
        except Exception as e:
            print(f"⚠️ Gagal update gift {slug}: {e}")

    await event.respond("✅ Semua slug yang valid telah diubah menjadi SOLD OUT!")

@bot.on(events.NewMessage(pattern=r"^/add\s+(.+)\s+(\d+)$"))
async def add_gift(event):
    user_id_exec = event.sender_id
    if user_id_exec not in OWNER_ID and user_id_exec not in ADMIN_ID:
        await event.reply("🚫 Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return

    PREVIEW_DIR = "/root/project/website/previews"
    os.makedirs(PREVIEW_DIR, exist_ok=True)

    links_str = event.pattern_match.group(1)
    user_id = int(event.pattern_match.group(2))

    links = links_str.split()
    added, updated, failed = 0, 0, 0
    results_display = []
    processed_slugs = []   # ⭐ simpan slug yang berhasil diproses

    for link in links:
        m = GIFT_LINK_PATTERN.match(link)
        if not m:
            results_display.append(f"{link} 🚫 Format salah")
            failed += 1
            continue

        slug = m.group(1)
        data = await fetch_gift_data(slug)
        if not data:
            results_display.append(f"{slug} 🚫 Data gift tidak ditemukan")
            failed += 1
            continue

        db_slug = data["slug"]
        display_name = format_slug_display(db_slug)

        api_owner_id = None
        telethon_result = None

        # ================= AMBIL DATA TELETHON =================
        try:
            telethon_result = await userbot(
                functions.payments.GetUniqueStarGiftRequest(slug=db_slug)
            )

            gift = telethon_result.gift

            if gift.owner_id and isinstance(gift.owner_id, types.PeerUser):
                api_owner_id = gift.owner_id.user_id

            # ⭐ SAVE STRINGIFY KE DB
            await save_stringify(db_slug, telethon_result)

        except Exception as e:
            print(f"⚠️ Gagal ambil owner/stringify API untuk {db_slug}: {e}")

        # ================= UPSERT gifts =================
        cur.execute("SELECT id FROM gifts WHERE LOWER(slug)=?", (db_slug.lower(),))
        row = cur.fetchone()

        if row:
            gift_id = row[0]
            cur.execute("""
                UPDATE gifts SET
                    user_id=?, owner_id=?, api_owner_id=?,
                    model=?, model_rarity=?,
                    background=?, background_rarity=?,
                    symbol=?, symbol_rarity=?,
                    original_details=?,
                    availability_issued=?, availability_total=?,
                    is_listed=1, is_sold=0, price=NULL
                WHERE id=?
            """, (
                user_id, user_id, api_owner_id,
                data["model"], data["model_rarity"],
                data["background"], data["background_rarity"],
                data["symbol"], data["symbol_rarity"],
                data["original_details"],
                data["availability_issued"], data["availability_total"],
                gift_id
            ))
            conn.commit()
            updated += 1
            results_display.append(f"{display_name} ✅ (updated)")
        else:
            cur.execute("""
                INSERT INTO gifts (
                    user_id, owner_id, api_owner_id, slug,
                    model, model_rarity,
                    background, background_rarity,
                    symbol, symbol_rarity,
                    original_details,
                    availability_issued, availability_total,
                    is_listed, is_sold, price
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, user_id, api_owner_id, db_slug,
                data["model"], data["model_rarity"],
                data["background"], data["background_rarity"],
                data["symbol"], data["symbol_rarity"],
                data["original_details"],
                data["availability_issued"], data["availability_total"],
                1, 0, None
            ))
            conn.commit()
            added += 1
            results_display.append(f"{display_name} ✅ (added)")

        processed_slugs.append(db_slug)

        # ================= PREVIEW =================
        try:
            final_path = os.path.join(PREVIEW_DIR, f"{db_slug}.jpg")

            if not os.path.exists(final_path):
                temp_path = await fetch_preview_from_webpagebot(db_slug)

                if temp_path and os.path.exists(temp_path):
                    if os.path.abspath(temp_path) != os.path.abspath(final_path):
                        shutil.copyfile(temp_path, final_path)

                    cur.execute("""
                        INSERT OR REPLACE INTO gift_previews
                        (slug, file_path, created_at)
                        VALUES (?, ?, ?)
                    """, (db_slug, final_path, int(time.time())))
                    conn.commit()

                    push_previews_to_github()

        except Exception as e:
            print(f"⚠️ Preview error {db_slug}: {e}")

        # ================= NOTIF =================
        try:
            msg_notif = f"""
🎁 **[{display_name}](https://t.me/nft/{db_slug}) berhasil disimpan di akun anda!**

Sekarang anda dapat mengaturnya untuk dijual.
"""
            buttons = [[Button.inline("🔄 IMPORT INVENTORY", data=f"gift_{db_slug}")]]
            await bot.send_message(user_id, msg_notif, buttons=buttons, link_preview=False)
        except Exception as e:
            print(f"⚠️ Gagal kirim notif: {e}")

    # ================= RESULT =================
    results_text = "\n".join(results_display)
    await event.reply(
        f"✅ Ditambahkan: {added}\n"
        f"🔄 Diperbarui: {updated}\n"
        f"🚫 Gagal: {failed}\n\n"
        f"{results_text}"
    )

    # ================= EXPORT HANYA SLUG YANG DIPROSES =================
    try:
        for slug in processed_slugs:
            export_single_gift_to_json(slug)

        push_json_to_github()
        print("🚀 Export incremental selesai")

    except Exception as e:
        print(f"⚠️ Export incremental gagal: {e}")

@bot.on(events.NewMessage(pattern=r"^/unadd\s+(https://t\.me/nft/[A-Za-z0-9_-]+)$"))
async def unadd_gift(event):
    if event.sender_id not in OWNER_ID:
        return  # silent, sesuai gaya kamu

    link = event.pattern_match.group(1)
    m = GIFT_LINK_PATTERN.match(link)
    if not m:
        return await event.reply("🚫 **__Input link gift tidak benar!__**")

    slug_input = m.group(1)

    # Ambil slug + user_id + owner_id
    cur.execute("""
        SELECT slug, user_id, owner_id
        FROM gifts
        WHERE LOWER(slug) = LOWER(?)
    """, (slug_input.lower(),))
    row = cur.fetchone()

    if not row:
        return await event.reply(f"❌ **__Gift `{slug_input}` belum pernah di-add!__**")

    db_slug, user_id, owner_id = row

    # Kalau owner_id-nya kosong juga → berarti memang belum proper di-add
    if owner_id is None:
        return await event.reply(
            f"⚠️ **__Gift `{db_slug}` tidak memiliki owner_id di database (belum pernah di-add secara valid)!__**"
        )

    if not user_id:
        return await event.reply(f"⚠️ **__Gift `{db_slug}` tidak memiliki pemilik aktif di database!__**")

    cur.execute("SELECT username FROM users WHERE user_id=?", (user_id,))
    u = cur.fetchone()
    username = u[0] if (u and u[0]) else "(tidak ada username)"

    cur.execute("UPDATE gifts SET user_id=NULL, is_listed=0, price=NULL, status_tfo=NULL WHERE slug=?", (db_slug,))
    conn.commit()
    
    msg = f"""
🗑️ **__Berhasil di-unadd!__**
🎁 **GIFT:** https://t.me/nft/{db_slug}
👤 **USER:** `{user_id}` ({username})
    """.strip()
    
    await event.reply(msg)

@bot.on(events.CallbackQuery(data=b"gift"))
async def gift_list(event):
    user_id = get_effective_user_id(event.sender_id)

    if user_id in processing_gift:
        return await event.answer("⌛ Reload...")
    processing_gift.add(user_id)

    try:
        cur.execute("SELECT slug FROM gifts WHERE user_id=? AND model IS NOT NULL", (user_id,))
        rows = cur.fetchall()

        if not rows:
            return await event.answer("🔎 Anda tidak memiliki gift yang tersimpan!", alert=True)

        buttons = []
        seen_slugs = set()
        row_buttons = []

        for r in rows:
            slug = r[0]
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)

            parts = slug.split("-")
            name = parts[0]
            number = parts[1] if len(parts) > 1 else ""
            display = f"{name} #{number}"

            row_buttons.append(Button.inline(display, data=f"gift_{slug}"))

            # Tambah ke baris setiap 2 tombol
            if len(row_buttons) == 2:
                buttons.append(row_buttons)
                row_buttons = []

        # Jika ada sisa 1 tombol
        if row_buttons:
            buttons.append(row_buttons)

        # Tombol kembali di baris terakhir
        buttons.append([Button.inline("🔙 KEMBALI", data="back_gift")])

        msg = "🔎 **__Silahkan pilih gift yang ingin anda atur, klik tombol dibawah ini!__**"

        try:
            await event.edit(msg, buttons=buttons)
        except:
            try:
                await event.respond(msg, buttons=buttons)
            except:
                pass

    finally:
        processing_gift.discard(user_id)

@bot.on(events.CallbackQuery(data=b"back_gift"))
async def back_gift(event):
    user_id = get_effective_user_id(event.sender_id)
    
    if user_id in deposit_sessions:
        del deposit_sessions[user_id]
        
    if user_id in withdraw_sessions:
        del withdraw_sessions[user_id]
        
    if user_id in withdraw_proof_sessions:
        del withdraw_proof_sessions[user_id]
    
    if user_id in processing_users:
        return await event.answer("⌛ Reload...")
    
    processing_users.add(user_id)
    try:
        await event.delete()
        await start(event)
    finally:
        processing_users.discard(user_id)

@bot.on(events.CallbackQuery(pattern=b"^gift_(.+)$"))
async def gift_detail(event):
    slug = event.pattern_match.group(1).decode()
    viewer_id = get_effective_user_id(event.sender_id)

    if viewer_id in waiting_up_input:
        del waiting_up_input[viewer_id]

    if viewer_id in waiting_payment_input:
        try:
            if waiting_payment_input[viewer_id] == slug:
                del waiting_payment_input[viewer_id]
        except:
            waiting_payment_input.pop(viewer_id, None)

    cur.execute("""
        SELECT model, model_rarity, background, background_rarity,
               symbol, symbol_rarity, original_details,
               availability_issued, availability_total, price, is_listed,
               user_id, msg_id
        FROM gifts WHERE slug=?
    """, (slug,))
    row = cur.fetchone()

    if not row:
        return await event.reply("❌ Data gift tidak ditemukan.")

    (model, model_rarity, background, background_rarity,
     symbol, symbol_rarity, original_details,
     availability_issued, availability_total, price, is_listed,
     holder_id, msg_id) = row

    # Ambil detail gift via Telethon
    try:
        result = await userbot(functions.payments.GetUniqueStarGiftRequest(slug=slug))
        gift = result.gift

        # Parsing atribut gift
        for attr in gift.attributes:
            if isinstance(attr, StarGiftAttributeModel):
                model = model or attr.name
                model_rarity = model_rarity or format_rarity(getattr(attr, "rarity_permille", None))
            elif isinstance(attr, StarGiftAttributeBackdrop):
                background = background or attr.name
                background_rarity = background_rarity or format_rarity(getattr(attr, "rarity_permille", None))
            elif isinstance(attr, StarGiftAttributePattern):
                symbol = symbol or attr.name
                symbol_rarity = symbol_rarity or format_rarity(getattr(attr, "rarity_permille", None))
            elif isinstance(attr, StarGiftAttributeOriginalDetails):
                original_details = original_details or "Minus"

        availability_issued = availability_issued or getattr(gift, "availability_issued", 0)
        availability_total = availability_total or getattr(gift, "availability_total", 0)

        # Update DB
        cur.execute("""
            UPDATE gifts SET model=?, model_rarity=?, background=?, background_rarity=?,
                            symbol=?, symbol_rarity=?, original_details=?,
                            availability_issued=?, availability_total=?
            WHERE slug=?
        """, (
            model, model_rarity, background, background_rarity,
            symbol, symbol_rarity, original_details,
            availability_issued, availability_total, slug
        ))
        conn.commit()

        # Ambil owner (jika ada)
        owner_display = "__Hide__"
        try:
            if gift.owner_id and isinstance(gift.owner_id, types.PeerUser):
                owner_entity = await userbot.get_entity(gift.owner_id.user_id)
                if getattr(owner_entity, "username", None):
                    owner_display = f"@{owner_entity.username}"
                else:
                    fullname = (owner_entity.first_name or "") + " " + (owner_entity.last_name or "")
                    owner_display = fullname.strip() if fullname.strip() else f"[{owner_entity.id}](tg://user?id={owner_entity.id})"
        except Exception as e:
            print(f"⚠️ Gagal ambil entity owner: {e}")
    except Exception as e:
        print(f"⚠️ Gagal ambil gift {slug}: {e}")
        owner_display = "❌ Unknown"

    # Holder dari DB
    holder_display = "❌ Unknown"
    if holder_id:
        cur.execute("SELECT username FROM users WHERE user_id=?", (holder_id,))
        row = cur.fetchone()
        if row and row[0]:
            holder_display = f"@{row[0]}"
        else:
            holder_display = f"[{holder_id}](tg://user?id={holder_id})"

    display_price = int(price * 1.02) if price else 0
    status_text = "Dijual" if is_listed else "Tidak Dijual"
    jual_text = "🚫 UNLISTED" if is_listed else "🛒 LISTED"

    # 🔗 Perbaikan bagian topic_url — pakai topic chat, bukan slug
    topic_url = f"https://t.me/nft/{slug}"  # fallback
    base_name = slug.split("-")[0]
    if base_name in slug_channel_map:
        topic_id, reply_id = slug_channel_map[base_name]
        topic_id_str = str(topic_id).replace("-100", "")
        topic_url = f"https://t.me/market_wine/{reply_id}/{msg_id}"

    buttons = [
        [Button.inline("💸 ADD PRICE", data=f"add_price_{slug}"),
         Button.inline(jual_text, data=f"status_jual_{slug}")],
        [Button.inline("🔖 SOLD OUT", data=f"sold_{slug}"),
         Button.inline("📨 UP POSTED", data=f"up_{slug}")],
        [Button.url("🛍️ CEK POST", topic_url)],
        [Button.inline("🔙 KEMBALI", data="gift")]
    ]

    # Pesan hasil
    msg = f"""
🎁 **DATA GIFT [{slug}](https://t.me/nft/{slug})**

✨ **Model:** {model or '❌ None'} ({model_rarity or '-'})
🖼️ **Background:** {background or '❌ None'} ({background_rarity or '-'})
👾 **Symbol:** {symbol or '❌ None'} ({symbol_rarity or '-'})
🔢 **Availability:** {availability_issued or 0}/{availability_total or 0}
🔎 **Original:** {original_details or 'No minus'}

🛍️ **Post:** {topic_url}
📊 **Status:** {status_text}
💸 **Price:** Rp{display_price:,}
    """

    await event.edit(msg, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=rb"^up_(.+)$"))
async def up_gift(event):
    slug = event.pattern_match.group(1).decode()
    user_id = event.sender_id

    cur.execute("SELECT msg_id FROM gifts WHERE slug=?", (slug,))
    row = cur.fetchone()
    if not row:
        return await event.answer("❌ Gift tidak ditemukan di database, jika ini sebuah kesalahan segera hubungi admin!", alert=True)

    msg_id = row[0]
    base_name = slug.split("-")[0]

    if base_name not in slug_channel_map:
        return await event.answer("⚠️ Tidak ada mapping topic untuk slug ini, laporkan kepada admin sertakan bukti screenshoot!", alert=True)

    topic_id, topic_reply_id = slug_channel_map[base_name]

    now = int(time.time())

    cur.execute("""
        SELECT timestamp FROM gift_up_logs 
        WHERE slug=? 
        ORDER BY timestamp DESC
    """, (slug,))
    logs = cur.fetchall()

    recent_logs = [t for (t,) in logs if now - t < 86400]

    if len(recent_logs) >= 3:
        last_up = datetime.fromtimestamp(recent_logs[0]).strftime("%H:%M:%S")
        return await event.answer(f"""
🎁 Gift {slug} sudah mencapai batas 3x sehari, coba lagi besok!

🕒 Last Up: {last_up} WIB
            """,
            alert=True
        )

    if recent_logs and (now - recent_logs[0]) < 3600:
        sisa = 3600 - (now - recent_logs[0])
        menit = int(sisa / 60)
        return await event.answer(f"""
🎁 Gift {slug} dapat di UP setelah 1 jam kemudian, tunggu {menit} menit lagi!
            """,
            alert=True)

    cur.execute(
        "INSERT INTO gift_up_logs (user_id, slug, timestamp) VALUES (?, ?, ?)",
        (user_id, slug, now)
    )
    conn.commit()

    waiting_up_input[user_id] = {
        "slug": slug,
        "msg_id": msg_id,
        "topic_id": topic_id
    }
    
    msg = f"""
📝 **__Silahkan kirim pesan untuk up gift {slug} ke channel @winedash, buatlah yang menarik!__**

^^• Klik 🚫 BATALKAN jika ingin dibatalkan.^^
    """
    
    buttons = [
      [Button.inline("🚫 BATALKAN", data=f"gift_{slug}")]]
    
    await event.respond(msg, buttons=buttons)
    await event.delete()

@bot.on(events.NewMessage)
async def handle_up_input(event):
    user_id = event.sender_id
    if user_id not in waiting_up_input:
        return

    data = waiting_up_input[user_id]
    slug = data["slug"]

    message_text = event.raw_text.strip()
    if not message_text:
        await event.respond("⚠️ Pesan tidak boleh kosong.")
        return

    data["pending_text"] = message_text
    waiting_up_input[user_id] = data

    confirm_buttons = [
        [Button.inline("✅ KONFIRMASI", data=f"confirm_up_send_{slug}"),
         Button.inline("❌ BATALKAN", data=f"cancel_up_{slug}")]
    ]
    
    preview = f"""
👋🏻 **__Hallo... apakah anda sudah yakin dengan tindakan anda yang sekarang untuk up gift {slug} dengan pesan:__**

^^{message_text}^^
    """

    await event.respond(preview, buttons=confirm_buttons, link_preview=False)

@bot.on(events.CallbackQuery(pattern=rb"^confirm_up_send_(.+)$"))
async def confirm_up_send(event):
    slug = event.pattern_match.group(1).decode()
    user_id = event.sender_id

    if user_id not in waiting_up_input:
        return await event.answer("⚠️ Tidak ada data input untuk dikirim, ulangi tindakan ini!", alert=True)

    data = waiting_up_input[user_id]
    message_text = data.get("pending_text")
    msg_id = data["msg_id"]
    topic_id = data["topic_id"]

    try:
        channel_entity = await bot.get_input_entity(CHANNEL_PENDING)
        topic_entity = await bot.get_input_entity(topic_id)

        reply_to = InputReplyToMessage(
            reply_to_msg_id=msg_id,
            reply_to_peer_id=topic_entity
        )

        sent = await bot(SendMessageRequest(
            peer=channel_entity,
            message=message_text,
            reply_to=reply_to
        ))

        sent_msg_id = None
        for update in sent.updates:
            if hasattr(update, "message") and hasattr(update.message, "id"):
                sent_msg_id = update.message.id
                break

        if not sent_msg_id:
            raise Exception("Tidak bisa mendapatkan message_id hasil pengiriman")

        try:
            cur.execute("""
                INSERT INTO up_messages (slug, user_id, chat_id, msg_id, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                slug,
                int(user_id),
                int(CHANNEL_PENDING),
                int(sent_msg_id),
                int(time.time())
            ))
            conn.commit()
        except Exception as e:
            print(f"⚠️ Gagal simpan up_messages: {e}")

        buttons = [
            [Button.inline("🔙 KEMBALI", data=f"gift_{slug}")]
        ]

        await event.edit("✅ **__BERHASIL TERKIRIM, SILAHKAN CEK @WINEDASH!__**", buttons=buttons)
        del waiting_up_input[user_id]

    except Exception as e:
        await event.edit(f"⚠️ Gagal kirim pesan:\n`{e}`", parse_mode="markdown")

@bot.on(events.NewMessage(pattern=r"^/data (https?://t\.me/nft/[\w-]+)$"))
async def data_gift(event):
    if event.sender_id not in OWNER_ID:
        return await event.reply("🚫 Anda tidak memiliki izin untuk menggunakan perintah ini.")

    try:
        url = event.pattern_match.group(1)
        slug = url.split("/")[-1]

        cur.execute("""
            SELECT model, model_rarity, background, background_rarity,
                   symbol, symbol_rarity, original_details,
                   availability_issued, availability_total, price, is_listed,
                   user_id, msg_id
            FROM gifts WHERE slug=?
        """, (slug,))
        row = cur.fetchone()

        (model, model_rarity, background, background_rarity,
         symbol, symbol_rarity, original_details,
         availability_issued, availability_total, price, is_listed,
         holder_id, msg_id) = row if row else (None,) * 13

        try:
            result = await userbot(functions.payments.GetUniqueStarGiftRequest(slug=slug))
            gift = result.gift

            for attr in gift.attributes:
                if isinstance(attr, StarGiftAttributeModel):
                    model = model or attr.name
                    model_rarity = model_rarity or format_rarity(getattr(attr, "rarity_permille", None))
                elif isinstance(attr, StarGiftAttributeBackdrop):
                    background = background or attr.name
                    background_rarity = background_rarity or format_rarity(getattr(attr, "rarity_permille", None))
                elif isinstance(attr, StarGiftAttributePattern):
                    symbol = symbol or attr.name
                    symbol_rarity = symbol_rarity or format_rarity(getattr(attr, "rarity_permille", None))
                elif isinstance(attr, StarGiftAttributeOriginalDetails):
                    original_details = original_details or "Minus"

            availability_issued = availability_issued or getattr(gift, "availability_issued", 0)
            availability_total = availability_total or getattr(gift, "availability_total", 0)

            cur.execute("""
                UPDATE gifts SET model=?, model_rarity=?, background=?, background_rarity=?,
                                symbol=?, symbol_rarity=?, original_details=?,
                                availability_issued=?, availability_total=?
                WHERE slug=?
            """, (
                model, model_rarity, background, background_rarity,
                symbol, symbol_rarity, original_details,
                availability_issued, availability_total, slug
            ))
            conn.commit()

            owner_display = "__Hide__"
            try:
                if gift.owner_id and isinstance(gift.owner_id, types.PeerUser):
                    owner_entity = await userbot.get_entity(gift.owner_id.user_id)
                    if getattr(owner_entity, "username", None):
                        owner_display = f"@{owner_entity.username}"
                    else:
                        fullname = (owner_entity.first_name or "") + " " + (owner_entity.last_name or "")
                        owner_display = fullname.strip() if fullname.strip() else f"[{owner_entity.id}](tg://user?id={owner_entity.id})"
            except Exception as e:
                print(f"⚠️ gagal ambil entity owner: {e}")

        except Exception as e:
            print(f"⚠️ gagal ambil gift {slug}: {e}")
            owner_display = "❌ Unknown"

        holder_display = "❌ Unknown"
        if holder_id:
            cur.execute("SELECT username FROM users WHERE user_id=?", (holder_id,))
            row = cur.fetchone()
            if row and row[0]:
                holder_display = f"@{row[0]}"
            else:
                holder_display = f"[{holder_id}](tg://user?id={holder_id})"

        display_price = int(price * 1.02) if price else 0
        status_text = "Dijual" if is_listed else "Tidak Dijual"
        jual_text = "🚫 UNLISTED" if is_listed else "🛒 LISTED"

        # 🔗 SAMA PERSIS SEPERTI gift_detail
        topic_url = f"https://t.me/nft/{slug}"  # fallback
        base_name = slug.split("-")[0]
        if base_name in slug_channel_map:
            topic_id, reply_id = slug_channel_map[base_name]
            topic_id_str = str(topic_id).replace("-100", "")
            topic_url = f"https://t.me/market_wine/{reply_id}/{msg_id}"

        buttons = [
            [Button.inline("💸 ADD PRICE", data=f"add_price_{slug}"),
             Button.inline(jual_text, data=f"status_jual_{slug}")],
            [Button.inline("🔖 SOLD OUT", data=f"sold_{slug}"),
             Button.inline("📨 UP POSTED", data=f"up_{slug}")],
            [Button.url("🛍️ CEK POST", topic_url)],
            [Button.inline("🔙 KEMBALI", data="gift")]
        ]

        msg = f"""
🎁 **DATA GIFT [{slug}](https://t.me/nft/{slug})**

^^✨ Model: {model or '❌ None'} ({model_rarity or '-'})
🖼️ Background: {background or '❌ None'} ({background_rarity or '-'})
👾 Symbol: {symbol or '❌ None'} ({symbol_rarity or '-'})
🔢 Availability: {availability_issued or 0}/{availability_total or 0}
🔎 Original: {original_details or 'No minus'}^^

👤 Owner: {owner_display}
📊 Status: {status_text}
💸 Price: Rp{display_price:,}
        """

        await event.reply(msg, buttons=buttons, link_preview=False)

    except Exception as e:
        print(f"❌ Error /data: {e}")
        await event.reply("⚠️ Terjadi kesalahan saat mengambil data gift.")

@bot.on(events.CallbackQuery(pattern=b"^sold_(.+)$"))
async def sold_out(event):
    slug = event.pattern_match.group(1).decode()
    user_id = get_effective_user_id(event.sender_id)

    buttons = [
        [Button.inline("✅ KONFIRMASI", data=f"confirm_sold_{slug}"),
         Button.inline("🚫 BATALKAN", data=f"gift_{slug}")]
    ]

    msg = f"""
❔ **__Apakah anda yakin gift ini benar-benar sold?__**

^^__• Setelah anda melakukan tindakan ini maka gift anda tidak akan terdaftar lagi di database, terkecuali ADMIN menambahkannya ke database anda!__^^
    """

    await event.edit(msg, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=b"^confirm_sold_(.+)$"))
async def confirm_sold_out(event):
    slug = event.pattern_match.group(1).decode()
    user_id = get_effective_user_id(event.sender_id)

    # ================= AMBIL MSG_ID =================
    cur.execute("SELECT msg_id FROM gifts WHERE slug=?", (slug,))
    row = cur.fetchone()
    if not row:
        return await event.answer(
            "❌ **__Gift tidak ditemukan di database!__**\n\n^^Jika ini sebuah kesalahan segera hubungi admin, Terimakasih!^^",
            alert=True
        )
    msg_id = row[0]

    # ================= CEK TOPIC CHAT =================
    slug_prefix = slug.split("-")[0]
    topic_error = False
    if slug_prefix not in slug_channel_map:
        topic_error = True
        print(f"🚫 Error: topic chat belum ditambahkan untuk slug_prefix {slug_prefix}")

    if not topic_error:
        chat_id, topic_id = slug_channel_map[slug_prefix]
        try:
            await bot.edit_message(chat_id, msg_id, f"🚫 **__[SOLD OUT!](https://t.me/nft/{slug})__**")
        except Exception as e:
            if "Content of the message was not modified" in str(e):
                print(f"ℹ️ Pesan gift {slug} sudah SOLD OUT, skip edit.")
            else:
                print(f"⚠️ Gagal edit pesan SOLD OUT {slug}: {e}")
    else:
        await event.answer("🚫 Error Topic Chat belum ditambahkan, segera hubungi admin!", alert=True)

    # ================= UPDATE DATABASE =================
    try:
        cur.execute("""
            UPDATE gifts
            SET model=NULL, model_rarity=NULL, background=NULL, background_rarity=NULL,
                symbol=NULL, symbol_rarity=NULL, original_details=NULL,
                availability_issued=NULL, availability_total=NULL, price=NULL,
                is_listed=0, user_id=NULL, is_sold=1
            WHERE slug=?
        """, (slug,))
        conn.commit()
        print(f"✅ Data gift {slug} dihapus dari database (is_sold=1).")
    except Exception as e:
        print(f"⚠️ Gagal reset data gift {slug}: {e}")

    # ================= SIMPAN USER SOLD GIFT =================
    try:
        cur.execute("""
            INSERT OR IGNORE INTO user_sold_gifts (user_id, slug)
            VALUES (?, ?)
        """, (user_id, slug))
        conn.commit()
    except Exception as e:
        print(f"⚠️ Gagal simpan user_sold_gifts {slug}: {e}")

    # ================= HAPUS ENTRY DI DATA.JSON =================
    try:
        export_file = "/root/project/website/export/data.json"
        os.makedirs(os.path.dirname(export_file), exist_ok=True)

        # buat file kosong jika belum ada
        if not os.path.exists(export_file):
            with open(export_file, "w", encoding="utf-8") as f:
                f.write("[]")

        with open(export_file, "r", encoding="utf-8") as f:
            data = json.load(f)  # data berupa list of dicts

        # filter slug yang sama
        new_data = [item for item in data if item.get("slug") != slug]

        if len(new_data) != len(data):
            with open(export_file, "w", encoding="utf-8") as f:
                json.dump(new_data, f, indent=2, ensure_ascii=False)
            print(f"🗑️ Entry {slug} dihapus dari data.json")
            push_json_to_github()  # otomatis push ke GitHub
        else:
            print(f"ℹ️ {slug} tidak ditemukan di data.json, skip hapus")
    except Exception as e:
        print(f"⚠️ Gagal update data.json untuk {slug}: {e}")

    # ================= HAPUS CALLBACK & KIRIM NOTIF =================
    try:
        await event.delete()
    except:
        pass

    msg = """
✨ **__Terimakasih telah menggunakan jasa kami di MARKET @WINEDASH, kami sebagai admin mengucapkan selamat dan ikut senang juga untuk anda karena berhasil menjual giftnya, saya harap anda segera mengisi RnK dibawah ini sesuai dengan pendapat dari hati, Terimakasih!__**
    """
    await event.answer("✅ SUCCESSFULLY, Gift diubah menjadi SOLD OUT!", alert=True)
    await event.respond(
        msg,
        buttons=[Button.url("🔎 RNK DISINI", "https://t.me/winedash/15")]
    )

    # ================= REFRESH GIFT DETAIL =================
    try:
        await start(event)
    except Exception as e:
        print(f"⚠️ Gagal refresh gift_detail untuk {slug}: {e}")

@bot.on(events.CallbackQuery(pattern=b"^status_jual_(.+)$"))
async def toggle_status_jual(event):
    slug = event.pattern_match.group(1).decode()
    slug_buy = slug_to_slugbuy(slug)
    user_id = get_effective_user_id(event.sender_id)

    cur.execute("""
        SELECT is_listed, price, msg_id, model, model_rarity, 
               background, background_rarity, symbol, symbol_rarity, 
               original_details, availability_issued, availability_total,
               user_id
        FROM gifts WHERE slug=?
    """, (slug,))
    row = cur.fetchone()
    if not row:
        return await event.answer("❌ Gift tidak ditemukan.", alert=True)

    (is_listed, price, msg_id,
     model, model_rarity, background, background_rarity,
     symbol, symbol_rarity, original_details,
     availability_issued, availability_total,
     holder_id) = row

    new_status = 0 if is_listed == 1 else 1

    if not all([model, background, symbol, availability_issued, availability_total]):
        try:
            result = await userbot(functions.payments.GetUniqueStarGiftRequest(slug=slug))
            gift = result.gift

            for attr in gift.attributes:
                if isinstance(attr, StarGiftAttributeModel):
                    model = model or attr.name
                    model_rarity = model_rarity or format_rarity(getattr(attr, "rarity_permille", None))
                elif isinstance(attr, StarGiftAttributeBackdrop):
                    background = background or attr.name
                    background_rarity = background_rarity or format_rarity(getattr(attr, "rarity_permille", None))
                elif isinstance(attr, StarGiftAttributePattern):
                    symbol = symbol or attr.name
                    symbol_rarity = symbol_rarity or format_rarity(getattr(attr, "rarity_permille", None))
                elif isinstance(attr, StarGiftAttributeOriginalDetails):
                    original_details = original_details or "Minus"

            availability_issued = availability_issued or getattr(gift, "availability_issued", 0)
            availability_total = availability_total or getattr(gift, "availability_total", 0)

            cur.execute("""
                UPDATE gifts SET model=?, model_rarity=?, background=?, background_rarity=?,
                                symbol=?, symbol_rarity=?, original_details=?,
                                availability_issued=?, availability_total=?
                WHERE slug=?
            """, (
                model, model_rarity, background, background_rarity,
                symbol, symbol_rarity, original_details,
                availability_issued, availability_total, slug
            ))
            conn.commit()
        except Exception as e:
            print(f"⚠️ Gagal ambil detail gift {slug}: {e}")

    # --- update status jual (PATCH SESUAI PERMINTAAN)
    if new_status == 1:
        cur.execute("UPDATE gifts SET is_listed=1, is_sold=0 WHERE slug=?", (slug,))
    else:
        cur.execute("UPDATE gifts SET is_listed=0 WHERE slug=?", (slug,))
    conn.commit()

    # --- ambil nama owner
    owner_display = "__Hide__"
    try:
        result = await userbot(functions.payments.GetUniqueStarGiftRequest(slug=slug))
        gift = result.gift
        if gift.owner_id and isinstance(gift.owner_id, types.PeerUser):
            try:
                owner_entity = await userbot.get_entity(gift.owner_id.user_id)
                if getattr(owner_entity, "username", None):
                    owner_display = f"@{owner_entity.username}"
                else:
                    fullname = (owner_entity.first_name or "") + " " + (owner_entity.last_name or "")
                    owner_display = fullname.strip() if fullname.strip() else f"[{owner_entity.id}](tg://user?id={owner_entity.id})"
            except Exception as e:
                print(f"⚠️ gagal ambil entity owner: {e}")
    except Exception as e:
        print(f"⚠️ gagal ambil owner dari gift {slug}: {e}")

    slug_prefix = slug.split("-")[0]
    gift_display_name = f"{format_slug_display(slug)}"

    # === STATUS: DIBUKA UNTUK DIJUAL ===
    if new_status == 1:
        display_price = int(price * 1.02) if price else 0

        msg_text = f"""
💸 **PRICE:** Rp{display_price:,}

^^🎁 **GIFT:** [{gift_display_name}](https://t.me/nft/{slug})
✨ **MODEL:** {model or '❌ None'} ({model_rarity or '-'})
🖼️ **BACKGROUND:** {background or '❌ None'} ({background_rarity or '-'})
👾 **SYMBOL:** {symbol or '❌ None'} ({symbol_rarity or '-'})
🔎 **NOTED:** {original_details or 'No Minus'}
🔢 **AVAILABILITY:** {availability_issued}/{availability_total}^^

**__-- MARKETPLACE BY @WINEDASH --__**
""".strip()

        buttons = [
            [Button.url("🛒 BELI GIFT", f"https://t.me/marketaldibot?start=beli_{slug_buy}"),
             Button.url("🔄 NEGO GIFT", f"https://t.me/marketaldibot?start=nego_{slug_buy}")],
            [Button.url("💬 CONTACT SUPPORT", "https://t.me/ftamous")]
        ]

        if slug_prefix not in slug_channel_map:
            return await event.answer("❌ Slug tidak punya mapping ke topic.", alert=True)

        chat_id, topic_id = slug_channel_map[slug_prefix]

        try:
            if not msg_id:
                reply_to = await get_topic_entry_msg_id(chat_id, topic_id)
                if not reply_to:
                    return await event.answer("⚠️ Gagal ambil reply_to dari topic.", alert=True)

                sent = await bot.send_message(chat_id, msg_text, buttons=buttons, reply_to=reply_to)
                cur.execute("UPDATE gifts SET msg_id=? WHERE slug=?", (sent.id, slug))
                conn.commit()
            else:
                try:
                    await bot.edit_message(chat_id, msg_id, msg_text, buttons=buttons)
                except Exception as e:
                    if "Content of the message was not modified" not in str(e):
                        reply_to = await get_topic_entry_msg_id(chat_id, topic_id)
                        sent = await bot.send_message(chat_id, msg_text, buttons=buttons, reply_to=reply_to)
                        cur.execute("UPDATE gifts SET msg_id=? WHERE slug=?", (sent.id, slug))
                        conn.commit()
        except Exception as e:
            print(f"❌ Gagal kirim/edit gift {slug}: {e}")

    # === STATUS: DITUTUP (UNLISTED) ===
    else:
        if msg_id and slug_prefix in slug_channel_map:
            chat_id, topic_id = slug_channel_map[slug_prefix]
            try:
                await bot.edit_message(chat_id, msg_id, f"**__[🎁 GIFT UNLISTED](https://t.me/nft/{slug})__**")
            except Exception as e:
                if "Content of the message was not modified" not in str(e):
                    print(f"❌ Gagal edit UNLISTED {slug}: {e}")

    try:
        await gift_detail(event)
    except Exception as e:
        print(f"⚠️ Gagal refresh gift_detail untuk {slug}: {e}")

@bot.on(events.CallbackQuery(pattern=b"^add_price_(.+)$"))
async def add_price(event):
    slug = event.pattern_match.group(1).decode()
    user_id = get_effective_user_id(event.sender_id)

    # ambil price dari DB dulu
    cur.execute("SELECT price FROM gifts WHERE LOWER(slug)=LOWER(?)", (slug,))
    row = cur.fetchone()

    if row:
        db_price = row[0]
    else:
        db_price = 0

    try:
        current_price = int(db_price) if db_price else 0
    except Exception:
        current_price = 0

    buttons = [
        [Button.inline("-1.000", data=f"price_{slug}_-1000"), Button.inline("+1.000", data=f"price_{slug}_1000")],
        [Button.inline("-2.000", data=f"price_{slug}_-2000"), Button.inline("+2.000", data=f"price_{slug}_2000")],
        [Button.inline("-5.000", data=f"price_{slug}_-5000"), Button.inline("+5.000", data=f"price_{slug}_5000")],
        [Button.inline("-10.000", data=f"price_{slug}_-10000"), Button.inline("+10.000", data=f"price_{slug}_10000")],
        [Button.inline("-20.000", data=f"price_{slug}_-20000"), Button.inline("+20.000", data=f"price_{slug}_20000")],
        [Button.inline("-50.000", data=f"price_{slug}_-50000"), Button.inline("+50.000", data=f"price_{slug}_50000")],
        [Button.inline("-100.000", data=f"price_{slug}_-100000"), Button.inline("+100.000", data=f"price_{slug}_100000")],
        [Button.inline("-200.000", data=f"price_{slug}_-200000"), Button.inline("+200.000", data=f"price_{slug}_200000")],
        [Button.inline("-500.000", data=f"price_{slug}_-500000"), Button.inline("+500.000", data=f"price_{slug}_500000")],
        [Button.inline("-1.000.000", data=f"price_{slug}_-1000000"), Button.inline("+1.000.000", data=f"price_{slug}_1000000")],
        [Button.inline("🗑️ RESET PRICE", data=f"price_{slug}_reset")],
        [Button.inline("✅ KONFIRMASI", data=f"price_confirm_{slug}"), Button.inline("🚫 BATALKAN", data=f"price_cancel_{slug}")]
    ]

    msg = f"""
^^[💰](https://t.me/nft/{slug}) **Price:** Rp{current_price:,}^^
"""
    await event.edit(msg, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=b"^price_(.+)_(\-?\d+|reset)$"))
async def update_price(event):
    slug = event.pattern_match.group(1).decode()
    delta = event.pattern_match.group(2).decode()
    user_id = get_effective_user_id(event.sender_id)

    cur.execute("SELECT price FROM gifts WHERE slug=?", (slug,))
    row = cur.fetchone()
    if not row:
        return await event.answer("❌ Gift tidak ditemukan.", alert=True)

    current_price = row[0] or 0

    if delta == "reset":
        new_price = 0
    else:
        new_price = max(0, current_price + int(delta))

    cur.execute("UPDATE gifts SET price=? WHERE slug=?", (new_price, slug))
    conn.commit()

    buttons = [
        [Button.inline("-1.000", data=f"price_{slug}_-1000"), Button.inline("+1.000", data=f"price_{slug}_1000")],
        [Button.inline("-2.000", data=f"price_{slug}_-2000"), Button.inline("+2.000", data=f"price_{slug}_2000")],
        [Button.inline("-5.000", data=f"price_{slug}_-5000"), Button.inline("+5.000", data=f"price_{slug}_5000")],
        [Button.inline("-10.000", data=f"price_{slug}_-10000"), Button.inline("+10.000", data=f"price_{slug}_10000")],
        [Button.inline("-20.000", data=f"price_{slug}_-20000"), Button.inline("+20.000", data=f"price_{slug}_20000")],
        [Button.inline("-50.000", data=f"price_{slug}_-50000"), Button.inline("+50.000", data=f"price_{slug}_50000")],
        [Button.inline("-100.000", data=f"price_{slug}_-100000"), Button.inline("+100.000", data=f"price_{slug}_100000")],
        [Button.inline("-200.000", data=f"price_{slug}_-200000"), Button.inline("+200.000", data=f"price_{slug}_200000")],
        [Button.inline("-500.000", data=f"price_{slug}_-500000"), Button.inline("+500.000", data=f"price_{slug}_500000")],
        [Button.inline("-1.000.000", data=f"price_{slug}_-1000000"), Button.inline("+1.000.000", data=f"price_{slug}_1000000")],
        [Button.inline("🗑️ RESET PRICE", data=f"price_{slug}_reset")],
        [Button.inline("✅ KONFIRMASI", data=f"price_confirm_{slug}"), Button.inline("🚫 BATALKAN", data=f"price_cancel_{slug}")]
    ]

    msg = f"""
^^[💰](https://t.me/nft/{slug}) **Price:** Rp{current_price:,}^^
    """
    await event.edit(msg, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=b"^price_confirm_(.+)$"))
async def confirm_price(event):
    slug = event.pattern_match.group(1).decode()
    slug_buy = slug_to_slugbuy(slug)
    user_id = get_effective_user_id(event.sender_id)

    cur.execute("""
        SELECT price, msg_id, is_listed, model, model_rarity, 
               background, background_rarity, symbol, symbol_rarity, 
               original_details, availability_issued, availability_total, user_id
        FROM gifts WHERE slug=?
    """, (slug,))
    row = cur.fetchone()
    if not row:
        return await event.answer("❌ Gift tidak ditemukan.", alert=True)

    (price, msg_id, is_listed,
     model, model_rarity, background, background_rarity,
     symbol, symbol_rarity, original_details,
     availability_issued, availability_total, owner_id_db) = row

    final_price = price or 0
    display_price = int(final_price * 1.02) if final_price else 0

    # --- Ambil nama owner ---
    owner_display = "__Hide__"
    try:
        result = await userbot(functions.payments.GetUniqueStarGiftRequest(slug=slug))
        gift = result.gift
        if gift.owner_id and isinstance(gift.owner_id, types.PeerUser):
            owner_entity = await userbot.get_entity(gift.owner_id.user_id)
            if getattr(owner_entity, "username", None):
                owner_display = f"@{owner_entity.username}"
            else:
                fullname = (owner_entity.first_name or "") + " " + (owner_entity.last_name or "")
                owner_display = fullname.strip() or f"[{owner_entity.id}](tg://user?id={owner_entity.id})"
    except Exception as e:
        print(f"⚠️ gagal ambil owner dari gift {slug}: {e}")

    slug_prefix = slug.split("-")[0]
    gift_display_name = f"{format_slug_display(slug)}"

    if is_listed == 1 and slug_prefix in slug_channel_map:
        chat_id, topic_id = slug_channel_map[slug_prefix]

        msg_text = f"""
💸 **PRICE:** Rp{display_price:,}

^^🎁 **GIFT:** [{gift_display_name}](https://t.me/nft/{slug})
✨ **MODEL:** {model or '❌ None'} ({model_rarity or '-'})
🖼️ **BACKGROUND:** {background or '❌ None'} ({background_rarity or '-'})
👾 **SYMBOL:** {symbol or '❌ None'} ({symbol_rarity or '-'})
🔎 **NOTED:** {original_details or 'No Minus'}
🔢 **AVAILABILITY:** {availability_issued}/{availability_total}^^

**__-- MARKETPLACE BY @WINEDASH --__**
""".strip()

        buttons = [
            [Button.url("🛒 BELI GIFT", f"https://t.me/marketaldibot?start=beli_{slug_buy}"),
             Button.url("🔄 NEGO GIFT", f"https://t.me/marketaldibot?start=nego_{slug_buy}")],
            [Button.url("💬 CONTACT SUPPORT", "https://t.me/ftamous")]
        ]

        try:
            # === Jika belum pernah dikirim ke topic ===
            if not msg_id:
                reply_to = await get_topic_entry_msg_id(chat_id, topic_id)
                if not reply_to:
                    return await event.answer("⚠️ Gagal ambil reply_to dari topic.", alert=True)

                sent = await bot.send_message(chat_id, msg_text, buttons=buttons, reply_to=reply_to)
                cur.execute("UPDATE gifts SET msg_id=? WHERE slug=?", (sent.id, slug))
                conn.commit()

                # === Kirim ke CHANNEL_PENDING (dengan media NFT) ===
                pending_text = f"""
**WTS GIFT UPGRADE**

🎁 **Gift:** [{gift_display_name}](https://t.me/nft/{slug})
✨ **Model:** {model or '-'} ({model_rarity or '-'})
🖼️ **Backdrop:** {background or '-'} ({background_rarity or '-'})
👾 **Symbol:** {symbol or '-'} ({symbol_rarity or '-'})
🔎 **Noted:** {original_details or 'No Minus'}

**ORDER TO [CLICK HERE](https://t.me/market_wine/{sent.id})**
""".strip()

                try:
                    result = await userbot(functions.payments.GetUniqueStarGiftRequest(slug=slug))
                    gift = result.gift

                    model_doc = next((a.document for a in gift.attributes if isinstance(a, StarGiftAttributeModel) and hasattr(a, "document")), None)
                    bg_doc = next((a.document for a in gift.attributes if isinstance(a, StarGiftAttributeBackdrop) and hasattr(a, "document")), None)
                    mime_type = getattr(model_doc, "mime_type", None)

                    if not model_doc:
                        print(f"⚠️ Gift {slug} tidak punya model document.")
                        await bot.send_message(CHANNEL_PENDING, pending_text)

                    elif mime_type in ["image/png", "image/jpeg"]:
                        model_io = BytesIO()
                        await bot.download_media(model_doc, file=model_io)
                        model_io.seek(0)
                        model_img = Image.open(model_io).convert("RGBA")

                        if bg_doc:
                            bg_io = BytesIO()
                            await bot.download_media(bg_doc, file=bg_io)
                            bg_io.seek(0)
                            bg_img = Image.open(bg_io).convert("RGBA").resize(model_img.size)
                            final_img = Image.alpha_composite(bg_img, model_img)
                        else:
                            final_img = model_img

                        final_img = final_img.convert("RGB")
                        nft_path = f"nft_{slug}.jpg"
                        final_img.save(nft_path, "JPEG")
                        await bot.send_file(CHANNEL_PENDING, nft_path)
                        await bot.send_message(CHANNEL_PENDING, pending_text)
                        print(f"✅ Gambar NFT dikirim untuk gift {slug}")

                    elif mime_type == "application/x-tgsticker":
                        await bot.download_media(model_doc, file=f"nft_{slug}.tgs")
                        await bot.send_file(CHANNEL_PENDING, f"nft_{slug}.tgs", force_document=True)
                        await bot.send_message(CHANNEL_PENDING, pending_text)
                        print(f"✅ Sticker NFT (.tgs) dikirim untuk gift {slug}")

                    else:
                        await bot.send_message(CHANNEL_PENDING, pending_text)
                        print(f"⚠️ Gift {slug} bukan gambar/sticker, kirim teks saja. (mime: {mime_type})")

                    print(f"📢 Gift {slug} dikirim ke CHANNEL_PENDING (via confirm_price)")

                except Exception as e:
                    print(f"⚠️ Gagal kirim media NFT untuk {slug}: {e}")
                    await bot.send_message(CHANNEL_PENDING, pending_text)

            else:
                try:
                    await bot.edit_message(chat_id, msg_id, msg_text, buttons=buttons)
                except Exception as e:
                    if "Content of the message was not modified" not in str(e):
                        print(f"⚠️ Edit harga gagal untuk {slug}, fallback kirim baru. Error: {e}")
                        reply_to = await get_topic_entry_msg_id(chat_id, topic_id)
                        sent = await bot.send_message(chat_id, msg_text, buttons=buttons, reply_to=reply_to)
                        cur.execute("UPDATE gifts SET msg_id=? WHERE slug=?", (sent.id, slug))
                        conn.commit()

        except Exception as e:
            print(f"❌ Gagal kirim/edit price gift {slug}: {e}")

    else:
        print(f"ℹ️ Gift {slug} belum dijual, skip edit harga.")

    # === Notifikasi konfirmasi ke user ===
    msg = f"""
✅ **__Berhasil diubah!__**
🎁 **Gift:** https://t.me/nft/{slug}
^^💰 **Price:** Rp{final_price:,}^^
"""
    buttons = [[Button.inline("🔙 KEMBALI", data=f"gift_{slug}")]]
    await event.edit(msg, buttons=buttons, link_preview=False)
    
    try:
        export_file = "/root/project/website/export/data.json"
        if os.path.exists(export_file):
            with open(export_file, "r", encoding="utf-8") as f:
                data = json.load(f)  # list of dicts

            # update harga gift ini
            updated = False
            for item in data:
                if item.get("slug") == slug:
                    item["price"] = int(final_price or 0)
                    item["saldo"] = int(final_price or 0)
                    updated = True
                    break

            if updated:
                with open(export_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"💰 Harga {slug} diperbarui di data.json")
                push_json_to_github()
            else:
                print(f"ℹ️ {slug} tidak ditemukan di data.json, skip update harga")
        else:
            print("⚠️ File data.json tidak ditemukan, skip update harga")
    except Exception as e:
        print(f"⚠️ Gagal update harga di data.json untuk {slug}: {e}")

@bot.on(events.NewMessage(pattern=r"^/cnego (\d+)$"))
async def reset_nego(event):
    try:
        sender_id = event.sender_id

        # hanya OWNER_ID yang bisa pakai perintah ini
        if sender_id not in OWNER_ID:
            return await event.reply("❌ Anda tidak memiliki izin untuk menjalankan perintah ini.")

        target_user_id = int(event.pattern_match.group(1))

        # cek apakah user ada di database users
        cur.execute("SELECT user_id, last_nego FROM users WHERE user_id=?", (target_user_id,))
        row = cur.fetchone()
        if not row:
            return await event.reply(f"❌ User `{target_user_id}` tidak ditemukan di database.")
        
        # reset last_nego ke 0 supaya bisa nego lagi
        cur.execute("UPDATE users SET last_nego=0 WHERE user_id=?", (target_user_id,))
        conn.commit()

        await event.reply(f"✅ Status nego user `{target_user_id}` telah di-reset. User sekarang bisa nego lagi tanpa menunggu 1 jam.")

    except Exception as e:
        print(f"⚠️ Error di /cnego: {e}")
        await event.reply(f"❌ Terjadi kesalahan saat mereset status nego:\n`{e}`")

@bot.on(events.NewMessage(pattern=r"^/start nego_(.+)"))
async def start_nego(event):
    try:
        user_id = event.sender_id
        slug_buy = event.pattern_match.group(1).strip()
        slug = slugbuy_to_slug(slug_buy)

        # --- FORCE SUBSCRIBE CHECK ---
        try:
            await bot.get_permissions(CHANNEL_SUBSCRIBE, user_id)
            is_subscribed = True
        except errors.UserNotParticipantError:
            is_subscribed = False
        except errors.ChannelPrivateError:
            is_subscribed = False
        except Exception as e:
            print(f"⚠️ Error cek subscribe (nego): {e}")
            is_subscribed = False

        if not is_subscribed:
            join_buttons = [
                [Button.url("📢 SUBSCRIBE CHANNEL", f"https://t.me/{CHANNEL_SUBSCRIBE.strip('@')}")],
                [Button.url("✅ SUDAH SUBSCRIBE", f"https://t.me/marketaldibot?start=nego_{slug_buy}")]
            ]
            await event.respond(
                f"""
⚠️ **__Sebelum melakukan nesiasi dipastikan anda sudah bergabung ke channel dibawah ini!__**
                """,
                buttons=join_buttons
            )
            return

        # --- CEK GIFT ---
        cur.execute("SELECT slug, price, user_id, model, background, symbol FROM gifts WHERE slug=?", (slug,))
        row = cur.fetchone()
        if not row:
            return await event.reply("❌ **__Gift Tidak ditemukan, segera hubungi admin /start__**")

        slug, base_price, owner_id, model, background, symbol = row
        if not base_price or base_price <= 0:
            return await event.reply("🔄 **__Gift ini baru saja mengubah harga!__**")

        price_with_markup = int(base_price * 1.02)
        now = int(time.time())

        # --- BATAS NEGO PER JAM ---
        if user_id not in OWNER_ID:
            cur.execute("SELECT last_nego FROM users WHERE user_id=?", (user_id,))
            row = cur.fetchone()
            last_nego = row[0] if row else 0

            if last_nego and now - last_nego < 3600:
                sisa = 3600 - (now - last_nego)
                menit = sisa // 60
                return await event.reply(
                    f"**__⏳ Anda hanya bisa melakukan nego setiap 1 jam, Coba lagi setelah {menit} menit!__**"
                )

            cur.execute("INSERT OR IGNORE INTO users (user_id, last_nego) VALUES (?, ?)", (user_id, 0))
            cur.execute("UPDATE users SET last_nego=? WHERE user_id=?", (now, user_id))
            conn.commit()

        # --- SIMPAN SESI NEGO ---
        cur.execute("""
            REPLACE INTO nego_sessions (user_id, slug, owner_id, base_price)
            VALUES (?, ?, ?, ?)
        """, (user_id, slug, owner_id, price_with_markup))
        conn.commit()

        # --- PESAN NEGO ---
        buttons = [[Button.inline("🚫 BATALKAN", data="batal_nego")]]
        msg_text = f"""
[🎁](https://t.me/nft/{slug}) **APAKAH ANDA INGIN NEGO?**

^^✨ Model: {model or '-'}
🖼️ Background: {background or '-'}
👾 Symbol: {symbol or '-'}
👤 Penjamin: @ftamous^^
💸 **Price:** Rp{price_with_markup:,}

__Setelah anda melakukan nego, anda akan diberikan batas waktu untuk konfirmasi harga deal dari pemilik gift, tidak perlu khawatir semua diakses penuh oleh owner (penjamin) setelah dikonfirmasi dengan harga nego anda, selanjutnya anda akan diarahkan ke pembayaran. Hati-hati anda akan terkena sanksi dan dianggap hnr jika negosiasi dikonfirmasi lalu anda tidak melakukan transaksi. Semua pengguna disini [ https://t.me/aldiep/5 ] yang akan memberikan sanksi kepada anda!__
        """.strip()

        await event.reply(msg_text, buttons=buttons)

    except Exception as e:
        print(f"⚠️ Error di /start nego_: {e}")
        await event.respond(f"⚠️ Terjadi kesalahan:\n`{e}`")

@bot.on(events.CallbackQuery(data=b"batal_nego"))
async def batal_nego(event):
    user_id = event.sender_id
    cur.execute("DELETE FROM nego_sessions WHERE user_id=?", (user_id,))
    conn.commit()
    await event.delete()
    await event.answer("❌ Berhasil reject permintaan nego!", alert=True)

@bot.on(events.NewMessage)
async def nego_input_handler(event):
    user_id = event.sender_id

    cur.execute("SELECT slug, owner_id, base_price FROM nego_sessions WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if not row:
        return

    slug, owner_id, price = row

    if not owner_id:
        cur.execute("SELECT user_id FROM gifts WHERE slug=?", (slug,))
        gift_owner = cur.fetchone()
        if not gift_owner:
            return await event.reply("⚠️ **__Gift tidak ditemukan atau sudah dihapus!__**")
        owner_id = gift_owner[0]

    text = (event.raw_text or "").strip().replace(".", "").replace(",", "")
    if not text.isdigit():
        return await event.reply(
            "**__Silahkan kirim harga yang ingin anda tawar, contoh:\n"
            "^^- 1.000\n- 10.000\n- 100.000\n- 1.000.000__**^^\n\n"
            "**__Harga nego harus dibawah harga pasang!__**"
        )

    nego_input = int(text)

    if nego_input >= price:
        return await event.reply(
            f"❌ **__Negosiasi harus lebih rendah dari harga pasang Rp{price:,}!__**"
        )

    deal_price = calculate_deal_price_from_nego_fee(nego_input)
    if deal_price <= 0:
        return await event.reply("⚠️ **__Nominal nego tidak valid!__**")

    final_with_fee = int(deal_price * 1.02)
    if final_with_fee >= price:
        return await event.reply(
            f"❌ **__Negosiasi (setelah fee) harus lebih rendah dari harga pasang Rp{price:,}!__**"
        )

    cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (user_id,))
    row_bal = cur.fetchone()
    saldo_user = row_bal[0] if row_bal else 0

    if saldo_user < nego_input:
        saldo_fmt = f"Rp{saldo_user:,}".replace(",", ".")
        harga_fmt = f"Rp{nego_input:,}".replace(",", ".")
        return await event.reply(
            f"💳 **Saldo kamu tidak cukup untuk nego ini.**\n\n"
            f"💸 Harga (input): `{harga_fmt}`\n"
            f"💳 Saldo saat ini: `{saldo_fmt}`\n\n"
            f"Silakan deposit dulu sebelum mengajukan nego."
        )

    saldo_baru = saldo_user - nego_input
    if row_bal is None:
        cur.execute(
            "INSERT INTO user_balance (user_id, balance) VALUES (?, ?)",
            (user_id, saldo_baru)
        )
    else:
        cur.execute(
            "UPDATE user_balance SET balance=? WHERE user_id=?",
            (saldo_baru, user_id)
        )
    conn.commit()

    try:
        buyer = await bot.get_entity(user_id)
        buyer_name = (buyer.first_name or "") + ((" " + buyer.last_name) if buyer.last_name else "")
        buyer_name = buyer_name.strip() or str(user_id)
        buyer_username = f"@{buyer.username}" if buyer.username else f"[{user_id}](tg://user?id={user_id})"
    except Exception:
        buyer_name = str(user_id)
        buyer_username = f"[{user_id}](tg://user?id={user_id})"

    notif_text = f"""
📩 **GIFT ANDA MEMILIKI PERMINTAAN NEGOSIASI!**

🎁 **Gift:** [{slug}](https://t.me/nft/{slug})
👤 **Buyer:** {buyer_username}
💰 **Price asli:** Rp{price:,}
💸 **Price nego:** Rp{deal_price:,}
    """.strip()

    buttons = [
        [
            Button.inline("💰 ACCEPT", data=f"accept_nego_{slug}_{user_id}"),
            Button.inline("🚫 REJECT", data=f"reject_nego_{slug}_{user_id}")
        ]
    ]

    try:
        await bot.send_message(owner_id, notif_text, buttons=buttons)
    except Exception as e:
        print(f"⚠️ Gagal kirim notif ke owner {owner_id}: {e}")

    deal_fmt = f"Rp{deal_price:,}".replace(",", ".")
    saldo_fmt = f"Rp{saldo_baru:,}".replace(",", ".")
    nego_input_fmt = f"Rp{nego_input:,}".replace(",", ".")
    
    msg = f"""
✅ **__Negosiasi nominal: {nego_input_fmt} pada gift [{slug}](https://t.me/nft/{slug}) berhasil dikirim!__**

💰 **Your Balance: {saldo_fmt}**
^^__Mohon tunggu konfirmasi dari owner gift, bot sudah berhasil mengirim notifikasi!__^^
    """
    
    buttons = [
      [Button.inline("🚫 BATALKAN NEGO", data=f"delnego_{slug}")]
    ]

    await event.reply(
        msg,
        buttons=buttons,
        link_preview=False
    )

    now = int(time.time())
    cur.execute(
        "SELECT id FROM nego_history WHERE slug=? AND user_id=? AND owner_id=?",
        (slug, user_id, owner_id)
    )
    existing = cur.fetchone()
    if existing:
        cur.execute(
            """
            UPDATE nego_history 
            SET offer_price=?, fixed_price=?, created_at=? 
            WHERE id=?
            """,
            (nego_input, deal_price, now, existing[0])
        )
    else:
        cur.execute(
            """
            INSERT INTO nego_history (slug, owner_id, user_id, fixed_price, offer_price, created_at) 
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (slug, owner_id, user_id, deal_price, nego_input, now)
        )
    conn.commit()

    cur.execute("DELETE FROM nego_sessions WHERE user_id=?", (user_id,))
    conn.commit()

@bot.on(events.CallbackQuery(pattern=b"^delnego_(.+)$"))
async def delnego(event):
    try:
        slug = event.pattern_match.group(1).decode().strip()
        buyer_id = event.sender_id

        cur.execute("""
            SELECT id, fixed_price, offer_price, created_at, owner_id
            FROM nego_history
            WHERE slug=? AND user_id=?
            ORDER BY created_at DESC
            LIMIT 1
        """, (slug, buyer_id))
        row = cur.fetchone()

        if not row:
            return await event.answer("⚠️ Kamu tidak memiliki nego aktif pada gift ini.", alert=True)

        nego_id, fixed_price, offer_price, created_at, owner_id = row

        now = int(time.time())
        if now - created_at < 3600:
            sisa = 3600 - (now - created_at)
            menit = sisa // 60
            return await event.answer(
                f"⏳ Kamu baru bisa membatalkan nego ini dalam {menit} menit.",
                alert=True
            )

        nominal_input = offer_price

        cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (buyer_id,))
        row_bal = cur.fetchone()
        saldo_user = row_bal[0] if row_bal else 0

        saldo_baru = saldo_user + nominal_input

        if row_bal is None:
            cur.execute(
                "INSERT INTO user_balance (user_id, balance) VALUES (?, ?)",
                (buyer_id, saldo_baru)
            )
        else:
            cur.execute(
                "UPDATE user_balance SET balance=? WHERE user_id=?",
                (saldo_baru, buyer_id)
            )
        conn.commit()

        cur.execute("DELETE FROM nego_history WHERE id=?", (nego_id,))
        conn.commit()

        nominal_fmt = f"Rp{nominal_input:,}".replace(",", ".")
        saldo_fmt = f"Rp{saldo_baru:,}".replace(",", ".")

        msg = f"""
❌ **__NEGO DIBATALKAN!__**

**Gift:** [{slug}](https://t.me/nft/{slug})
**Nominal:** `{nominal_fmt}`
**Saldo anda:** `{saldo_fmt}`

^^__Negosiasi berhasil dibatalkan.__^^
        """

        await event.edit(msg)

        try:
            await bot.send_message(
                owner_id,
                f"🚫 **__Buyer membatalkan negosiasi untuk gift [{slug}](https://t.me/nft/{slug}).__**",
                link_preview=False
            )
        except:
            pass

    except Exception as e:
        print(f"⚠️ Error delnego: {e}")
        try:
            await event.answer("❌ Terjadi kesalahan saat membatalkan nego.", alert=True)
        except:
            pass

@bot.on(events.CallbackQuery(pattern=b"^accept_nego_(.+)_(\d+)$"))
async def accept_nego(event):
    try:
        data = event.pattern_match.group(1).decode()
        buyer_id = int(event.pattern_match.group(2).decode())
        slug = data.strip()
        owner_id = event.sender_id

        cur.execute("""
            SELECT fixed_price, offer_price
            FROM nego_history
            WHERE slug=? AND user_id=? AND owner_id=?
            ORDER BY created_at DESC
            LIMIT 1
        """, (slug, buyer_id, owner_id))
        nego = cur.fetchone()

        if not nego:
            return await event.answer(
                "🚫 Gift sudah tidak ber-status nego, jika ini sebuah kesalahan segera hubungi ADMIN!",
                alert=True
            )

        fixed_price, offer_price = nego
        deal_price = int(fixed_price or 0)
        if deal_price <= 0:
            return await event.answer("⚠️ Harga deal tidak valid.", alert=True)

        cur.execute("""
            SELECT id,
                   price,
                   user_id,
                   owner_id,
                   api_owner_id,
                   is_sold,
                   is_listed,
                   status_tfo,
                   model, model_rarity,
                   background, background_rarity,
                   symbol, symbol_rarity,
                   msg_id
            FROM gifts
            WHERE slug=? AND owner_id=?
        """, (slug, owner_id))
        row = cur.fetchone()

        if not row:
            return await event.answer("❌ Gift tidak ditemukan atau owner tidak cocok.", alert=True)

        (gift_id,
         current_price,
         user_id_db,
         owner_id_db,
         api_owner_id_db,
         is_sold,
         is_listed,
         status_tfo,
         model,
         model_rarity,
         background,
         background_rarity,
         symbol,
         symbol_rarity,
         msg_id) = row

        if is_listed == 0:
            return await event.answer("🚫 Gift ini sudah tidak tersedia untuk nego.", alert=True)

        if status_tfo in ("pending_tfo", "done_tfo", "canceled", "expired"):
            return await event.answer("🚫 Gift ini sedang / sudah dalam proses TFO.", alert=True)

        tz = pytz.timezone("Asia/Jakarta")
        now_dt = datetime.now(tz)
        now_ts = int(now_dt.timestamp())
        now_str = now_dt.strftime("%d-%m-%Y %H:%M:%S")

        cur.execute("""
            UPDATE gifts
            SET buyer_id=?,
                price=?,
                status_tfo=?,
                is_listed=0,
                pending_tfo_at=?,
                pending_msg_id=NULL
            WHERE id=?
        """, (buyer_id, deal_price, "pending_tfo", now_ts, gift_id))
        conn.commit()

        try:
            slug_prefix = slug.split("-")[0]
            topic_error = False
            if slug_prefix not in slug_channel_map:
                topic_error = True
                print(f"🚫 Error: topic chat belum ditambahkan untuk slug_prefix {slug_prefix}")

            if not topic_error and msg_id:
                chat_id, topic_id = slug_channel_map[slug_prefix]
                try:
                    new_text = f"[🚫](https://t.me/nft/{slug}) **__SOLD OUT (NEGO)!__**"
                    await bot.edit_message(chat_id, msg_id, new_text)
                except Exception as e:
                    if "Content of the message was not modified" in str(e):
                        print(f"ℹ️ Pesan gift {slug} sudah di-status SOLD OUT, skip edit.")
                    else:
                        print(f"⚠️ Gagal edit pesan listing NEGO {slug}: {e}")
            elif topic_error:
                print("⚠️ Tidak bisa edit pesan karena topic chat belum di-mapping di slug_channel_map.")
        except Exception as e:
            print(f"⚠️ Error saat mencoba edit pesan listing gift (nego) {slug}: {e}")

        deal_fmt = f"Rp{deal_price:,}".replace(",", ".")
        nego_fee_fmt = f"Rp{(offer_price or deal_price):,}".replace(",", ".")

        gift_link = f"https://t.me/nft/{slug}"
        slug_text = slug.replace("-", " #")

        msg_buyer = f"""
✅ **PENAWARAN NEGO ANDA DITERIMA!**

[🎁]({gift_link}) **Gift:** {slug_text}
💸 **Harga Deal (tanpa fee):** `{deal_fmt}`

**LITERASI! - [https://t.me/winedash/6317]**
^^**Gift anda sekarang berstatus PENDING TFO. Owner akan melakukan TFO ke akun anda, dan anda wajib menampilkan gift tersebut di profil hingga bot mengirim notifikasi bahwa gift berhasil di TFO.**^^
        """.strip()

        try:
            sent_buyer = await bot.send_message(buyer_id, msg_buyer)
            save_tfo_message(slug, sent_buyer.chat_id, sent_buyer.id)
        except Exception as e:
            print(f"⚠️ Gagal kirim notif ke buyer (nego) {buyer_id}: {e}")

        try:
            buyer_entity = await bot.get_entity(buyer_id)
            buyer_fullname = (buyer_entity.first_name or "") + ((" " + buyer_entity.last_name) if buyer_entity.last_name else "")
            buyer_fullname = buyer_fullname.strip() or str(buyer_id)
            buyer_mention = f"[{buyer_fullname}](tg://user?id={buyer_id})"
            buyer_username = f"@{buyer_entity.username}" if buyer_entity.username else "❌ Tidak ada"
        except Exception:
            buyer_mention = f"`{buyer_id}`"
            buyer_username = "❌ Tidak ada"

        msg_owner = f"""
[💰]({gift_link}) **__ANDA MENERIMA NEGO DAN GIFT TERJUAL!__**

==> **__DATA BUYER__**
🆔 **ID:** `{buyer_id}`
👤 **Name:** {buyer_mention}
🪪 **Username:** {buyer_username}
⏰ **Time:** {now_str}
💸 **Harga Deal (tanpa fee):** {deal_fmt}

**LITERASI! - [https://t.me/winedash/6317]**
^^Silakan TFO gift anda ke buyer di atas. Setelah TFO, pastikan buyer menampilkan gift di profil sampai bot mengirim notifikasi bahwa gift sudah berhasil di TFO. Gift yang di-HIDE tidak akan terdeteksi dan saldo anda tidak akan bertambah!^^
        """.strip()

        try:
            sent_owner = await bot.send_message(owner_id, msg_owner, link_preview=True)
            save_tfo_message(slug, sent_owner.chat_id, sent_owner.id)
        except Exception as e:
            print(f"⚠️ Gagal kirim notif ke owner (nego) {owner_id}: {e}")

        admin_msg = f"""
[💰]({gift_link}) **__GIFT SOLD OUT PENDING TFO (NEGO)!__**

🎁 **Gift:** {slug_text}
💸 **Harga Deal (tanpa fee):** {deal_fmt}
🆔 **Buyer ID:** `{buyer_id}`
👤 **Buyer name:** {buyer_mention}
🪪 **Buyer username:** {buyer_username}

^^**__Hallo... bos @ftamous, ini transaksi NEGO yang perlu dipantau!__**^^
        """.strip()

        buttons_admin = [[Button.inline("🚫 BATALKAN", data=f"batal_tfo_{slug}")]]
        try:
            pending_msg_admin = await bot.send_message(GROUP_ADMIN, admin_msg, buttons=buttons_admin)
            save_tfo_message(slug, pending_msg_admin.chat_id, pending_msg_admin.id)
        except Exception as e:
            print(f"⚠️ Gagal kirim ke GROUP_ADMIN (nego): {e}")
            pending_msg_admin = None

        channel_msg = f"""
[💰]({gift_link}) **GIFT SOLD OUT PENDING TFO (NEGO)**

🎁 **Gift:** {slug_text}
💳 **Harga Deal (tanpa fee):** {deal_fmt}
⏰ **Waktu:** {now_str}
🆔 **Buyer id:** `{buyer_id}`
👤 **Buyer name:** {buyer_mention}
🪪 **Buyer username:** {buyer_username}

^^__Gift ini sudah dibeli (hasil NEGO) oleh buyer di atas. Owner gift diperintahkan untuk melakukan TFO dan bot akan mengirim notifikasi otomatis setelah tindakan ini!__^^
        """.strip()

        buttons_channel = [[Button.inline("🚫 BATALKAN", data=f"batal_tfo_{slug}")]]
        try:
            pending_msg = await bot.send_message(CHANNEL_PENDING, channel_msg, buttons=buttons_channel)
            pending_msg_id = pending_msg.id
            cur.execute("UPDATE gifts SET pending_msg_id=? WHERE id=?", (pending_msg_id, gift_id))
            conn.commit()
            save_tfo_message(slug, pending_msg.chat_id, pending_msg.id)
        except Exception as e:
            print(f"⚠️ Gagal kirim ke CHANNEL_PENDING (nego): {e}")
            pending_msg_id = None

        try:
            await event.answer("✅ Nego diterima", alert=True)
            await event.delete()
        except Exception as e:
            print(f"⚠️ Gagal jawab callback accept_nego: {e}")

        asyncio.create_task(resume_monitor_tfo())

    except Exception as e:
        print(f"❌ Error di accept_nego slug={locals().get('slug', '???')}: {e}")
        try:
            await event.answer("❌ Terjadi kesalahan saat memproses ACCEPT NEGO.", alert=True)
        except:
            pass

@bot.on(events.CallbackQuery(pattern=b"^reject_nego_(.+)_(\d+)$"))
async def reject_nego(event):
    try:
        data = event.pattern_match.group(1).decode()
        buyer_id = int(event.pattern_match.group(2).decode())
        slug = data.strip()
        owner_id = event.sender_id

        cur.execute("""
            SELECT fixed_price, offer_price
            FROM nego_history
            WHERE slug=? AND user_id=? AND owner_id=?
            ORDER BY created_at DESC
            LIMIT 1
        """, (slug, buyer_id, owner_id))
        nego = cur.fetchone()
        if not nego:
            return await event.answer("⚠️ Data nego tidak ditemukan.", alert=True)

        fixed_price, offer_price = nego

        nominal_input = offer_price

        cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (buyer_id,))
        row_bal = cur.fetchone()
        saldo_user = row_bal[0] if row_bal else 0

        saldo_baru = saldo_user + nominal_input

        if row_bal is None:
            cur.execute(
                "INSERT INTO user_balance (user_id, balance) VALUES (?, ?)",
                (buyer_id, saldo_baru)
            )
        else:
            cur.execute(
                "UPDATE user_balance SET balance=? WHERE user_id=?",
                (saldo_baru, buyer_id)
            )

        conn.commit()

        nominal_fmt = f"Rp{nominal_input:,}".replace(",", ".")
        saldo_fmt = f"Rp{saldo_baru:,}".replace(",", ".")

        notif_buyer = f"""
❌ **__PENAWARAN ANDA DITOLAK!__**

💸 **Nego:** `{nominal_fmt}`
💳 **Saldo di perbarui:** `{saldo_fmt}`
        """

        try:
            await bot.send_message(buyer_id, notif_buyer)
        except Exception as e:
            print(f"⚠️ Gagal kirim notif ke buyer {buyer_id}: {e}")

        await event.edit(
            f"🚫 **Kamu menolak penawaran untuk gift "
            f"[{slug}](https://t.me/nft/{slug})**"
        )

        cur.execute("DELETE FROM nego_sessions WHERE user_id=?", (buyer_id,))
        conn.commit()

    except Exception as e:
        print(f"⚠️ Error di reject_nego: {e}")
        try:
            await event.answer("❌ Terjadi kesalahan saat menolak nego.", alert=True)
        except:
            pass

@bot.on(events.NewMessage(pattern=r"^/start beli_(.+)$"))
async def start_beli(event):
    try:
        slug_buy = event.pattern_match.group(1)
        slug = slugbuy_to_slug(slug_buy)
        buyer_id = get_effective_user_id(event.sender_id)
        sender = await event.get_sender()

        # =========================
        # CEK SUBSCRIBE CHANNEL
        # =========================
        try:
            await bot.get_permissions(CHANNEL_SUBSCRIBE, buyer_id)
            is_subscribed = True
        except (errors.UserNotParticipantError, errors.ChannelPrivateError):
            is_subscribed = False
        except Exception as e:
            print(f"⚠️ Error cek subscribe (beli): {e}")
            is_subscribed = False

        if not is_subscribed:
            buttons = [
                [Button.url("📢 SUBSCRIBE CHANNEL", f"https://t.me/{CHANNEL_SUBSCRIBE.strip('@')}")],
                [Button.url("✅ SUDAH SUBSCRIBE", f"https://t.me/marketaldibot?start=beli_{slug_buy}")]
            ]
            return await event.respond(
                "⚠️ **__Sebelum melakukan pembelian gift titipan WINEDASH, "
                "pastikan anda sudah bergabung pada channel dibawah ini!__**",
                buttons=buttons
            )

        # =========================
        # SIMPAN / UPDATE USER
        # =========================
        fullname = getattr(sender, "first_name", "") or ""
        username = sender.username or ""

        tz = pytz.timezone("Asia/Jakarta")
        now = datetime.now(tz).strftime("%d.%m.%Y %H:%M:%S")

        cur.execute("SELECT first_start FROM users WHERE user_id=?", (buyer_id,))
        row_user = cur.fetchone()

        if not row_user:
            cur.execute("""
                INSERT INTO users (user_id, fullname, username, first_start, last_start)
                VALUES (?, ?, ?, ?, ?)
            """, (buyer_id, fullname, username, now, now))
        else:
            cur.execute("""
                UPDATE users
                SET fullname=?, username=?, last_start=?
                WHERE user_id=?
            """, (fullname, username, now, buyer_id))
        conn.commit()

        # =========================
        # AMBIL DATA GIFT
        # =========================
        cur.execute("""
            SELECT price, model, model_rarity,
                   background, background_rarity,
                   symbol, symbol_rarity,
                   user_id, is_sold
            FROM gifts
            WHERE slug=?
        """, (slug,))
        row = cur.fetchone()

        if not row:
            return await event.reply("❌ Gift tidak ditemukan di database.")

        (price, model, model_rarity,
         background, background_rarity,
         symbol, symbol_rarity,
         owner_id, is_sold) = row

        if buyer_id == owner_id and buyer_id not in OWNER_ID:
            return await event.reply(
                "🤷🏻 **__Berbicara dengan diri sendiri sepertinya lebih asik, "
                "tetapi ini bukan waktunya!__**"
            )

        if is_sold == 1:
            return await event.reply(
                "🚫 **__Gift ini sudah terjual [SOLD OUT]. "
                "Silakan pilih gift lainnya.__**"
            )

        harga_display = int(price * 1.02) if price else 0

        # =========================
        # 💰 CEK SALDO & WICASH (FIX UTAMA)
        # =========================
        cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (buyer_id,))
        r = cur.fetchone()
        saldo = r[0] if r else 0

        cur.execute("SELECT wicash FROM wicash_wallet WHERE user_id=?", (buyer_id,))
        r = cur.fetchone()
        wicash = r[0] if r else 0

        saldo_ok = saldo >= harga_display
        wicash_ok = wicash >= harga_display

        if saldo_ok and wicash_ok:
            buy_callback = f"confirm_buy_{slug}"
        elif saldo_ok:
            buy_callback = f"confirm_beli_{slug}"
        elif wicash_ok:
            buy_callback = f"buy_wicash_{slug}"
        else:
            buy_callback = f"confirm_buy_{slug}"

        # =========================
        # PESAN KONFIRMASI
        # =========================
        msg = f"""
**KONFIMASI PEMBELIAN GIFT!**

🎁 Gift: https://t.me/nft/{slug}
✨ Model: {model} ({model_rarity})
🖼️ Background: {background} ({background_rarity})
👾 Symbol: {symbol} ({symbol_rarity})
💸 Harga: Rp{harga_display:,}
👤 Penjamin: @ftamous

^^__Klik tombol__ **💸 TRANSFER** __dibawah ini untuk pembelian gift, anda akan di berikan qris otomatis dengan nominal sesuai harga gift, setelah berhasil membayar maka otomatis bot akan mendeteksi pembayaran anda dan tidak perlu mengirim bukti pembayaran__^^
        """.strip().replace(",", ".")

        buttons = [
            [Button.inline("👤 Hubungi Admin", data=f"tanya_{slug}")],
            [
                Button.inline("💰 BUY NOW", data=buy_callback),
                Button.inline("❌ BATALKAN", data="cancel_buy")
            ]
        ]

        await event.reply(msg, buttons=buttons, link_preview=True)

    except Exception as e:
        print(f"❌ Error start_beli slug={slug_buy}: {e}")
        await event.reply(
            "⚠️ Terjadi kesalahan saat memproses pembelian.\n"
            f"`{e}`"
        )

@bot.on(events.CallbackQuery(pattern=b"^confirm_buy_(.+)$"))
async def confirm_buy(event):
    slug = event.pattern_match.group(1).decode()
    buyer_id = get_effective_user_id(event.sender_id)

    cur.execute("""
        SELECT price, is_sold, is_listed
        FROM gifts
        WHERE LOWER(slug)=LOWER(?)
    """, (slug,))
    row = cur.fetchone()

    if not row:
        return await event.answer("❌ Gift tidak ditemukan.", alert=True)

    price, is_sold, is_listed = row
    if is_sold == 1 or is_listed == 0:
        return await event.answer("🚫 Gift sudah tidak tersedia.", alert=True)

    harga_deal = int(price * 1.02)

    cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (buyer_id,))
    r = cur.fetchone()
    saldo = r[0] if r else 0

    cur.execute("SELECT wicash FROM wicash_wallet WHERE user_id=?", (buyer_id,))
    r = cur.fetchone()
    wicash = r[0] if r else 0

    if wicash >= harga_deal:
        msg = f"""
💳 **PILIH METODE PEMBAYARAN**

🎁 **Harga Gift:** `Rp{harga_deal:,}`
💰 **Saldo:** `Rp{saldo:,}`
💎 **Wicash:** `Rp{wicash:,}`

^^__Menu pilihan ini akan selalu muncul jika anda memiliki koin wicash yang cukup, koin wicash anda dapat digunakan hanya untuk membeli gift di winedash, silakan klik tombol dibawah ini untuk memilih metode pembayaran yang ingin anda gunakan.__^^
        """.replace(",", ".")

        buttons = [
            [
                Button.inline("💰 PAKAI SALDO", data=f"buy_saldo_{slug}"),
                Button.inline("💎 PAKAI WICASH", data=f"buy_wicash_{slug}")
            ],
            [Button.inline("❌ BATALKAN", data="cancel_buy")]
        ]

        return await event.edit(msg, buttons=buttons)

    await confirm_buy_callback(event)

@bot.on(events.CallbackQuery(pattern=b"^confirm_beli_(.+)$"))
async def confirm_buy_callback(event):
    try:
        slug = event.pattern_match.group(1).decode()
        buyer_id = get_effective_user_id(event.sender_id)

        cur.execute("""
            SELECT id,
                   price,
                   user_id,
                   owner_id,
                   api_owner_id,
                   is_sold,
                   is_listed,
                   status_tfo,
                   model, model_rarity,
                   background, background_rarity,
                   symbol, symbol_rarity,
                   msg_id
            FROM gifts
            WHERE LOWER(slug) = LOWER(?)
        """, (slug,))
        row = cur.fetchone()

        if not row:
            return await event.answer("❌ Gift tidak ditemukan.", alert=True)

        (gift_id,
         price,
         user_id_db,
         owner_id_db,
         api_owner_id_db,
         is_sold,
         is_listed,
         status_tfo,
         model,
         model_rarity,
         background,
         background_rarity,
         symbol,
         symbol_rarity,
         msg_id) = row

        owner_id = owner_id_db or user_id_db

        if buyer_id == owner_id and buyer_id not in OWNER_ID and buyer_id not in ADMIN_ID:
            return await event.answer("🤷🏻 Tidak bisa membeli gift milik sendiri.", alert=True)

        harga_ftm = int(price or 0)
        if harga_ftm <= 0:
            return await event.answer("❌ Pembelian gagal, gift tidak memiliki harga!", alert=True)

        harga_fee = int(harga_ftm * 1.02)
        harga_deal = harga_fee

        cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (buyer_id,))
        row_bal = cur.fetchone()
        saldo_user = row_bal[0] if row_bal else 0

        if saldo_user < harga_deal:
            saldo_fmt = f"Rp{saldo_user:,}".replace(",", ".")
            harga_fmt = f"Rp{harga_deal:,}".replace(",", ".")

            msg = f"""
💳 **Saldo tidak mencukupi, silakan lakukan deposit terlebih dahulu untuk menambahkan saldo!**

**Price:** {harga_fmt}
**Saldo:** {saldo_fmt}
            """.strip()

            buttons = [
                [Button.inline("💳 DEPOSIT", data="deposit")],
                [Button.inline("🚫 BATALKAN", data="back_gift")]
            ]

            try:
                # Gunakan respond, tidak edit message langsung
                sent_msg = await event.respond(msg, buttons=buttons)
                save_tfo_message(slug, sent_msg.chat_id, sent_msg.id)
            except Exception as e:
                print(f"⚠️ Gagal kirim pesan saldo kurang: {e}")
                try:
                    await event.answer("⚠️ Saldo tidak cukup. Silakan deposit dulu.", alert=True)
                except:
                    pass
            return

        # potong saldo
        saldo_baru = saldo_user - harga_deal
        if row_bal is None:
            cur.execute("INSERT INTO user_balance (user_id, balance) VALUES (?, ?)", (buyer_id, saldo_baru))
        else:
            cur.execute("UPDATE user_balance SET balance=? WHERE user_id=?", (saldo_baru, buyer_id))
        conn.commit()

        # WAKTU ASIA/JAKARTA
        tz = pytz.timezone("Asia/Jakarta")
        now_dt = datetime.now(tz)
        now_ts = int(now_dt.timestamp())
        now_str = now_dt.strftime("%d-%m-%Y %H:%M:%S")

        cur.execute("""
            UPDATE gifts
            SET buyer_id=?,
                status_tfo=?,
                is_listed=0,
                pending_tfo_at=?,
                pending_msg_id=NULL
            WHERE id=?
        """, (buyer_id, "pending_tfo", now_ts, gift_id))
        conn.commit()

        # Edit listing gift jika ada
        try:
            slug_prefix = slug.split("-")[0]
            topic_error = False
            if slug_prefix not in slug_channel_map:
                topic_error = True
                print(f"🚫 Error: topic chat belum ditambahkan untuk slug_prefix {slug_prefix}")

            if not topic_error and msg_id:
                chat_id, topic_id = slug_channel_map[slug_prefix]
                try:
                    new_text = f"[🚫](https://t.me/nft/{slug}) **__SOLD OUT!__**"
                    await bot.edit_message(chat_id, msg_id, new_text)
                except Exception as e:
                    if "Content of the message was not modified" in str(e):
                        print(f"ℹ️ Pesan gift {slug} sudah di-status PENDING TFO, skip edit.")
                    else:
                        print(f"⚠️ Gagal edit pesan PENDING TFO {slug}: {e}")
            elif topic_error:
                print("⚠️ Tidak bisa edit pesan karena topic chat belum di-mapping di slug_channel_map.")
        except Exception as e:
            print(f"⚠️ Error saat mencoba edit pesan listing gift {slug}: {e}")

        harga_ftm_fmt = f"Rp{harga_ftm:,}".replace(",", ".")
        harga_fee_fmt = f"Rp{harga_fee:,}".replace(",", ".")
        saldo_fmt = f"Rp{saldo_baru:,}".replace(",", ".")
        slug_link = slug
        gift_link = f"https://t.me/nft/{slug_link}"
        slug_text = slug.replace("-", " #")

        msg_buyer = f"""
✅ **PEMBELIAN GIFT BERHASIL!**

[🎁]({gift_link}) **Gift:** {slug_text}
💸 **Harga Base:** `{harga_ftm_fmt}`
💸 **Harga + Fee (2%):** `{harga_fee_fmt}`
💳 **Saldo:** `{saldo_fmt}`

^^**__Anda sudah berhasil membeli gift, bot sudah mengirim notifikasi ke owner gift untuk melakukan TFO ke akun anda. Harap literasi / membaca syarat & ketentuan yang berlaku & diwajibkan, klik tombol dibawah ini!__**^^
        """.strip()
        
        buttons = [
          [Button.url("📄 Baca Selengkapnya...", "https://t.me/winedash/6317")]
        ]

        try:
            sent_buyer = await bot.send_message(buyer_id, msg_buyer, buttons=buttons)
            await event.delete()
            save_tfo_message(slug, sent_buyer.chat_id, sent_buyer.id)
        except Exception as e:
            print(f"⚠️ Gagal kirim notif ke buyer {buyer_id}: {e}")

        try:
            buyer_entity = await bot.get_entity(buyer_id)
            buyer_fullname = (buyer_entity.first_name or "") + ((" " + buyer_entity.last_name) if buyer_entity.last_name else "")
            buyer_fullname = buyer_fullname.strip() or str(buyer_id)
            buyer_mention = f"[{buyer_fullname}](tg://user?id={buyer_id})"
            buyer_username = f"@{buyer_entity.username}" if buyer_entity.username else "❌ Tidak ada"
        except Exception:
            buyer_mention = f"`{buyer_id}`"
            buyer_username = "❌ Tidak ada"

        fee_fmt = harga_fee_fmt
        harga_fmt = harga_ftm_fmt

        msg_owner = f"""
[💰]({gift_link}) **__GIFT ANDA BERHASIL TERJUAL!__**

==> **__DATA BUYER__**
🆔 **ID:** `{buyer_id}`
👤 **Name:** {buyer_mention}
🪪 **Username:** {buyer_username}
⏰ **Time:** {now_str}
💸 **Harga:** {fee_fmt}
💳 **Saldo di terima:** {harga_fmt}

^^**__Sebelum anda TFO gift ke buyer, silakan literasi / membaca syarat & ketentuan yang berlaku dan diwajibkan, klik tombol dibawah ini.__**^^
        """.strip()
        
        buttons = [
          [Button.url("📄 Baca Selengkapnya...", "https://t.me/winedash/6317")]
        ]

        try:
            sent_owner = await bot.send_message(owner_id, msg_owner, buttons=buttons)
            save_tfo_message(slug, sent_owner.chat_id, sent_owner.id)
        except Exception as e:
            print(f"⚠️ Gagal kirim notif ke owner {owner_id}: {e}")

        admin_msg = f"""
[💰]({gift_link}) **__GIFT SOLD OUT PENDING TFO!__**

🎁 **Gift:** {slug_text}
💸 **Harga:** {fee_fmt}
🆔 **Buyer ID:** `{buyer_id}`
👤 **Buyer name:** {buyer_mention}
🪪 **Buyer username:** {buyer_username}

^^**__Hallo... bos @ftamous, bot memerlukan tindakan anda!__**^^
        """.strip()

        buttons_admin = [[Button.inline("🚫 BATALKAN", data=f"batal_tfo_{slug}")]]
        try:
            pending_msg_admin = await bot.send_message(GROUP_ADMIN, admin_msg, buttons=buttons_admin)
            save_tfo_message(slug, pending_msg_admin.chat_id, pending_msg_admin.id)
        except Exception as e:
            print(f"⚠️ Gagal kirim ke GROUP_ADMIN: {e}")
            pending_msg_admin = None

        channel_msg = f"""
[💰]({gift_link}) **GIFT SOLD OUT PENDING TFO**

🎁 **Gift:** {slug_text}
💳 **Harga Base:** {fee_fmt}
⏰ **Waktu:** {now_str}
🆔 **Buyer id:** `{buyer_id}`
👤 **Buyer name:** {buyer_mention}
🪪 **Buyer username:** {buyer_username}
        """.strip()

        buttons_channel = [
            [Button.inline("🚫 BATALKAN", data=f"batal_tfo_{slug}")]
        ]

        try:
            pending_msg = await bot.send_message(CHANNEL_PENDING, channel_msg, buttons=buttons_channel)
            pending_msg_id = pending_msg.id
            cur.execute("UPDATE gifts SET pending_msg_id=? WHERE id=?", (pending_msg_id, gift_id))
            conn.commit()
            save_tfo_message(slug, pending_msg.chat_id, pending_msg.id)
        except Exception as e:
            print(f"⚠️ Gagal kirim ke CHANNEL_PENDING: {e}")
            pending_msg_id = None

        try:
            await event.edit(
                "✅ Pembelian gift berhasil! Cek DM untuk detail.",
                alert=True
            )
            await event.delete()

            if event.message:
                save_tfo_message(slug, event.chat_id, event.message.id)
        except Exception as e:
            print(f"⚠️ Gagal jawab callback confirm_buy: {e}")

        asyncio.create_task(resume_monitor_tfo())

    except Exception as e:
        print(f"❌ Error di confirm_buy_callback slug={locals().get('slug', '???')}: {e}")
        try:
            await event.answer("❌ Terjadi kesalahan saat memproses pembelian gift.", alert=True)
        except:
            pass

@bot.on(events.CallbackQuery(pattern=b"^buy_wicash_(.+)$"))
async def buy_with_wicash(event):
    try:
        slug = event.pattern_match.group(1).decode()
        buyer_id = get_effective_user_id(event.sender_id)

        cur.execute("""
            SELECT id,
                   price,
                   user_id,
                   owner_id,
                   api_owner_id,
                   is_sold,
                   is_listed,
                   status_tfo,
                   model, model_rarity,
                   background, background_rarity,
                   symbol, symbol_rarity,
                   msg_id
            FROM gifts
            WHERE LOWER(slug) = LOWER(?)
        """, (slug,))
        row = cur.fetchone()

        if not row:
            return await event.answer("❌ Gift tidak ditemukan.", alert=True)

        (gift_id,
         price,
         user_id_db,
         owner_id_db,
         api_owner_id_db,
         is_sold,
         is_listed,
         status_tfo,
         model,
         model_rarity,
         background,
         background_rarity,
         symbol,
         symbol_rarity,
         msg_id) = row

        owner_id = owner_id_db or user_id_db

        if buyer_id == owner_id and buyer_id not in OWNER_ID and buyer_id not in ADMIN_ID:
            return await event.answer("🤷🏻 Tidak bisa membeli gift milik sendiri.", alert=True)

        harga_ftm = int(price or 0)
        if harga_ftm <= 0:
            return await event.answer("❌ Pembelian gagal, gift tidak memiliki harga!", alert=True)

        harga_fee = int(harga_ftm * 1.02)
        harga_deal = harga_fee

        cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (buyer_id,))
        row_bal = cur.fetchone()
        saldo_user = row_bal[0] if row_bal else 0

        if saldo_user < harga_deal:
            saldo_fmt = f"Rp{saldo_user:,}".replace(",", ".")
            harga_fmt = f"Rp{harga_deal:,}".replace(",", ".")

            msg = f"""
💳 **Saldo tidak mencukupi, silakan lakukan deposit terlebih dahulu untuk menambahkan saldo!**

**Price:** {harga_fmt}
**Saldo:** {saldo_fmt}
            """.strip()

            buttons = [
                [Button.inline("💳 DEPOSIT", data="deposit")],
                [Button.inline("🚫 BATALKAN", data="back_gift")]
            ]

            try:
                # Gunakan respond, tidak edit message langsung
                sent_msg = await event.respond(msg, buttons=buttons)
                save_tfo_message(slug, sent_msg.chat_id, sent_msg.id)
            except Exception as e:
                print(f"⚠️ Gagal kirim pesan saldo kurang: {e}")
                try:
                    await event.answer("⚠️ Saldo tidak cukup. Silakan deposit dulu.", alert=True)
                except:
                    pass
            return

        cur.execute("SELECT wicash FROM wicash_wallet WHERE user_id=?", (buyer_id,))
        r = cur.fetchone()
        wicash_user = r[0] if r else 0

        if wicash_user < harga_deal:
            wicash_fmt = f"Rp{wicash_user:,}".replace(",", ".")
            harga_fmt = f"Rp{harga_deal:,}".replace(",", ".")

            msg = f"""
💎 **Wicash tidak mencukupi!**

**Price:** {harga_fmt}
**Wicash:** {wicash_fmt}
            """.strip()

            buttons = [[Button.inline("🚫 BATALKAN", data="back_gift")]]
            await event.respond(msg, buttons=buttons)
            return

        # ===== POTONG WICASH =====
        wicash_baru = wicash_user - harga_deal
        cur.execute(
            "UPDATE wicash_wallet SET wicash=? WHERE user_id=?",
            (wicash_baru, buyer_id)
        )
        conn.commit()

        # ===== UPDATE GIFT =====
        tz = pytz.timezone("Asia/Jakarta")
        now_dt = datetime.now(tz)
        now_ts = int(now_dt.timestamp())
        now_str = now_dt.strftime("%d-%m-%Y %H:%M:%S")

        cur.execute("""
            UPDATE gifts
            SET buyer_id=?,
                status_tfo='pending_tfo',
                is_listed=0,
                pending_tfo_at=?,
                pay_method='wicash',
                pending_msg_id=NULL
            WHERE id=?
        """, (buyer_id, now_ts, gift_id))
        conn.commit()

        try:
            slug_prefix = slug.split("-")[0]
            topic_error = False
            if slug_prefix not in slug_channel_map:
                topic_error = True
                print(f"🚫 Error: topic chat belum ditambahkan untuk slug_prefix {slug_prefix}")

            if not topic_error and msg_id:
                chat_id, topic_id = slug_channel_map[slug_prefix]
                try:
                    new_text = f"[🚫](https://t.me/nft/{slug}) **__SOLD OUT!__**"
                    await bot.edit_message(chat_id, msg_id, new_text)
                except Exception as e:
                    if "Content of the message was not modified" in str(e):
                        print(f"ℹ️ Pesan gift {slug} sudah di-status PENDING TFO, skip edit.")
                    else:
                        print(f"⚠️ Gagal edit pesan PENDING TFO {slug}: {e}")
            elif topic_error:
                print("⚠️ Tidak bisa edit pesan karena topic chat belum di-mapping di slug_channel_map.")
        except Exception as e:
            print(f"⚠️ Error saat mencoba edit pesan listing gift {slug}: {e}")

        harga_ftm_fmt = f"Rp{harga_ftm:,}".replace(",", ".")
        harga_fee_fmt = f"Rp{harga_fee:,}".replace(",", ".")
        saldo_fmt = f"Rp{wicash_baru:,}".replace(",", ".")   # ✅ tampilkan WICASH
        gift_link = f"https://t.me/nft/{slug}"
        slug_text = slug.replace("-", " #")

        msg_buyer = f"""
✅ **PEMBELIAN GIFT BERHASIL!**

[🎁]({gift_link}) **Gift:** {slug_text}
💸 **Harga Base:** `{harga_ftm_fmt}`
💸 **Harga + Fee (2%):** `{harga_fee_fmt}`
💳 **Saldo:** `{saldo_fmt}`

^^**__Anda sudah berhasil membeli gift, bot sudah mengirim notifikasi ke owner gift untuk melakukan TFO ke akun anda. Harap literasi / membaca syarat & ketentuan yang berlaku & diwajibkan, klik tombol dibawah ini!__**^^
        """.strip()
        
        buttons = [
          [Button.url("📄 Baca Selengkapnya...", "https://t.me/winedash/6317")]
        ]

        try:
            sent_buyer = await bot.send_message(buyer_id, msg_buyer, buttons=buttons)
            await event.delete()
            save_tfo_message(slug, sent_buyer.chat_id, sent_buyer.id)
        except Exception as e:
            print(f"⚠️ Gagal kirim notif ke buyer {buyer_id}: {e}")

        try:
            buyer_entity = await bot.get_entity(buyer_id)
            buyer_fullname = (buyer_entity.first_name or "") + ((" " + buyer_entity.last_name) if buyer_entity.last_name else "")
            buyer_fullname = buyer_fullname.strip() or str(buyer_id)
            buyer_mention = f"[{buyer_fullname}](tg://user?id={buyer_id})"
            buyer_username = f"@{buyer_entity.username}" if buyer_entity.username else "❌ Tidak ada"
        except Exception:
            buyer_mention = f"`{buyer_id}`"
            buyer_username = "❌ Tidak ada"

        fee_fmt = harga_fee_fmt
        harga_fmt = harga_ftm_fmt

        msg_owner = f"""
[💰]({gift_link}) **__GIFT ANDA BERHASIL TERJUAL!__**

==> **__DATA BUYER__**
🆔 **ID:** `{buyer_id}`
👤 **Name:** {buyer_mention}
🪪 **Username:** {buyer_username}
⏰ **Time:** {now_str}
💸 **Harga:** {fee_fmt}
💳 **Saldo di terima:** {harga_fmt}

^^**__Sebelum anda TFO gift ke buyer, silakan literasi / membaca syarat & ketentuan yang berlaku dan diwajibkan, klik tombol dibawah ini.__**^^
        """.strip()
        
        buttons = [
          [Button.url("📄 Baca Selengkapnya...", "https://t.me/winedash/6317")]
        ]

        try:
            sent_owner = await bot.send_message(owner_id, msg_owner, buttons=buttons)
            save_tfo_message(slug, sent_owner.chat_id, sent_owner.id)
        except Exception as e:
            print(f"⚠️ Gagal kirim notif ke owner {owner_id}: {e}")

        admin_msg = f"""
[💰]({gift_link}) **__GIFT SOLD OUT PENDING TFO!__**

🎁 **Gift:** {slug_text}
💸 **Harga:** {fee_fmt}
🆔 **Buyer ID:** `{buyer_id}`
👤 **Buyer name:** {buyer_mention}
🪪 **Buyer username:** {buyer_username}

^^**__Hallo... bos @ftamous, bot memerlukan tindakan anda!__**^^
        """.strip()

        buttons_admin = [[Button.inline("🚫 BATALKAN", data=f"batal_tfo_{slug}")]]
        try:
            pending_msg_admin = await bot.send_message(GROUP_ADMIN, admin_msg, buttons=buttons_admin)
            save_tfo_message(slug, pending_msg_admin.chat_id, pending_msg_admin.id)
        except Exception as e:
            print(f"⚠️ Gagal kirim ke GROUP_ADMIN: {e}")
            pending_msg_admin = None

        channel_msg = f"""
[💰]({gift_link}) **GIFT SOLD OUT PENDING TFO**

🎁 **Gift:** {slug_text}
💳 **Harga Base:** {fee_fmt}
⏰ **Waktu:** {now_str}
🆔 **Buyer id:** `{buyer_id}`
👤 **Buyer name:** {buyer_mention}
🪪 **Buyer username:** {buyer_username}
        """.strip()

        buttons_channel = [
            [Button.inline("🚫 BATALKAN", data=f"batal_tfo_{slug}")]
        ]

        try:
            pending_msg = await bot.send_message(CHANNEL_PENDING, channel_msg, buttons=buttons_channel)
            pending_msg_id = pending_msg.id
            cur.execute("UPDATE gifts SET pending_msg_id=? WHERE id=?", (pending_msg_id, gift_id))
            conn.commit()
            save_tfo_message(slug, pending_msg.chat_id, pending_msg.id)
        except Exception as e:
            print(f"⚠️ Gagal kirim ke CHANNEL_PENDING: {e}")
            pending_msg_id = None

        try:
            await event.edit(
                "✅ Pembelian gift berhasil! Cek DM untuk detail.",
                alert=True
            )
            await event.delete()

            if event.message:
                save_tfo_message(slug, event.chat_id, event.message.id)
        except Exception as e:
            print(f"⚠️ Gagal jawab callback confirm_buy: {e}")

        asyncio.create_task(resume_monitor_tfo())
        
        event.pattern_match = type(
            "", (), {"group": lambda s, i: slug.encode()}
        )()

    except Exception as e:
        print(f"❌ Error buy_with_wicash slug={locals().get('slug', '???')}: {e}")
        try:
            await event.answer("❌ Terjadi kesalahan saat membeli dengan Wicash.", alert=True)
        except:
            pass

@bot.on(events.NewMessage(pattern=r"^/donetfo\s+(.+)$"))
async def donetfo_command(event):
    sender_id = event.sender_id

    if sender_id not in OWNER_ID and sender_id not in ADMIN_ID:
        return await event.reply("🚫 Perintah ini hanya untuk ADMIN / OWNER.")

    slug_input = event.pattern_match.group(1).strip()

    # normalize slug
    if slug_input.startswith("https://t.me/nft/"):
        slug = slug_input.split("/")[-1]
    else:
        slug = slug_input

    slug_lower = slug.lower()

    # ============================
    # AMBIL DATA GIFT
    # ============================
    cur.execute("""
        SELECT id, buyer_id, user_id, owner_id, price,
               model, model_rarity,
               background, background_rarity,
               symbol, symbol_rarity,
               msg_id
        FROM gifts
        WHERE LOWER(slug)=?
    """, (slug_lower,))
    row = cur.fetchone()

    if not row:
        return await event.reply("❌ Gift tidak ditemukan di database.")

    (gift_id,
     buyer_id,
     user_id_db,
     owner_id_db,
     price,
     model,
     model_rarity,
     background,
     background_rarity,
     symbol,
     symbol_rarity,
     msg_id_db) = row

    if not buyer_id:
        return await event.reply("🚫 Gift ini belum memiliki buyer.")

    owner_marketplace_id = owner_id_db or user_id_db
    base_price = int(price or 0)

    owner_balance_fmt = None

    if base_price > 0 and owner_marketplace_id:
        cur.execute(
            "SELECT balance FROM user_balance WHERE user_id=?",
            (owner_marketplace_id,)
        )
        row_owner = cur.fetchone()
        owner_balance = row_owner[0] if row_owner else 0
        new_owner_balance = owner_balance + base_price

        if row_owner:
            cur.execute(
                "UPDATE user_balance SET balance=? WHERE user_id=?",
                (new_owner_balance, owner_marketplace_id)
            )
        else:
            cur.execute(
                "INSERT INTO user_balance (user_id, balance) VALUES (?, ?)",
                (owner_marketplace_id, new_owner_balance)
            )

        conn.commit()
        owner_balance_fmt = f"Rp{new_owner_balance:,}".replace(",", ".")

        await process_referral_bonus(buyer_id, base_price)

    cur.execute("""
        UPDATE gifts
        SET status_tfo='done_tfo',
            api_owner_id=?,
            is_sold=1,
            is_listed=0
        WHERE id=?
    """, (buyer_id, gift_id))
    conn.commit()

    try:
        await delete_all_tfo_messages(slug)
    except Exception as e:
        print(f"⚠️ delete_all_tfo_messages gagal: {e}")

    # ============================
    # FORMAT UMUM
    # ============================
    gift_link = f"https://t.me/nft/{slug}"
    slug_text = slug.replace("-", " #")
    harga_fmt = f"Rp{base_price:,}".replace(",", ".")

    # ============================
    # 🔔 NOTIF BUYER (SAMA DENGAN monitor_tfo)
    # ============================
    try:
        await bot.send_message(
            buyer_id,
            f"""
[✅]({gift_link}) **__SUCCESSFULLY TRANSFER OWNERSHIP!__**

🎁 **Gift:** {slug_text}
✨ **Model:** {model or '-'} ({model_rarity or '-'})
🖼️ **Backdrop:** {background or '-'} ({background_rarity or '-'})
👾 **Symbol:** {symbol or '-'} ({symbol_rarity or '-'})
💸 **Price:** {harga_fmt}

^^**__Gift sudah ada di akun anda, transaksi pembelian selesai dan Terimakasih sudah menggunakan jasa kami!__**^^
            """.strip(),
            link_preview=False
        )
    except Exception as e:
        print(f"⚠️ Gagal kirim ke buyer: {e}")

    # ============================
    # 🔔 NOTIF OWNER (SAMA DENGAN monitor_tfo)
    # ============================
    try:
        await bot.send_message(
            owner_marketplace_id,
            f"""
[💰]({gift_link}) **__GIFT BERHASIL DI TFO & BALANCE DITAMBAHKAN!__**

🎁 **Gift:** {slug_text}
💸 **Price:** {harga_fmt}
🧾 **Status:** __SUCCESS__
{f"💳 **New Balance:** `{owner_balance_fmt}`" if owner_balance_fmt else ""}

^^**__Gift berhasil di TFO ke buyer, dan balance sudah kami tambahkan ke akun anda. Terimakasih sudah menggunakan jasa kami!__**^^
            """.strip(),
            link_preview=False
        )
    except Exception as e:
        print(f"⚠️ Gagal kirim ke owner: {e}")

    # ============================
    # 🔔 LOG ADMIN
    # ============================
    try:
        await bot.send_message(
            GROUP_ADMIN,
            f"""
⚡ **FORCE DONE TFO (ADMIN)**

🎁 **Gift:** {slug_text}
🆔 **Buyer:** `{buyer_id}`
🆔 **Owner:** `{owner_marketplace_id}`
💸 **Harga:** {harga_fmt}
👤 **Executor:** `{sender_id}`
            """.strip()
        )
    except Exception as e:
        print(f"⚠️ Gagal kirim log admin: {e}")

    await event.reply(f"✅ Gift `{slug}` berhasil **FORCE DONE TFO**.")

@bot.on(events.CallbackQuery(data="cancel_buy"))
async def cancel_buy(event):
    user_id = event.sender_id
    await event.delete()
    await start(event)

@bot.on(events.CallbackQuery(pattern=b"^tanya_(.+)$"))
async def buy_gift(event):
    slug = event.pattern_match.group(1).decode()
    user_id = event.sender_id

    if user_id in contact_sessions and contact_sessions[user_id].get("active"):
        return await event.answer(
            "❌ Kamu masih terhubung dengan admin, selesaikan terlebih dahulu atau klik BATALKAN untuk memutuskan!\n",
            alert=True
        )

    contact_sessions[user_id] = {"slug": slug, "active": True}
    buttons = [[Button.inline("🚫 BERHENTI MENGHUBUNGI", data="stop_hub")]]
    
    msg = f"""
✨ **__Hallo... ada yang bisa dibantu? kami sebagai admin MARKET @WINEDASH dengan senang akan membantu mu dan bertanggung jawab di MARKET!, silahkan kirim pesan anda terkait https://t.me/nft/{slug}
    """
    
    await event.respond(
        msg,
        buttons=buttons,
        link_preview=False
    )

@bot.on(events.CallbackQuery(pattern=b"^tf_(.+)$"))
async def tf_gift(event):
    user_id = event.sender_id

    try:
        slug = event.pattern_match.group(1).decode()
        await event.answer("🛒 Proses pembelian gift...", alert=True)

        if user_id in transfer_sessions:
            return

        # Ambil harga dari DB
        cur.execute("SELECT price FROM gifts WHERE slug=?", (slug,))
        row = cur.fetchone()
        if not row:
            return await event.edit("❌ Gift tidak ditemukan di database (price missing).")

        price = row[0] or 0  # pastikan angka, bukan None

        # Sama seperti start_beli: harga * 1.02
        harga_display = int(price * 1.02) if price else 0

        if harga_display <= 0:
            return await event.edit("❌ Nominal harga gift tidak valid.")

        # Batas aman 2 miliar (int32)
        if harga_display > 2_000_000_000:
            return await event.edit("❌ Nominal terlalu besar untuk diproses.")

        transfer_sessions[user_id] = slug

        # Loading message
        loading = await event.respond("⏳ Sedang generate QRIS pembayaran gift...")

        # Panggil API Cashify DENGAN INT POLOS (tanpa titik/koma)
        result = generate_qris_v2(harga_display)
        if not result["success"]:
            transfer_sessions.pop(user_id, None)
            return await loading.edit(f"❌ Gagal generate QRIS.\nError: `{result['error']}`")

        data = result["data"]

        # --- AMBIL NOMINAL DARI API + FALLBACK ---
        # kalau API ngasih None, pakai harga_display supaya tidak NoneType.
        original_amount_raw = data.get("originalAmount", harga_display)
        total_amount_raw = data.get("totalAmount", harga_display)
        unique_nominal_raw = data.get("uniqueNominal", 0)

        # Kalau masih None juga, paksa fallback
        if original_amount_raw is None:
            original_amount_raw = harga_display
        if total_amount_raw is None:
            total_amount_raw = harga_display
        if unique_nominal_raw is None:
            unique_nominal_raw = 0

        # Helper: convert ke int aman, hapus titik/koma kalau string
        def to_int_safely(val):
            if isinstance(val, str):
                val = val.replace(".", "").replace(",", "")
            return int(val)

        try:
            original_amount = to_int_safely(original_amount_raw)
            total_amount = to_int_safely(total_amount_raw)
            unique_nominal = to_int_safely(unique_nominal_raw)
        except Exception as e:
            transfer_sessions.pop(user_id, None)
            await loading.edit(
                "❌ Data nominal dari Cashify tidak valid (gagal cast ke int):\n"
                f"`{e}`\n\n"
                f"Raw:\n"
                f"- originalAmount: `{original_amount_raw}`\n"
                f"- totalAmount: `{total_amount_raw}`\n"
                f"- uniqueNominal: `{unique_nominal_raw}`"
            )
            return

        # Cek range aman int32
        for label, val in [
            ("original_amount", original_amount),
            ("total_amount", total_amount),
            ("unique_nominal", unique_nominal),
        ]:
            if val < -2147483648 or val > 2147483647:
                transfer_sessions.pop(user_id, None)
                return await loading.edit(
                    f"❌ Nilai {label} di luar batas int32: `{val}`"
                )

        qr_string = data.get("qr_string")
        if not qr_string:
            transfer_sessions.pop(user_id, None)
            return await loading.edit("❌ Respon Cashify tidak mengandung `qr_string`.")

        transaction_id = data.get("transactionId")
        if not transaction_id:
            transfer_sessions.pop(user_id, None)
            return await loading.edit("❌ Respon Cashify tidak mengandung `transactionId`.")

        # Build URL QR
        qr_url = build_qr_image_url(qr_string)

        # Timestamp detik
        now_ts = int(time.time())
        expired_ts = now_ts + 5 * 60  # 5 menit

        # Simpan ke DB
        cur.execute("""
            INSERT INTO gift_qris_transactions
                (user_id, slug, transaction_id, amount, created_at, expired_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            int(user_id),
            slug,
            transaction_id,
            int(total_amount),
            int(now_ts),
            int(expired_ts)
        ))
        conn.commit()

        harga_fmt = f"Rp{total_amount:,}".replace(",", ".")
        caption = f"""
🧾 **PEMBELIAN GIFT WINEDASH**

🎁 Gift: https://t.me/nft/{slug}
📄 Transaction ID: `{transaction_id}`
💰 Nominal: `{harga_fmt}`
🔢 Fee: `{unique_nominal}`

^^**__Silakan scan QRIS di atas, jangan ubah nominal saat membayar dan akan expired setelah 5 menit, anda tidak di perlukan mengirim bukti pembayaran karena sudah otomatis terdeteksi oleh bot__**^^
        """.strip()

        msg_bayar = await bot.send_file(
            event.chat_id,
            file=qr_url,
            caption=caption,
        )
        
        await loading.delete()
        await asyncio.sleep(300)
        await msg_bayar.delete()

    except Exception as e:
        print("❌ Error di tf_gift:", repr(e))
        transfer_sessions.pop(user_id, None)
        try:
            await event.respond(f"⚠️ Terjadi kesalahan saat generate QRIS:\n`{e}`")
        except:
            pass

@bot.on(events.NewMessage(pattern=r"^/start bukti_(.+)"))
async def start_bukti(event):
    try:
        user_id = event.sender_id
        if user_id not in OWNER_ID:
            return await event.reply("❌ Fitur ini hanya untuk OWNER ADMIN.")

        slug = event.pattern_match.group(1).strip()
        pending_bukti[user_id] = slug

        buttons = [[Button.inline("❌ BATALKAN", data=f"cancel_bukti_{slug}")]]
        await event.respond(
            f"""
📸 **Kirim foto bukti transfer untuk gift:** `{slug}`

Silakan kirim 1 foto (bukti transfer bank / e-wallet).  
Gunakan tombol di bawah jika ingin membatalkan.
""",
            buttons=buttons,
            link_preview=False,
        )
    except Exception as e:
        print(f"❌ Error start_bukti: {e}")

@bot.on(events.CallbackQuery(pattern=b"^cancel_bukti_(.+)$"))
async def cancel_bukti(event):
    try:
        user_id = event.sender_id
        if user_id not in OWNER_ID:
            return await event.answer("❌ Kamu bukan OWNER!", alert=True)
        slug = event.pattern_match.group(1).decode().strip()
        if user_id in pending_bukti:
            del pending_bukti[user_id]
        await event.edit(f"❌ Pengiriman bukti untuk `{slug}` dibatalkan.")
    except Exception as e:
        print(f"❌ Error cancel_bukti: {e}")

@bot.on(events.NewMessage(func=lambda e: e.sender_id in OWNER_ID and e.photo))
async def handle_bukti_photo(event):
    try:
        user_id = event.sender_id
        if user_id not in pending_bukti:
            return  # bukan dalam sesi kirim bukti

        slug = pending_bukti[user_id]
        del pending_bukti[user_id]

        cur.execute("SELECT owner_id, user_id FROM gifts WHERE LOWER(slug)=?", (slug.lower(),))
        row = cur.fetchone()
        if not row:
            return await event.reply(f"❌ Gift `{slug}` tidak ditemukan di database.")

        owner_id, user_id_gift = row
        gift_owner = owner_id or user_id_gift
        if not gift_owner:
            return await event.reply(f"❌ Gift `{slug}` tidak memiliki owner valid.")

        # Forward foto ke pemilik gift
        await event.forward_to(gift_owner)

        await event.reply(f"✅ Bukti transfer untuk gift `{slug}` berhasil dikirim ke owner (`{gift_owner}`).")

    except Exception as e:
        print(f"❌ Error handle_bukti_photo: {e}")
        await event.reply("❌ Gagal memproses bukti transfer, coba lagi.")

@bot.on(events.CallbackQuery(pattern=b"^batal_tfo_(.+)$"))
async def batal_tfo(event):
    if event.sender_id not in OWNER_ID:
        await event.answer("❌ Anda tidak punya izin untuk membatalkan!", alert=True)
        return

    slug = event.pattern_match.group(1).decode().strip()
    slug_lower = slug.lower()

    # Ambil data gift PENDING TFO, termasuk buyer & price
    cur.execute("""
        SELECT id,
               price,
               buyer_id,
               user_id,
               owner_id,
               is_sold,
               is_listed,
               status_tfo
        FROM gifts
        WHERE LOWER(slug)=? AND status_tfo=?
    """, (slug_lower, "pending_tfo"))
    row = cur.fetchone()

    if not row:
        await event.answer("⚠️ Gift ini tidak dalam status pending TFO.", alert=True)
        try:
            await event.delete()
        except Exception:
            pass
        return

    (gift_id,
     price,
     buyer_id,
     user_id_db,
     owner_id_db,
     is_sold,
     is_listed,
     status_tfo) = row

    # Pastikan ada buyer & harga valid
    buyer_id = buyer_id or 0
    harga_base = int(price or 0)

    if buyer_id == 0 or harga_base <= 0:
        await event.answer("⚠️ Data buyer / harga gift tidak valid untuk refund.", alert=True)
        return

    # Harga + 2% fee (saldo yang harus dikembalikan ke buyer)
    harga_deal = int(harga_base * 1.02)

    # === Refund saldo ke buyer ===
    try:
        cur.execute("SELECT balance FROM user_balance WHERE user_id=?", (buyer_id,))
        row_bal = cur.fetchone()

        if row_bal is None:
            new_balance = harga_deal
            cur.execute(
                "INSERT INTO user_balance (user_id, balance) VALUES (?, ?)",
                (buyer_id, new_balance)
            )
        else:
            current_bal = row_bal[0] or 0
            new_balance = current_bal + harga_deal
            cur.execute(
                "UPDATE user_balance SET balance=? WHERE user_id=?",
                (new_balance, buyer_id)
            )
        conn.commit()
    except Exception as e:
        print(f"⚠️ Gagal refund saldo buyer {buyer_id} untuk gift {slug}: {e}")
        await event.answer("❌ Gagal mengembalikan saldo buyer, pembatalan TFO dibatalkan.", alert=True)
        return

    try:
        cur.execute("""
            UPDATE gifts
            SET status_tfo=NULL,
                pending_tfo_at=NULL,
                pending_msg_id=NULL,
                is_listed=0,
                is_sold=1
            WHERE id=? AND status_tfo=?
        """, (gift_id, "pending_tfo"))
        conn.commit()
    except Exception as e:
        print(f"⚠️ Gagal update status gift {slug} saat batal TFO: {e}")
        await event.answer("❌ Gagal membatalkan TFO gift!", alert=True)
        return

    try:
        harga_fmt = f"Rp{harga_base:,}".replace(",", ".")
        harga_deal_fmt = f"Rp{harga_deal:,}".replace(",", ".")
        saldo_baru_fmt = f"Rp{new_balance:,}".replace(",", ".")

        msg_buyer = f"""
🚫 **TFO GIFT DIBATALKAN OLEH ADMIN**

🎁 **Gift:** {slug.replace("-", " #")}
💸 **Harga Base:** `{harga_fmt}`
💸 **Refund (harga + 2%):** `{harga_deal_fmt}`
💳 **Saldo Sekarang:** `{saldo_baru_fmt}`

^^__TFO untuk gift ini telah dibatalkan oleh admin, saldo Anda sudah dikembalikan penuh (harga + fee 2%).__^^
        """.strip()

        await bot.send_message(buyer_id, msg_buyer)
    except Exception as e:
        print(f"⚠️ Gagal kirim notif batal TFO ke buyer {buyer_id}: {e}")

    try:
        await event.delete()
    except Exception as e:
        print(f"⚠️ Gagal hapus pesan pending TFO: {e}")

    await event.answer(
        f"✅ Gift '{slug}' berhasil dibatalkan dari status TFO, saldo buyer sudah direfund (harga + 2%) dan gift di-set SOLD!",
        alert=True
    )

@bot.on(events.CallbackQuery(pattern=b"^price_cancel_(.+)$"))
async def cancel_price(event):
    slug = event.pattern_match.group(1).decode()
    user_id = get_effective_user_id(event.sender_id)
    await event.answer(f"🔎 Pengaturan harga untuk gift {slug}", alert=True)
    await gift_detail(event)

@bot.on(events.NewMessage(func=lambda e: e.photo))
async def collect_photos(event):
    user_id = event.sender_id

    if user_id not in active_sessions:
        return

    photo = await event.download_media(file=bytes)
    user_photos[user_id].append(photo)
    await event.respond(f"📸 Foto {len(user_photos[user_id])} diterima. Kirim foto lain atau ketik /done jika selesai.")


@bot.on(events.NewMessage(pattern=r"^/done$"))
async def done_grid(event):
    user_id = event.sender_id

    if user_id not in active_sessions:
        await event.respond("❌ Kamu belum memulai sesi grid. Gunakan /grid terlebih dahulu.")
        return

    if len(user_photos.get(user_id, [])) < 2:
        await event.respond("❌ Minimal 2 foto diperlukan untuk membuat grid.")
        return

    photos = user_photos[user_id]
    images = [Image.open(io.BytesIO(p)) for p in photos]

    n = len(images)
    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)

    widths, heights = zip(*(img.size for img in images))
    max_width = max(widths)
    max_height = max(heights)

    grid_width = cols * max_width
    grid_height = rows * max_height
    new_im = Image.new('RGB', (grid_width, grid_height), (255, 255, 255))

    i = 0
    for r in range(rows):
        for c in range(cols):
            if i >= n:
                break
            img = images[i]
            new_im.paste(img, (c * max_width, r * max_height))
            i += 1

    output = io.BytesIO()
    new_im.save(output, format="JPEG")
    output.seek(0)
    output.name = "grid.jpg"

    await bot.send_file(
        event.chat_id,
        output,
        caption="✅ Hasil grid foto kamu:",
        force_document=False
    )

    del user_photos[user_id]
    active_sessions.discard(user_id)


@bot.on(events.NewMessage(pattern=r"^/batal$"))
async def cancel_grid(event):
    user_id = event.sender_id

    if user_id in active_sessions:
        active_sessions.discard(user_id)
        user_photos.pop(user_id, None)
        await event.respond("❌ Sesi grid dibatalkan.")
    else:
        await event.respond("⚠️ Tidak ada sesi aktif untuk dibatalkan.")

@bot.on(events.CallbackQuery(data=b"bantuan"))
async def bantuan_menu(event):
    try:
        bantuan_buttons = []
        row = []
        for label, msg_id in TEMPLATE_BANTUAN.items():
            cb_data = f"bantuan_item:{msg_id}".encode()
            row.append(Button.inline(label, data=cb_data))

            if len(row) == 2:
                bantuan_buttons.append(row)
                row = []
        if row:
            bantuan_buttons.append(row)

        bantuan_buttons.append([Button.inline("⬅️ KEMBALI", data="back_gift")])
        
        msg = f"""
**__Klik tombol dibawah ini untuk melihat penjelasan & tutorial setiap fitur bot, pilih sesuai dengan susunan dibawah ini!__**

1. Bagaimana cara deposit?
2. Bagaimana cara withdraw?
3. Apa fungsi tombol 🎁 INVENTORY?
4. Bagaimana cara mengatur gift yang di titipkan ke WINEDASH?
5. Bagaimana cara membeli gift stars otomatis?
        """

        await event.respond(
            msg,
            buttons=bantuan_buttons
        )
        await event.delete()

    except Exception as e:
        print(f"⚠️ Error di bantuan_menu: {e}")
        await event.answer("Terjadi kesalahan membuka menu bantuan.", alert=True)

@bot.on(events.CallbackQuery(pattern=b"bantuan_item:"))
async def bantuan_item_handler(event):
    try:
        data = event.data.decode()
        _, msg_id_str = data.split(":", 1)
        msg_id = int(msg_id_str)

        template_msg = await bot.get_messages(CHANNEL_PENDING, ids=msg_id)
        if not template_msg:
            await event.answer("Template tidak ditemukan.", alert=True)
            return
          
        buttons = [
          [Button.inline("🔙 KEMBALI", data="bantuan")]
        ]

        await bot.send_message(event.chat_id, template_msg, buttons=buttons)
        await event.delete()

    except Exception as e:
        print(f"⚠️ Error di bantuan_item_handler: {e}")
        try:
            await event.answer("Gagal mengambil bantuan.", alert=True)
        except:
            pass

@bot.on(events.NewMessage(pattern='/restore'))
async def _(event):
    global conn, cur

    if not event.is_reply:
        await event.reply("❌ Balas pesan ini ke file .db yang ingin di-restore.")
        return

    reply_msg = await event.get_reply_message()

    if not reply_msg.document or not reply_msg.file.name.endswith(".db"):
        await event.reply("❌ File harus berformat .db")
        return

    await event.reply("⏬ Mengunduh file database...")

    # Tutup koneksi database dengan benar
    try:
        if conn:
            conn.close()
    except:
        pass

    # Buat file backup dari database lama
    backup_name = f"backup_before_restore_{int(time.time())}.db"
    try:
        if os.path.exists(DB_PATH):
            import shutil
            shutil.copy2(DB_PATH, backup_name)
            print(f"✅ Backup database lama dibuat: {backup_name}")
    except Exception as e:
        print(f"⚠️ Gagal membuat backup: {e}")

    # Hapus database lama jika ada
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except Exception as e:
            print(f"⚠️ Gagal hapus database lama: {e}")

    # Download database baru
    try:
        await reply_msg.download_media(file=DB_PATH)
        print(f"✅ Database baru diunduh: {DB_PATH}")
    except Exception as e:
        await event.reply(f"❌ Gagal mengunduh file: {e}")
        return

    # Reconnect database
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cur = conn.cursor()
        print("✅ Database berhasil di-restore dan di-reconnect")
    except Exception as e:
        await event.reply(f"❌ Gagal menghubungkan ke database: {e}")
        return

    await event.reply("✅ Database berhasil di-restore dari file yang diunggah.")

@bot.on(events.NewMessage(pattern="/backup"))
async def manual_backup(event):
    await backup_database("Backup manual oleh admin")
    await event.reply("✅ Backup sedang dikirim")

async def backup_database(send_caption: str):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    temp_path = f"/tmp/backup_{timestamp}.db"

    try:
        # 🔒 Backup dari koneksi AKTIF (AMAN)
        backup_conn = sqlite3.connect(temp_path)
        conn.backup(backup_conn)
        backup_conn.close()

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"

        async with aiohttp.ClientSession() as session:
            form = aiohttp.FormData()
            form.add_field("chat_id", str(CHANNEL_BACKUP))
            form.add_field("caption", send_caption)

            with open(temp_path, "rb") as f:
                form.add_field(
                    "document",
                    f,
                    filename=f"backup_{timestamp}.db",
                    content_type="application/x-sqlite3"
                )

                async with session.post(url, data=form) as r:
                    if r.status != 200:
                        print("❌ Backup gagal:", await r.text())
                    else:
                        print("✅ Backup terkirim")

    finally:
        try:
            os.remove(temp_path)
        except:
            pass

async def auto_backup():
    while True:
        await backup_database(f"Backup otomatis ({datetime.now()})")
        await asyncio.sleep(300)

async def main():
    print("🎁 BOT MARKETPLACE GIFT BERJALAN")

    global conn, cur
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
    cur = conn.cursor()
    
    cur.execute("PRAGMA journal_mode=WAL")
    cur.execute("PRAGMA synchronous=NORMAL")
    conn.commit()

    asyncio.create_task(monitor_nego())
    asyncio.create_task(resume_monitor_tfo())
    asyncio.create_task(monitor_owner())
    
    backup_task = asyncio.create_task(auto_backup())
    
    asyncio.create_task(monitor_deposit_qris())
    asyncio.create_task(monitor_up())
    asyncio.create_task(monitor_price())
    asyncio.create_task(heartbeat())
    push_json_to_github()

    try:
        await bot.run_until_disconnected()
        await logs.run_until_disconnected()
    finally:
        backup_task.cancel()
        try:
            await backup_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    try:
        bot.loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n👋 Bot dihentikan oleh user")
    except Exception as e:
        print(f"❌ Error utama: {e}")
