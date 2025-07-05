import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.path import Path

# Create figure and axis
fig, ax = plt.subplots(figsize=(12, 10))

# Set background color
ax.set_facecolor('#f0f0f0')

# Define colors
colors = {
    'validator': '#2b5797',
    'task_node': '#00bcf2',
    'storage_node': '#5c2d91',
    'relay_node': '#008272',
    'user_node': '#107c10',
    'connection': '#666666',
    'cluster': '#0078d7',
    'text': 'white'
}

# Function to create a node
def create_node(x, y, radius, label, node_type='validator'):
    circle = plt.Circle((x, y), radius, facecolor=colors[node_type], edgecolor='black', alpha=0.8)
    ax.add_patch(circle)
    ax.text(x, y, label, ha='center', va='center', color=colors['text'], fontsize=10, fontweight='bold')
    return circle

# Function to connect nodes
def connect_nodes(node1, node2, style='solid', width=1, alpha=0.6):
    x1, y1 = node1.center
    x2, y2 = node2.center
    line = plt.Line2D([x1, x2], [y1, y2], color=colors['connection'], 
                      linewidth=width, alpha=alpha, linestyle=style)
    ax.add_line(line)

# Function to create a cluster
def create_cluster(nodes, label=None):
    # Get coordinates of nodes
    coords = [node.center for node in nodes]
    x_coords, y_coords = zip(*coords)
    
    # Create a convex hull around the nodes
    hull_path = []
    center_x = sum(x_coords) / len(x_coords)
    center_y = sum(y_coords) / len(y_coords)
    
    # Sort points by angle
    angles = []
    for x, y in coords:
        angle = np.arctan2(y - center_y, x - center_x)
        angles.append(angle)
    
    sorted_coords = [coords[i] for i in np.argsort(angles)]
    
    # Add buffer around nodes
    buffer = 0.4
    hull_coords = []
    for x, y in sorted_coords:
        dx, dy = x - center_x, y - center_y
        dist = np.sqrt(dx**2 + dy**2)
        hull_coords.append((x + buffer * dx / dist, y + buffer * dy / dist))
    
    # Create path codes
    codes = [Path.MOVETO] + [Path.LINETO] * (len(hull_coords) - 1) + [Path.CLOSEPOLY]
    hull_coords.append(hull_coords[0])  # Close the path
    
    # Create the path
    path = Path(hull_coords, codes)
    patch = patches.PathPatch(path, facecolor=colors['cluster'], alpha=0.2, edgecolor=colors['cluster'])
    ax.add_patch(patch)
    
    # Add label if provided
    if label:
        label_x = sum([c[0] for c in hull_coords]) / len(hull_coords)
        label_y = max([c[1] for c in hull_coords]) + 0.3
        ax.text(label_x, label_y, label, ha='center', va='center', fontsize=12, 
                fontweight='bold', bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.3'))

# Title
ax.text(5, 9.5, 'Synergy Network Topology', ha='center', fontsize=18, fontweight='bold')

# Create nodes
# Validator nodes in clusters
validator_cluster1 = [
    create_node(2, 7, 0.3, 'V1', 'validator'),
    create_node(2.8, 7.5, 0.3, 'V2', 'validator'),
    create_node(3.5, 6.8, 0.3, 'V3', 'validator'),
    create_node(2.5, 6.2, 0.3, 'V4', 'validator'),
    create_node(3.2, 6, 0.3, 'V5', 'validator')
]

validator_cluster2 = [
    create_node(7, 7, 0.3, 'V6', 'validator'),
    create_node(7.8, 7.5, 0.3, 'V7', 'validator'),
    create_node(8.5, 6.8, 0.3, 'V8', 'validator'),
    create_node(7.5, 6.2, 0.3, 'V9', 'validator'),
    create_node(8.2, 6, 0.3, 'V10', 'validator')
]

validator_cluster3 = [
    create_node(2, 3, 0.3, 'V11', 'validator'),
    create_node(2.8, 3.5, 0.3, 'V12', 'validator'),
    create_node(3.5, 2.8, 0.3, 'V13', 'validator'),
    create_node(2.5, 2.2, 0.3, 'V14', 'validator'),
    create_node(3.2, 2, 0.3, 'V15', 'validator')
]

validator_cluster4 = [
    create_node(7, 3, 0.3, 'V16', 'validator'),
    create_node(7.8, 3.5, 0.3, 'V17', 'validator'),
    create_node(8.5, 2.8, 0.3, 'V18', 'validator'),
    create_node(7.5, 2.2, 0.3, 'V19', 'validator'),
    create_node(8.2, 2, 0.3, 'V20', 'validator')
]

# Task nodes
task_nodes = [
    create_node(1, 5, 0.3, 'T1', 'task_node'),
    create_node(5, 8, 0.3, 'T2', 'task_node'),
    create_node(9, 5, 0.3, 'T3', 'task_node'),
    create_node(5, 1, 0.3, 'T4', 'task_node')
]

# Storage nodes
storage_nodes = [
    create_node(3, 8.5, 0.3, 'S1', 'storage_node'),
    create_node(8, 8.5, 0.3, 'S2', 'storage_node'),
    create_node(3, 1.5, 0.3, 'S3', 'storage_node'),
    create_node(8, 1.5, 0.3, 'S4', 'storage_node')
]

# Relay nodes at the center
relay_node = create_node(5, 5, 0.4, 'Relay', 'relay_node')

# User nodes
user_nodes = [
    create_node(1, 9, 0.25, 'U1', 'user_node'),
    create_node(5, 9, 0.25, 'U2', 'user_node'),
    create_node(9, 9, 0.25, 'U3', 'user_node'),
    create_node(1, 1, 0.25, 'U4', 'user_node'),
    create_node(9, 1, 0.25, 'U5', 'user_node')
]

# Create clusters
create_cluster(validator_cluster1, "Validator Cluster 1")
create_cluster(validator_cluster2, "Validator Cluster 2")
create_cluster(validator_cluster3, "Validator Cluster 3")
create_cluster(validator_cluster4, "Validator Cluster 4")

# Connect nodes within clusters
for cluster in [validator_cluster1, validator_cluster2, validator_cluster3, validator_cluster4]:
    for i in range(len(cluster)):
        for j in range(i+1, len(cluster)):
            connect_nodes(cluster[i], cluster[j], style='solid', width=1, alpha=0.4)

# Connect relay node to all validator clusters
for node in validator_cluster1 + validator_cluster2 + validator_cluster3 + validator_cluster4:
    connect_nodes(relay_node, node, style='solid', width=1.5, alpha=0.6)

# Connect task nodes to relay
for node in task_nodes:
    connect_nodes(relay_node, node, style='dashed', width=1.5, alpha=0.6)

# Connect storage nodes to relay
for node in storage_nodes:
    connect_nodes(relay_node, node, style='dotted', width=1.5, alpha=0.6)

# Connect user nodes to relay
for node in user_nodes:
    connect_nodes(relay_node, node, style='dashdot', width=1, alpha=0.6)

# Add a legend
legend_elements = [
    patches.Patch(facecolor=colors['validator'], edgecolor='black', alpha=0.8, label='Validator Nodes'),
    patches.Patch(facecolor=colors['task_node'], edgecolor='black', alpha=0.8, label='Task Nodes'),
    patches.Patch(facecolor=colors['storage_node'], edgecolor='black', alpha=0.8, label='Storage Nodes'),
    patches.Patch(facecolor=colors['relay_node'], edgecolor='black', alpha=0.8, label='Relay Node'),
    patches.Patch(facecolor=colors['user_node'], edgecolor='black', alpha=0.8, label='User Nodes'),
    patches.Patch(facecolor=colors['cluster'], alpha=0.2, label='Validator Clusters')
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

# Add explanatory notes
notes = """
Synergy Network Topology Features:

1. Validator Clusters: Groups of validators that collaborate on tasks
   and consensus using Proof of Synergy (PoSy)

2. Task Nodes: Specialized nodes that manage and distribute 
   computational tasks across validator clusters

3. Storage Nodes: Provide decentralized storage services for 
   blockchain data and off-chain content

4. Relay Node: Central coordination point that facilitates 
   communication between different node types

5. User Nodes: End-user access points for interacting with 
   the Synergy Network

Key Properties:
- Dynamic cluster formation and reshuffling
- Task-based resource allocation
- Post-Quantum cryptographic security
- Collaborative consensus mechanism
"""

props = dict(boxstyle='round', facecolor='white', alpha=0.7)
ax.text(1, 4.2, notes, fontsize=9, verticalalignment='top', bbox=props)

# Set limits and remove axes
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Save the figure
plt.savefig('/home/ubuntu/synergy_network/architecture/diagrams/network_topology.png', dpi=300, bbox_inches='tight')
plt.close()

print("Network topology diagram created successfully!")
