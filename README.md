# Valorant-Style Game Account System (Streamlit + SQLite)

## Features
- **Real Database:** SQLite database with all user data
- **User Registration:** New users can register accounts
- **Login System:** All error/status messages (Incorrect Password, Ban, Suspension, etc.)
- **Dashboard:** Account details (Name, Region, Country, Level, Rank, etc.)
- **Store:** Valorant, Radiant, Kingdom points
- **Inventory:** Skins, Battlepass, Buddies, Agents, Cards, Titles
- **Match History:** Add and view match history
- **Profile Edit:** Update user details
- **Valorant-inspired modern UI**

## Demo Login
- **Username:** demo
- **Email:** demo@valorant.com
- **Password:** valorant123

## How to Run
1. Python 3.8+ install karen
2. Terminal open karen aur project folder me aaen:
   ```bash
   cd sattar
   pip install -r requirements.txt
   streamlit run app_with_db.py
   ```
3. Browser me open ho jayega: [http://localhost:8501](http://localhost:8501)

## Database Features
- **User Management:** Registration, login, profile management
- **Data Persistence:** All data saved in SQLite database
- **Real-time Updates:** Changes reflect immediately
- **Scalable:** Easy to add more users and features

## Files
- `app_with_db.py` - Main application with database
- `database.py` - Database functions and setup
- `valorant_game.db` - SQLite database (auto-created)
- `requirements.txt` - Python dependencies

## Customization
- Database schema easily modifiable in `database.py`
- UI customization in `app_with_db.py`
- Add more features by extending database functions

---
**Production Ready with Real Database!** 