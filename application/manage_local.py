import os
import sys
from dotenv import load_dotenv
from unipath import Path
from django.core.management import execute_from_command_line

# Load environment variables from a .env file if it exists
BASE_DIR = Path(__file__).ancestor(2)  # Reference the project root
common_env_path = BASE_DIR.child('common.env')
local_env_path = BASE_DIR.child('local.env')

if os.path.exists(common_env_path):
    if (load_dotenv(common_env_path)):
        print(f"Loaded common.env from {common_env_path}")

if os.path.exists(local_env_path):
    if (load_dotenv(local_env_path, override=True)):
        print(f"Loaded local.env from {local_env_path}")

os.environ['DJANGO_SETTINGS_MODULE'] = 'dreamsuite.settings.local'

execute_from_command_line(sys.argv)
