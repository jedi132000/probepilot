"""
AI Copilot Component
Intelligent assistance for system analysis and troubleshooting
"""

import gradio as gr
import json
from datetime import datetime
import random

def create_ai_copilot():
    """Create the AI copilot interface"""
    
    with gr.Tab("🤖 AI Copilot", elem_id="ai-copilot") as tab:
        with gr.Row():
            gr.Markdown("""
            # 🤖 ProbePilot AI Copilot
            ## Your Intelligent Assistant for System Analysis
            
            Ask questions about your system's behavior, get insights from telemetry data,
            and receive recommendations for performance optimization and troubleshooting.
            """)
        
        with gr.Row():
            # Chat Interface
            with gr.Column(scale=2):
                gr.Markdown("### 💬 Chat with Copilot")
                
                chatbot = gr.Chatbot(
                    value=get_initial_chat_history(),
                    height=400,
                    avatar_images=("👤", "🤖")
                )
                
                with gr.Row():
                    chat_input = gr.Textbox(
                        placeholder="Ask me about your system performance, security events, or any issues...",
                        container=False,
                        scale=4
                    )
                    send_btn = gr.Button("Send", variant="primary", scale=1)
                
                # Quick Action Buttons
                with gr.Row():
                    gr.Markdown("**Quick Actions:**")
                
                with gr.Row():
                    analyze_btn = gr.Button("📊 Analyze Current Performance", size="sm")
                    security_btn = gr.Button("🔒 Security Summary", size="sm")
                    optimization_btn = gr.Button("⚡ Optimization Tips", size="sm")
                    troubleshoot_btn = gr.Button("🔧 Troubleshoot Issues", size="sm")
            
            # Insights Panel
            with gr.Column(scale=1):
                gr.Markdown("### 🧠 AI Insights")
                
                insights_panel = gr.HTML("""
                <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
                    <h4 style="color: #3b82f6; margin-top: 0;">🎯 Performance Alert</h4>
                    <p>CPU usage spike detected on nginx process. Consider scaling horizontally or optimizing worker configuration.</p>
                </div>
                
                <div style="background: rgba(34, 197, 94, 0.1); border: 1px solid #22c55e; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
                    <h4 style="color: #22c55e; margin-top: 0;">✅ System Health</h4>
                    <p>Overall system performance is within normal parameters. Memory usage stable at 65%.</p>
                </div>
                
                <div style="background: rgba(251, 191, 36, 0.1); border: 1px solid #fbbf24; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
                    <h4 style="color: #fbbf24; margin-top: 0;">⚠️ Network Notice</h4>
                    <p>Unusual traffic pattern detected from 192.168.1.50. Recommend reviewing firewall rules.</p>
                </div>
                """)
                
                gr.Markdown("### 📈 Recommendations")
                
                recommendations = gr.Textbox(
                    value=get_current_recommendations(),
                    lines=8,
                    interactive=False,
                    container=True
                )
        
        # Analysis Tools
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 🔍 Analysis Tools")
                
                analysis_type = gr.Dropdown(
                    label="Analysis Type",
                    choices=[
                        "Performance Bottleneck Analysis",
                        "Security Threat Assessment", 
                        "Resource Optimization",
                        "Anomaly Detection",
                        "Capacity Planning",
                        "Root Cause Analysis"
                    ],
                    value="Performance Bottleneck Analysis"
                )
                
                time_window = gr.Dropdown(
                    label="Time Window",
                    choices=["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last Week"],
                    value="Last 24 Hours"
                )
                
                run_analysis_btn = gr.Button("🚀 Run Analysis", variant="primary")
                
                analysis_results = gr.Textbox(
                    label="Analysis Results",
                    lines=10,
                    interactive=False
                )
        
        # Event Handlers
        def respond_to_chat(message, history):
            """Generate AI copilot response"""
            if not message.strip():
                return history, ""
            
            # Add user message to history
            history.append([message, None])
            
            # Generate AI response based on message content
            response = generate_ai_response(message)
            
            # Add AI response to history
            history.append([None, response])
            
            return history, ""
        
        def quick_action(action_type):
            """Handle quick action buttons"""
            responses = {
                "analyze": "📊 **Current Performance Analysis:**\n\n• CPU: 24% average, nginx showing 85% spike\n• Memory: 65% usage, stable allocation patterns\n• Network: 150MB/s inbound, 120MB/s outbound\n• Disk I/O: Normal patterns, no bottlenecks detected\n\n**Recommendation:** Scale nginx horizontally to handle increased load.",
                
                "security": "🔒 **Security Summary:**\n\n• 3 failed SSH attempts from 192.168.1.50\n• Port scan detected and blocked\n• All critical services running with normal patterns\n• No malware signatures detected\n\n**Status:** Low threat level, continue monitoring external IPs.",
                
                "optimization": "⚡ **Optimization Opportunities:**\n\n• Enable nginx compression to reduce bandwidth by 30%\n• Tune PostgreSQL shared_buffers to 2GB\n• Implement Redis caching for frequent queries\n• Consider upgrading to SSD for database storage\n\n**Estimated Impact:** 15-25% performance improvement",
                
                "troubleshoot": "🔧 **Current Issues Detected:**\n\n• High CPU usage on nginx (PID: 1234)\n• Memory fragmentation in java process\n• Slow disk response times > 10ms\n\n**Solutions:**\n1. Restart nginx with optimized config\n2. Tune JVM garbage collection\n3. Check disk health and defragmentation"
            }
            
            return responses.get(action_type, "Analysis complete.")
        
        def run_detailed_analysis(analysis_type, time_window):
            """Run detailed analysis based on selected parameters"""
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            analysis_results = f"""
🔍 **{analysis_type}** - {time_window}
Generated at: {timestamp}

📊 **Key Findings:**
• Analyzed 15,847 data points from {time_window.lower()}
• Detected 3 performance anomalies
• Identified 2 optimization opportunities
• No critical security threats found

🎯 **Performance Metrics:**
• Average Response Time: 245ms (+12% from baseline)
• Error Rate: 0.08% (within acceptable range)
• Throughput: 1,247 req/sec (-5% from peak)
• Resource Utilization: 67% (optimal range)

💡 **Recommendations:**
1. Optimize database query execution plans
2. Implement connection pooling for web tier
3. Enable compression for static assets
4. Consider CDN for improved response times

⚠️ **Alerts:**
• CPU spike detected at 15:30 (resolved)
• Memory usage trending upward (monitor)
• Network latency increased 8% (investigate)

📈 **Trend Analysis:**
Overall system performance remains stable with minor optimization opportunities identified.
"""
            
            return analysis_results
        
        # Wire up event handlers
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
            fn=lambda: quick_action("analyze"),
            outputs=[recommendations]
        )
        
        security_btn.click(
            fn=lambda: quick_action("security"),
            outputs=[recommendations]
        )
        
        optimization_btn.click(
            fn=lambda: quick_action("optimization"),
            outputs=[recommendations]
        )
        
        troubleshoot_btn.click(
            fn=lambda: quick_action("troubleshoot"),
            outputs=[recommendations]
        )
        
        run_analysis_btn.click(
            fn=run_detailed_analysis,
            inputs=[analysis_type, time_window],
            outputs=[analysis_results]
        )
    
    return tab

