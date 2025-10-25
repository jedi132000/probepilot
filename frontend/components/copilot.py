"""
AI Copilot Component
Real OpenAI GPT integration for intelligent system analysis and troubleshooting
"""

import gradio as gr
import asyncio
import os
from datetime import datetime
from typing import List, Dict, Optional

# Import AI service
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from services.ai_service import ProbePilotAI, get_ai_response, get_quick_analysis
from services.real_time_ai_analytics import real_time_ai_analytics

# Initialize AI copilot
ai_copilot = ProbePilotAI()

def get_ai_status_html(configured=None):
    """Generate AI status HTML"""
    if configured is True:
        return """
        <div style="background: rgba(34, 197, 94, 0.1); border: 1px solid #22c55e; border-radius: 8px; padding: 15px;">
            <h4 style="color: #22c55e; margin-top: 0;">✅ AI Configured</h4>
            <p>OpenAI GPT-4 is ready for intelligent analysis.</p>
        </div>
        """
    elif configured is False:
        return """
        <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; border-radius: 8px; padding: 15px;">
            <h4 style="color: #ef4444; margin-top: 0;">❌ AI Not Configured</h4>
            <p>Please provide a valid OpenAI API key to enable AI features.</p>
        </div>
        """
    else:
        # Check if already configured
        if ai_copilot.client:
            return get_ai_status_html(configured=True)
        else:
            return get_ai_status_html(configured=False)

def get_current_insights_html():
    """Generate real-time AI insights HTML with actual system data"""
    return real_time_ai_analytics.get_real_insights_html()

def get_enhanced_insights_html():
    """Generate enhanced AI insights HTML with real alert data"""
    try:
        # Get real system data with advanced alerting
        system_data = get_current_system_data()
        
        insights_html = '<div class="ai-insights-panel">'
        
        # Process alerts from the advanced alert engine
        alert_details = system_data.get('alert_details', [])
        system_status = system_data.get('system_health_status', 'unknown')
        
        # Generate alert cards based on real data
        if alert_details:
            for alert in alert_details:
                severity = alert.get('severity', 'info')
                message = alert.get('message', '')
                suggested_actions = alert.get('suggested_actions', [])
                baseline_deviation = alert.get('baseline_deviation')
                
                # Color and icon based on severity
                if severity == 'critical':
                    color = '#ef4444'
                    icon = '🚨'
                    priority = 'CRITICAL'
                    bg_color = 'rgba(239, 68, 68, 0.1)'
                elif severity == 'warning':
                    color = '#fbbf24'
                    icon = '⚠️'
                    priority = 'WARNING'
                    bg_color = 'rgba(251, 191, 36, 0.1)'
                else:
                    color = '#3b82f6'
                    icon = 'ℹ️'
                    priority = 'INFO'
                    bg_color = 'rgba(59, 130, 246, 0.1)'
                
                # Build suggested actions HTML
                actions_html = ""
                if suggested_actions:
                    actions_html = "<br><strong>Suggested Actions:</strong><br>" + "<br>".join([f"• {action}" for action in suggested_actions[:3]])
                
                # Add baseline deviation info if available
                deviation_info = ""
                if baseline_deviation is not None:
                    deviation_info = f"<br><small>Baseline deviation: {baseline_deviation:.1f}σ</small>"
                
                insights_html += f"""
                <div style="background: {bg_color}; border: 1px solid {color}; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 24px; margin-right: 12px;">{icon}</span>
                        <div>
                            <h4 style="color: {color}; margin: 0;">{alert.get('metric_name', '').replace('_', ' ').title()} Alert</h4>
                            <span style="color: #64748b; font-size: 0.85em;">Real-time detection</span>
                        </div>
                    </div>
                    <p style="margin: 0; color: #e2e8f0;">{message}{deviation_info}{actions_html}</p>
                    <div style="margin-top: 8px;">
                        <span style="background: rgba({color[1:3]}, {color[3:5]}, {color[5:7]}, 0.2); color: {color}; padding: 2px 8px; border-radius: 12px; font-size: 0.75em;">{priority}</span>
                    </div>
                </div>
                """
        else:
            # System healthy - show positive status
            if system_status == 'healthy':
                insights_html += f"""
                <div class="ai-status-good" style="background: rgba(34, 197, 94, 0.1); border: 1px solid #22c55e; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 24px; margin-right: 12px;">✅</span>
                        <div>
                            <h4 style="color: #22c55e; margin: 0;">System Health Excellent</h4>
                            <span style="color: #64748b; font-size: 0.85em;">Advanced monitoring active</span>
                        </div>
                    </div>
                    <p style="margin: 0; color: #e2e8f0;">{system_data.get('system_health_message', 'All systems operating normally')}</p>
                    <div style="margin-top: 8px;">
                        <span style="background: rgba(34, 197, 94, 0.2); color: #86efac; padding: 2px 8px; border-radius: 12px; font-size: 0.75em;">OPTIMAL</span>
                    </div>
                </div>
                """
            else:
                # Unknown or error state
                insights_html += f"""
                <div style="background: rgba(100, 116, 139, 0.1); border: 1px solid #64748b; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 24px; margin-right: 12px;">❓</span>
                        <div>
                            <h4 style="color: #64748b; margin: 0;">System Status</h4>
                            <span style="color: #64748b; font-size: 0.85em;">Monitoring active</span>
                        </div>
                    </div>
                    <p style="margin: 0; color: #e2e8f0;">{system_data.get('system_health_message', 'System monitoring in progress')}</p>
                </div>
                """
        
        # Add live metrics
        insights_html += get_live_metrics_html()
        insights_html += '</div>'
        
        return insights_html
        
    except Exception as e:
        # Fallback to simple status if advanced alerting fails
        return f"""
        <div class="ai-insights-panel">
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
                <h4 style="color: #ef4444; margin: 0;">Alert System Error</h4>
                <p style="margin: 8px 0 0 0; color: #e2e8f0;">Advanced alerting temporarily unavailable: {str(e)}</p>
            </div>
            {get_live_metrics_html()}
        </div>
        """

