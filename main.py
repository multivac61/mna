import numpy as np
import sympy as sym

class Component:
    def __init__(self, n1, n0, value=0, name=None):
        self.n1, self.n0 = n1, n0
        self.name = name
        self.value = value


class VoltageSource(Component):
    def __init__(self, n1, n0, value=0, name=None):
        super().__init__(n1, n0, value, name)

    def simulate(self, t):
        return self.value


class CurrentSource(Component):
    def __init__(self, n1, n0, value=0, name=None):
        super().__init__(n1, n0, value, name)


class Resistor(Component):
    def __init__(self, n1, n0, value=0, name=None):
        super().__init__(n1, n0, value, name)

    def impedance(self):
        return 1 / self.value


class Capacitor(Component):
    def __init__(self, n1, n0, value=0, name=None):
        super().__init__(n1, n0, value, name)
        self.s = sym.symbols('s')  # complex frequency s = \sigma + j\omega

    def impedance(self):
        return 1 / (self.s * self.value)


class Inductor(Component):
    def __init__(self, n1, n0, value=0, name=None):
        super().__init__(n1, n0, value, name)
        self.s = sym.symbols('s')  # complex frequency s = \sigma + j\omega

    def impedance(self):
        return self.s * self.value


def num_nodes(components):
    unique_nodes = set()
    for component in components:
        unique_nodes.add(component.n1)
        unique_nodes.add(component.n0)
    return len(unique_nodes)


def analyze_mna(components):
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
        n1, n0 = component.n1, component.n0
        if any(isinstance(component, t) for t in [Resistor, Capacitor, Inductor]):
            G[n1, n1] += component.impedance()
            G[n0, n0] += component.impedance()
            G[n1, n0] -= component.impedance()
            G[n0, n1] -= component.impedance()

        elif isinstance(component, VoltageSource):
            idx = len(voltage_sources)
            voltage_sources.append(component)

            B[n1, idx] += 1
            C[idx, n1] += 1
            B[n0, idx] -= 1
            C[idx, n0] -= 1

            E[g_size + idx] = component.value
        elif isinstance(component, CurrentSource):
            E[n1] += component.value
            E[n0] -= component.value

    A = np.block([
        [G, B],
        [C, D]
    ])

    return np.linalg.solve(A[1:, 1:], E[1:] - I[1:])


bassman_tonestack = [
    VoltageSource(1, 0, value=1),
    Resistor(1, 2, value=1),
    Resistor(1, 3, value=1),
    Resistor(2, 3, value=1),
    Resistor(3, 4, value=1),
    Resistor(2, 4, value=1),
    Resistor(4, 0, value=1),
]
assert np.allclose(analyze_mna(bassman_tonestack), np.array([1, 3 / 4, 3 / 4, 1 / 2, -1 / 2]))

bassman_tonestack_2 = [
    VoltageSource(1, 0, value=1),
    Resistor(1, 2, value=1),
    Resistor(1, 3, value=2),
    Resistor(2, 3, value=3),
    Resistor(3, 4, value=4),
    Resistor(2, 4, value=5),
    Resistor(4, 0, value=6),
]
assert np.allclose(analyze_mna(bassman_tonestack_2), np.array([1, 44 / 47, 85 / 94, 63 / 94, -21 / 188]))

hd2_2 = [
    VoltageSource(1, 0, value=2),
    VoltageSource(3, 0, value=3),
    Resistor(1, 2, value=4),
    Resistor(2, 3, value=12),
    Resistor(2, 4, value=2),
    Resistor(4, 0, value=3)
]
num_nodes(hd2_2)
assert np.allclose(analyze_mna(hd2_2), np.array([2, 45 / 32, 3, 27 / 32, -19 / 128, -17 / 128]))

g1, g2, g3, g4, v1, v2 = 1 / 4, 1 / 12, 1 / 2, 1 / 3, 2, 3

a = sym.Matrix([
    [g1, -g1, 0, 0, 1, 0],  # KCL í a
    [-g1, g1 + g2 + g3, -g2, -g3, 0, 0],  # KCL í b
    [0, -g2, g2, 0, 0, 1],  # KCL í c
    [0, -g3, 0, g3 + g4, 0, 0],  # KCL í d
    [1, 0, 0, 0, 0, 0],  # KVL yfir v1
    [0, 0, 1, 0, 0, 0],  # KVL yfir v2
])

