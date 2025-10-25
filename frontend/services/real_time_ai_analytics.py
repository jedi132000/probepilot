"""
Real-time AI Analytics for ProbePilot
Integrates AI analysis with live system metrics and probe data
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from services.ai_service import ProbePilotAI
from services.metrics_client import metrics_client
import logging

logger = logging.getLogger(__name__)

class RealTimeAIAnalytics:
    """Real-time AI analytics using actual system metrics"""
    
    def __init__(self):
        self.ai_copilot = ProbePilotAI()
        self.last_analysis_time = None
        self.cached_insights = None
        self.cache_duration = 30  # seconds
    
    def get_current_system_context(self) -> str:
        """Build comprehensive system context from real metrics"""
        metrics = metrics_client.get_system_metrics()
        probes = metrics_client.get_active_probes()
        
        if not metrics:
            return "System metrics unavailable - backend connection issue"
        
        # Extract real metrics
        cpu_percent = metrics.get('cpu', {}).get('usage_percent', 0)
        memory_percent = metrics.get('memory', {}).get('percent', 0)
        memory_used = metrics.get('memory', {}).get('used', 0)
        memory_total = metrics.get('memory', {}).get('total', 0)
        
        disk_percent = metrics.get('disk', {}).get('percent', 0)
        disk_used = metrics.get('disk', {}).get('used', 0)
        disk_total = metrics.get('disk', {}).get('total', 0)
        
        network_sent = metrics.get('network', {}).get('bytes_sent', 0)
        network_recv = metrics.get('network', {}).get('bytes_recv', 0)
        
        load_avg = metrics.get('cpu', {}).get('load_average', [0, 0, 0])
        
        # Format the context
        context = f"""Current System Status (Real-time data from {datetime.now().strftime('%H:%M:%S')}):

CPU Performance:
- Current Usage: {cpu_percent:.1f}%
- Load Average: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f} (1m, 5m, 15m)
- CPU Cores: {metrics.get('cpu', {}).get('count', 'Unknown')}

Memory Status:
- Usage: {memory_percent:.1f}% ({memory_used / (1024**3):.1f}GB of {memory_total / (1024**3):.1f}GB)
- Available: {(memory_total - memory_used) / (1024**3):.1f}GB free

Storage:
- Disk Usage: {disk_percent:.1f}% ({disk_used / (1024**3):.1f}GB of {disk_total / (1024**3):.1f}GB)

Network Activity:
- Bytes Sent: {network_sent / (1024**2):.1f}MB total
- Bytes Received: {network_recv / (1024**2):.1f}MB total

Active eBPF Probes: {len(probes) if probes else 0}"""
        
        if probes:
            context += "\nActive Probes Details:"
            for probe in probes[:5]:  # Limit to first 5 probes
                if isinstance(probe, dict):
                    context += f"\n- {probe.get('name', 'Unknown')}: {probe.get('type', 'Unknown')} ({probe.get('status', 'Unknown')})"
        
        return context
    
    def analyze_system_health(self) -> Dict[str, Any]:
        """Analyze current system health with AI"""
        metrics = metrics_client.get_system_metrics()
        if not metrics:
            return {"status": "error", "message": "Unable to fetch system metrics"}
        
        cpu_percent = metrics.get('cpu', {}).get('usage_percent', 0)
        memory_percent = metrics.get('memory', {}).get('percent', 0)
        load_avg = metrics.get('cpu', {}).get('load_average', [0, 0, 0])
        
        alerts = []
        recommendations = []
        
        # CPU Analysis
        if cpu_percent > 80:
            alerts.append({
                "level": "HIGH",
                "type": "CPU",
                "message": f"High CPU usage detected: {cpu_percent:.1f}%",
                "color": "#ef4444"
            })
            recommendations.append("Consider scaling CPU resources or optimizing high-usage processes")
        elif cpu_percent > 60:
            alerts.append({
                "level": "MEDIUM", 
                "type": "CPU",
                "message": f"Moderate CPU usage: {cpu_percent:.1f}%",
                "color": "#f59e0b"
            })
        
        # Memory Analysis
        if memory_percent > 90:
            alerts.append({
                "level": "HIGH",
                "type": "MEMORY",
                "message": f"Critical memory usage: {memory_percent:.1f}%",
                "color": "#ef4444"
            })
            recommendations.append("Memory usage critical - investigate memory leaks or increase RAM")
        elif memory_percent > 80:
            alerts.append({
                "level": "MEDIUM",
                "type": "MEMORY", 
                "message": f"High memory usage: {memory_percent:.1f}%",
                "color": "#f59e0b"
            })
            recommendations.append("Monitor memory usage closely - consider optimization")
        
        # Load Average Analysis
        cpu_count = metrics.get('cpu', {}).get('count', 1)
        if load_avg[0] > cpu_count * 1.5:
            alerts.append({
                "level": "MEDIUM",
                "type": "LOAD",
                "message": f"High system load: {load_avg[0]:.2f} (cores: {cpu_count})",
                "color": "#f59e0b"
            })
        
        return {
            "status": "success",
            "alerts": alerts,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_ai_insights(self, force_refresh=False) -> str:
        """Get AI-powered insights based on real system data"""
        current_time = datetime.now()
        
        # Use cache if available and recent
        if (not force_refresh and 
            self.cached_insights and 
            self.last_analysis_time and 
            (current_time - self.last_analysis_time).seconds < self.cache_duration):
            return self.cached_insights
        
        try:
            # Get real system context
            system_context = self.get_current_system_context()
            analysis = self.analyze_system_health()
            
            # Prepare AI prompt with real data
            prompt = f"""Analyze this real-time system data and provide actionable insights:

