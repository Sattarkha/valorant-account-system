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