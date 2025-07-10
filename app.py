import streamlit as st
from datetime import datetime
from database import create_user, verify_user, get_user_data, auto_verify_email, add_match_history, update_user_details, purchase_skin, purchase_bundle
import database as db
import pandas as pd
import os
from urllib.parse import parse_qs
import sqlite3
from scrape_valorant_skins import scrape_valorant_skins
from database import calculate_account_skin_value

# Initialize database
db.init_database()
db.create_demo_user()

# Temporary: Drop and recreate bundle_skins table with image_url column
import sqlite3
conn = sqlite3.connect('valorant_game.db')
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS bundle_skins')
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
print("bundle_skins table recreated with image_url column.")

# --- Custom CSS for Valorant Theme with Dracula Sidebar ---
VALORANT_CSS = """
<style>
body, .stApp {
    background-color: #0f1923;
    color: #fff;
}
/* Sidebar ONLY Dracula theme */
[data-testid="stSidebar"], .sidebar .sidebar-content {
    background: #44475a !important;
    background-color: #44475a !important;
}
/* Top header bar fix */
header[data-testid="stHeader"] {
    background: #0f1923 !important;
    color: #fff !important;
    border: none !important;
    box-shadow: none !important;
}
.stButton>button {
    background: #ff4655;
    color: white;
    border-radius: 8px;
    font-weight: bold;
}
.stButton>button:hover {
    background: #ff4655cc;
}
.stFormSubmitButton>button {
    background: linear-gradient(135deg, #ff4655, #ff6b7a) !important;
    color: white !important;
    border-radius: 25px !important;
    font-weight: bold !important;
    border: none !important;
    padding: 12px 30px !important;
    font-size: 16px !important;
    letter-spacing: 1px !important;
    box-shadow: 0 4px 15px rgba(255, 70, 85, 0.3) !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
    height: 50px !important;
}
.stFormSubmitButton>button:hover {
    background: linear-gradient(135deg, #ff6b7a, #ff4655) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(255, 70, 85, 0.4) !important;
}
.stFormSubmitButton>button:active {
    transform: translateY(0) !important;
    box-shadow: 0 2px 10px rgba(255, 70, 85, 0.3) !important;
}
.stTextInput>div>div>input {
    background: #1a232e;
    color: #fff;
}
label, .css-1c7y2kd, .stTextInput label, .stTextInput>label, .stTextInput label span {
    color: #fff !important;
}
</style>
"""

st.markdown(VALORANT_CSS, unsafe_allow_html=True)

# --- Session State ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'

