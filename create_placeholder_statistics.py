"""
Create placeholder images for Statistics Generator carousel
These are temporary placeholders - replace with actual dashboard screenshots
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path

# PSE Brand Colors
PSE_COLORS = {
    'forest_green': '#275258',
    'forest_green_light': '#3a6b72',
    'forest_green_lighter': '#e8f0f1',
    'orange': '#fb923c',
    'orange_light': '#fed7aa',
    'white': '#ffffff',
    'black': '#252728',
    'gray': '#6b7280',
}

OUTPUT_DIR = Path(__file__).parent / 'assets'

def create_statistics_placeholder(number, title, subtitle):
    """Create a placeholder image for statistics tool"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Background
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_facecolor(PSE_COLORS['forest_green_lighter'])
    
    # Main border
    border = mpatches.Rectangle((0.5, 0.5), 9, 9, 
                                fill=False, 
                                edgecolor=PSE_COLORS['forest_green'],
                                linewidth=4)
    ax.add_patch(border)
    
    # Number badge
    circle = mpatches.Circle((5, 7.5), 1.2, 
                            facecolor=PSE_COLORS['orange'],
                            edgecolor=PSE_COLORS['forest_green'],
                            linewidth=3)
    ax.add_patch(circle)
    ax.text(5, 7.5, str(number), 
           ha='center', va='center',
           fontsize=80, fontweight='bold',
           color=PSE_COLORS['white'])
    
    # Title
    ax.text(5, 5.5, title,
           ha='center', va='center',
           fontsize=32, fontweight='bold',
           color=PSE_COLORS['forest_green'])
    
    # Subtitle
    ax.text(5, 4.5, subtitle,
           ha='center', va='center',
           fontsize=20,
           color=PSE_COLORS['gray'],
           style='italic')
    
    # Mock dashboard elements
    # Sidebar
    sidebar = mpatches.Rectangle((0.8, 1), 1.5, 3.5,
                                facecolor=PSE_COLORS['forest_green'],
                                alpha=0.3)
    ax.add_patch(sidebar)
    
    # Chart area
    chart = mpatches.Rectangle((2.5, 1), 6.7, 3.5,
                              facecolor=PSE_COLORS['white'],
                              edgecolor=PSE_COLORS['gray'],
                              linewidth=2,
                              alpha=0.8)
    ax.add_patch(chart)
    
    # Footer text
    ax.text(5, 0.8, 'PLACEHOLDER: Replace with actual dashboard screenshot',
           ha='center', va='center',
           fontsize=14,
           color=PSE_COLORS['orange'],
           style='italic',
           weight='bold')
    
    ax.axis('off')
    plt.tight_layout()
    
    # Save
    filepath = OUTPUT_DIR / f'tool_statistics_{number}.png'
    fig.savefig(filepath, dpi=150, bbox_inches='tight', 
               facecolor=PSE_COLORS['forest_green_lighter'])
    plt.close()
    
    print(f"✓ Created {filepath}")


# Create three placeholder images
create_statistics_placeholder(1, 
                             "Statistics by Geography", 
                             "County, State, and Utility Territory Views")

create_statistics_placeholder(2, 
                             "Demographic Filtering", 
                             "Income, Race, Housing Type, and More")

create_statistics_placeholder(3, 
                             "Interactive Visualizations", 
                             "Charts, Maps, and Data Downloads")

print("\n" + "="*60)
print("✓ Created 3 placeholder images for Statistics Generator")
print(f"✓ Location: {OUTPUT_DIR}")
print("="*60)
print("\nREMINDER: Replace these placeholders with actual dashboard")
print("screenshots showing real Statistics Generator features!")
