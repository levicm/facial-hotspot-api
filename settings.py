import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL').replace('postgres://', 'postgresql://')
print(DATABASE_URL )
