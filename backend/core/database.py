"""
ProbePilot Database Configuration
Redis-based data persistence
"""
import redis
import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class RedisDatabase:
    """Redis-based database for ProbePilot"""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
        self.db = db
        self.client = None
        self.connected = False
    
    def connect(self):
        """Connect to Redis database"""
        try:
            self.client = redis.Redis(
                host=self.host, 
                port=self.port, 
                db=self.db,
                decode_responses=True
            )
            # Test connection
            self.client.ping()
            self.connected = True
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
            return self
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.connected = False
            return self
    
    def disconnect(self):
        """Disconnect from Redis database"""
        if self.client:
            self.client.close()
        self.connected = False
        logger.info("Disconnected from Redis")
    
    def is_connected(self):
        """Check if database is connected"""
        if not self.client:
            return False
        try:
            self.client.ping()
            return True
        except:
            self.connected = False
            return False
    
    def set_probe_data(self, probe_id: str, data: Dict[str, Any]):
        """Store probe data in Redis"""
        if not self.is_connected() or not self.client:
            return False
        try:
            key = f"probe:{probe_id}"
            self.client.hset(key, mapping={
                "data": json.dumps(data),
                "updated_at": str(data.get("timestamp", ""))
            })
            return True
        except Exception as e:
            logger.error(f"Failed to store probe data: {e}")
            return False
    
    def get_probe_data(self, probe_id: str) -> Optional[Dict[str, Any]]:
        """Get probe data from Redis"""
        if not self.is_connected() or not self.client:
            return None
        try:
            key = f"probe:{probe_id}"
            data = self.client.hget(key, "data")
            if data and isinstance(data, str):
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get probe data: {e}")
            return None
    
    def get_all_probes(self) -> List[Dict[str, Any]]:
        """Get all probe data from Redis"""
        if not self.is_connected() or not self.client:
            return []
        try:
            keys = self.client.keys("probe:*")
            probes = []
            if keys:
                for key in keys:
                    data = self.client.hget(key, "data")
                    if data and isinstance(data, str):
                        probe_data = json.loads(data)
                        probe_data["id"] = key.replace("probe:", "")
                        probes.append(probe_data)
            return probes
        except Exception as e:
            logger.error(f"Failed to get all probes: {e}")
            return []
    
    def store_system_event(self, event: Dict[str, Any]):
        """Store system event in Redis"""
        if not self.is_connected() or not self.client:
            return False
        try:
            # Store events in a sorted set with timestamp as score
            timestamp = event.get("timestamp", 0)
            self.client.zadd("system:events", {json.dumps(event): timestamp})
            # Keep only last 1000 events
            self.client.zremrangebyrank("system:events", 0, -1001)
            return True
        except Exception as e:
            logger.error("Failed to store system event: %s", e)
            return False
    
    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent system events from Redis"""
        if not self.is_connected() or not self.client:
            return []
        try:
            # Get most recent events (highest scores)
            events_data = self.client.zrevrange("system:events", 0, limit-1)
            events = []
            if events_data:
                for event_json in events_data:
                    try:
                        if isinstance(event_json, str):
                            events.append(json.loads(event_json))
                    except json.JSONDecodeError:
                        continue
            return events
        except Exception as e:
            logger.error("Failed to get recent events: %s", e)
            return []

# Global database instance
db = RedisDatabase()

def get_database():
    """Get database instance"""
    return db