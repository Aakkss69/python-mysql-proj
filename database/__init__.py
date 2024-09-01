import sys

print("Initializing database")

# Check Python version
required_version = (3, 6)  # Specify your minimum required Python version
current_version = sys.version_info

if current_version >= required_version:
    print(f"Python version: {current_version.major}.{current_version.minor} - OK")
else:
    print(f"Python version: {current_version.major}.{current_version.minor} - ERROR: Python {required_version[0]}.{required_version[1]} or higher is required.")
    sys.exit(1)

# Check necessary imports
try:
    import mysql.connector
    print("mysql.connector import - OK")
except ImportError as e:
    print(f"mysql.connector import - ERROR: {e}")
    sys.exit(1)

try:
    from .config import DATABASE_CONFIG
    print("config import - OK")
except ImportError as e:
    print(f"config import - ERROR: {e}")
    sys.exit(1)

# Add any additional import checks here if needed
