import os
import sys
import pandas as pd
from dotenv import load_dotenv
import mysql.connector
load_dotenv(override=True)
basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(basedir)

class InitMySql:
    def __init__(self):
        host_name = os.getenv('MYSQL_HOST', 'localhost')
        user_name = os.getenv('MYSQL_USER', 'root')
        user_password = os.getenv('MYSQL_PASSWORD')
        db_name = os.getenv('MYSQL_NAME', 'swastik_test')
        self.connection_pool = self.connect_to_db(host_name, user_name, user_password, db_name)
        self.file_path = os.path.join(basedir, 'data')
        print(f"File path: {self.file_path}")
        os.makedirs(self.file_path, exist_ok=True)

    def run_all(self):
        """Run all the methods in the class to initialize the MySQL database.
        step1: create the swastik_test database in init method
        step2: create the table from csv file and load the data within project
        step3: create the meta table to store the metadata of the tables
        step4: create a scheduled event in MySQL to update the meta table automatically when new table detected
        step5: we can test with adding new table to database and check if metatable is updated automatically
        """
        try:
            # step 1 initialization
            connection = self.connection_pool.get_connection()
            cursor = connection.cursor()
            # step 2 populate the new created database with table and data
            self.create_table_from_csv(connection, f'{self.file_path}/retailsales.csv', 'test_retailsales')
            # step 3 create the meta table to store the metadata of the tables
            self.create_meta_table(connection, 'test_database_meta')
            # step 4 create a scheduled event in MySQL to update the meta table automatically when new table detected
            script_dir = os.path.dirname(__file__)  
            sql_file_path = os.path.join(script_dir, 'manage_metadata.sql')
            with open(sql_file_path, 'r') as file:
                create_event_sql = file.read()
                cursor.execute("SHOW EVENTS WHERE Name = 'UpdateMetadataForNewTables';")
                event_exists = cursor.fetchone()
                if event_exists:
                    print(f"The event UpdateMetadataForNewTables exists.")
                else:
                    print("Creating new event... ")
                    cursor.execute(create_event_sql)                    
                
                connection.commit()

            # step 5 test
            # self.create_table_from_csv(connection, f'{self.file_path}/retailsales_new.csv', 'test_new_table')
            cursor.execute("SELECT * FROM test_database_meta")
            print(cursor.fetchall())

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close() 

    def connect_to_db(self, host_name, user_name, user_password, db_name):
        try:
            connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password
            )
            cursor = connection.cursor()
            
            cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
            database_exists = cursor.fetchone()            
            if not database_exists:
                cursor.execute(f"CREATE DATABASE {db_name}")
                print(f"Database {db_name} created successfully.")
            
            cursor.close()
            connection.close()
            
            connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="mypool",
                pool_size=5,
                host=host_name,
                user=user_name,
                passwd=user_password,
                database=db_name
            )
            print("Connection pool to MySQL DB successful")
            return connection_pool
        except mysql.connector.Error as e:
            print(f"The error '{e}' occurred")
            return None
        
    def create_table_from_csv(self, connection, csv_file_path, table_name):
        df = pd.read_csv(csv_file_path)
        headers = df.columns
        print(f"Headers: {headers}")

        cursor = connection.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}'")
        if cursor.fetchone()[0] == 0:
            # Table does not exist, create table and insert data
            column_definitions = ", ".join([f"`{header}` VARCHAR(255)" for header in headers])
            create_table_query = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({column_definitions});"
            cursor.execute(create_table_query)
            connection.commit()
            print(f"Table '{table_name}' created successfully")

            # Replace NaN values with None (which translates to NULL in SQL)
            df = df.where(pd.notnull(df), None)

            placeholders = ", ".join(["%s"] * len(headers))
            insert_query = f"INSERT INTO `{table_name}` ({', '.join([f'`{header}`' for header in headers])}) VALUES ({placeholders})"
            for row in df.itertuples(index=False, name=None):  
                cursor.execute(insert_query, row)
            connection.commit()
            print(f"Data inserted into '{table_name}' successfully")
        else:
            print(f"Table '{table_name}' already exists. Skipping creation and data insertion.")

    def create_meta_table(self, connection, meta_table_name):
        cursor = connection.cursor()
        check_table_exists_query = f"""
        SELECT COUNT(*)
        FROM information_schema.tables 
        WHERE table_name = '{meta_table_name}';
        """
        cursor.execute(check_table_exists_query)
        if cursor.fetchone()[0] == 0:
            create_meta_query = f"""
            CREATE TABLE IF NOT EXISTS {meta_table_name} (
                table_name VARCHAR(255),
                column_name VARCHAR(255),
                data_type VARCHAR(255),
                data_length INT,
                nullable BOOLEAN,
                default_value VARCHAR(255),
                is_primary_key BOOLEAN,
                is_unique BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            );"""
            cursor.execute(create_meta_query)   
            connection.commit()
            print(f"Meta table '{meta_table_name}' created successfully")
            # Populate the meta table with metadata of all tables
            self.populate_meta_table(connection, meta_table_name)
        else:
            print(f"Meta table '{meta_table_name}' already exists. Skipping creation and data insertion.")

    def populate_meta_table(self, connection, meta_table_name):
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        for table in tables:
            if table[0] == meta_table_name:
                continue

            cursor.execute(f"DESCRIBE {table[0]}")
            columns = cursor.fetchall()

            for column in columns:
                column_name = column[0]
                data_type = column[1]
                nullable = column[2] == 'YES'
                default_value = column[4]
                is_primary_key = column[3] == 'PRI'
                is_unique = False

                data_length = None
                if '(' in data_type:
                    data_type, length_str = data_type.split('(')
                    data_length = int(length_str.rstrip(')'))

                insert_query = f"""
                INSERT INTO {meta_table_name} (table_name, column_name, data_type, data_length, nullable, default_value, is_primary_key, is_unique)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (table[0], column_name, data_type, data_length, nullable, default_value, is_primary_key, is_unique))

        connection.commit()
        print("Metadata populated successfully")


InitMySql().run_all()