def get_initial_chat_history():
    """Get initial chat history to welcome users"""
    return [
        [None, "👋 Hello! I'm your ProbePilot AI Copilot. I can help you analyze system performance, troubleshoot issues, and optimize your infrastructure. What would you like to know about your system?"],
        ["What's the current system status?", "🟢 Your system is running well! Here's a quick overview:\n\n• **CPU Usage:** 24% (Normal)\n• **Memory:** 8.2GB used / 16GB total (51%)\n• **Active Probes:** 12 running successfully\n• **Network:** 150MB/s inbound traffic\n\nI notice nginx is showing higher CPU usage than usual. Would you like me to investigate further?"],
        ["Yes, please check the nginx performance", "🔍 I've analyzed the nginx performance data:\n\n**Findings:**\n• CPU usage spiked to 85% at 15:30\n• Request queue length increased to 127\n• Response time average: 245ms (+45ms from baseline)\n\n**Root Cause:** Traffic surge from new marketing campaign\n\n**Recommendations:**\n1. Scale nginx horizontally (add 2 more instances)\n2. Enable response caching for static content\n3. Implement rate limiting for API endpoints\n\nWould you like me to generate the configuration changes?"]
    ]

def generate_ai_response(message):
    """Generate contextual AI response based on user message"""
    message_lower = message.lower()
    
    # Performance-related queries
    if any(word in message_lower for word in ['performance', 'slow', 'cpu', 'memory', 'speed']):
        return """🚀 **Performance Analysis:**

I've analyzed your system performance metrics:

• **Current CPU:** 24% average, with nginx showing elevated usage
• **Memory Status:** 8.2GB/16GB used (healthy level)
• **Response Times:** Web services averaging 245ms
• **Throughput:** 1,247 requests/second

**Immediate Actions Recommended:**
1. Scale nginx worker processes from 4 to 8
2. Enable compression to reduce bandwidth by 30%
3. Implement Redis caching for database queries

Would you like me to generate the specific configuration changes?"""
    
    # Security-related queries
    elif any(word in message_lower for word in ['security', 'attack', 'threat', 'intrusion', 'malware']):
        return """🔒 **Security Status Report:**

Current threat level: **LOW** 🟢

**Recent Security Events:**
• 3 failed SSH attempts from 192.168.1.50 (blocked)
• Port scan detected and automatically mitigated
• All critical services showing normal authentication patterns

**Security Posture:**
• Firewall: Active with 47 rules
• IDS/IPS: Monitoring 15 threat feeds
• Certificate Status: All valid, none expiring soon

**Recommendations:**
1. Consider IP blocking for 192.168.1.50
2. Enable two-factor authentication for SSH
3. Review and update security policies quarterly

Need help with any specific security concerns?"""
    
    # Network-related queries
    elif any(word in message_lower for word in ['network', 'connection', 'bandwidth', 'latency']):
        return """🌐 **Network Analysis:**

**Current Network Status:**
• Inbound Traffic: 150MB/s (normal range)
• Outbound Traffic: 120MB/s (normal range)
• Active Connections: 2,847 TCP, 456 UDP
• Latency: 45ms average (good performance)

**Top Connections:**
1. 192.168.1.100 → api.example.com:443 (HTTPS)
2. 192.168.1.101 → db.internal:5432 (PostgreSQL)
3. 192.168.1.102 → cache.internal:6379 (Redis)

**Network Health:** ✅ All connections stable

**Optimization Opportunities:**
• Enable connection pooling for database connections
• Implement CDN for static content delivery
• Consider upgrading to HTTP/3 for improved performance

Any specific network issues you'd like me to investigate?"""
    
    # Error or problem-related queries
    elif any(word in message_lower for word in ['error', 'problem', 'issue', 'fail', 'down']):
        return """🔧 **Issue Analysis:**

I've scanned your system for current issues:

**Active Issues Detected:**
1. **Medium Priority:** nginx CPU usage spike (85%) 
   - *Resolution:* Scale horizontally or optimize config
   
2. **Low Priority:** PostgreSQL query performance 
   - *Resolution:* Update statistics and reindex tables

**Recent Resolved Issues:**
• Network timeout resolved at 14:45
• Memory leak in python process fixed automatically
• SSL certificate renewal completed successfully

**System Health Score:** 87/100 (Good)

**Next Steps:**
1. Address nginx scaling immediately
2. Schedule database maintenance window
3. Monitor memory usage trends

Would you like detailed troubleshooting steps for any of these issues?"""
    
    # Default response for other queries
    else:
        responses = [
            """I'm here to help with your system observability needs! I can assist with:

🔍 **Performance Analysis** - CPU, memory, and application performance
🔒 **Security Monitoring** - Threat detection and security posture
🌐 **Network Analysis** - Traffic patterns and connectivity issues
🛠️ **Troubleshooting** - Root cause analysis and resolution steps
📊 **Data Insights** - Trends, anomalies, and optimization opportunities

What specific aspect of your system would you like to explore?""",

            """Based on your current telemetry data, here's what I'm monitoring:

• **12 Active Probes** collecting real-time data
• **15,847 Events** processed in the last hour
• **3 Minor Alerts** requiring attention
• **Overall System Health:** 87/100

Is there a particular metric or system component you'd like me to focus on?""",

            """I can provide insights on various aspects of your infrastructure:

**Available Analysis Types:**
1. Performance bottleneck identification
2. Security threat assessment
3. Resource optimization recommendations
4. Anomaly detection and alerting
5. Capacity planning assistance
6. Root cause analysis for issues

Which type of analysis would be most helpful right now?"""
        ]
        
        return random.choice(responses)

def get_current_recommendations():
    """Get current system recommendations"""
    return """🎯 **Current Recommendations:**

• Scale nginx horizontally (add 2 instances)
• Enable compression for static assets  
• Implement Redis caching layer
• Update PostgreSQL query plans
• Review firewall rules for 192.168.1.50

📈 **Performance Impact:**
• Estimated 25% response time improvement
• 30% reduction in bandwidth usage
• 15% decrease in database load

⏱️ **Implementation Priority:**
1. High: nginx scaling (immediate)
2. Medium: caching implementation (this week)
3. Low: database optimization (next sprint)"""