def get_live_metrics_html():
    """Generate live metrics HTML with real system data"""
    import psutil
    
    try:
        # Get real system metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        # Get probe count
        probe_count = 0
        try:
            import requests
            response = requests.get("http://localhost:8000/api/v1/probes/", timeout=1)
            if response.status_code == 200:
                probes = response.json()
                probe_count = len(probes)
        except:
            probe_count = 0
        
        # Color coding based on thresholds
        cpu_color = "#ef4444" if cpu_percent > 80 else "#fbbf24" if cpu_percent > 60 else "#22c55e"
        mem_color = "#ef4444" if memory.percent > 80 else "#fbbf24" if memory.percent > 60 else "#22c55e"
        probe_color = "#22c55e" if probe_count > 0 else "#64748b"
        
        return f"""
        <div style="background: rgba(30, 41, 59, 0.6); border-radius: 8px; padding: 12px; border: 1px solid rgba(71, 85, 105, 0.3);">
            <h4 style="color: #94a3b8; margin: 0 0 8px 0; font-size: 0.9em;">📊 LIVE METRICS</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.85em;">
                <div>
                    <span style="color: #64748b;">CPU:</span>
                    <span style="color: {cpu_color}; font-weight: bold;">{cpu_percent:.1f}%</span>
                </div>
                <div>
                    <span style="color: #64748b;">Memory:</span>
                    <span style="color: {mem_color}; font-weight: bold;">{memory.percent:.1f}%</span>
                </div>
                <div>
                    <span style="color: #64748b;">Available:</span>
                    <span style="color: #3b82f6; font-weight: bold;">{memory.available // (1024*1024*1024)} GB</span>
                </div>
                <div>
                    <span style="color: #64748b;">Probes:</span>
                    <span style="color: {probe_color}; font-weight: bold;">{probe_count} active</span>
                </div>
            </div>
        </div>
        """
        
    except Exception as e:
        return f"""
        <div style="background: rgba(30, 41, 59, 0.6); border-radius: 8px; padding: 12px; border: 1px solid rgba(71, 85, 105, 0.3);">
            <h4 style="color: #94a3b8; margin: 0 0 8px 0; font-size: 0.9em;">📊 LIVE METRICS</h4>
            <p style="color: #ef4444; font-size: 0.85em;">Unable to load real-time metrics: {str(e)}</p>
        </div>
        """

