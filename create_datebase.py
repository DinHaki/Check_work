import sqlite3 as sql


with sql.connect('datebase.db') as db:
    cursor = db.cursor()

    cursor.executescript("""
    
    DROP TABLE IF EXISTS Users;
    DROP TABLE IF EXISTS Comments;
    DROP TABLE IF EXISTS Lots;
    DROP TABLE IF EXISTS History_Lots;


    CREATE TABLE IF NOT EXISTS Users(
        id INTEGER PRIMARY KEY,
        user_name TEXT, 
        user_type TEXT CHECK(user_type IN ('admin', 's_admin', 'blocked', 'user', 'support')) NOT NULL DEFAULT 'user',
        balance INREGER CHECK(balance >= 0)  DEFAULT 0.0 
    );

    CREATE TABLE IF NOT EXISTS Comments(                 
        id INTEGER PRIMARY KEY,
        user_id_sender INTEGER,
        user_id_suspect INTEGER,
        content TEXT(300),

        is_approved BOOLEAN DEFAULT 0,
        
        messages_id_report INTEGER DEFAULT 0                          
    );
                         
    CREATE TABLE IF NOT EXISTS Lots(                    
        id INTEGER PRIMARY KEY,
        
        name TEXT(100),
        descriprion TEXT(100),
        price_start REAL DEFAULT 0.0 CHECK(price_start >= 0),
        address TEXT,
        media_ids TEXT,                                  
        id_seller INTEGER,
        
        messages_ids TEXT DEFAULT NONE,
        
        contract_fid INTEGER DEFAULT 0,
        is_approved BOOLEAN DEFAULT 0,
        
        main_group_message_id INTEGER DEFAULT 0,
        main_group_media_messages_ids TEXT,
                         
        FOREIGN KEY (id_seller) REFERENCES Users(id)
    );
    
    CREATE TABLE IF NOT EXISTS History_Lots(
        id INTEGER PRIMARY KEY,

        user_id INTEGER,
        lot_id INTEGER,
        
        price REAL DEFAULT 0.0 CHECK(price >= 0),
                         
        FOREIGN KEY (user_id) REFERENCES Users(id),
        FOREIGN KEY (lot_id) REFERENCES Lots(id)
    );
    
    """)

print('ready')
