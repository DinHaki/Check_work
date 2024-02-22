import sqlite3


class DataBase:
    def __init__(self, db_file):
        self.db_file = db_file

    def is_user_exists(self, user_id):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()
            return bool(cursor.execute(f'SELECT id FROM Users WHERE id={user_id}').fetchall())
        
        except Exception as e:
            print(f"Произошла ошибка: {e}")
    
    def is_user_exists_by_name(self, user_name):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()
            return bool(cursor.execute(f'SELECT id FROM Users WHERE user_name="{user_name}"').fetchall())
        
        except Exception as e:
            print(f"Произошла ошибка: {e}")
    
    def add_user(self, user_id, user_name):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()

            if not self.is_user_exists(user_id):
                cursor.execute(f'INSERT INTO Users (id, user_name) VALUES ({user_id}, "{user_name}")')
                cursor.execute("COMMIT")
        
        except Exception as e:
            print(f"Произошла ошибка: {e}")
        
    def get_user_type(self, user_id):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()
        
            if self.is_user_exists(user_id):
                return cursor.execute(f'SELECT user_type FROM Users WHERE id={user_id}').fetchall()[0][0]
            else:
                return 'not found'

        
        except Exception as e:
            print(f"Произошла ошибка: {e}")
    
    def get_user_name(self, user_id):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()
        
            if self.is_user_exists(user_id):
                return cursor.execute(f'SELECT user_name FROM Users WHERE id={user_id}').fetchall()[0][0]
            else:
                return 'not found'

        
        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def change_user_type(self, user_name, user_type):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()
            
            cursor.execute(f'UPDATE Users SET user_type="{user_type}" WHERE user_name="{user_name}"')
            cursor.execute("COMMIT")
            
        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def get_user_info(self, user_name):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()
            
            return cursor.execute(f'SELECT * FROM Users WHERE user_name="{user_name}"').fetchone()
        
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return -1



    def create_lot(self, name, descriprion, price_start, address, media_ids, id_seller):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()
            
            id_new = cursor.execute(f'SELECT MAX(id) FROM lots').fetchone()[0]
            if id_new:
                id_new += 1
            else:
                id_new = 1

            cursor.execute(f'INSERT INTO Lots (id, name, descriprion, price_start, address, media_ids, id_seller)' +
                           f'VALUES ({id_new}, "{name}", "{descriprion}", {price_start}, "{address}", "{media_ids}", {id_seller})')
            cursor.execute("COMMIT")
            return id_new
        
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return -1
    
    def fill_lot_messages_ids(self, lot_id, messages_ids):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()
            
            cursor.execute(f'UPDATE Lots SET messages_ids = "{" ".join(map(str, messages_ids))}" WHERE id={lot_id}')
            cursor.execute("COMMIT")
        
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return -1

    def fill_lot_contract_fid(self, lot_id, contract_fid):
        pass
        # TODO: release

    def get_messages_ids(self, lot_id):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()
            
            return list(map(int, cursor.execute(f'SELECT messages_ids FROM Lots WHERE id={lot_id}').fetchone()[0].split()))
        
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return -1

    def set_lot_is_approved(self, lot_id, is_approved):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()
            
            cursor.execute(f'UPDATE Lots SET is_approved = {int(is_approved)} WHERE id={lot_id}')
            cursor.execute("COMMIT")
        
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return -1

    def get_lot_info(self, lot_id):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()
            
            return cursor.execute(f'SELECT * FROM Lots WHERE id={lot_id}').fetchone()
        
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return -1
    
    def fill_lot_main_group_message_id(self, lot_id, main_group_message_id):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()
            
            cursor.execute(f'UPDATE Lots SET main_group_message_id = {main_group_message_id} WHERE id={lot_id}')
            cursor.execute("COMMIT")
        
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return -1

    def fill_lot_main_group_media_messages_ids(self, lot_id, main_group_media_messages_ids):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()
            
            cursor.execute(f'UPDATE Lots SET main_group_media_messages_ids = "{main_group_media_messages_ids}" WHERE id={lot_id}')
            cursor.execute("COMMIT")
        
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return -1



    def add_bet(self, user_id, lot_id, price):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()

            cursor.execute(f'INSERT INTO History_Lots (user_id, lot_id, price) VALUES ({user_id}, {lot_id}, {price})')
            cursor.execute("COMMIT")
        
        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def get_max_bet(self, lot_id):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()

            max_bet = cursor.execute(f'SELECT MAX(price) FROM History_Lots WHERE lot_id={lot_id}').fetchone()[0]
            return int(max_bet) if max_bet else 0
        
        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def get_history(self, user_id):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()

            history = []
            for _, lot_id in cursor.execute(f'SELECT id, lot_id FROM History_Lots WHERE user_id={user_id} ORDER BY id DESC').fetchall():
                if lot_id not in history:
                    history.append(lot_id)
            return history
        
        except Exception as e:
            print(f"Произошла ошибка: {e}")
    
    def get_lots_history(self, id_seller):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()

            return list(map(lambda v: v[0], cursor.execute(f'SELECT id FROM Lots WHERE id_seller={id_seller} ORDER BY id DESC').fetchall()))
        
        except Exception as e:
            print(f"Произошла ошибка: {e}")



    def create_report(self, user_id_sender, user_id_suspect, content, messages_id_report):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()
            
            cursor.execute(f'INSERT INTO Comments (user_id_sender, user_id_suspect, content, messages_id_report)' +
                            f'VALUES ("{user_id_sender}", "{user_id_suspect}", "{content}", {messages_id_report})')
            cursor.execute("COMMIT")
            
        except Exception as e:
            print(f"Произошла ошибка: {e}")
    
    def get_new_report_id(self):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()
            
            id_new = cursor.execute(f'SELECT MAX(id) FROM Comments').fetchone()[0]
            if id_new:
                id_new += 1
            else:
                id_new = 1
            
            return id_new
        
        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def get_approved_reports_count(self, user_id_suspect):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()
            
            return cursor.execute(f'SELECT COUNT(*) FROM Comments WHERE user_id_suspect="{user_id_suspect}" AND is_approved=1').fetchone()[0]
        
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return -1
    
    def approve_report(self, report_id):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()
            
            cursor.execute(f'UPDATE Comments SET is_approved = 1 WHERE id={report_id}')
            cursor.execute("COMMIT")
        
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return -1

    def get_report_info(self, report_id):
        try:
            db = sqlite3.connect(self.db_file)
            cursor = db.cursor()
            
            return cursor.execute(f'SELECT * FROM Comments WHERE id={report_id}').fetchone()
        
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return -1

    def check_balance(self, name_user):
            try:
                db = sqlite3.connect(self.db_file)
                cursor = db.cursor()
            
                return cursor.execute(f'SELECT balance FROM Users WHERE user_name="{name_user}"').fetchone()[0]
            
            except Exception as e:
                print(f"Произошла ошибка: {e}")




if __name__ == '__main__':
    db = DataBase(db_file='datebase.db')
