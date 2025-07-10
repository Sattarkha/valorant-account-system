import requests
from bs4 import BeautifulSoup
import csv
import sqlite3
from database import insert_bundle_and_skins
from database import calculate_account_skin_value

URL = "https://www.pcgamesn.com/valorant/skins"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

def scrape_valorant_skins():
    # --- Force sample data for demo ---
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
    for bundle in sample_bundles:
        insert_bundle_and_skins(bundle['bundle_name'], bundle['skins'])
    print("Forcefully added sample data for demo.")
    # --- End force sample data ---
    return
    response = requests.get(URL, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch page: {response.status_code}")
        # Sample data add karo agar scraping fail ho
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
        for bundle in sample_bundles:
            insert_bundle_and_skins(bundle['bundle_name'], bundle['skins'])
        print("Added sample data due to scraping failure.")
        return
    soup = BeautifulSoup(response.text, 'html.parser')
    bundles = []
    # Better scraping logic - multiple selectors try karo
    # Method 1: Direct skin names
    skin_elements = soup.find_all(['h2', 'h3', 'h4', 'strong', 'b'])
    if skin_elements:
        current_bundle = None
        for element in skin_elements:
            text = element.get_text(strip=True)
            if 'bundle' in text.lower() or 'collection' in text.lower():
                current_bundle = text
                bundles.append({'bundle_name': current_bundle, 'skins': []})
            elif any(gun in text.lower() for gun in ['vandal', 'phantom', 'operator', 'sheriff', 'ghost', 'classic', 'spectre', 'guardian', 'bucky', 'shorty', 'frenzy', 'judge', 'marshal', 'outlaw', 'bulldog', 'ares', 'odin']):
                if current_bundle:
                    skin_type = 'melee' if any(melee in text.lower() for melee in ['knife', 'sword', 'dagger', 'karambit', 'claw', 'hammer', 'axe']) else 'gun'
                    # Try to find price nearby
                    price = 1775  # Default price
                    next_sibling = element.find_next_sibling()
                    if next_sibling and 'VP' in next_sibling.get_text():
                        try:
                            price = int(''.join(filter(str.isdigit, next_sibling.get_text())))
                        except:
                            pass
                    bundles[-1]['skins'].append({
                        'skin_name': text,
                        'skin_type': skin_type,
                        'value_vp': price,
                        'image_url': None
                    })
    # Method 2: If no bundles found, create individual skins
    if not bundles:
        individual_skins = [
            {'skin_name': 'Prime Vandal', 'skin_type': 'gun', 'value_vp': 1775, 'image_url': None},
            {'skin_name': 'Oni Phantom', 'skin_type': 'gun', 'value_vp': 1775, 'image_url': None},
            {'skin_name': 'Reaver Vandal', 'skin_type': 'gun', 'value_vp': 1775, 'image_url': None},
            {'skin_name': 'Elderflame Operator', 'skin_type': 'gun', 'value_vp': 2475, 'image_url': None},
            {'skin_name': 'Glitchpop Vandal', 'skin_type': 'gun', 'value_vp': 2175, 'image_url': None},
            {'skin_name': 'Ion Sheriff', 'skin_type': 'gun', 'value_vp': 1775, 'image_url': None},
            {'skin_name': 'Magepunk Ghost', 'skin_type': 'gun', 'value_vp': 1775, 'image_url': None},
            {'skin_name': 'Sovereign Ghost', 'skin_type': 'gun', 'value_vp': 1775, 'image_url': None},
            {'skin_name': 'Singularity Phantom', 'skin_type': 'gun', 'value_vp': 2175, 'image_url': None},
            {'skin_name': 'Spectrum Phantom', 'skin_type': 'gun', 'value_vp': 2675, 'image_url': None}
        ]
        bundles.append({'bundle_name': 'Individual Skins', 'skins': individual_skins})
    # Database me insert karo
    for bundle in bundles:
        insert_bundle_and_skins(bundle['bundle_name'], bundle['skins'])
    # CSV me save karen
    with open('valorant_skins_bundles.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['bundle_name', 'skin_name', 'skin_type', 'value_vp', 'image_url'])
        writer.writeheader()
        for bundle in bundles:
            for skin in bundle['skins']:
                writer.writerow({
                    'bundle_name': bundle['bundle_name'],
                    'skin_name': skin['skin_name'],
                    'skin_type': skin['skin_type'],
                    'value_vp': skin['value_vp'],
                    'image_url': skin['image_url']
                })
    print(f"Scraped {len(bundles)} bundles. Data saved to valorant_skins_bundles.csv")

def show_skins():
    conn = sqlite3.connect('valorant_game.db')
    cursor = conn.cursor()
    cursor.execute('SELECT skin_name, vp_price, tier FROM skins')
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()

if __name__ == "__main__":
    from database import insert_unicorny_skins
    insert_unicorny_skins()
    show_skins()
    # Demo user ki total skin value print karo
    import sqlite3
    conn = sqlite3.connect('valorant_game.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ?', ('demo',))
    row = cursor.fetchone()
    if row:
        demo_user_id = row[0]
        result = calculate_account_skin_value(demo_user_id)
        print(f"Demo user ki total skin value: {result['total_value_vp']} VP")
        print("Details:")
        for detail in result['details']:
            print(detail)
    else:
        print("Demo user nahi mila.")
    conn.close()

import sqlite3

conn = sqlite3.connect('valorant_game.db')
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS skins')
conn.commit()
conn.close()
print("Old skins table deleted.") 