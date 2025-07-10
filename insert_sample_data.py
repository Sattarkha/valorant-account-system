import sqlite3

sample_bundles = [
    {
        'bundle_name': 'Prime Bundle',
        'skins': [
            {'skin_name': 'Prime Vandal', 'skin_type': 'gun', 'value_vp': 1775, 'image_url': None},
            {'skin_name': 'Prime Classic', 'skin_type': 'gun', 'value_vp': 1775, 'image_url': None},
            {'skin_name': 'Prime Guardian', 'skin_type': 'gun', 'value_vp': 1775, 'image_url': None},
            {'skin_name': 'Prime Spectre', 'skin_type': 'gun', 'value_vp': 1775, 'image_url': None},
            {'skin_name': 'Prime Karambit', 'skin_type': 'melee', 'value_vp': 3550, 'image_url': None}
        ]
    },
    {
        'bundle_name': 'Oni Bundle',
        'skins': [
            {'skin_name': 'Oni Phantom', 'skin_type': 'gun', 'value_vp': 1775, 'image_url': None},
            {'skin_name': 'Oni Guardian', 'skin_type': 'gun', 'value_vp': 1775, 'image_url': None},
            {'skin_name': 'Oni Bucky', 'skin_type': 'gun', 'value_vp': 1775, 'image_url': None},
            {'skin_name': 'Oni Shorty', 'skin_type': 'gun', 'value_vp': 1775, 'image_url': None},
            {'skin_name': 'Oni Claw', 'skin_type': 'melee', 'value_vp': 3550, 'image_url': None}
        ]
    },
    {
        'bundle_name': 'Reaver Bundle',
        'skins': [
            {'skin_name': 'Reaver Vandal', 'skin_type': 'gun', 'value_vp': 1775, 'image_url': None},
            {'skin_name': 'Reaver Operator', 'skin_type': 'gun', 'value_vp': 1775, 'image_url': None},
            {'skin_name': 'Reaver Guardian', 'skin_type': 'gun', 'value_vp': 1775, 'image_url': None},
            {'skin_name': 'Reaver Sheriff', 'skin_type': 'gun', 'value_vp': 1775, 'image_url': None},
            {'skin_name': 'Reaver Knife', 'skin_type': 'melee', 'value_vp': 3550, 'image_url': None}
        ]
    }
]

conn = sqlite3.connect('valorant_game.db')
cursor = conn.cursor()

# Clear old data
cursor.execute('DELETE FROM bundle_skins')
cursor.execute('DELETE FROM bundles')
conn.commit()

# Insert new sample data
for bundle in sample_bundles:
    cursor.execute('INSERT INTO bundles (bundle_name) VALUES (?)', (bundle['bundle_name'],))
    bundle_id = cursor.lastrowid
    for skin in bundle['skins']:
        cursor.execute('''
            INSERT INTO bundle_skins (bundle_id, skin_name, skin_type, value_vp, image_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (bundle_id, skin['skin_name'], skin['skin_type'], skin['value_vp'], skin['image_url']))
conn.commit()
conn.close()
print('Sample bundles and skins inserted!') 