{system_context}

Current Analysis:
- Alerts: {len(analysis.get('alerts', []))} detected
- Recommendations: {len(analysis.get('recommendations', []))} available

Please provide:
1. Brief health assessment (2-3 sentences)
2. Top priority recommendation if any issues detected
3. Any notable patterns or optimizations

Keep response concise and actionable. Focus on the most critical insights."""
            
            # Get AI response
            if self.ai_copilot.client:
                ai_response = await self.ai_copilot.analyze_system(prompt)
                
                # Cache the result
                self.cached_insights = ai_response
                self.last_analysis_time = current_time
                
                return ai_response
            else:
                return "AI analysis unavailable - OpenAI API key not configured"
                
        except Exception as e:
            logger.error(f"Error getting AI insights: {e}")
            return f"AI analysis temporarily unavailable: {str(e)}"
    
    def get_real_insights_html(self) -> str:
        """Generate real-time insights HTML with actual system data"""
        analysis = self.analyze_system_health()
        metrics = metrics_client.get_system_metrics()
        probes = metrics_client.get_active_probes()
        
        if analysis["status"] == "error":
            return """
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; border-radius: 8px; padding: 15px;">
                <h4 style="color: #ef4444; margin-top: 0;">⚠️ System Metrics Unavailable</h4>
                <p>Unable to fetch real-time system data for AI analysis.</p>
            </div>
            """
        
        # Build alerts HTML
        alerts_html = ""
        for alert in analysis.get("alerts", []):
            alerts_html += f"""
            <div style="background: rgba(30, 41, 59, 0.6); border-radius: 8px; padding: 12px; border: 1px solid rgba(71, 85, 105, 0.3); margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="color: #e2e8f0; margin: 0; font-size: 0.9em;">🚨 {alert['type']} ALERT</h4>
                    </div>
                </div>
                <p style="margin: 8px 0 0 0; color: #e2e8f0; font-size: 0.9em;">{alert['message']}</p>
                <div style="margin-top: 8px;">
                    <span style="background: rgba({self._hex_to_rgba(alert['color'])}, 0.2); color: {alert['color']}; padding: 2px 8px; border-radius: 12px; font-size: 0.75em;">{alert['level']}</span>
                </div>
            </div>
            """
        
        if not alerts_html:
            alerts_html = """
            <div style="background: rgba(34, 197, 94, 0.1); border: 1px solid #22c55e; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
                <h4 style="color: #22c55e; margin-top: 0;">✅ System Health Normal</h4>
                <p>All system metrics are within normal operational ranges.</p>
            </div>
            """
        
        # Real metrics display
        if metrics:
            cpu_percent = metrics.get('cpu', {}).get('usage_percent', 0)
            memory_percent = metrics.get('memory', {}).get('percent', 0)
            memory_used = metrics.get('memory', {}).get('used', 0)
            network_sent = metrics.get('network', {}).get('bytes_sent', 0)
            probe_count = len(probes) if probes else 0
            
            metrics_html = f"""
            <div style="background: rgba(30, 41, 59, 0.6); border-radius: 8px; padding: 12px; border: 1px solid rgba(71, 85, 105, 0.3);">
                <h4 style="color: #94a3b8; margin: 0 0 8px 0; font-size: 0.9em;">📊 LIVE METRICS</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.85em;">
                    <div>
                        <span style="color: #64748b;">CPU:</span>
                        <span style="color: {self._get_metric_color(cpu_percent, [70, 90])}; font-weight: bold;">{cpu_percent:.1f}%</span>
                    </div>
                    <div>
                        <span style="color: #64748b;">Memory:</span>
                        <span style="color: {self._get_metric_color(memory_percent, [80, 95])}; font-weight: bold;">{memory_percent:.1f}%</span>
                    </div>
                    <div>
                        <span style="color: #64748b;">Network:</span>
                        <span style="color: #3b82f6; font-weight: bold;">{network_sent / (1024**2):.0f}MB</span>
                    </div>
                    <div>
                        <span style="color: #64748b;">Probes:</span>
                        <span style="color: {'#22c55e' if probe_count > 0 else '#ef4444'}; font-weight: bold;">{probe_count} active</span>
                    </div>
                </div>
            </div>
            """
        else:
            metrics_html = """
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; border-radius: 8px; padding: 15px;">
                <h4 style="color: #ef4444; margin-top: 0;">📊 Metrics Unavailable</h4>
                <p>Unable to fetch real-time system metrics.</p>
            </div>
            """
        
        return f"""
        <div style="background: rgba(15, 23, 42, 0.8); border-radius: 12px; padding: 20px; border: 1px solid rgba(51, 65, 85, 0.3);">
            {alerts_html}
            {metrics_html}
            <div style="margin-top: 10px; text-align: center; color: #64748b; font-size: 0.8em;">
                Last updated: {datetime.now().strftime('%H:%M:%S')}
            </div>
        </div>
        """
    
    def _get_metric_color(self, value: float, thresholds: list) -> str:
        """Get color based on metric value and thresholds"""
        if value < thresholds[0]:
            return "#22c55e"  # Green
        elif value < thresholds[1]:
            return "#f59e0b"  # Yellow
        else:
            return "#ef4444"  # Red
    
    def _hex_to_rgba(self, hex_color: str) -> str:
        """Convert hex color to rgba values"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"{rgb[0]}, {rgb[1]}, {rgb[2]}"

# Global instance
real_time_ai_analytics = RealTimeAIAnalytics()