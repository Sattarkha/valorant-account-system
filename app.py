import streamlit as st
from datetime import datetime
from database import create_user, verify_user, get_user_data, auto_verify_email, add_match_history, update_user_details
import database as db
import pandas as pd
import os

# Initialize database
db.init_database()
db.create_demo_user()

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

# --- Inventory Page ---
def inventory_page():
    user_data = get_user_data(st.session_state.user_id)
    inv = user_data['inventory']
    
    st.title("🎒 Inventory")
    
    # Item prices
    prices = {
        'skins': 875,
        'battlepass': 1000,
        'buddies': 475,
        'agents': 1000,
        'cards': 375,
        'titles': 200,
    }
    # Total value calculation
    total_value = (
        len(inv['skins']) * prices['skins'] +
        len(inv['battlepass']) * prices['battlepass'] +
        len(inv['buddies']) * prices['buddies'] +
        len(inv['agents']) * prices['agents'] +
        len(inv['cards']) * prices['cards'] +
        len(inv['titles']) * prices['titles']
    )
    st.markdown(f"<h4 style='color:#ff4655;'>Total Value: {total_value} VP</h4>", unsafe_allow_html=True)
    
    # Breakdown
    st.markdown("<b>Breakdown:</b>", unsafe_allow_html=True)
    st.write(f"Skins ({len(inv['skins'])}): {len(inv['skins']) * prices['skins']} VP")
    st.write(f"Battlepass ({len(inv['battlepass'])}): {len(inv['battlepass']) * prices['battlepass']} VP")
    st.write(f"Buddies ({len(inv['buddies'])}): {len(inv['buddies']) * prices['buddies']} VP")
    st.write(f"Agents ({len(inv['agents'])}): {len(inv['agents']) * prices['agents']} VP")
    st.write(f"Cards ({len(inv['cards'])}): {len(inv['cards']) * prices['cards']} VP")
    st.write(f"Titles ({len(inv['titles'])}): {len(inv['titles']) * prices['titles']} VP")
    
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
    st.title("📥 Bulk Import Users")
    st.write("Ek CSV file upload karein jisme username aur password columns hoon.")
    
    uploaded_file = st.file_uploader("CSV File Upload karein", type=["csv"])
    if uploaded_file:
        import pandas as pd
        df = pd.read_csv(uploaded_file)
        if 'username' not in df.columns or 'password' not in df.columns:
            st.error("CSV me 'username' aur 'password' columns lazmi hain!")
        else:
            st.write("### Results:")
            results = []
            for idx, row in df.iterrows():
                user_data = verify_user(row['username'], None, row['password'])
                if user_data:
                    results.append({"username": row['username'], "status": "Success"})
                else:
                    results.append({"username": row['username'], "status": "Fail"})
            st.dataframe(results)

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

# --- Main App ---
def main():
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
        
        menu = ["📊 Dashboard", "🛒 Store", "🎒 Inventory", "📈 Match History", "✏️ Edit Profile", "📝 Bulk Registration", "🚪 Logout"]
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
        elif choice == "🚪 Logout":
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.current_page = 'login'
            st.rerun()

if __name__ == "__main__":
    main() 