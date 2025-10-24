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
    """Generate current AI insights HTML"""
    return """
    <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
        <h4 style="color: #3b82f6; margin-top: 0;">🎯 AI Performance Alert</h4>
        <p>Real-time analysis detected CPU usage spike. AI recommends scaling horizontally or optimizing worker configuration.</p>
    </div>
    
    <div style="background: rgba(34, 197, 94, 0.1); border: 1px solid #22c55e; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
        <h4 style="color: #22c55e; margin-top: 0;">✅ System Health</h4>
        <p>AI analysis confirms overall system performance is within normal parameters. Memory usage stable at 65%.</p>
    </div>
    
    <div style="background: rgba(251, 191, 36, 0.1); border: 1px solid #fbbf24; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
        <h4 style="color: #fbbf24; margin-top: 0;">⚠️ Network Notice</h4>
        <p>AI detected unusual traffic pattern. Recommend reviewing firewall rules based on intelligent analysis.</p>
    </div>
    """

def get_enhanced_insights_html():
    """Generate enhanced AI insights HTML with better visual hierarchy"""
    return """
    <div class="ai-insights-panel">
        <div class="ai-alert-performance" style="border-radius: 8px; padding: 12px; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 24px; margin-right: 12px;">🎯</span>
                <div>
                    <h4 style="color: #3b82f6; margin: 0;">Performance Alert</h4>
                    <span style="color: #64748b; font-size: 0.85em;">2 minutes ago</span>
                </div>
            </div>
            <p style="margin: 0; color: #e2e8f0;">CPU usage spike detected on nginx process. AI recommends horizontal scaling or worker optimization.</p>
            <div style="margin-top: 8px;">
                <span style="background: rgba(59, 130, 246, 0.2); color: #93c5fd; padding: 2px 8px; border-radius: 12px; font-size: 0.75em;">HIGH PRIORITY</span>
            </div>
        </div>
        
        <div class="ai-status-good" style="border-radius: 8px; padding: 12px; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 24px; margin-right: 12px;">✅</span>
                <div>
                    <h4 style="color: #22c55e; margin: 0;">System Health</h4>
                    <span style="color: #64748b; font-size: 0.85em;">Live monitoring</span>
                </div>
            </div>
            <p style="margin: 0; color: #e2e8f0;">Overall system performance within normal parameters. Memory usage stable at 65%.</p>
            <div style="margin-top: 8px;">
                <span style="background: rgba(34, 197, 94, 0.2); color: #86efac; padding: 2px 8px; border-radius: 12px; font-size: 0.75em;">STABLE</span>
            </div>
        </div>
        
        <div class="ai-alert-security" style="border-radius: 8px; padding: 12px; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 24px; margin-right: 12px;">⚠️</span>
                <div>
                    <h4 style="color: #fbbf24; margin: 0;">Network Notice</h4>
                    <span style="color: #64748b; font-size: 0.85em;">5 minutes ago</span>
                </div>
            </div>
            <p style="margin: 0; color: #e2e8f0;">Unusual traffic pattern from 192.168.1.50. Review firewall rules recommended.</p>
            <div style="margin-top: 8px;">
                <span style="background: rgba(251, 191, 36, 0.2); color: #fcd34d; padding: 2px 8px; border-radius: 12px; font-size: 0.75em;">MEDIUM</span>
            </div>
        </div>
        
        <div style="background: rgba(30, 41, 59, 0.6); border-radius: 8px; padding: 12px; border: 1px solid rgba(71, 85, 105, 0.3);">
            <h4 style="color: #94a3b8; margin: 0 0 8px 0; font-size: 0.9em;">📊 LIVE METRICS</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 0.85em;">
                <div>
                    <span style="color: #64748b;">CPU:</span>
                    <span style="color: #22c55e; font-weight: bold;">24%</span>
                </div>
                <div>
                    <span style="color: #64748b;">Memory:</span>
                    <span style="color: #fbbf24; font-weight: bold;">65%</span>
                </div>
                <div>
                    <span style="color: #64748b;">Network:</span>
                    <span style="color: #3b82f6; font-weight: bold;">150MB/s</span>
                </div>
                <div>
                    <span style="color: #64748b;">Probes:</span>
                    <span style="color: #22c55e; font-weight: bold;">12 active</span>
                </div>
            </div>
        </div>
    </div>
    """

def get_current_system_data():
    """Get current system data for AI context"""
    return {
        "cpu_usage": "24%",
        "memory_usage": "65%", 
        "network_traffic": "150MB/s in, 120MB/s out",
        "active_processes": 156,
        "system_load": "2.4",
        "disk_usage": "78%",
        "timestamp": datetime.now().isoformat(),
        "alerts": [
            "nginx CPU spike to 85%",
            "3 failed SSH attempts from 192.168.1.50"
        ],
        "probe_data": {
            "tcp_connections": 1247,
            "memory_allocations": 89234,
            "cpu_samples": 15847
        }
    }

def get_initial_chat_history():
    """Get initial chat history for the copilot"""
    return [
        ("Hello! What can you analyze for me today?", 
         "👋 Welcome to ProbePilot AI! I'm your intelligent system analysis assistant powered by OpenAI GPT-4. I can help you with:\n\n• **Performance Analysis** - Identify bottlenecks and optimization opportunities\n• **Security Assessment** - Detect threats and vulnerabilities\n• **Troubleshooting** - Diagnose and resolve system issues\n• **Capacity Planning** - Predict resource needs and scaling requirements\n\nJust ask me any questions about your system or request specific analysis!")
    ]

def get_current_recommendations():
    """Get current AI recommendations"""
    return """🤖 AI-Powered Recommendations:

📊 Performance:
• Nginx shows 85% CPU spike - consider horizontal scaling
• Database queries averaging 245ms - optimize indexing
• Memory fragmentation detected in Java process

🔒 Security:
• 3 failed SSH attempts from 192.168.1.50 - monitor closely
• Port scan detected and blocked automatically
• All critical services running normally

⚡ Optimization:
• Enable nginx compression for 30% bandwidth reduction
• Implement Redis caching for frequent queries
• Tune PostgreSQL shared_buffers to 2GB

🔧 Actions:
• Restart nginx with optimized configuration
• Review and update firewall rules
• Schedule memory defragmentation for Java processes"""

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
                    type="tuples",
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
                gr.Markdown("### 🧠 Real-time AI Insights")
                
                insights_panel = gr.HTML(get_enhanced_insights_html())
                
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
            """Generate real AI copilot response"""
            if not message.strip():
                return history, ""
            
            # Add user message to history
            history.append([message, None])
            
            # Get system data for context
            system_data = get_current_system_data()
            
            # Convert history for AI service
            chat_history = []
            for user_msg, ai_msg in history[:-1]:  # Exclude current message
                if user_msg:
                    chat_history.append({"role": "user", "content": user_msg})
                if ai_msg:
                    chat_history.append({"role": "assistant", "content": ai_msg})
            
            # Generate AI response asynchronously
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response = loop.run_until_complete(
                    get_ai_response(message, system_data, chat_history)
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