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
        x = []
        c = self.con.cursor()

        for row in c.execute(
               'SELECT * FROM sites WHERE ' + dict_key + ' LIKE ' + dict_value
            ):
            x.append(row)

        y = []
        for i in x:
            c.row_factory = dict_factory(c, i)
            y.append(c.row_factory)

        return y
    
    def search_site_to_view(self, site):
        x = []
        c = self.con.cursor()

        for row in c.execute(
                'SELECT * FROM sites WHERE site = ?', (site,)
            ):
            x.append(row)

        y = []
        for i in x:
            c.row_factory = dict_factory(c, i)
            y.append(c.row_factory)

        return y
    
    def search_sitename(self, site):
        x = []
        c = self.con.cursor()

        for row in c.execute(
            'SELECT * FROM sites WHERE site LIKE ' + site
            ):
            x.append(row)

        y = []
        for i in x:
            c.row_factory = dict_factory(c, i)
            y.append(c.row_factory)

        return y
    
    # DB OPS WITH CIRCUITS
    def save_circuit(self, vendor, circuit_type, speed, circuit_number, enni, vlan, start_date, contract_term, end_date, siteA, siteB, comments):
        c = self.con.cursor()

        c.execute(
            'INSERT INTO circuits (vendor, circuit_type, speed, circuit_number, enni, vlan, start_date, contract_term, end_date, siteA, siteB, comments) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', 
            (vendor, circuit_type, speed, circuit_number, enni, vlan, start_date, contract_term, end_date, siteA, siteB, comments)
        )
        self.con.commit()
        return c.lastrowid
