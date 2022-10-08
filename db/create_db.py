import os
import sqlite3

db_name = 'ongoing.db'
schema_create = 'create_tables.sql'

db_exists = not os.path.exists(db_name)

with sqlite3.connect(db_name) as conn:
	if db_exists:
		print('Creating schema')
		with open(schema_create, 'rt') as file:
			schema = file.read()
		conn.executescript(schema)
		
		print('Creating done')	
	else:
		print('DB already exists.')