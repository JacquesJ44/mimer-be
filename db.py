import sqlite3

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

class DbUtil:
    def __init__(self):
        self.con = sqlite3.connect('mimir.db', check_same_thread=False)

    # DB OPS WITH USERS
    # Save a new user
    def save_user(self, name, surname, email, password):
        c = self.con.cursor()

        c.execute(
            'INSERT INTO users (name, surname, email, password) VALUES (?,?,?,?)', (name, surname, email, password)
        ) 
        self.con.commit()
        return c.lastrowid

    # Search for a user in the users table
    def get_user_by_email(self, email):
        c = self.con.cursor()

        c.execute(
            'SELECT * FROM users WHERE email = ?', (email,)
        )
        return c.fetchone()
    
    # DB OPS WITH SITES
    # Save a new site
    def save_site(self, site, latitude, longitude, building, street, number, suburb, city, postcode, province):
        c = self.con.cursor()

        c.execute(
            'INSERT INTO sites (site, latitude, longitude, building, street, number, suburb, city, postcode, province) VALUES (?,?,?,?,?,?,?,?,?,?)', 
            (site, latitude, longitude, building, street, number, suburb, city, postcode, province)
        )
        self.con.commit()
        return c.lastrowid

    # Search if a site already exists in the db before saving it
    def search_site(self, site):
        c = self.con.cursor()

        c.execute(
            'SELECT * FROM sites WHERE site = ?', (site,)
        )
        return c.fetchone()
    
    # Search the db for similar sites as searched for on the Sites page
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
    
    # Search a site to view in the ViewSite page
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
    
    # Search sitename to add the site in AddCircuits
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
    
    # Delete a site
    def delete_site(self, site):
        c = self.con.cursor()

        c.execute(
            'DELETE FROM sites WHERE site = ?', (site,)
        )
        
        self.con.commit()
        return c.lastrowid
    
    # DB OPS WITH CIRCUITS
    # Save a new circuit
    def save_circuit(self, vendor, circuitType, speed, circuitNumber, enni, vlan, startDate, contractTerm, endDate, siteA, siteB, comments, status):
        c = self.con.cursor()

        c.execute(
            'INSERT INTO circuits (vendor, circuitType, speed, circuitNumber, enni, vlan, startDate, contractTerm, endDate, siteA, siteB, comments, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', 
            (vendor, circuitType, speed, circuitNumber, enni, vlan, startDate, contractTerm, endDate, siteA, siteB, comments, status)
        )
        self.con.commit()
        return c.lastrowid

    # Search the db for similar circuit as searched for on the Circuits page
    def search_similar_circuit(self, dict_key, dict_value):
        x = []
        c = self.con.cursor()

        for row in c.execute(
               'SELECT * FROM circuits WHERE ' + dict_key + ' LIKE ' + dict_value
            ):
            x.append(row)

        y = []
        for i in x:
            c.row_factory = dict_factory(c, i)
            y.append(c.row_factory)

        return y
    
    # Search a circuit to view in the ViewCircuit page
    def search_circuit_to_view(self, id):
        x = []
        c = self.con.cursor()

        for row in c.execute(
                'SELECT * FROM circuits WHERE id = ?', (id,)
            ):
            x.append(row)

        y = []
        for i in x:
            c.row_factory = dict_factory(c, i)
            y.append(c.row_factory)

        return y
    
    # Update an existing record in db
    def update_circuit(self, dict_key, dict_value, id):
        c = self.con.cursor()

        c.execute("UPDATE circuits SET " + dict_key + "='" + dict_value + "' WHERE id = ?", (id,)
        )

        self.con.commit()
        return c.lastrowid