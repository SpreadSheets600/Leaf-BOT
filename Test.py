import sqlite3
import re

# Connect to the target SQLite database
target_conn = sqlite3.connect('target.db')  # Change 'target.db' to your target database file
target_cursor = target_conn.cursor()

# Read the MySQL dump file
sql_file_path = 's67_LoginSequrity.sql'  # Path to your MySQL dump file
with open(sql_file_path, 'r') as file:
    sql_script = file.read()

# Preprocess the dump file:
# 1. Remove MySQL-specific 'AUTO_INCREMENT'
sql_script = sql_script.replace('AUTO_INCREMENT', '')

# 2. Replace MySQL data types with SQLite-compatible types
sql_script = sql_script.replace('INT', 'INTEGER')  # Replace INT with INTEGER
sql_script = re.sub(r'VARCHAR\([0-9]+\)', 'TEXT', sql_script)  # Replace VARCHAR(x) with TEXT

# 3. Remove MySQL-specific engine definitions and charset
sql_script = re.sub(r'ENGINE=\w+', '', sql_script)  # Remove ENGINE=InnoDB or similar
sql_script = re.sub(r'DEFAULT CHARSET=\w+', '', sql_script)  # Remove DEFAULT CHARSET=utf8mb4

# 4. Replace MySQL-specific `DEFAULT CURRENT_TIMESTAMP` with SQLite-compatible syntax
sql_script = sql_script.replace('DEFAULT CURRENT_TIMESTAMP', "DEFAULT (strftime('%Y-%m-%d %H:%M:%f', 'now'))")

# 5. Replace DEFAULT TRUE/FALSE with DEFAULT 1/0 for booleans
sql_script = sql_script.replace('DEFAULT TRUE', 'DEFAULT 1')
sql_script = sql_script.replace('DEFAULT FALSE', 'DEFAULT 0')

# 6. Remove backticks used for quoting identifiers in MySQL
sql_script = sql_script.replace('`', '')

# 7. Remove MySQL-specific COLLATE clauses
sql_script = re.sub(r'COLLATE [a-zA-Z0-9_]+', '', sql_script)

# Execute the SQL script on the target database
try:
    target_cursor.executescript(sql_script)
    target_conn.commit()
    print("Data migration completed successfully!")
except sqlite3.Error as e:
    print(f"An error occurred: {e}")

# Close the connection
target_conn.close()
