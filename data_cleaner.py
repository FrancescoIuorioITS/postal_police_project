from db_connection import with_database

@with_database
class DataCleaner:
    def delete_connections(self):
        query = "MATCH ()-[r:CONNECTED_TO]->() DELETE r"
        self.connector.execute_query(query)
        print("All connections deleted.")

    def delete_phone_numbers(self):
        query = "MATCH (p:PhoneNumber) DETACH DELETE p"
        self.connector.execute_query(query)
        print("All phone numbers deleted.")

    def delete_people(self):
        query = "MATCH (p:Person) DETACH DELETE p"
        self.connector.execute_query(query)
        print("All people deleted.")

    def delete_traditional_cells(self):
        query = "MATCH (c:Cell {type: 'traditional'}) DETACH DELETE c"
        self.connector.execute_query(query)
        print("All traditional cells deleted.")

    def delete_5g_cells(self):
        query = "MATCH (c:Cell {type: '5G'}) DETACH DELETE c"
        self.connector.execute_query(query)
        print("All 5G cells deleted.")

    def delete_all_cells(self):
        query = "MATCH (c:Cell) DETACH DELETE c"
        self.connector.execute_query(query)
        print("All cells deleted.")

    def delete_all_data(self):
        self.delete_connections()
        self.delete_phone_numbers()
        self.delete_people()
        self.delete_all_cells()
        print("All data deleted from the database.")


    def verify_empty_database(self):
        categories = {
            'People': 'MATCH (p:Person) RETURN COUNT(p) as count',
            'Phone Numbers': 'MATCH (ph:PhoneNumber) RETURN COUNT(ph) as count',
            'Traditional Cells': 'MATCH (c:Cell {type: "traditional"}) RETURN COUNT(c) as count',
            '5G Cells': 'MATCH (c:Cell {type: "5G"}) RETURN COUNT(c) as count',
            'Connections': 'MATCH ()-[r:CONNECTED_TO]->() RETURN COUNT(r) as count'
        }
        
        total_count = 0
        for category, query in categories.items():
            result = self.connector.execute_query(query)
            count = result[0]['count'] if result else 0
            total_count += count
            print(f"{category}: {count}")
        
        if total_count == 0:
            print("Database is completely empty.")
        else:
            print(f"Database contains a total of {total_count} nodes/relationships.")

if __name__ == "__main__":
    cleaner = DataCleaner()
    
    cleaner.delete_connections()
    # cleaner.delete_phone_numbers()
    # cleaner.delete_people()
    # cleaner.delete_traditional_cells()
    # cleaner.delete_5g_cells()
    
    # cleaner.delete_all_data()
    
    cleaner.verify_empty_database()
