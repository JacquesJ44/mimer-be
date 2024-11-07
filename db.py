import pymysql

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

class DbUtil:
    def __init__(self):
        self.con = pymysql.connect(host='localhost', user='root', database='mimir')

    # DB OPS WITH USERS
    # Save a new user
    def save_user(self, name, surname, email, password):
        c = self.con.cursor()

        c.execute(
            'INSERT INTO users (name, surname, email, password) VALUES (%s, %s, %s, %s)', (name, surname, email, password)
        ) 
        self.con.commit()
        return c.lastrowid

    # Search for a user in the users table
    def get_user_by_email(self, email):
        c = self.con.cursor()

        c.execute(
            'SELECT * FROM users WHERE email = %s', (email,)
        )
        return c.fetchone()
    
    # DB OPS WITH SITES
    # Save a new site
    def save_site(self, site, latitude, longitude, building, street, number, suburb, city, postcode, province):
        c = self.con.cursor()

        c.execute(
            'INSERT INTO sites (site, latitude, longitude, building, street, number, suburb, city, postcode, province) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', 
            (site, latitude, longitude, building, street, number, suburb, city, postcode, province)
        )
        self.con.commit()
        return c.lastrowid

    # Search if a site already exists in the db before saving it
    def search_site(self, site):
        c = self.con.cursor()

        c.execute(
            'SELECT * FROM sites WHERE site = %s', (site,)
        )
        return c.fetchone()
    
    # Search the db for similar sites as searched for on the Sites page
    def search_similar_site(self, query, dict_values):
        c = self.con.cursor()
        
        c.execute(query, dict_values)
        x = c.fetchall()

        y = [dict_factory(c, i) for i in x]

        return y
    
    # Search a site to view in the ViewSite page
    def search_site_to_view(self, site):
        c = self.con.cursor()

        c.execute('SELECT * FROM sites WHERE site = %s', (site,))
        x = c.fetchall()
        y = [dict_factory(c, i) for i in x]
        
        return y
    
    # Search sitename to add the site in AddCircuits
    def search_sitename(self, query, value):
        c = self.con.cursor()
        c.execute(query, value)
        x = c.fetchall()

        y = [dict_factory(c, i) for i in x]

        return y
    
    # Delete a site
    def delete_site(self, site):
        c = self.con.cursor()

        c.execute(
            'DELETE FROM sites WHERE site = %s', (site,)
        )
        
        self.con.commit()
        return c.lastrowid
    
    # DB OPS WITH CIRCUITS
    # Save a new circuit
    def save_circuit(self, vendor, circuitType, speed, circuitNumber, enni, vlan, startDate, contractTerm, endDate, mrc, siteA, siteB, comments, status, doc):
        with self.con.cursor() as c:
            c.execute(
                'INSERT INTO circuits (vendor, circuitType, speed, circuitNumber, enni, vlan, startDate, contractTerm, endDate, mrc, siteA, siteB, comments, status, doc) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', 
                (vendor, circuitType, speed, circuitNumber, enni, vlan, startDate, contractTerm, endDate, mrc, siteA, siteB, comments, status, doc)
            )
            self.con.commit()
            return c.lastrowid

    # Search the db for similar circuit as searched for on the Circuits page
    def search_similar_circuit(self, query, dict_values):
        c = self.con.cursor()
        
        c.execute(query, dict_values)
        x = c.fetchall()

        y = [dict_factory(c, i) for i in x]

        return y
    
    # Search a circuit to view in the ViewCircuit page
    def search_circuit_to_view(self, id):
       c = self.con.cursor()

       c.execute('SELECT * FROM circuits WHERE id = %s', (id,))
       x = c.fetchall()
       y = [dict_factory(c, i) for i in x]
       
       return y
    
    # Update an existing record in db
    def update_circuit(self, dict_key, dict_value, id):
        c = self.con.cursor()

        c.execute(f"UPDATE circuits SET {dict_key} = %s WHERE id = %s", (dict_value, id)
        )
        self.con.commit()
        return c.lastrowid