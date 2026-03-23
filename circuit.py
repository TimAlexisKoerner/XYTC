from qiskit import QuantumCircuit, QuantumRegister
from lattice import XYTCLattice

class XYTCCircuit:
    def __init__(self, lattice: XYTCLattice):
        """
        Initializes a quantum circuit mapped to the provided XYTC lattice.
        """
        self.lattice = lattice
        
        # Initialize a quantum register with 2*L^2 qubits
        self.qr = QuantumRegister(self.lattice.num_qubits, 'q')
        self.qc = QuantumCircuit(self.qr)

    def bp(self, x: int, y: int):
        """
        Applies the Plaquette operator (Pauli-Z) to the vertex at (x, y).
        """
        # Find the plaquette at the given coordinates
        for p in self.lattice.plaquettes:
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
        for s in self.lattice.stars_s1 + self.lattice.stars_s2:
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
        for s in self.lattice.stars_s1 + self.lattice.stars_s2:
            if s['coord'] == (x, y):
                for q_idx in s['qubits']:
                    self.qc.y(self.qr[q_idx])
                self.qc.barrier()
                return
        raise ValueError(f"No star found at coordinates ({x}, {y})")

    def draw(self, *args, **kwargs):
        """Pass-through to visualize the underlying Qiskit circuit."""
        return self.qc.draw(*args, **kwargs)