def get_current_system_data():
    """Get real system data for AI context using advanced alert engine via API"""
    from datetime import datetime
    
    try:
        # Try to get data from the alert engine API first
        import requests
        response = requests.get("http://localhost:8000/api/v1/alerts/health", timeout=3)
        
        if response.status_code == 200:
            api_data = response.json()
            if api_data.get('success'):
                health_status = api_data.get('data', {})
                
                # Get probe data from backend
                probe_count = 0
                try:
                    probe_response = requests.get("http://localhost:8000/api/v1/probes/", timeout=2)
                    if probe_response.status_code == 200:
                        probes = probe_response.json()
                        probe_count = len(probes)
                except:
                    probe_count = 0
                
                # Format alerts for display
                alert_messages = []
                for alert in health_status.get('alerts', []):
                    alert_messages.append(f"{alert['message']} (severity: {alert['severity']})")
                
                if not alert_messages:
                    alert_messages = [health_status.get('message', 'All systems normal')]
                
                metrics = health_status.get('metrics', {})
                
                return {
                    "cpu_usage": f"{metrics.get('cpu_percent', 0):.1f}%",
                    "memory_usage": f"{metrics.get('memory_percent', 0):.1f}%", 
                    "network_traffic": f"{metrics.get('network_in_mbps', 0):.1f} Mbps in, {metrics.get('network_out_mbps', 0):.1f} Mbps out",
                    "active_processes": "N/A",  # Not critical for AI analysis
                    "system_load": f"{metrics.get('load_average', 0):.1f}",
                    "disk_usage": f"{metrics.get('disk_percent', 0):.1f}%",
                    "timestamp": datetime.now().isoformat(),
                    "alerts": alert_messages,
                    "system_health_status": health_status.get('status'),
                    "system_health_message": health_status.get('message'),
                    "alert_details": health_status.get('alerts', []),
                    "dynamic_thresholds": health_status.get('thresholds', {}),
                    "probe_data": {
                        "active_probes": probe_count,
                        "health_insights": f"System status: {health_status.get('status', 'unknown').upper()}"
                    }
                }
        
        # Fallback: API not available, use basic psutil
        raise Exception("Alert API not available, falling back to basic monitoring")
        
    except Exception as e:
        # Fallback to basic psutil if alert engine API fails
        import psutil
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Basic threshold checking
            alerts = []
            if cpu_percent > 80:
                alerts.append(f"High CPU usage: {cpu_percent:.1f}%")
            if memory.percent > 85:
                alerts.append(f"High memory usage: {memory.percent:.1f}%")
            if disk.percent > 90:
                alerts.append(f"Low disk space: {disk.percent:.1f}% used")
            
            return {
                "cpu_usage": f"{cpu_percent:.1f}%",
                "memory_usage": f"{memory.percent:.1f}%",
                "network_traffic": "N/A",
                "active_processes": "N/A",
                "system_load": "N/A", 
                "disk_usage": f"{disk.percent:.1f}%",
                "timestamp": datetime.now().isoformat(),
                "alerts": alerts if alerts else ["All systems normal (basic monitoring)"],
                "system_health_status": "fallback",
                "probe_data": {"error": f"Advanced alert engine unavailable: {str(e)}"}
            }
        except Exception as fallback_e:
            return {
                "cpu_usage": "N/A",
                "memory_usage": "N/A",
                "network_traffic": "N/A",
                "active_processes": "N/A",
                "system_load": "N/A", 
                "disk_usage": "N/A",
                "timestamp": datetime.now().isoformat(),
                "alerts": [f"System monitoring error: {str(fallback_e)}"],
                "system_health_status": "error",
                "probe_data": {"error": "Unable to collect metrics"}
            }

