"""
ProbePilot Database Configuration
Simple database connection management
"""

class Database:
    """Simple database mock for development"""
    
    def __init__(self):
        self.connected = True
        self.data = {}
    
    def connect(self):
        """Connect to database"""
        self.connected = True
        return self
    
    def disconnect(self):
        """Disconnect from database"""
        self.connected = False
    
    def is_connected(self):
        """Check if database is connected"""
        return self.connected

# Global database instance
db = Database()

def get_database():
    """Get database instance"""
    return db