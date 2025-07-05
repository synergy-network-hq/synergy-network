import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Create figure and axis
fig, ax = plt.subplots(figsize=(12, 10))

# Set background color
ax.set_facecolor('#f0f0f0')

# Define colors
colors = {
    'box': '#2b5797',
    'arrow': '#0078d7',
    'text': 'white',
    'background': '#f0f0f0',
    'highlight': '#00bcf2'
}

# Function to create a box
def create_box(x, y, width, height, label, color=colors['box']):
    box = patches.Rectangle((x, y), width, height, linewidth=1, edgecolor='black',
                           facecolor=color, alpha=0.8)
    ax.add_patch(box)
    ax.text(x + width/2, y + height/2, label, ha='center', va='center', 
            color=colors['text'], fontsize=12, fontweight='bold')

# Function to create an arrow
def create_arrow(x1, y1, x2, y2, label=None):
    ax.arrow(x1, y1, x2-x1, y2-y1, head_width=0.15, head_length=0.2, 
             fc=colors['arrow'], ec=colors['arrow'], width=0.05)
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2, label, ha='center', va='center', 
                color='black', fontsize=10, fontweight='bold', 
                bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.3'))

# Title
ax.text(5, 9.5, 'Proof of Synergy (PoSy) Consensus Flow', ha='center', fontsize=18, fontweight='bold')

# Create boxes for the main components
create_box(1, 8, 2, 1, 'Task Pool')
create_box(7, 8, 2, 1, 'Validator Set')
create_box(1, 6, 2, 1, 'Task Allocator')
create_box(4, 6, 2, 1, 'Cluster Formation')
create_box(7, 6, 2, 1, 'Synergy Points')
create_box(1, 4, 2, 1, 'Task Execution')
create_box(4, 4, 2, 1, 'PBFT Consensus')
create_box(7, 4, 2, 1, 'Result Verification')
create_box(4, 2, 2, 1, 'Block Formation')
create_box(4, 0.5, 2, 1, 'State Update')

# Create arrows to show the flow
create_arrow(2, 8, 2, 7, 'Tasks')
create_arrow(8, 8, 8, 7, 'Validators')
create_arrow(2, 7, 2, 6)
create_arrow(8, 7, 8, 6)
create_arrow(2, 6, 4, 6, 'Assign')
create_arrow(6, 6, 7, 6)
create_arrow(3, 6, 3, 5, 'Tasks')
create_arrow(5, 6, 5, 5, 'Clusters')
create_arrow(8, 6, 8, 5, 'Points')
create_arrow(3, 5, 3, 4)
create_arrow(5, 5, 5, 4)
create_arrow(8, 5, 8, 4)
create_arrow(3, 4, 4, 4, 'Results')
create_arrow(6, 4, 7, 4, 'Verify')
create_arrow(5, 4, 5, 3, 'Consensus')
create_arrow(5, 3, 5, 2)
create_arrow(5, 2, 5, 1.5, 'New Block')
create_arrow(5, 1.5, 5, 0.5)
create_arrow(6, 0.5, 8, 0.5, 'Update Points')
create_arrow(8, 0.5, 8.5, 0.5)
create_arrow(8.5, 0.5, 8.5, 8.5)
create_arrow(8.5, 8.5, 8, 8.5)
create_arrow(8, 8.5, 7.5, 8.5)

# Add explanatory notes
notes = [
    (1.5, 7.5, "1. Tasks submitted to pool"),
    (7.5, 7.5, "2. Validators registered"),
    (3, 5.5, "3. Tasks assigned to clusters"),
    (7, 5.5, "4. Clusters formed randomly"),
    (2, 3.5, "5. Validators execute tasks"),
    (5, 3.5, "6. PBFT used within clusters"),
    (7.5, 3.5, "7. Results verified by multiple clusters"),
    (6, 2.5, "8. Validated results form new block"),
    (6, 1, "9. State updated, rewards distributed"),
    (9, 4.5, "10. Synergy Points updated based on contributions")
]

for x, y, text in notes:
    ax.text(x, y, text, ha='center', va='center', fontsize=9,
            bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.3'))

# Set limits and remove axes
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Save the figure
plt.savefig('/home/ubuntu/synergy_network/architecture/diagrams/consensus_flow.png', dpi=300, bbox_inches='tight')
plt.close()

print("Consensus flow diagram created successfully!")