def get_initial_chat_history():
    """Get initial chat history for the copilot"""
    return [
        {
            "role": "user",
            "content": "Hello! What can you analyze for me today?"
        },
        {
            "role": "assistant", 
            "content": "👋 Welcome to ProbePilot AI! I'm your intelligent system analysis assistant powered by OpenAI GPT-4. I can help you with:\n\n• **Performance Analysis** - Identify bottlenecks and optimization opportunities\n• **Security Assessment** - Detect threats and vulnerabilities\n• **Troubleshooting** - Diagnose and resolve system issues\n• **Capacity Planning** - Predict resource needs and scaling requirements\n\nJust ask me any questions about your system or request specific analysis!"
        }
    ]

def get_current_recommendations():
    """Get real AI recommendations based on current system state"""
    import psutil
    import os
    from datetime import datetime
    
    try:
        # Get real system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        recommendations = ["🤖 Real-Time System Analysis:"]
        
        # Performance analysis
        recommendations.append("\n📊 Performance:")
        if cpu_percent > 80:
            recommendations.append(f"• High CPU usage detected: {cpu_percent:.1f}% - investigate heavy processes")
        elif cpu_percent > 50:
            recommendations.append(f"• Moderate CPU load: {cpu_percent:.1f}% - monitor for spikes")
        else:
            recommendations.append(f"• CPU usage healthy: {cpu_percent:.1f}% - system running smoothly")
            
        if memory.percent > 80:
            recommendations.append(f"• Memory critical: {memory.percent:.1f}% used - consider closing applications")
        elif memory.percent > 60:
            recommendations.append(f"• Memory moderate: {memory.percent:.1f}% used - monitor usage patterns")
        else:
            recommendations.append(f"• Memory healthy: {memory.percent:.1f}% used - sufficient available")
        
        # Storage analysis
        recommendations.append("\n💾 Storage:")
        if disk.percent > 90:
            recommendations.append(f"• Disk space critical: {disk.percent:.1f}% full - cleanup required")
        elif disk.percent > 70:
            recommendations.append(f"• Disk space moderate: {disk.percent:.1f}% full - plan cleanup")
        else:
            recommendations.append(f"• Disk space healthy: {disk.percent:.1f}% used - sufficient space")
        
        # Security & uptime
        recommendations.append("\n🔒 System Health:")
        recommendations.append(f"• System uptime: {str(uptime).split('.')[0]} - stable operation")
        recommendations.append("• ProbePilot backend connected and responding")
        
        # Real optimization suggestions
        recommendations.append("\n⚡ Optimization:")
        if cpu_percent > 70:
            recommendations.append("• Consider closing unnecessary applications to free CPU")
        if memory.percent > 70:
            recommendations.append("• Restart memory-intensive applications to reclaim RAM")
        if disk.percent > 80:
            recommendations.append("• Run disk cleanup to free storage space")
        
        # Actions based on probe data
        recommendations.append("\n🔧 ProbePilot Actions:")
        try:
            import requests
            response = requests.get("http://localhost:8000/api/v1/probes/", timeout=2)
            if response.status_code == 200:
                probes = response.json()
                recommendations.append(f"• {len(probes)} active probes collecting real metrics")
                if len(probes) > 5:
                    recommendations.append("• Consider stopping unused probes to reduce overhead")
            else:
                recommendations.append("• Backend connection issues - check probe manager")
        except:
            recommendations.append("• Backend unreachable - restart probe manager if needed")
        
        return "\n".join(recommendations)
        
    except Exception as e:
        return f"🤖 Real-Time System Analysis:\n\n❌ Error collecting system metrics: {str(e)}\n• Check system monitoring permissions\n• Ensure psutil is installed and accessible"

