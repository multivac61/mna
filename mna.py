import numpy as np


# Assumptions
# -----------
# - Nodes are numbered 0, 1, 2, ... (no gaps)
# - The unknown current flows into nodes 1/3 (+) and out of nodes 0/2 (-)
# n1 (+) --\   /-- (+) n3
#           ? ?
# n0 (-) --/   \-- (-) n2

class Component:
    def __init__(self, nodes, name=None):
        self.nodes, self.name = nodes, name
        self.num_unknown_currents = 0


class ResistiveVoltageSource(Component):
    def __init__(self, nodes, v=0, r=0, name=None):
        super().__init__(nodes, name)
        self.v, self.r = v, r
        self.num_unknown_currents = 1

    def stamp(self, G, B, C, D, E, idx):
        n1, n0 = self.nodes
        B[n1, idx] += 1
        B[n0, idx] -= 1
        C[idx, n1] += 1
        C[idx, n0] -= 1
        D[idx, idx] -= self.r
        E[G.shape[0] + idx] = self.v


class VoltageSource(Component):
    def __init__(self, nodes, v=0, name=None):
        super().__init__(nodes, name)
        self.v = v
        self.num_unknown_currents = 1

    def stamp(self, G, B, C, _D, E, idx):
        n1, n0 = self.nodes
        B[n1, idx] += 1
        B[n0, idx] -= 1
        C[idx, n1] += 1
        C[idx, n0] -= 1

        E[G.shape[0] + idx] = self.v


class CurrentSource(Component):
    def __init__(self, nodes, i=0, name=None):
        super().__init__(nodes, name)
        self.i = i

    def stamp(self, _G, _B, _C, _D, E, _idx):
        n1, n0 = self.nodes
        E[n1] += self.i
        E[n0] -= self.i


class Resistor(Component):
    def __init__(self, nodes, r=0, name=None):
        super().__init__(nodes, name)
        self.r = r

    def stamp(self, G, _B, _C, _D, _E, _idx):
        (n1, n0), g = self.nodes, 1 / self.r
        G[n1, n1] += g
        G[n0, n0] += g
        G[n1, n0] -= g
        G[n0, n1] -= g


class Capacitor(Component):
    def __init__(self, nodes, c=0, name=None):
        super().__init__(nodes, name)
        self.z = 1 / c

    def stamp(self, G, _B, _C, _D, _E, _idx):
        G[n1, n1] += self.z
        G[n0, n0] += self.z
        G[n1, n0] -= self.z
        G[n0, n1] -= self.z


class Inductor(Component):
    def __init__(self, nodes, l=0, name=None):
        super().__init__(nodes, name)
        self.l = l

    def stamp(self, G, _B, _C, _D, _E, _idx):
        G[n1, n1] += self.l
        G[n0, n0] += self.l
        G[n1, n0] -= self.l
        G[n0, n1] -= self.l


class OpenCircuit(Component):
    def __init__(self, nodes, name=None):
        super().__init__(nodes, name)

    def stamp(self, _G, _B, _C, _D, _E, _idx):
        pass


class ShortCircuit(Component):
    def __init__(self, nodes, name=None):
        super().__init__(nodes, name)
        # TODO: check if this is correct
        self.norator = Norator(nodes, name)
        self.nullator = Nullator(nodes, name)

    def stamp(self, G, B, C, D, E, idx):
        self.norator.stamp(G, B, C, D, E, idx)
        self.nullator.stamp(G, B, C, D, E, idx)


class Nullator(Component):
    def __init__(self, nodes, name=None):
        super().__init__(nodes, name)
        self.num_unknown_currents = 1

    def stamp(self, _G, _B, C, _D, _E, idx):
        n1, n0 = self.nodes
        C[idx, n1] += 1
        C[idx, n0] -= 1


class Norator(Component):
    def __init__(self, nodes, name=None):
        super().__init__(nodes, name)

    def stamp(self, _G, B, _C, _D, _E, idx):
        n1, n0 = self.nodes
        B[n1, idx] += 1
        B[n0, idx] -= 1


