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
    'highlight': '#00bcf2',
    'secondary': '#5c2d91'
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
ax.text(5, 9.5, 'Post-Quantum Cryptography Implementation', ha='center', fontsize=18, fontweight='bold')

# Create boxes for the main components
create_box(1, 8, 3, 1, 'Key Generation Module', colors['secondary'])
create_box(6, 8, 3, 1, 'Address Generation', colors['secondary'])
create_box(1, 6, 3, 1, 'Dilithium-3 Signatures', colors['secondary'])
create_box(6, 6, 3, 1, 'Kyber Encryption', colors['secondary'])
create_box(1, 4, 3, 1, 'Transaction Signing', colors['box'])
create_box(6, 4, 3, 1, 'Transaction Verification', colors['box'])
create_box(3.5, 2, 3, 1, 'Quantum-Resistant Hashing', colors['box'])
create_box(3.5, 0.5, 3, 1, 'Blockchain State', colors['box'])

# Create arrows to show the flow
create_arrow(2.5, 8, 2.5, 7, 'Generate Keys')
create_arrow(7.5, 8, 7.5, 7, 'Create Address')
create_arrow(2.5, 7, 2.5, 6)
create_arrow(7.5, 7, 7.5, 6)
create_arrow(2.5, 6, 2.5, 5, 'Sign Data')
create_arrow(7.5, 6, 7.5, 5, 'Encrypt Data')
create_arrow(2.5, 5, 2.5, 4)
create_arrow(7.5, 5, 7.5, 4)
create_arrow(4, 4, 6, 4, 'Verify')
create_arrow(5, 4, 5, 3, 'Hash Data')
create_arrow(5, 3, 5, 2)
create_arrow(5, 2, 5, 1.5, 'Store Hash')
create_arrow(5, 1.5, 5, 0.5)

# Add explanatory notes
notes = [
    (1.5, 7.5, "1. Generate Dilithium-3 key pairs"),
    (7.5, 7.5, "2. Create Bech32m addresses with sYnQ/sYnU prefix"),
    (2, 5.5, "3. Sign transactions with Dilithium-3"),
    (7, 5.5, "4. Use Kyber for encryption when needed"),
    (2, 3.5, "5. Transactions include PQ signatures"),
    (7, 3.5, "6. Verify signatures against public keys"),
    (5, 2.5, "7. Use SHA3-256/BLAKE3 for hashing"),
    (5, 1, "8. Store state with quantum-resistant integrity")
]

for x, y, text in notes:
    ax.text(x, y, text, ha='center', va='center', fontsize=9,
            bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.3'))

# Add a legend
legend_elements = [
    patches.Patch(facecolor=colors['secondary'], edgecolor='black', alpha=0.8, label='Cryptographic Primitives'),
    patches.Patch(facecolor=colors['box'], edgecolor='black', alpha=0.8, label='Blockchain Operations')
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

# Add PQC details box
pqc_details = """
Dilithium-3 (CRYSTALS):
- Signature size: ~2.7KB
- Public key size: ~1.3KB
- Security level: 128-bit post-quantum

Kyber (CRYSTALS):
- Ciphertext size: ~1KB
- Public key size: ~0.8KB
- Security level: 128-bit post-quantum

Hash Functions:
- SHA3-256: 256-bit output
- BLAKE3: Variable output size
"""

props = dict(boxstyle='round', facecolor='white', alpha=0.7)
ax.text(8.5, 2.5, pqc_details, fontsize=9, verticalalignment='top', bbox=props)

# Set limits and remove axes
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Save the figure
plt.savefig('/home/ubuntu/synergy_network/architecture/diagrams/pqc_implementation.png', dpi=300, bbox_inches='tight')
plt.close()

print("Post-Quantum Cryptography implementation diagram created successfully!")
