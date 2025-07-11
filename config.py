from dotenv import load_dotenv
import os

load_dotenv()

# BOT
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Google Drive
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")     # id folder drive
SERVICE_ACCOUNT_PATH = os.getenv("SERVICE_ACCOUNT_PATH")

# ────────────── User ID ──────────────
ALLOWED_USER_IDS = {
    #1825371102, 

}

# ────────────── ID Admin ──────────────
ADMIN_IDS = {
    #1825371102, 
}
