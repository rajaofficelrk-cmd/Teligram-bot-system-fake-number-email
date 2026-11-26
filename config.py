import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN', '').strip()
OWNER_ID = int(os.getenv('OWNER_ID', '0') or 0)
BOT_NAME = os.getenv('BOT_NAME', 'RK RAJA ULTIMATE XWD')
DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/rk_raja.db')
AI_API_KEY = os.getenv('AI_API_KEY', '').strip()
AI_BASE_URL = os.getenv('AI_BASE_URL', 'https://api.openai.com/v1').rstrip('/')
AI_MODEL = os.getenv('AI_MODEL', 'gpt-4o-mini')
