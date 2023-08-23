import sqlite3

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

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
    def save_site(self, site, latitude, longitude, building, street, number, suburb, city, postcode, province):
        c = self.con.cursor()

        c.execute(
            'INSERT INTO sites (site, latitude, longitude, building, street, number, suburb, city, postcode, province) VALUES (?,?,?,?,?,?,?,?,?,?)', 
            (site, latitude, longitude, building, street, number, suburb, city, postcode, province)
        )
        self.con.commit()
        return c.lastrowid
    
    def search_site(self, site):
        c = self.con.cursor()

        c.execute(
            'SELECT * FROM sites WHERE site = ?', (site,)
        )
        return c.fetchone()
    
    def search_similar_site(self, dict_key, dict_value):
        c = self.con.cursor()

        c.execute(
            'SELECT * FROM sites WHERE ' + dict_key + ' LIKE ' + dict_value
        )
        return c.fetchall()
    
    # def search_similar_site_to_view(self, site):
    #     c = self.con.cursor()

    #     row = c.execute(
    #         'SELECT * FROM sites WHERE site = ?', (site,)
    #     )
    #     x= []
    #     for i in row:
    #         c.row_factory = dict_factory(c, i)
    #         x.append(c.row_factory)
    #     return x