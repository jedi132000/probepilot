# ProbePilot Brand Guidelines 🎨

## Brand Identity

**ProbePilot** represents precision, control, and navigation in the complex world of infrastructure observability. Our aviation-inspired theme conveys expertise, reliability, and the ability to navigate through challenging technical terrain.

## Logo Inspiration

### Visual Concepts
- **Pilot's Dashboard**: Control sticks, cockpit gauges, aviation instruments
- **Radar/Navigation**: Subtle "radar" or "trace" lines circling a central point
- **Flight Path**: Clean lines suggesting navigation and trajectory
- **Mission Control**: Command center aesthetics with modern tech styling

### Style Guidelines
- **Modern and Clean**: Avoid overly complex designs
- **Professional**: Suitable for enterprise and developer audiences
- **Memorable**: Distinctive enough to stand out in the observability space
- **Scalable**: Works well from favicon size to large displays

## Color Palette

### Primary Colors
- **Mission Blue**: `#1E3A8A` - Trust, stability, technology
- **Sky Blue**: `#3B82F6` - Innovation, clarity, openness
- **Cockpit Green**: `#10B981` - Success, monitoring, "all systems go"

### Secondary Colors
- **Alert Orange**: `#F59E0B` - Attention, warnings, action required
- **Deep Purple**: `#7C3AED` - Advanced technology, depth
- **Neutral Gray**: `#6B7280` - Professional, balanced

### Usage Guidelines
- **Primary Brand Color**: Mission Blue for logos and headers
- **UI Accents**: Sky Blue for interactive elements
- **Success States**: Cockpit Green for positive indicators
- **Warnings/Alerts**: Alert Orange for attention-grabbing elements
- **Text/Secondary**: Neutral Gray for body text and secondary elements

## Typography

### Recommended Fonts
- **Headlines**: Inter, Roboto, or system fonts with clean, modern aesthetics
- **Body Text**: System fonts for optimal readability
- **Code/Technical**: JetBrains Mono, Fira Code, or other monospace fonts

## Voice & Tone

### Brand Voice
- **Expert but Approachable**: Technical depth without intimidation
- **Confident**: "Mission Control" implies competence and reliability
- **Action-Oriented**: Focus on "piloting," "navigating," "commanding"
- **Solution-Focused**: Emphasis on making complex observability simple

### Key Messaging Themes
- **Control**: "Mission Control," "Cockpit," "Command"
- **Navigation**: "Pilot," "Navigate," "Chart your course"
- **Precision**: "Zero-friction," "Real-time," "Precision observability"
- **Accessibility**: "Made simple," "Everyone can pilot"

## Positioning Statements

1. **"ProbePilot: Your Mission Control for Kernel Observability."**
2. **"Navigate clouds and clusters with precision — ProbePilot puts you in command of your eBPF telemetry."**
3. **"ProbePilot: The cockpit for real-time, zero-friction performance insights."**
4. **"Take flight with eBPF-powered visibility. Piloting your infrastructure just got easier!"**

## Elevator Pitch

> **ProbePilot is the unified GUI and telemetry engine for cloud-native and on-prem environments, making eBPF-powered observability and incident response accessible to everyone. Deploy, visualize, and action your probes — all from one mission-ready platform.**

## Usage Examples

### Taglines
- "The cockpit for real-time, zero-friction performance insights"
- "Your Mission Control for Kernel Observability"
- "Navigate. Monitor. Command."
- "eBPF Observability Made Simple"

### Button Text Examples
- "Take Flight" (instead of "Get Started")
- "Launch Dashboard" (instead of "Open Dashboard")
- "Mission Control" (instead of "Admin Panel")
- "Deploy Probes" (instead of "Install Agents")

## Brand Applications

### Gradio Theme Integration
The aviation brand is implemented through custom Gradio themes and CSS styling:

```python
# Primary brand colors in Gradio theme
aviation_theme = gr.themes.Base(
    primary_hue=gr.themes.Color(
        c500="#3b82f6",   # Sky Blue
        c700="#1d4ed8",   # Medium Blue  
        c900="#1e3a8a"    # Mission Blue
    ),
    secondary_hue=gr.themes.Color(
        c500="#10b981"    # Cockpit Green
    )
)
```

### Custom CSS Styling
Mission control aesthetics through backdrop blur effects and glass morphism:

```css
.mission-control-header {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 12px;
    backdrop-filter: blur(10px);
}

.status-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
}
```

### UI Component Guidelines
- **Status Indicators**: Use colored circles (green/orange/red) for system health
- **Buttons**: Primary actions in Mission Blue, secondary in neutral tones
- **Panels**: Semi-transparent backgrounds with subtle borders
- **Charts**: Dark backgrounds with bright accent colors for readability

### Website Headers
Use the aviation theme consistently across marketing materials while maintaining professional credibility.

### Documentation
Balance technical accuracy with approachable explanations, using aviation metaphors where they enhance understanding.

### Gradio Interface Elements
Incorporate subtle aviation-inspired design elements without overwhelming the functional interface.

---

*This brand guide ensures consistent representation of ProbePilot across all touchpoints while maintaining our core identity as the premier eBPF observability platform.*