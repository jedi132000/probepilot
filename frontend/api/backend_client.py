"""
Backend API client for ProbePilot Gradio frontend
Handles communication with FastAPI backend services
"""

import httpx
import asyncio
from typing import Dict, List, Optional, Any
import json
from datetime import datetime

class BackendClient:
    """Client for communicating with ProbePilot FastAPI backend"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)
        
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system health and status"""
        try:
            response = await self.client.get("/api/v1/system/status")
            return response.json()
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_active_probes(self) -> List[Dict[str, Any]]:
        """Get list of currently active probes"""
        try:
            response = await self.client.get("/api/v1/probes/")
            return response.json()
        except Exception as e:
            return []
    
    async def deploy_probe(self, probe_config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy a new eBPF probe"""
        try:
            response = await self.client.post("/api/v1/probes/", json=probe_config)
            
            # Check if response is successful
            if response.status_code >= 200 and response.status_code < 300:
                try:
                    return response.json()
                except Exception as json_error:
                    return {
                        "success": False,
                        "error": f"JSON parsing error: {str(json_error)}. Response: {response.text[:100]}"
                    }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text[:100]}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}"
            }
    
    async def advance_probe_state(self, probe_id: str) -> Dict[str, Any]:
        """Advance probe to next deployment state"""
        try:
            response = await self.client.post(f"/api/v1/probes/{probe_id}/advance")
            return response.json()
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_metrics(self, 
                         probe_id: Optional[str] = None,
                         start_time: Optional[str] = None,
                         end_time: Optional[str] = None) -> Dict[str, Any]:
        """Get telemetry metrics data"""
        try:
            params = {}
            if probe_id:
                params["probe_id"] = probe_id
            if start_time:
                params["start_time"] = start_time
            if end_time:
                params["end_time"] = end_time
                
            response = await self.client.get("/api/v1/metrics", params=params)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def stop_probe(self, probe_id: str) -> Dict[str, Any]:
        """Stop a running probe"""
        try:
            response = await self.client.delete(f"/api/v1/probes/{probe_id}")
            return response.json()
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_alerts(self) -> List[Dict[str, Any]]:
        """Get active alerts and notifications"""
        try:
            response = await self.client.get("/api/v1/alerts")
            return response.json()
        except Exception as e:
            return []
    
    async def query_copilot(self, query: str) -> Dict[str, Any]:
        """Send query to AI Copilot service"""
        try:
            response = await self.client.post(
                "/api/v1/copilot/query",
                json={"query": query}
            )
            return response.json()
        except Exception as e:
            return {
                "response": f"Sorry, I'm having trouble connecting to the AI service: {str(e)}",
                "error": True
            }
    
    def __del__(self):
        """Cleanup client connection"""
        try:
            if hasattr(self, 'client') and self.client:
                # Don't create tasks in __del__ as it causes warnings
                pass
        except:
            pass