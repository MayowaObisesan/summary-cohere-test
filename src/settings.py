# Blessed - Mayowa Obisesan
# Summary Settings File
# March 4, 2023.
import os

from dotenv import load_dotenv

load_dotenv()

summary_allowed_origins = [
    "http://createsummary.com",
    "http://www.createsummary.com",
    "http://api.createsummary.com",
    "https://createsummary.com",
    "https://createsummary.com/summary",
    "https://createsummary.com/summary/search",
    "https://www.createsummary.com",
    "https://api.createsummary.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5000",
    "http://localhost:4000",
    "*",
]

# COHERE_API_KEY
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# GOOGLE API CONFIGURATION - MAY 29, 2023.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
NUMBER_SEARCH_RESULT = 10

# DICTDATABASE CONFIGURATION - MARCH 22, 2022.
DDB_STORAGE_DIRECTORY = "./ddb_storage"
DDB_USE_COMPRESSION = False
DDB_INDENT = "\t"  # int for the number of spaces or None for no indentation.
DDB_USE_ORJSON = True
DDB_SLEEP_TIMEOUT = 0.001  # 1ms, default value

# DETA BASE CONFIGURATION - March 30, 2022.
QUERY_DATA_EXPIRE_IN = 3600  # Expiration time in seconds

# VERCEL ROUTES CONFIGURATION
# ===========================
# "builds": [
#     {
#         "src": "main.py", "use": "@vercel/python"
#     }
# ],
# "routes": [
#     {
#         "src": "/(.*)", "dest": "main.py"
#     }
# ],
# 	"headers": [
#     {
#       "source": "/(.*)",
#       "headers": [
#         { "key": "Access-Control-Allow-Credentials", "value": "true" },
#         { "key": "Access-Control-Allow-Origin", "value": "*" },
#         { "key": "Access-Control-Allow-Methods", "value": "GET,OPTIONS,PATCH,DELETE,POST,PUT" },
#         { "key": "Access-Control-Allow-Headers", "value": "X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version" }
#       ]
#     }
#   ]