class VoltageControlledCurrentSource(Component):
    def __init__(self, nodes, mu=0, name=None):
        super().__init__(nodes, name)
        self.mu = mu

    def stamp(self, G, _B, _C, _D, _E, _idx):
        n1, n0, n3, n2 = self.nodes
        G[n3, n1] -= self.mu
        G[n3, n0] += self.mu
        G[n2, n1] += self.mu
        G[n2, n0] -= self.mu


class VoltageControlledVoltageSource(Component):
    def __init__(self, nodes, mu=0, name=None):
        super().__init__(nodes, name)
        self.num_unknown_currents = 1
        self.mu = mu

    def stamp(self, _G, B, C, _D, _E, idx):
        # TODO: Test that this code is indeed correct wrt polarity
        n1, n0, n3, n2 = self.nodes
        B[n3, idx] += 1
        B[n2, idx] -= 1
        C[idx, n3] += 1
        C[idx, n2] -= 1
        C[idx, n1] -= self.mu
        C[idx, n0] += self.mu


class CurrentControlledCurrentSource(Component):
    def __init__(self, nodes, a=0, name=None):
        super().__init__(nodes, name)
        self.num_unknown_currents = 1
        self.a = a

    def stamp(self, _G, _B, _C, _D, _E, _idx):
        assert False, "Not implemented"


class CurrentControlledVoltageSource(Component):
    def __init__(self, nodes, r=0, name=None):
        super().__init__(nodes, name)
        self.num_unknown_currents = 2
        self.r = r

    def stamp(self, _G, _B, _C, _D, _E, _idx):
        assert False, "Not implemented"


class IdealOperationalAmplifier(Component):
    def __init__(self, nodes, name=None):
        super().__init__(nodes, name)
        self.num_unknown_currents = 1

    def stamp(self, _G, B, C, _D, _E, idx):
        n1, n0, n3, n2 = self.nodes
        B[n3, idx] += 1
        B[n2, idx] -= 1
        C[idx, n1] += 1
        C[idx, n0] -= 1


class IdealTransformer(Component):
    def __init__(self, nodes, l1=0, l2=0, name=None):
        super().__init__(nodes, name=name)
        self.l1, self.l2 = l1, l2
        self.num_unknown_currents = 2

    def stamp(self, _G, _B, _C, _D, _E, _unknown_currents):
        n1, n0, n3, n2 = self.nodes
        assert False
        pass


def num_nodes(components):
    return len(nodes(components))


def nodes(circuit):
    return set(node for component in circuit for node in component.nodes)


def total_unknown_currents(components):
    return sum(component.num_unknown_currents for component in components)


def solve_mna(circuit, zeros=np.zeros, block=np.block, return_populated_system=False):
    g_size = num_nodes(circuit)
    b_size = total_unknown_currents(circuit)
    num_unknown_currents = 0  # This variable grows as more circuit with unknown currents are added

    assert nodes(circuit) == set(range(g_size)), "Nodes must be in a range from 0 (ground) to num_nodes - 1"

    G = zeros((g_size, g_size))
    B = zeros((g_size, b_size))
    C = zeros((b_size, g_size))
    D = zeros((b_size, b_size))
    E = zeros((g_size + b_size))

    for component in circuit:
        component.stamp(G, B, C, D, E, num_unknown_currents)
        num_unknown_currents += component.num_unknown_currents

    assert b_size == num_unknown_currents, "Number of unknown currents must be equal to unknown currents in the circuit"

    A = block([[G, B], [C, D]])

    if return_populated_system:
        return A[1:, 1:], E[1:]

    # NOTE: The number of independent KCLs is always one less than the number of nodes.
    # Any node may be chosen as *datum node* (ground node) and the solution will be the same.
    # I choose the ground node as the datum node, so I discard the first row and column of the matrix.
    return np.linalg.solve(A[1:, 1:], E[1:])  # Discard ground node
