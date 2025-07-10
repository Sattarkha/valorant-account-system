import streamlit as st
from datetime import datetime
import database as db
from scrape_valorant_skins import scrape_valorant_skins
from database import calculate_account_skin_value

# Initialize database
db.init_database()
db.create_demo_user()

# --- Custom CSS for Valorant Theme ---
VALORANT_CSS = """
<style>
body, .stApp {
    background-color: #0f1923;
    color: #fff;
}
.sidebar .sidebar-content {
    background: #1a232e;
}
/* Button styling */
.stButton>button {
    background: linear-gradient(90deg, #ff4655, #ff6b7a) !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: bold !important;
    border: none !important;
    padding: 8px 16px !important;
    box-shadow: 0 4px 8px rgba(255, 70, 85, 0.3) !important;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #ff6b7a, #ff4655) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 12px rgba(255, 70, 85, 0.4) !important;
}
/* Form submit button */
.stFormSubmitButton>button {
    background: linear-gradient(90deg, #00d4aa, #00b894) !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: bold !important;
    border: none !important;
    padding: 10px 20px !important;
    box-shadow: 0 4px 8px rgba(0, 212, 170, 0.3) !important;
}
.stFormSubmitButton>button:hover {
    background: linear-gradient(90deg, #00b894, #00d4aa) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 12px rgba(0, 212, 170, 0.4) !important;
}
/* Input fields */
.stTextInput>div>div>input {
    background: #1a232e !important;
    color: #fff !important;
    border: 2px solid #2a3441 !important;
    border-radius: 8px !important;
}
.stTextInput>div>div>input:focus {
    border-color: #ff4655 !important;
    box-shadow: 0 0 0 2px rgba(255, 70, 85, 0.2) !important;
}
/* Input label headings white */
label, .css-1c7y2kd, .stTextInput label, .stTextInput>label, .stTextInput label span {
    color: #fff !important;
    font-weight: 600 !important;
}
/* Selectbox styling */
.stSelectbox>div>div>select {
    background: #1a232e !important;
    color: #fff !important;
    border: 2px solid #2a3441 !important;
    border-radius: 8px !important;
}
/* Number input */
.stNumberInput>div>div>input {
    background: #1a232e !important;
    color: #fff !important;
    border: 2px solid #2a3441 !important;
    border-radius: 8px !important;
}
/* Sidebar selectbox */
.sidebar .stSelectbox>div>div>select {
    background: #2a3441 !important;
    color: #fff !important;
    border: 2px solid #3a4451 !important;
    border-radius: 8px !important;
}
/* Success/Error messages */
.stAlert {
    border-radius: 8px !important;
    border: none !important;
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
                success = db.create_user(username, email, password, name, region, country)
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
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            login_btn = st.form_submit_button("Login")
        with col2:
            register_btn = st.form_submit_button("Register")
        
        if login_btn:
            user_data = db.verify_user(username, email, password)
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
                db.auto_verify_email(user_data['user_id'])
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
    user_data = db.get_user_data(st.session_state.user_id)
    d = user_data['details']
    
    st.title("📊 Dashboard")
    st.subheader("👤 Account Details")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Name:** {d['name']}")
        st.write(f"**Region:** {d['region']}")
        st.write(f"**Country:** {d['country']}")
        st.write(f"**Level:** {d['level']}")
    with col2:
        st.write(f"**Rank:** {d['rank']}")
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

# --- Store Page ---
def store_page():
    user_data = db.get_user_data(st.session_state.user_id)
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
    user_data = db.get_user_data(st.session_state.user_id)
    inv = user_data['inventory']
    
    st.title("🎒 Inventory")
    
    tabs = st.tabs(["🔫 Skins", "🎯 Battlepass", "🐾 Buddies", "👤 Agents", "🃏 Cards", "🏆 Titles"])
    
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
    user_data = db.get_user_data(st.session_state.user_id)
    matches = user_data['match_history']
    
    st.title("📈 Match History")
    
    # Add new match form
    with st.expander("➕ Add New Match"):
        with st.form("add_match"):
            result = st.selectbox("🏆 Result", ["Win", "Loss", "Draw"])
            score = st.text_input("📊 Score (e.g., 13-7)")
            submitted = st.form_submit_button("➕ Add Match")
            
            if submitted and score:
                db.add_match_history(st.session_state.user_id, result, score)
                st.success("Match added!")
                st.rerun()
    
    # Display matches
    if matches:
        for match in matches:
            color = "green" if match['result'] == 'Win' else "red" if match['result'] == 'Loss' else "orange"
            st.markdown(f"""
            <div style="background: #1a232e; padding: 10px; border-radius: 5px; margin: 5px 0;">
                <span style="color: {color}; font-weight: bold;">{match['result']}</span> | 
                <span>{match['date']}</span> | 
                <span>{match['score']}</span> | 
                <a href="{match['link']}" target="_blank">Link</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("No matches found")

# --- Profile Edit Page ---
def profile_edit_page():
    user_data = db.get_user_data(st.session_state.user_id)
    d = user_data['details']
    
    st.title("✏️ Edit Profile")
    
    with st.form("edit_profile"):
        name = st.text_input("Name", value=d['name'])
        region = st.selectbox("Region", ["NA", "EU", "AP", "KR", "BR", "LATAM"], index=["NA", "EU", "AP", "KR", "BR", "LATAM"].index(d['region']) if d['region'] in ["NA", "EU", "AP", "KR", "BR", "LATAM"] else 0)
        country = st.text_input("Country", value=d['country'])
        level = st.number_input("Level", min_value=1, value=d['level'])
        rank = st.selectbox("Rank", ["Unranked", "Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ascendant", "Immortal", "Radiant"], index=["Unranked", "Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ascendant", "Immortal", "Radiant"].index(d['rank']) if d['rank'] in ["Unranked", "Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ascendant", "Immortal", "Radiant"] else 0)
        
        submitted = st.form_submit_button("Update Profile")
        
        if submitted:
            db.update_user_details(st.session_state.user_id, name=name, region=region, country=country, level=level, rank=rank)
            st.success("Profile updated successfully!")

# --- Main App ---
def main():
    if not st.session_state.logged_in:
        if st.session_state.current_page == 'register':
            registration_page()
        else:
            login_page()
    else:
        # Sidebar navigation
        st.sidebar.title("🧭 Navigation")
        menu = ["📊 Dashboard", "🛒 Store", "🎒 Inventory", "📈 Match History", "✏️ Edit Profile", "🚪 Logout"]
        choice = st.sidebar.selectbox("📋 Menu", menu)
        
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
        elif choice == "🚪 Logout":
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.current_page = 'login'
            st.rerun()

if __name__ == "__main__":
    main() 