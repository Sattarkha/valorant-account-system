import sqlite3
import hashlib
from datetime import datetime

def init_database():
    conn = sqlite3.connect('valorant_game.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            ban_type TEXT,
            ban_reason TEXT,
            suspension_end TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User details table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_details (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            region TEXT,
            country TEXT,
            level INTEGER DEFAULT 1,
            rank TEXT,
            registration_date TEXT,
            phone_verified BOOLEAN DEFAULT 0,
            email_verified BOOLEAN DEFAULT 0,
            episode TEXT,
            act TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Store table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS store (
            user_id INTEGER PRIMARY KEY,
            valorant_points INTEGER DEFAULT 0,
            radiant_points INTEGER DEFAULT 0,
            kingdom_points INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Inventory tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_skins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            skin_name TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_battlepass (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            battlepass_name TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_buddies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            buddy_name TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            agent_name TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            card_name TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_titles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title_name TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Skins table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skin_name TEXT UNIQUE NOT NULL,
            vp_price INTEGER NOT NULL,
            tier TEXT NOT NULL
        )
    ''')
    
    # Match history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            match_date TEXT,
            result TEXT,
            score TEXT,
            link TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Bundles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bundles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bundle_name TEXT UNIQUE NOT NULL
        )
    ''')
    # Bundle skins table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bundle_skins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bundle_id INTEGER,
            skin_name TEXT NOT NULL,
            skin_type TEXT,
            value_vp INTEGER,
            image_url TEXT,
            FOREIGN KEY (bundle_id) REFERENCES bundles (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, email, password, name, region, country):
    conn = sqlite3.connect('valorant_game.db')
    cursor = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', (username, email, password_hash))
        
        user_id = cursor.lastrowid
        
        # Create user details
        cursor.execute('''
            INSERT INTO user_details (user_id, name, region, country, registration_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, name, region, country, datetime.now().strftime('%Y-%m-%d')))
        
        # Create store
        cursor.execute('''
            INSERT INTO store (user_id, valorant_points, radiant_points, kingdom_points)
            VALUES (?, 1000, 200, 300)
        ''', (user_id,))
        
        # Add default inventory items
        default_skins = ['Classic Pistol', 'Vandal']
        for skin in default_skins:
            cursor.execute('INSERT INTO inventory_skins (user_id, skin_name) VALUES (?, ?)', (user_id, skin))
        
        default_agents = ['Jett', 'Phoenix']
        for agent in default_agents:
            cursor.execute('INSERT INTO inventory_agents (user_id, agent_name) VALUES (?, ?)', (user_id, agent))
        
        cursor.execute('INSERT INTO inventory_battlepass (user_id, battlepass_name) VALUES (?, ?)', (user_id, 'Episode 1'))
        cursor.execute('INSERT INTO inventory_buddies (user_id, buddy_name) VALUES (?, ?)', (user_id, 'Default Buddy'))
        cursor.execute('INSERT INTO inventory_cards (user_id, card_name) VALUES (?, ?)', (user_id, 'Default Card'))
        cursor.execute('INSERT INTO inventory_titles (user_id, title_name) VALUES (?, ?)', (user_id, 'Rookie'))
        
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(username, email, password):
    conn = sqlite3.connect('valorant_game.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, password_hash, status, ban_type, suspension_end, email_verified
        FROM users u
        LEFT JOIN user_details ud ON u.id = ud.user_id
        WHERE u.username = ?
    ''', (username,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        user_id, stored_hash, status, ban_type, suspension_end, email_verified = result
        if stored_hash == hash_password(password):
            return {
                'user_id': user_id,
                'status': status,
                'ban_type': ban_type,
                'suspension_end': suspension_end,
                'email_verified': email_verified
            }
    return None

def get_user_data(user_id):
    conn = sqlite3.connect('valorant_game.db')
    cursor = conn.cursor()
    
    # Get user details
    cursor.execute('SELECT * FROM user_details WHERE user_id = ?', (user_id,))
    details = cursor.fetchone()
    
    # Get store
    cursor.execute('SELECT * FROM store WHERE user_id = ?', (user_id,))
    store = cursor.fetchone()
    
    # Get inventory
    cursor.execute('SELECT skin_name FROM inventory_skins WHERE user_id = ?', (user_id,))
    skins = [row[0] for row in cursor.fetchall()]
    
    cursor.execute('SELECT battlepass_name FROM inventory_battlepass WHERE user_id = ?', (user_id,))
    battlepass = [row[0] for row in cursor.fetchall()]
    
    cursor.execute('SELECT buddy_name FROM inventory_buddies WHERE user_id = ?', (user_id,))
    buddies = [row[0] for row in cursor.fetchall()]
    
    cursor.execute('SELECT agent_name FROM inventory_agents WHERE user_id = ?', (user_id,))
    agents = [row[0] for row in cursor.fetchall()]
    
    cursor.execute('SELECT card_name FROM inventory_cards WHERE user_id = ?', (user_id,))
    cards = [row[0] for row in cursor.fetchall()]
    
    cursor.execute('SELECT title_name FROM inventory_titles WHERE user_id = ?', (user_id,))
    titles = [row[0] for row in cursor.fetchall()]
    
    # Get match history
    cursor.execute('SELECT * FROM match_history WHERE user_id = ? ORDER BY match_date DESC', (user_id,))
    matches = cursor.fetchall()
    
    conn.close()
    
    return {
        'details': {
            'name': details[1] if details else '',
            'region': details[2] if details else '',
            'country': details[3] if details else '',
            'level': details[4] if details else 1,
            'rank': details[5] if details else '',
            'registration_date': details[6] if details else '',
            'phone_verified': bool(details[7]) if details else False,
            'email_verified': bool(details[8]) if details else False,
            'episode': details[9] if len(details) > 9 and details[9] else '',
            'act': details[10] if len(details) > 10 and details[10] else '',
        },
        'store': {
            'valorant_points': store[1] if store else 0,
            'radiant_points': store[2] if store else 0,
            'kingdom_points': store[3] if store else 0,
        },
        'inventory': {
            'skins': skins,
            'battlepass': battlepass,
            'buddies': buddies,
            'agents': agents,
            'cards': cards,
            'titles': titles,
        },
        'match_history': [
            {
                'date': match[2],
                'result': match[3],
                'score': match[4],
                'link': match[5]
            } for match in matches
        ]
    }

def update_user_details(user_id, **kwargs):
    conn = sqlite3.connect('valorant_game.db')
    cursor = conn.cursor()
    
    for key, value in kwargs.items():
        cursor.execute(f'UPDATE user_details SET {key} = ? WHERE user_id = ?', (value, user_id))
    
    conn.commit()
    conn.close()

def add_match_history(user_id, result, score, link="#"):
    conn = sqlite3.connect('valorant_game.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO match_history (user_id, match_date, result, score, link)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, datetime.now().strftime('%Y-%m-%d'), result, score, link))
    
    conn.commit()
    conn.close()

def auto_verify_email(user_id):
    """Auto-verify email for demo purposes"""
    conn = sqlite3.connect('valorant_game.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE user_details SET email_verified = 1 WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()

# Top 20 popular Valorant skins with price and tier
POPULAR_SKINS = [
    ("Prime Vandal", 1775, "Premium Edition"),
    ("Elderflame Operator", 2475, "Ultra Edition"),
    ("Reaver Vandal", 1775, "Premium Edition"),
    ("Oni Phantom", 1775, "Premium Edition"),
    ("Glitchpop Vandal", 2175, "Premium Edition"),
    ("Ion Sheriff", 1775, "Premium Edition"),
    ("Magepunk Ghost", 1775, "Premium Edition"),
    ("Sovereign Ghost", 1775, "Premium Edition"),
    ("Singularity Phantom", 2175, "Premium Edition"),
    ("Ruination Sword", 4350, "Exclusive Edition"),
    ("Spectrum Phantom", 2675, "Exclusive Edition"),
    ("RGX 11z Pro Vandal", 2175, "Premium Edition"),
    ("Sentinels of Light Sheriff", 2175, "Premium Edition"),
    ("BlastX Phantom", 2175, "Premium Edition"),
    ("Forsaken Vandal", 1775, "Premium Edition"),
    ("Ion Phantom", 1775, "Premium Edition"),
    ("Prime Classic", 1775, "Premium Edition"),
    ("Reaver Sheriff", 1775, "Premium Edition"),
    ("Elderflame Vandal", 2475, "Ultra Edition"),
    ("Glitchpop Phantom", 2175, "Premium Edition"),
]

def insert_popular_skins():
    conn = sqlite3.connect('valorant_game.db')
    cursor = conn.cursor()
    try:
        for skin_name, vp_price, tier in POPULAR_SKINS:
            cursor.execute('''
                INSERT OR IGNORE INTO skins (skin_name, vp_price, tier)
                VALUES (?, ?, ?)
            ''', (skin_name, vp_price, tier))
        conn.commit()
    finally:
        conn.close()

def insert_prime_vandal_skin():
    conn = sqlite3.connect('valorant_game.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO skins (skin_name, vp_price, tier)
            VALUES (?, ?, ?)
        ''', ("Prime Vandal", 1775, "Premium Edition"))
        conn.commit()
    finally:
        conn.close()

# Unicorny set ki skins aur prices
UNICORNY_SKINS = [
    ("Frenzy", 875, "Select Edition"),
    ("Guardian", 875, "Select Edition"),
    ("Spectre", 875, "Select Edition"),
    ("Vandal", 875, "Select Edition"),
    ("Wonderstallion Hammer (melee)", 3550, "Exclusive Edition"),
]

def insert_bundle_and_skins(bundle_name, skins):
    """
    skins: list of dicts with keys: skin_name, skin_type, value_vp, image_url
    """
    conn = sqlite3.connect('valorant_game.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT OR IGNORE INTO bundles (bundle_name) VALUES (?)', (bundle_name,))
        cursor.execute('SELECT id FROM bundles WHERE bundle_name = ?', (bundle_name,))
        bundle_id = cursor.fetchone()[0]
        for skin in skins:
            cursor.execute('''
                INSERT INTO bundle_skins (bundle_id, skin_name, skin_type, value_vp, image_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (bundle_id, skin['skin_name'], skin['skin_type'], skin['value_vp'], skin.get('image_url')))
        conn.commit()
    finally:
        conn.close()

def calculate_account_skin_value(user_id):
    """
    User ki owned skins ki total value (VP) calculate karta hai.
    """
    conn = sqlite3.connect('valorant_game.db')
    cursor = conn.cursor()
    # User ki inventory_skins se skin_name lein
    cursor.execute('SELECT skin_name FROM inventory_skins WHERE user_id = ?', (user_id,))
    owned_skins = [row[0] for row in cursor.fetchall()]
    total_value = 0
    details = []
    for skin in owned_skins:
        # bundle_skins table se price uthao
        cursor.execute('SELECT value_vp, bundle_id FROM bundle_skins WHERE skin_name = ?', (skin,))
        result = cursor.fetchone()
        if result:
            value_vp, bundle_id = result
            # Bundle ka naam bhi nikal lo
            cursor.execute('SELECT bundle_name FROM bundles WHERE id = ?', (bundle_id,))
            bundle_row = cursor.fetchone()
            bundle_name = bundle_row[0] if bundle_row else None
            total_value += value_vp if value_vp else 0
            details.append({'skin_name': skin, 'bundle': bundle_name, 'value_vp': value_vp})
        else:
            details.append({'skin_name': skin, 'bundle': None, 'value_vp': None})
    conn.close()
    return {'total_value_vp': total_value, 'details': details}

def purchase_skin(user_id, skin_name):
    """
    User ek skin buy karta hai. Points check karo, inventory update karo.
    Return: (success, message)
    """
    conn = sqlite3.connect('valorant_game.db')
    cursor = conn.cursor()
    # Skin ki value nikaalo
    cursor.execute('SELECT value_vp FROM bundle_skins WHERE skin_name = ?', (skin_name,))
    row = cursor.fetchone()
    if not row or row[0] is None:
        conn.close()
        return False, 'Skin price not found.'
    price = row[0]
    # User ke points dekho
    cursor.execute('SELECT valorant_points FROM store WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, 'User store not found.'
    points = row[0]
    # Already owned?
    cursor.execute('SELECT 1 FROM inventory_skins WHERE user_id = ? AND skin_name = ?', (user_id, skin_name))
    if cursor.fetchone():
        conn.close()
        return False, 'Already owned.'
    if points < price:
        conn.close()
        return False, 'Not enough points.'
    # Purchase
    cursor.execute('UPDATE store SET valorant_points = valorant_points - ? WHERE user_id = ?', (price, user_id))
    cursor.execute('INSERT INTO inventory_skins (user_id, skin_name) VALUES (?, ?)', (user_id, skin_name))
    conn.commit()
    conn.close()
    return True, 'Purchase successful!'

def purchase_bundle(user_id, bundle_id):
    """
    User ek bundle buy karta hai. Saari skins ek sath milti hain, total price sum hota hai.
    Return: (success, message)
    """
    conn = sqlite3.connect('valorant_game.db')
    cursor = conn.cursor()
    # Bundle ki saari skins nikaalo
    cursor.execute('SELECT skin_name, value_vp FROM bundle_skins WHERE bundle_id = ?', (bundle_id,))
    skins = cursor.fetchall()
    if not skins:
        conn.close()
        return False, 'Bundle not found.'
    # Already owned skins filter karo
    owned = set()
    cursor.execute('SELECT skin_name FROM inventory_skins WHERE user_id = ?', (user_id,))
    for row in cursor.fetchall():
        owned.add(row[0])
    to_buy = [(name, price) for name, price in skins if name not in owned]
    if not to_buy:
        conn.close()
        return False, 'All skins already owned.'
    total_price = sum(price for name, price in to_buy if price)
    # User ke points dekho
    cursor.execute('SELECT valorant_points FROM store WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, 'User store not found.'
    points = row[0]
    if points < total_price:
        conn.close()
        return False, 'Not enough points.'
    # Purchase
    cursor.execute('UPDATE store SET valorant_points = valorant_points - ? WHERE user_id = ?', (total_price, user_id))
    for name, price in to_buy:
        cursor.execute('INSERT INTO inventory_skins (user_id, skin_name) VALUES (?, ?)', (user_id, name))
    conn.commit()
    conn.close()
    return True, f'Bundle purchased! {len(to_buy)} new skins added.'

# Initialize database with demo user
def create_demo_user():
    conn = sqlite3.connect('valorant_game.db')
    cursor = conn.cursor()
    
    # Check if demo user exists
    cursor.execute('SELECT id FROM users WHERE username = ?', ('demo',))
    if not cursor.fetchone():
        create_user('demo', 'demo@valorant.com', 'valorant123', 'Demo Player', 'EU', 'France')
        
        # Get demo user ID
        cursor.execute('SELECT id FROM users WHERE username = ?', ('demo',))
        demo_user_id = cursor.fetchone()[0]
        
        # Update demo user details
        update_user_details(demo_user_id, level=45, rank='Platinum', phone_verified=True, email_verified=True)
        
        # Update store
        cursor.execute('''
            UPDATE store 
            SET valorant_points = 1200, radiant_points = 300, kingdom_points = 500
            WHERE user_id = ?
        ''', (demo_user_id,))
        
        # Add demo inventory
        demo_skins = ['Prime Vandal', 'Elderflame Operator']
        for skin in demo_skins:
            cursor.execute('INSERT INTO inventory_skins (user_id, skin_name) VALUES (?, ?)', (demo_user_id, skin))
        
        demo_agents = ['Jett', 'Phoenix', 'Sage']
        for agent in demo_agents:
            cursor.execute('INSERT INTO inventory_agents (user_id, agent_name) VALUES (?, ?)', (demo_user_id, agent))
        
        cursor.execute('INSERT INTO inventory_battlepass (user_id, battlepass_name) VALUES (?, ?)', (demo_user_id, 'Episode 6'))
        cursor.execute('INSERT INTO inventory_buddies (user_id, buddy_name) VALUES (?, ?)', (demo_user_id, 'Valorant Buddy'))
        cursor.execute('INSERT INTO inventory_cards (user_id, card_name) VALUES (?, ?)', (demo_user_id, 'Valorant Card'))
        cursor.execute('INSERT INTO inventory_titles (user_id, title_name) VALUES (?, ?)', (demo_user_id, 'The Unstoppable'))
        
        # Add demo matches
        demo_matches = [
            ('2023-06-01', 'Win', '13-7'),
            ('2023-05-28', 'Loss', '8-13'),
        ]
        for date, result, score in demo_matches:
            cursor.execute('''
                INSERT INTO match_history (user_id, match_date, result, score, link)
                VALUES (?, ?, ?, ?, ?)
            ''', (demo_user_id, date, result, score, '#'))
        
        conn.commit()
    
    conn.close() 