"""
Aviation-themed Gradio theme for ProbePilot Mission Control
"""

import gradio as gr

def get_aviation_theme():
    """Create custom aviation-inspired theme for ProbePilot"""
    
    return gr.themes.Base(
        primary_hue=gr.themes.Color(
            name="mission_blue",
            c50="#eff6ff",    # Very light sky blue
            c100="#dbeafe",   # Light sky blue
            c200="#bfdbfe",   # Lighter blue
            c300="#93c5fd",   # Light blue
            c400="#60a5fa",   # Medium light blue
            c500="#3b82f6",   # Sky Blue (primary)
            c600="#2563eb",   # Medium blue
            c700="#1d4ed8",   # Darker blue
            c800="#1e40af",   # Dark blue
            c900="#1e3a8a",   # Mission Blue (darkest)
            c950="#172554"    # Very dark blue
        ),
        secondary_hue=gr.themes.Color(
            name="cockpit_green",
            c50="#ecfdf5",
            c100="#d1fae5", 
            c200="#a7f3d0",
            c300="#6ee7b7",
            c400="#34d399",
            c500="#10b981",   # Cockpit Green (primary)
            c600="#059669",
            c700="#047857",
            c800="#065f46",
            c900="#064e3b",
            c950="#022c22"
        ),
        neutral_hue=gr.themes.Color(
            name="aviation_gray",
            c50="#f9fafb",
            c100="#f3f4f6",
            c200="#e5e7eb", 
            c300="#d1d5db",
            c400="#9ca3af",
            c500="#6b7280",   # Neutral Gray
            c600="#4b5563",
            c700="#374151",
            c800="#1f2937",
            c900="#111827",
            c950="#030712"
        ),
        font=[
            gr.themes.GoogleFont("Inter"),
            "system-ui",
            "sans-serif"
        ],
        font_mono=[
            gr.themes.GoogleFont("JetBrains Mono"),
            "Consolas", 
            "monospace"
        ]
    ).set(
        # Button styling
        button_primary_background_fill="*primary_500",
        button_primary_background_fill_hover="*primary_600",
        button_primary_text_color="white",
        button_primary_border_color="*primary_600",
        
        button_secondary_background_fill="*neutral_100",
        button_secondary_background_fill_hover="*neutral_200", 
        button_secondary_text_color="*neutral_800",
        button_secondary_border_color="*neutral_300",
        
        # Input styling
        input_background_fill="*neutral_50",
        input_border_color="*primary_300",
        input_border_color_focus="*primary_500",
        
        # Block styling
        block_background_fill="rgba(255, 255, 255, 0.05)",
        block_border_color="*primary_200",
        block_border_width="1px",
        block_padding="16px",
        block_radius="8px",
        
        # Panel styling
        panel_background_fill="rgba(255, 255, 255, 0.08)",
        panel_border_color="*primary_300",
        
        # Text colors
        body_text_color="*neutral_800",
        body_text_color_subdued="*neutral_600",
        
        # Layout
        layout_gap="16px",
        container_radius="12px"
    )