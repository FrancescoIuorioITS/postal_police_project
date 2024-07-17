import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from functools import wraps

# Load environment variables from .env file
load_dotenv()

class Neo4jConnector:
    def __init__(self):
        self.driver = None
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        
        if not all([uri, user, password]):
            raise ValueError("Missing Neo4j credentials in .env file")
        
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
        except Exception as e:
            print(f"Failed to create the driver: {e}")
        
    def close(self):
        if self.driver is not None:
            self.driver.close()

    def verify_connectivity(self):
        try:
            self.driver.verify_connectivity()
            print("Connection to Neo4j database verified successfully!")
            return True
        except ServiceUnavailable as e:
            print(f"Unable to connect to Neo4j database: {e}")
            return False

    def execute_query(self, query, parameters=None):
        assert self.driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.driver.session()
            response = list(session.run(query, parameters))
        except Exception as e:
            print(f"Query failed: {e}")
        finally:
            if session is not None:
                session.close()
        return response
    

class DatabaseContextManager:
    def __init__(self, connector):
        self.connector = connector

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.connector.close()

def with_database(cls):
    class Wrapped(cls):
        def __init__(self, *args, **kwargs):
            self.db_context = DatabaseContextManager(args[0])
            super().__init__(self.db_context.connector, *args[1:], **kwargs)

        def __enter__(self):
            self.db_context.__enter__()
            return self

        def __exit__(self, *args):
            return self.db_context.__exit__(*args)

    return Wrapped

# Example usage
if __name__ == "__main__":
    connector = Neo4jConnector()
    
    if connector.verify_connectivity():
        # Example query
        result = connector.execute_query("MATCH (n) RETURN count(n) as count")
        if result:
            print(f"Number of nodes in the database: {result[0]['count']}")
    
    connector.close()