b = sym.Matrix([0, 0, 0, 0, v1, v2])
mna = a.LUsolve(b)
assert np.allclose(analyze_mna(hd2_2), np.array(mna).astype(float).T)

hd2_4 = [
    CurrentSource(2, 0, value=3),
    CurrentSource(1, 0, value=-1),
    CurrentSource(3, 0, value=-2),
    CurrentSource(5, 0, value=4),
    CurrentSource(4, 0, value=2),
    Resistor(1, 0, value=1),
    Resistor(1, 3, value=1 / 2),
    Resistor(1, 2, value=1),
    Resistor(2, 3, value=1 / 3),
    Resistor(2, 4, value=1 / 2),
    Resistor(3, 0, value=1),
    Resistor(3, 4, value=1),
    Resistor(3, 5, value=1 / 3),
    Resistor(4, 5, value=1 / 2),
    Resistor(5, 0, value=1 / 2),
]

i1, i2, i3, i4, i5 = 3, -1, -2, 4, 2
g1, g2, g3, g4, g5, g6, g7, g8, g9, g10 = 1, 2, 1, 3, 2, 1, 1, 3, 2, 2

a = sym.Matrix([
    [g1 + g2 + g3, -g3, -g2, 0, 0],  # KCL í a (ekki i2, er í b vigri)
    [-g3, g3 + g4 + g5, -g4, -g5, 0],  # KCL í b (ekki i1, er í b vigri)
    [-g2, -g4, g2 + g4 + g6 + g7 + g8, -g7, -g8],  # KCL í c (ekki i3, er í b vigri)
    [0, -g5, -g7, g5 + g7 + g9, -g9],  # KCL í d (ekki i5, er í b vigri)
    [0, 0, -g8, -g9, g8 + g9 + g10],  # KCL í e (ekki i4, er í b vigri)
])

b = sym.Matrix([i2, i1, i3, i5, i4])

mna = a.LUsolve(b)
assert num_nodes(hd2_4) == 6
assert np.allclose(analyze_mna(hd2_4), np.array(mna).astype(float).T)

hd2_4b = [
    VoltageSource(2, 0, value=3),
    VoltageSource(1, 0, value=-1),
    VoltageSource(3, 0, value=-2),
    VoltageSource(5, 0, value=4),
    VoltageSource(4, 0, value=2),
    Resistor(1, 0, value=1),
    Resistor(1, 3, value=1 / 2),
    Resistor(1, 2, value=1),
    Resistor(2, 3, value=1 / 3),
    Resistor(2, 4, value=1 / 2),
    Resistor(3, 0, value=1),
    Resistor(3, 4, value=1),
    Resistor(3, 5, value=1 / 3),
    Resistor(4, 5, value=1 / 2),
    Resistor(5, 0, value=1 / 2),
]
num_nodes(hd2_4)

i1, i2, i3, i4, i5 = 3, -1, -2, 4, 2
g1, g2, g3, g4, g5, g6, g7, g8, g9, g10 = 1, 2, 1, 3, 2, 1, 1, 3, 2, 2

a = sym.Matrix([
    [g1 + g2 + g3, -g3, -g2, 0, 0],  # KCL í a (ekki i2, er í b vigri)
    [-g3, g3 + g4 + g5, -g4, -g5, 0],  # KCL í b (ekki i1, er í b vigri)
    [-g2, -g4, g2 + g4 + g6 + g7 + g8, -g7, -g8],  # KCL í c (ekki i3, er í b vigri)
    [0, -g5, -g7, g5 + g7 + g9, -g9],  # KCL í d (ekki i5, er í b vigri)
    [0, 0, -g8, -g9, g8 + g9 + g10],  # KCL í e (ekki i4, er í b vigri)
])

b = sym.Matrix([[i2, i1, i3, i5, i4]]).T

mna = a.LUsolve(b)
assert np.allclose(analyze_mna(hd2_4), np.array(mna).astype(float).T)
