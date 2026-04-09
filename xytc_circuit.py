from qiskit import QuantumCircuit, QuantumRegister
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class XYTCCircuit:
    def __init__(self, L: int):
        """
        Initializes a quantum circuit mapped to the provided XYTC lattice.
        """
        self.L = L
        self.num_qubits = 2 * L * L
        
        self.stars_s1 = []
        self.stars_s2 = []
        self.plaquettes = []
        self.qubit_coords = {}
        
        self._build_lattice()
        
        self.qr = QuantumRegister(self.num_qubits, 'q')
        self.qc = QuantumCircuit(self.qr)

    def _h_qubit(self, x, y):
        """Index for horizontal qubit at midpoint of bottom edge of square (x,y)"""
        return (x % self.L) + (y % self.L) * self.L

    def _v_qubit(self, x, y):
        """Index for vertical qubit at midpoint of left edge of square (x,y)"""
        return self.L * self.L + (x % self.L) + (y % self.L) * self.L

    def _build_lattice(self):
        # 1. Map Qubits exactly to the midpoints of the edges
        for y in range(self.L):
            for x in range(self.L):
                self.qubit_coords[self._h_qubit(x, y)] = (x + 0.5, y)
                self.qubit_coords[self._v_qubit(x, y)] = (x, y + 0.5)

        # 2. Build Stars (Faces) and Plaquettes (Vertices)
        for y in range(self.L):
            for x in range(self.L):
                s_qubits = [
                    self._h_qubit(x, y),           # Bottom edge
                    self._h_qubit(x, y + 1),       # Top edge
                    self._v_qubit(x, y),           # Left edge
                    self._v_qubit(x + 1, y)        # Right edge
                ]
                
                if (x + y) % 2 == 0:
                    self.stars_s1.append({'coord': (x, y), 'qubits': s_qubits})
                else:
                    self.stars_s2.append({'coord': (x, y), 'qubits': s_qubits})

                p_qubits = [
                    self._h_qubit(x, y),           # Right of vertex
                    self._h_qubit(x - 1, y),       # Left of vertex
                    self._v_qubit(x, y),           # Top of vertex
                    self._v_qubit(x, y - 1)        # Bottom of vertex
                ]
                self.plaquettes.append({'coord': (x, y), 'qubits': p_qubits})

    def bp(self, x: int, y: int):
        """
        Applies the Plaquette operator (Pauli-Z) to the vertex at (x, y).
        """
        # Find the plaquette at the given coordinates
        for p in self.plaquettes:
            if p['coord'] == (x, y):
                for q_idx in p['qubits']:
                    self.qc.z(self.qr[q_idx])
                # Add a barrier for visual clarity in circuit diagrams
                self.qc.barrier()
                return
        raise ValueError(f"No plaquette found at coordinates ({x}, {y})")

    def as_x(self, x: int, y: int):
        """
        Applies the Star X operator (Pauli-X) to the square at (x, y).
        """
        # Search through both s1 and s2 star lists
        for s in self.stars_s1 + self.stars_s2:
            if s['coord'] == (x, y):
                for q_idx in s['qubits']:
                    self.qc.x(self.qr[q_idx])
                self.qc.barrier()
                return
        raise ValueError(f"No star found at coordinates ({x}, {y})")

    def as_y(self, x: int, y: int):
        """
        Applies the Star Y operator (Pauli-Y) to the square at (x, y).
        """
        for s in self.stars_s1 + self.stars_s2:
            if s['coord'] == (x, y):
                for q_idx in s['qubits']:
                    self.qc.y(self.qr[q_idx])
                self.qc.barrier()
                return
        raise ValueError(f"No star found at coordinates ({x}, {y})")

    def draw(self, *args, **kwargs):
        """Pass-through to visualize the underlying Qiskit circuit."""
        return self.qc.draw(*args, **kwargs)
    

    def plot(self, ax=None, state_lines=None):
        """
        Plots the true geometry matching Figure 3 of the paper.
        Draws periodic boundary qubits on the outer edges.
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.set_aspect('equal')
            ax.axis('off')

        ax.set_xticks(range(self.L))
        ax.set_yticks(range(self.L))
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Draw s1 stars (shaded squares)
        for star in self.stars_s1:
            x, y = star['coord']
            ax.add_patch(patches.Rectangle((x, y), 1, 1, facecolor='lightgray', edgecolor='black', zorder=1))

        # Draw s2 stars (unshaded squares)
        for star in self.stars_s2:
            x, y = star['coord']
            ax.add_patch(patches.Rectangle((x, y), 1, 1, facecolor='white', edgecolor='black', zorder=1))

        # Draw qubits at the edge midpoints
        for q_idx, (qx, qy) in self.qubit_coords.items():
            ax.plot(qx, qy, 'ko', markersize=6, zorder=3)
            
            # Visual wrap-around for periodic boundaries
            if qx == 0:
                ax.plot(self.L, qy, 'ko', markersize=6, zorder=3)
            if qy == 0:
                ax.plot(qx, self.L, 'ko', markersize=6, zorder=3)

        # Draw state lines crossing through the spins
        if state_lines:
            for (p1, p2) in state_lines:
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'k-', linewidth=3, zorder=4)

        ax.set_xlim(0, self.L)
        ax.set_ylim(0, self.L)

        return ax