# --- Registration Page ---
def registration_page():
    st.title("🎮 Valorant Account Registration")
    
    with st.form("registration_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        name = st.text_input("Full Name")
        region = st.selectbox("Region", ["NA", "EU", "AP", "KR", "BR", "LATAM"])
        country = st.text_input("Country")
        
        submitted = st.form_submit_button("Register")
        
        if submitted:
            if password != confirm_password:
                st.error("Passwords do not match!")
            elif not all([username, email, password, name, region, country]):
                st.error("All fields are required!")
            else:
                success = create_user(username, email, password, name, region, country)
                if success:
                    st.success("Registration successful! Please login.")
                    st.session_state.current_page = 'login'
                    st.rerun()
                else:
                    st.error("Username or email already exists!")

# --- Login Page ---
def login_page():
    st.title("🔐 Valorant Account Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            login_btn = st.form_submit_button("Login")
        with col2:
            register_btn = st.form_submit_button("Register")
        
        if login_btn:
            user_data = verify_user(username, None, password)  # Email hata diya
            if not user_data:
                st.error("Credential's not match")
            elif user_data['status'] == 'banned':
                if user_data['ban_type'] == 'permanent':
                    st.error("Permenant Ban")
                else:
                    st.error(f"Temporary suspension until {user_data['suspension_end']}")
            elif user_data['status'] == 'suspended':
                st.error(f"Temporary suspension until {user_data['suspension_end']}")
            elif user_data['status'] == 'locked':
                st.error("Account Locked")
            elif not user_data['email_verified']:
                # Auto-verify email for demo purposes
                auto_verify_email(user_data['user_id'])
                st.success("✅ Email auto-verified! You can now login.")
                st.rerun()
            else:
                st.session_state.logged_in = True
                st.session_state.user_id = user_data['user_id']
                st.session_state.current_page = 'dashboard'
                st.rerun()
        
        if register_btn:
            st.session_state.current_page = 'register'
            st.rerun()

# --- Dashboard Page ---
def dashboard_page():
    user_data = get_user_data(st.session_state.user_id)
    d = user_data['details']

    st.title("📊 Dashboard")
    st.subheader("👤 Account Details")
    
    # Rank icon mapping (emoji fallback)
    rank_icons = {
        'Iron': '⚫',
        'Bronze': '🥉',
        'Silver': '🥈',
        'Gold': '🥇',
        'Platinum': '💎',
        'Diamond': '🔷',
        'Ascendant': '🟩',
        'Immortal': '🔴',
        'Radiant': '🌟',
        'Unranked': '❔',
    }
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Name:** {d['name']}")
        st.write(f"**Region:** {d['region']}")
        st.write(f"**Country:** {d['country']}")
        st.write(f"**Level:** {d['level']}")
    with col2:
        rank_value = d['rank'] if d['rank'] else 'Unranked'
        icon_path = os.path.join(os.path.dirname(__file__), "rank_icons", f"{rank_value.lower()}.png")
        if os.path.exists(icon_path):
            st.image(icon_path, width=40)
        else:
            icon = rank_icons.get(rank_value, '❔')
            st.write(icon)
        rank_line = rank_value
        if d.get('episode') or d.get('act'):
            rank_line += f" - Episode {d.get('episode','')} Act {d.get('act','')}"
        st.write(f"**Rank:** {rank_line}")
        st.write(f"**Registration date:** {d['registration_date']}")
        st.write(f"**Phone verified:** {'Yes' if d['phone_verified'] else 'No'}")
        st.write(f"**Email verified:** {'Yes' if d['email_verified'] else 'No'}")
    
    if not d['rank']:
        st.warning("Unranked")
    else:
        st.success("Ready for Competitive")
    # --- Scrape Skins Button ---
    if st.button("Scrape Valorant Bundles & Skins"):
        scrape_valorant_skins()
        st.success("Scraping complete! Data updated.")
    # --- Account Value Button ---
    if st.button("Show My Account Skin Value"):
        result = calculate_account_skin_value(st.session_state.user_id)
        st.info(f"Total Skin Value: {result['total_value_vp']} VP")
        st.write(result['details'])

    # User data link
    user_link = f"{st.get_option('server.address') or 'http://localhost:8501'}?user_id={st.session_state.user_id}"
    st.markdown(f"[🔗 View as Link]({user_link})  ")
    st.code(user_link, language='text')

# --- Store Page ---
def store_page():
    user_data = get_user_data(st.session_state.user_id)
    s = user_data['store']
    st.title("🛒 Store")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Valorant Points", s['valorant_points'])
    with col2:
        st.metric("Radiant Points", s['radiant_points'])
    with col3:
        st.metric("Kingdom Points", s['kingdom_points'])
    st.subheader("Available Skins")
    import sqlite3
    conn = sqlite3.connect('valorant_game.db')
    cursor = conn.cursor()
    cursor.execute('SELECT skin_name, value_vp FROM bundle_skins')
    skins = cursor.fetchall()
    for skin_name, value_vp in skins:
        col1, col2 = st.columns([3,1])
        with col1:
            st.write(f"{skin_name} - {value_vp if value_vp else 'N/A'} VP")
        with col2:
            if st.button(f"Buy {skin_name}"):
                success, msg = purchase_skin(st.session_state.user_id, skin_name)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
    st.subheader("Available Bundles")
    cursor.execute('SELECT id, bundle_name FROM bundles')
    bundles = cursor.fetchall()
    for bundle_id, bundle_name in bundles:
        cursor.execute('SELECT value_vp FROM bundle_skins WHERE bundle_id = ?', (bundle_id,))
        prices = [row[0] for row in cursor.fetchall() if row[0]]
        total_price = sum(prices)
        skin_count = len(prices)
        col1, col2 = st.columns([3,1])
        with col1:
            st.write(f"{bundle_name} - {skin_count} skins - {total_price} VP")
        with col2:
            if st.button(f"Buy Bundle {bundle_id}"):
                success, msg = purchase_bundle(st.session_state.user_id, bundle_id)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
    conn.close()

# --- Inventory Page ---
def inventory_page():
    user_data = get_user_data(st.session_state.user_id)
    inv = user_data['inventory']
    
    st.title("🎒 Inventory")
    
    # Item prices (only skins and battlepass count for total value)
    skin_value = 875  # Dummy value, can be updated later
    battlepass_value = 1000
    total_value = len(inv['skins']) * skin_value + len(inv['battlepass']) * battlepass_value
    st.markdown(f"<h4 style='color:#ff4655;'>Total Value: {total_value} VP</h4>", unsafe_allow_html=True)
    
    # Breakdown
    st.markdown("<b>Breakdown:</b>", unsafe_allow_html=True)
    st.write(f"Skins ({len(inv['skins'])}): {len(inv['skins']) * skin_value} VP")
    st.write(f"Battlepass ({len(inv['battlepass'])}): {len(inv['battlepass']) * battlepass_value} VP")
    st.write(f"Buddies ({len(inv['buddies'])}): -")
    st.write(f"Agents ({len(inv['agents'])}): -")
    st.write(f"Cards ({len(inv['cards'])}): -")
    st.write(f"Titles ({len(inv['titles'])}): -")
    
    # Export Data Button
    if st.button("⬇️ Export All Data (CSV)"):
        # Profile
        profile_df = pd.DataFrame([user_data['details']])
        # Inventory
        inventory_df = pd.DataFrame({
            'skins': [', '.join(inv['skins'])],
            'battlepass': [', '.join(inv['battlepass'])],
            'buddies': [', '.join(inv['buddies'])],
            'agents': [', '.join(inv['agents'])],
            'cards': [', '.join(inv['cards'])],
            'titles': [', '.join(inv['titles'])],
        })
        # Match History
        match_df = pd.DataFrame(user_data['match_history'])
        # Combine all
        with pd.ExcelWriter('user_export.xlsx') as writer:
            profile_df.to_excel(writer, sheet_name='Profile', index=False)
            inventory_df.to_excel(writer, sheet_name='Inventory', index=False)
            match_df.to_excel(writer, sheet_name='MatchHistory', index=False)
        with open('user_export.xlsx', 'rb') as f:
            st.download_button('Download Exported Data', f, file_name='user_export.xlsx')
    
    # Tabs ke naam ke sath count
    tab_names = [
        f"🔫 Skins ({len(inv['skins'])})",
        f"🎯 Battlepass ({len(inv['battlepass'])})",
        f"🐾 Buddies ({len(inv['buddies'])})",
        f"👤 Agents ({len(inv['agents'])})",
        f"🃏 Cards ({len(inv['cards'])})",
        f"🏆 Titles ({len(inv['titles'])})",
    ]
    tabs = st.tabs(tab_names)
    
    with tabs[0]:
        st.subheader("🔫 Skins")
        if inv['skins']:
            for skin in inv['skins']:
                st.write(f"🔸 {skin}")
        else:
            st.write("❌ No skins owned")
    
    with tabs[1]:
        st.subheader("🎯 Battlepass")
        if inv['battlepass']:
            for bp in inv['battlepass']:
                st.write(f"🔸 {bp}")
        else:
            st.write("❌ No battlepass owned")
    
    with tabs[2]:
        st.subheader("🐾 Buddies")
        if inv['buddies']:
            for buddy in inv['buddies']:
                st.write(f"🔸 {buddy}")
        else:
            st.write("❌ No buddies owned")
    
    with tabs[3]:
        st.subheader("👤 Agents")
        if inv['agents']:
            for agent in inv['agents']:
                st.write(f"🔸 {agent}")
        else:
            st.write("❌ No agents owned")
    
    with tabs[4]:
        st.subheader("🃏 Cards")
        if inv['cards']:
            for card in inv['cards']:
                st.write(f"🔸 {card}")
        else:
            st.write("❌ No cards owned")
    
    with tabs[5]:
        st.subheader("🏆 Titles")
        if inv['titles']:
            for title in inv['titles']:
                st.write(f"🔸 {title}")
        else:
            st.write("❌ No titles owned")

# --- Match History Page ---
def match_history_page():
    user_data = get_user_data(st.session_state.user_id)
    matches = user_data['match_history']
    
    st.title("📈 Match History")
    
    # Add new match form
    with st.expander("➕ Add New Match"):
        with st.form("add_match"):
            result = st.selectbox("🏆 Result", ["Win", "Loss", "Draw"])
            score = st.text_input("📊 Score (e.g., 13-7)")
            submitted = st.form_submit_button("➕ Add Match")
            
            if submitted and score:
                add_match_history(st.session_state.user_id, result, score)
                st.success("Match added!")
                st.rerun()
    
    # Display matches
    if matches:
        for match in matches:
            color = "green" if match['result'] == 'Win' else "red" if match['result'] == 'Loss' else "orange"
            st.markdown(f"""
            <div style=\"background: #1a232e; padding: 10px; border-radius: 5px; margin: 5px 0;\">
                <span style=\"color: {color}; font-weight: bold;\">{match['result']}</span> | 
                <span>{match['date']}</span> | 
                <span>{match['score']}</span> | 
                <a href=\"{match['link']}\" target=\"_blank\" style=\"color: #2196f3; font-weight: bold; text-decoration: underline;\">Link</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("No matches found")

# --- Profile Edit Page ---
def profile_edit_page():
    user_data = get_user_data(st.session_state.user_id)
    d = user_data['details']
    
    st.title("✏️ Edit Profile")
    
    with st.form("edit_profile"):
        name = st.text_input("Name", value=d['name'])
        region = st.selectbox("Region", ["NA", "EU", "AP", "KR", "BR", "LATAM"], index=["NA", "EU", "AP", "KR", "BR", "LATAM"].index(d['region']) if d['region'] in ["NA", "EU", "AP", "KR", "BR", "LATAM"] else 0)
        country = st.text_input("Country", value=d['country'])
        level = st.number_input("Level", min_value=1, value=d['level'])
        rank = st.selectbox("Rank", ["Unranked", "Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ascendant", "Immortal", "Radiant"], index=["Unranked", "Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ascendant", "Immortal", "Radiant"].index(d['rank']) if d['rank'] in ["Unranked", "Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ascendant", "Immortal", "Radiant"] else 0)
        episode = st.text_input("Episode", value=d.get('episode', ''))
        act = st.text_input("Act", value=d.get('act', ''))
        
        submitted = st.form_submit_button("Update Profile")
        
        if submitted:
            update_user_details(st.session_state.user_id, name=name, region=region, country=country, level=level, rank=rank, episode=episode, act=act)
            st.success("Profile updated successfully!")

# --- Bulk Import Page ---
def bulk_import_page():
    st.title("📥 Bulk Account Check")
    st.write("Upload a CSV file containing username and password columns.")
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
    if uploaded_file:
        import pandas as pd
        df = pd.read_csv(uploaded_file)
        if 'username' not in df.columns or 'password' not in df.columns:
            st.error("The CSV must have 'username' and 'password' columns!")
        else:
            st.write("### Results:")
            results = []
            for idx, row in df.iterrows():
                username = str(row['username']).strip()
                password = str(row['password']).strip()
                # Check if user exists
                from database import hash_password
                import sqlite3
                conn = sqlite3.connect('valorant_game.db')
                cursor = conn.cursor()
                cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
                user_row = cursor.fetchone()
                conn.close()
                status = ""
                user_link = ""
                if not user_row:
                    status = "User Not Found"
                else:
                    user_id, stored_hash = user_row
                    if stored_hash != hash_password(password):
                        status = "Password Incorrect"
                    else:
                        user_data = verify_user(username, None, password)
                        if user_data['status'] == 'locked':
                            status = "Account Locked"
                        elif user_data['status'] == 'banned':
                            if user_data['ban_type'] == 'permanent':
                                status = "Permanently Banned"
                            else:
                                status = f"Suspended until {user_data['suspension_end']}"
                        elif not user_data['email_verified']:
                            status = "Email Verification Required"
                        else:
                            details = get_user_data(user_data['user_id'])['details']
                            inv = get_user_data(user_data['user_id'])['inventory']
                            if not details['rank'] or details['rank'].lower() == 'unranked':
                                status = "Unranked Account"
                            elif details['rank']:
                                status = f"Rank Ready: {details['rank']}"
                            if inv['skins']:
                                status += f" | Skins: {', '.join(inv['skins'])}"
                            user_link = f"{st.get_option('server.address') or 'http://localhost:8501'}?user_id={user_data['user_id']}"
                results.append({
                    "username": username,
                    "status": status,
                    "user_link": user_link
                })
            st.dataframe(pd.DataFrame(results))
            for r in results:
                if r['user_link']:
                    st.markdown(f"[{r['username']} Data Link]({r['user_link']})")

# --- Bulk Registration Page ---
def bulk_registration_page():
    st.title("📝 Bulk Registration")
    st.write("Upload a CSV file with columns: username, email, password, name, region, country. Each row will be registered as a new user. Password must be plain text.")
    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"], key="bulk_reg")
    if uploaded_file:
        import pandas as pd
        df = pd.read_csv(uploaded_file)
        required_cols = ["username", "email", "password", "name", "region", "country"]
        if not all(col in df.columns for col in required_cols):
            st.error("CSV must have these columns: username, email, password, name, region, country")
        else:
            st.write("### Registration Results:")
            results = []
            for idx, row in df.iterrows():
                try:
                    success = create_user(
                        str(row['username']).strip(),
                        str(row['email']).strip(),
                        str(row['password']).strip(),
                        str(row['name']).strip(),
                        str(row['region']).strip(),
                        str(row['country']).strip()
                    )
                    if success:
                        results.append({"username": row['username'], "status": "Registered"})
                    else:
                        results.append({"username": row['username'], "status": "Already Exists/Fail"})
                except Exception as e:
                    results.append({"username": row.get('username', ''), "status": f"Error: {e}"})
            st.dataframe(results)
            st.success("Bulk registration process completed. Now you can login with these accounts.")

# Skins se related imports, function calls, aur UI hata diye gaye hain

def user_data_view_page():
    query_params = st.query_params
    user_id = query_params.get('user_id', [None])[0]
    if not user_id:
        st.error('No user_id provided in link.')
        return
    try:
        user_id = int(user_id)
    except ValueError:
        st.error('Invalid user_id.')
        return
    from database import get_user_data
    user_data = get_user_data(user_id)
    if not user_data or not user_data['details']['name']:
        st.error('User not found.')
        return
    d = user_data['details']
    st.title(f"👤 {d['name']} (User ID: {user_id})")
    st.write(f"**Region:** {d['region']}")
    st.write(f"**Country:** {d['country']}")
    st.write(f"**Level:** {d['level']}")
    st.write(f"**Rank:** {d['rank']}")
    st.write(f"**Registration date:** {d['registration_date']}")
    st.write(f"**Phone verified:** {'Yes' if d['phone_verified'] else 'No'}")
    st.write(f"**Email verified:** {'Yes' if d['email_verified'] else 'No'}")
    st.markdown('---')
    st.header('Inventory')
    inv = user_data['inventory']
    st.write(f"Skins: {', '.join(inv['skins']) if inv['skins'] else 'None'}")
    st.write(f"Battlepass: {', '.join(inv['battlepass']) if inv['battlepass'] else 'None'}")
    st.write(f"Buddies: {', '.join(inv['buddies']) if inv['buddies'] else 'None'}")
    st.write(f"Agents: {', '.join(inv['agents']) if inv['agents'] else 'None'}")
    st.write(f"Cards: {', '.join(inv['cards']) if inv['cards'] else 'None'}")
    st.write(f"Titles: {', '.join(inv['titles']) if inv['titles'] else 'None'}")
    st.markdown('---')
    st.header('Match History')
    matches = user_data['match_history']
    if matches:
        for match in matches:
            st.write(f"{match['date']} | {match['result']} | {match['score']} | {match['link']}")
    else:
        st.write('No matches found.')

# --- Main App ---
def main():
    # Skins se related koi bhi initialization ya function call nahi hai
    query_params = st.query_params
    if 'user_id' in query_params:
        user_data_view_page()
        return
    if not st.session_state.logged_in:
        if st.session_state.current_page == 'register':
            registration_page()
        else:
            login_page()
    else:
        # Modern Sidebar navigation with Dracula theme
        st.sidebar.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #bd93f9; margin-bottom: 5px;">🎮</h2>
            <h3 style="color: #f8f8f2; margin: 0;">Valorant Hub</h3>
        </div>
        """, unsafe_allow_html=True)
        
        menu = [
            "📊 Dashboard", "🛒 Store", "🎒 Inventory", "📈 Match History",
            "✏️ Edit Profile", "📝 Bulk Registration", "📥 Bulk Account Check", "🚪 Logout"
        ]
        choice = st.sidebar.selectbox("🧭 Navigation", menu)
        
        if choice == "📊 Dashboard":
            dashboard_page()
        elif choice == "🛒 Store":
            store_page()
        elif choice == "🎒 Inventory":
            inventory_page()
        elif choice == "📈 Match History":
            match_history_page()
        elif choice == "✏️ Edit Profile":
            profile_edit_page()
        elif choice == "📝 Bulk Registration":
            bulk_registration_page()
        elif choice == "📥 Bulk Account Check":
            bulk_import_page()
        elif choice == "🚪 Logout":
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.current_page = 'login'
            st.rerun()

if __name__ == "__main__":
    main() 