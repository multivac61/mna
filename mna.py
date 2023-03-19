import numpy as np
import sympy as sym


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

    def populate(self, G, B, C, D, I, E, voltage_sources):
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

    def populate(self, G, B, C, D, I, E, voltage_sources):
        E[self.n1] += self.value
        E[self.n0] -= self.value


class Resistor(Component):
    def __init__(self, n1, n0, value=0, name=None):
        super().__init__(n1, n0, value, name)

    def populate(self, G, *_):
        G[self.n1, self.n1] += 1 / self.value
        G[self.n0, self.n0] += 1 / self.value
        G[self.n1, self.n0] -= 1 / self.value
        G[self.n0, self.n1] -= 1 / self.value


class Capacitor(Component):
    def __init__(self, n1, n0, value=0, name=None):
        super().__init__(n1, n0, value, name)
        self.s = sym.symbols('s')  # complex frequency s = \sigma + j\omega

    def populate(self, G, *_):
        G[self.n1, self.n1] += 1 / (self.s * self.value)
        G[self.n0, self.n0] += 1 / (self.s * self.value)
        G[self.n1, self.n0] -= 1 / (self.s * self.value)
        G[self.n0, self.n1] -= 1 / (self.s * self.value)


class Inductor(Component):
    def __init__(self, n1, n0, value=0, name=None):
        super().__init__(n1, n0, value, name)
        self.s = sym.symbols('s')  # complex frequency s = \sigma + j\omega

    def populate(self, G, *_):
        G[self.n1, self.n1] += self.s * self.value
        G[self.n0, self.n0] += self.s * self.value
        G[self.n1, self.n0] -= self.s * self.value
        G[self.n0, self.n1] -= self.s * self.value


def num_nodes(components):
    return len(set(node for component in components for node in component.nodes()))


def solve_mna(components):
    g_size = num_nodes(components)
    b_size = [isinstance(c, VoltageSource) for c in components].count(True)

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

    return np.linalg.solve(A[1:, 1:], E[1:] - I[1:])  # Discard ground node
