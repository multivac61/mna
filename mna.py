import numpy as np


class Component:
    def __init__(self, n1, n0, value=0, name=None):
        self.n1, self.n0 = n1, n0
        self.name = name
        self.value = value

    def nodes(self):
        return self.n1, self.n0


class VoltageSource(Component):
    def __init__(self, n1, n0, value=0, name=None):
        super().__init__(n1, n0, value, name)

    def populate(self, G, B, C, _D, _I, E, voltage_sources):
        idx = len(voltage_sources)
        voltage_sources.append(self)

        B[self.n1, idx] += 1
        C[idx, self.n1] += 1
        B[self.n0, idx] -= 1
        C[idx, self.n0] -= 1

        E[len(G) + idx] = self.value


class CurrentSource(Component):
    def __init__(self, n1, n0, value=0, name=None):
        super().__init__(n1, n0, value, name)

    def populate(self, _G, _B, _C, _D, _I, E, _voltage_sources):
        E[self.n1] += self.value
        E[self.n0] -= self.value


class Resistor(Component):
    def __init__(self, n1, n0, value=0, name=None):
        super().__init__(n1, n0, value, name)

    def populate(self, G, _B, _C, _D, _I, _E, _voltage_sources):
        G[self.n1, self.n1] += 1 / self.value
        G[self.n0, self.n0] += 1 / self.value
        G[self.n1, self.n0] -= 1 / self.value
        G[self.n0, self.n1] -= 1 / self.value


class Capacitor(Component):
    def __init__(self, n1, n0, value=0, name=None):
        super().__init__(n1, n0, value, name)

    def populate(self, G, _B, _C, _D, _I, _E, _voltage_sources):
        G[self.n1, self.n1] += 1 / self.value
        G[self.n0, self.n0] += 1 / self.value
        G[self.n1, self.n0] -= 1 / self.value
        G[self.n0, self.n1] -= 1 / self.value


class Inductor(Component):
    def __init__(self, n1, n0, value=0, name=None):
        super().__init__(n1, n0, value, name)

    def populate(self, G, _B, _C, _D, _I, _E, _voltage_sources):
        G[self.n1, self.n1] += self.value
        G[self.n0, self.n0] += self.value
        G[self.n1, self.n0] -= self.value
        G[self.n0, self.n1] -= self.value


class TwoPort(Component):
    def __init__(self, n1, n0, n3, n2, value=0, name=None):
        super().__init__(n1, n0, value, name)
        self.n3, self.n2 = n3, n2

    def nodes(self):
        return self.n1, self.n0, self.n3, self.n2


def num_nodes(components):
    return len(set(node for component in components for node in component.nodes()))


def solve_mna(components):
    g_size = num_nodes(components)
    b_size = sum(1 for c in components if isinstance(c, VoltageSource))

    G = np.zeros((g_size, g_size))
    B = np.zeros((g_size, b_size))
    C = np.zeros((b_size, g_size))
    D = np.zeros((b_size, b_size))
    I = np.zeros(g_size + b_size)
    E = np.zeros(g_size + b_size)
    voltage_sources = []

    for component in components:
        component.populate(G, B, C, D, I, E, voltage_sources)

    A = np.block([
        [G, B],
        [C, D]
    ])

    # NOTE: The number of independent Kirchhoff's Circuit Law equations is always one less than the number of nodes.
    # Any node may be chosen as *datum node* (ground node) and the solution will be the same. Here we discard ground.
    return np.linalg.solve(A[1:, 1:], E[1:] - I[1:])  # Discard ground node
