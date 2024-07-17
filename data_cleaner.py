from db_connection import Neo4jConnector

class DatabaseCleaner:
    def __init__(self):
        self.connector = Neo4jConnector()

    def clean_database(self):
        query = "MATCH (n) DETACH DELETE n"
        self.connector.execute_query(query)
        print("Database cleaned: All nodes and relationships have been removed.")

    def verify_empty_database(self):
        query = "MATCH (n) RETURN COUNT(n) as count"
        result = self.connector.execute_query(query)
        count = result[0]['count'] if result else 0
        if count == 0:
            print("Database is empty.")
        else:
            print(f"Database still contains {count} nodes.")

    def close(self):
        self.connector.close()

if __name__ == "__main__":
    cleaner = DatabaseCleaner()
    
    # Clean the database
    cleaner.clean_database()
    
    # Verify that the database is empty
    cleaner.verify_empty_database()
    
    cleaner.close()
