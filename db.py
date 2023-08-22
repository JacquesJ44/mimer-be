import sqlite3

class DbUtil:
    # DB OPS WITH USERS
    def __init__(self):
        self.con = sqlite3.connect('mimir.db', check_same_thread=False)

    def save_user(self, name, surname, email, password):
        c = self.con.cursor()

        c.execute(
            'INSERT INTO users (name, surname, email, password) VALUES (?,?,?,?)', (name, surname, email, password)
        ) 
        self.con.commit()
        return c.lastrowid
    
    def get_user_by_email(self, email):
        c = self.con.cursor()

        c.execute(
            'SELECT * FROM users WHERE email = ?', (email,)
        )
        return c.fetchone()
    
    # DB OPS WITH SITES
    def save_site(self, customer, latitude, longitude, building, street, number, suburb, city, postcode, province):
        c = self.con.cursor()

        c.execute(
            'INSERT INTO sites (customer, latitude, longitude, building, street, number, suburb, city, postcode, province) VALUES (?,?,?,?,?,?,?,?,?,?)', 
            (customer, latitude, longitude, building, street, number, suburb, city, postcode, province)
        )
        self.con.commit()
        return c.lastrowid
    
    def search_site(self, customer):
        c = self.con.cursor()

        c.execute(
            'SELECT * FROM sites WHERE customer = ?', (customer,)
        )
        return c.fetchone()
    
    def search_similar_site(self, dict_key, dict_value):
        c = self.con.cursor()

        c.execute(
            'SELECT * FROM sites WHERE ' + dict_key + ' LIKE ' + dict_value
        )
        return c.fetchall()
    