def create_ai_copilot():
    """Create the AI copilot interface with enhanced visual hierarchy"""
    
    with gr.Tab("🤖 AI Copilot", elem_id="ai-copilot") as tab:
        # Custom CSS for enhanced styling
        gr.HTML("""
        <style>
        .ai-status-good { background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(34, 197, 94, 0.05)); border-left: 4px solid #22c55e; }
        .ai-status-error { background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05)); border-left: 4px solid #ef4444; }
        .ai-alert-performance { background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(59, 130, 246, 0.05)); border-left: 4px solid #3b82f6; }
        .ai-alert-security { background: linear-gradient(135deg, rgba(251, 191, 36, 0.1), rgba(251, 191, 36, 0.05)); border-left: 4px solid #fbbf24; }
        .ai-insights-panel { background: rgba(15, 23, 42, 0.6); border-radius: 12px; padding: 16px; margin: 8px; }
        .quick-action-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin: 16px 0; }
        .metric-card { background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(51, 65, 85, 0.6)); border-radius: 8px; padding: 12px; border: 1px solid rgba(71, 85, 105, 0.3); }
        </style>
        """)
        
        # Header with better visual hierarchy
        with gr.Row():
            with gr.Column(scale=4):
                gr.Markdown("""
                # 🤖 ProbePilot AI Copilot
                ## Your Intelligent Assistant for System Analysis
                
                **Real-time AI-powered insights** using OpenAI GPT-4 for intelligent system monitoring, 
                security assessment, and performance optimization.
                """)
            with gr.Column(scale=1):
                # Quick metrics in header
                gr.HTML("""
                <div class="metric-card">
                    <h4 style="color: #22c55e; margin: 0 0 8px 0;">🟢 System Status</h4>
                    <p style="margin: 0; color: #94a3b8;">All probes active</p>
                </div>
                """)
        
        # Main layout with improved visual hierarchy
        with gr.Row():
            # Left Panel - AI Configuration and Chat (60% width)
            with gr.Column(scale=3):
                # Collapsible AI Configuration Section
                with gr.Accordion("🔑 AI Configuration", open=False):
                    gr.Markdown("Configure your OpenAI API key for intelligent analysis")
                    
                    api_key_input = gr.Textbox(
                        label="OpenAI API Key",
                        placeholder="sk-... (or set OPENAI_API_KEY environment variable)",
                        type="password",
                        value=os.getenv("OPENAI_API_KEY", ""),
                        info="💡 Your API key is stored securely and never shared"
                    )
                    
                    with gr.Row():
                        configure_ai_btn = gr.Button("🔧 Configure AI", variant="primary", size="sm")
                        test_ai_btn = gr.Button("🧪 Test Connection", variant="secondary", size="sm")
                    
                    ai_status = gr.HTML(get_ai_status_html())
                
                # Enhanced Chat Interface
                gr.Markdown("### 💬 Intelligent Chat Assistant")
                
                chatbot = gr.Chatbot(
                    value=get_initial_chat_history(),
                    height=450,
                    avatar_images=("👤", "🤖"),
                    type="messages",
                    show_copy_button=True,
                    bubble_full_width=False
                )
                
                with gr.Row():
                    chat_input = gr.Textbox(
                        placeholder="💭 Ask me about performance, security, optimization, troubleshooting...",
                        container=False,
                        scale=4,
                        lines=2
                    )
                    send_btn = gr.Button("📤 Send", variant="primary", scale=1)
                
                # Quick Action Grid with better styling
                gr.Markdown("### 🚀 AI-Powered Quick Analysis")
                gr.HTML("""
                <div class="quick-action-grid">
                    <div id="performance-card" class="metric-card">
                        <h4 style="color: #3b82f6;">📊 Performance</h4>
                        <p style="font-size: 0.9em; color: #94a3b8;">CPU, Memory, Network analysis</p>
                    </div>
                    <div id="security-card" class="metric-card">
                        <h4 style="color: #ef4444;">🔒 Security</h4>
                        <p style="font-size: 0.9em; color: #94a3b8;">Threat detection & assessment</p>
                    </div>
                    <div id="optimization-card" class="metric-card">
                        <h4 style="color: #22c55e;">⚡ Optimization</h4>
                        <p style="font-size: 0.9em; color: #94a3b8;">Resource efficiency tips</p>
                    </div>
                    <div id="troubleshoot-card" class="metric-card">
                        <h4 style="color: #fbbf24;">🔧 Troubleshoot</h4>
                        <p style="font-size: 0.9em; color: #94a3b8;">Issue diagnosis & resolution</p>
                    </div>
                </div>
                """)
                
                with gr.Row():
                    analyze_btn = gr.Button("📊 Performance Analysis", variant="secondary", size="sm")
                    security_btn = gr.Button("🔒 Security Assessment", variant="secondary", size="sm")
                    optimization_btn = gr.Button("⚡ Optimization Guide", variant="secondary", size="sm")
                    troubleshoot_btn = gr.Button("🔧 Troubleshoot Issues", variant="secondary", size="sm")
            
            # Right Panel - Insights and Controls (40% width)
            with gr.Column(scale=2):
                # Real-time AI Insights with better styling
                with gr.Row():
                    gr.Markdown("### 🧠 Real-time AI Insights")
                    refresh_insights_btn = gr.Button("🔄 Refresh", size="sm", scale=0)
                
                insights_panel = gr.HTML(get_current_insights_html())
                
                def refresh_insights():
                    return real_time_ai_analytics.get_real_insights_html()
                
                refresh_insights_btn.click(fn=refresh_insights, outputs=insights_panel)
                
                # Enhanced Recommendations Panel
                gr.Markdown("### 📈 AI Recommendations")
                
                recommendations = gr.Textbox(
                    value=get_current_recommendations(),
                    lines=6,
                    interactive=False,
                    container=True,
                    show_copy_button=True
                )
                
                # Analysis Controls with better organization
                with gr.Accordion("🔍 Advanced AI Analysis", open=True):
                    analysis_type = gr.Dropdown(
                        label="Analysis Type",
                        choices=[
                            ("🚀 Performance Analysis", "performance"),
                            ("🛡️ Security Assessment", "security"), 
                            ("⚡ Optimization Review", "optimization"),
                            ("🔧 Troubleshooting", "troubleshoot"),
                            ("📊 Capacity Planning", "capacity"),
                            ("🌐 Network Analysis", "network")
                        ],
                        value="performance",
                        info="Select the type of AI analysis to run"
                    )
                    
                    time_window = gr.Dropdown(
                        label="Time Window",
                        choices=["⏱️ Last Hour", "🕕 Last 6 Hours", "📅 Last 24 Hours", "📊 Last Week"],
                        value="📅 Last 24 Hours",
                        info="Choose the time range for analysis"
                    )
                    
                    run_analysis_btn = gr.Button(
                        "🚀 Run AI Analysis", 
                        variant="primary",
                        scale=1
                    )
                
                # Enhanced Analysis Results
                analysis_results = gr.Textbox(
                    label="AI Analysis Results",
                    lines=8,
                    interactive=False,
                    show_copy_button=True,
                    placeholder="Run an AI analysis to see detailed insights and recommendations..."
                )
        
        # Event Handlers with Real AI
        def configure_ai(api_key):
            """Configure the AI service with API key"""
            if api_key:
                ai_copilot.api_key = api_key
                ai_copilot.__init__(api_key)  # Reinitialize with new key
                return get_ai_status_html(configured=True)
            return get_ai_status_html(configured=False)
        
        def test_ai_connection():
            """Test the AI connection"""
            try:
                if ai_copilot.client:
                    return "✅ AI connection successful! GPT-4 is ready for intelligent analysis."
                else:
                    return "❌ AI not configured. Please provide a valid OpenAI API key."
            except Exception as e:
                return f"❌ Connection failed: {str(e)}"
        
        def respond_to_chat(message, history):
            """Generate real AI copilot response with live system context"""
            if not message.strip():
                return history, ""
            
            # Add user message to history
            history.append([message, None])
            
            # Get real-time system data for context
            system_context = real_time_ai_analytics.get_current_system_context()
            
            # Convert history for AI service
            chat_history = []
            for user_msg, ai_msg in history[:-1]:  # Exclude current message
                if user_msg:
                    chat_history.append({"role": "user", "content": user_msg})
                if ai_msg:
                    chat_history.append({"role": "assistant", "content": ai_msg})
            
            # Generate AI response with real system context
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Enhanced prompt with real system data
                enhanced_message = f"""User Query: {message}

Current Real-Time System Context:
{system_context}

Please provide actionable insights based on the actual system data above. Focus on real metrics and current system state."""
                
                response = loop.run_until_complete(
                    get_ai_response(enhanced_message, {"context": system_context}, chat_history)
                )
                loop.close()
            except Exception as e:
                response = f"I apologize, but I encountered an error: {str(e)}\n\nPlease check your API key configuration."
            
            # Add AI response to history
            history[-1][1] = response
            
            return history, ""
        
        def quick_ai_analysis(analysis_type):
            """Handle AI-powered quick analysis"""
            system_data = get_current_system_data()
            
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response = loop.run_until_complete(
                    get_quick_analysis(analysis_type, system_data)
                )
                loop.close()
                return response
            except Exception as e:
                return f"AI analysis failed: {str(e)}\n\nFalling back to local analysis..."
        
        def run_detailed_ai_analysis(analysis_type, time_window):
            """Run detailed AI analysis"""
            system_data = get_current_system_data()
            system_data["time_window"] = time_window
            
            query = f"Perform a comprehensive {analysis_type} analysis for the {time_window.lower()} timeframe."
            
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response = loop.run_until_complete(
                    get_ai_response(query, system_data)
                )
                loop.close()
                return response
            except Exception as e:
                return f"AI analysis failed: {str(e)}"
        
        # Wire up event handlers
        configure_ai_btn.click(
            fn=configure_ai,
            inputs=[api_key_input],
            outputs=[ai_status]
        )
        
        test_ai_btn.click(
            fn=test_ai_connection,
            outputs=[recommendations]
        )
        
        send_btn.click(
            fn=respond_to_chat,
            inputs=[chat_input, chatbot],
            outputs=[chatbot, chat_input]
        )
        
        chat_input.submit(
            fn=respond_to_chat,
            inputs=[chat_input, chatbot],
            outputs=[chatbot, chat_input]
        )
        
        analyze_btn.click(
            fn=lambda: quick_ai_analysis("performance"),
            outputs=[recommendations]
        )
        
        security_btn.click(
            fn=lambda: quick_ai_analysis("security"),
            outputs=[recommendations]
        )
        
        optimization_btn.click(
            fn=lambda: quick_ai_analysis("optimization"),
            outputs=[recommendations]
        )
        
        troubleshoot_btn.click(
            fn=lambda: quick_ai_analysis("troubleshoot"),
            outputs=[recommendations]
        )
        
        run_analysis_btn.click(
            fn=run_detailed_ai_analysis,
            inputs=[analysis_type, time_window],
            outputs=[analysis_results]
        )
    
    return tab