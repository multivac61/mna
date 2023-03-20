import numpy as np


# The unknown current flows into nodes 1/3 (+) and out of nodes 0/2 (-)
class Component:
    # + n1 --\
    #         ?
    #         |
    # - n0 --/
    def __init__(self, n1, n0, value=0, name=None):
        self.n1, self.n0 = n1, n0
        self.name = name
        self.value = value

    def nodes(self):
        return self.n1, self.n0

    def num_unknown_currents(self):
        return 0


class VoltageSource(Component):
    def __init__(self, n1, n0, value=0, name=None):
        super().__init__(n1, n0, value, name)

    def num_unknown_currents(self):
        return 1

    def stamp(self, G, B, C, _D, _I, E, unknown_currents):
        idx = num_unknown_currents(_unknown_currents)
        unknown_currents.append(self)

        B[self.n1, idx] += 1
        B[self.n0, idx] -= 1
        C[idx, self.n1] += 1
        C[idx, self.n0] -= 1

        E[len(G) + idx] = self.value


class CurrentSource(Component):
    def __init__(self, n1, n0, value=0, name=None):
        super().__init__(n1, n0, value, name)

    def stamp(self, _G, _B, _C, _D, _I, E, _unknown_currents):
        E[self.n1] += self.value
        E[self.n0] -= self.value


class Resistor(Component):
    def __init__(self, n1, n0, value=0, name=None):
        super().__init__(n1, n0, value, name)

    def stamp(self, G, _B, _C, _D, _I, _E, _unknown_currents):
        G[self.n1, self.n1] += 1 / self.value
        G[self.n0, self.n0] += 1 / self.value
        G[self.n1, self.n0] -= 1 / self.value
        G[self.n0, self.n1] -= 1 / self.value


class Capacitor(Component):
    def __init__(self, n1, n0, value=0, name=None):
        super().__init__(n1, n0, value, name)

    def stamp(self, G, _B, _C, _D, _I, _E, _unknown_currents):
        G[self.n1, self.n1] += 1 / self.value
        G[self.n0, self.n0] += 1 / self.value
        G[self.n1, self.n0] -= 1 / self.value
        G[self.n0, self.n1] -= 1 / self.value


class Inductor(Component):
    def __init__(self, n1, n0, value=0, name=None):
        super().__init__(n1, n0, value, name)

    def stamp(self, G, _B, _C, _D, _I, _E, _unknown_currents):
        G[self.n1, self.n1] += self.value
        G[self.n0, self.n0] += self.value
        G[self.n1, self.n0] -= self.value
        G[self.n0, self.n1] -= self.value


class OpenCircuit(Component):
    def __init__(self, n1, n0, value=0, name=None):
        super().__init__(n1, n0, value, name)

    def stamp(self, _G, _B, _C, _D, _I, _E, _unknown_currents):
        pass

class ShortCircuit(Component):
    def __init__(self, n1, n0, value=0, name=None)
        super().__init__(n1, n0, value, name)
        self.norator = Norator(n1, n0, value, name)
        self.nullator = Norator(n1, n0, value, name)

    def stamp(self, _G, _B, _C, _D, _I, _E, _unknown_currents):
        idx = num_unknown_currents(_unknown_currents)
        unknown_currents.append(self)

        # Combined nullator and norator
        self.norator.stamp(_G, _B, _C, _D, _I, _E, _unknown_currents)
        self.nullator.stamp(_G, _B, _C, _D, _I, _E, _unknown_currents)


class Nullator(Component):
    def __init__(self, n1, n0, value=0, name=None):
        super().__init__(n1, n0, value, name)

    def num_unknown_currents(self):
        return 1

    def stamp(self, _G, _B, _C, _D, _I, _E, _unknown_currents):
        idx = num_unknown_currents(_unknown_currents)
        unknown_currents.append(self)

        C[idx, self.n1] += 1
        C[idx, self.n0] -= 1

class Norator(Component):
    def __init__(self, n1, n0, value=0, name=None):
        super().__init__(n1, n0, value, name)

    def stamp(self, _G, _B, _C, _D, _I, _E, _unknown_currents):
        B[self.n1, idx] += 1
        B[self.n0, idx] -= 1


class TwoPort(Component):
    # + n1 --\   /-- + n3
    #         ? ?
    #         | |
    # - n0 --/   \-- - n2
    def __init__(self, n1, n0, n3, n2, value=0, name=None):
        super().__init__(n1, n0, value, name)
        self.n3, self.n2 = n3, n2

    def nodes(self):
        return self.n1, self.n0, self.n3, self.n2

class VoltageControlledCurrentSource(TwoPort):
    def __init__(self, n1, n0, n3, n2, value=0, name=None):
        super().__init__(n1, n0, n3, n2, value, name)

    def simulate(self, _G, _B, _C, _D, _I, _E, _unknown_currents):
        G[self.n3, self.n3] += self.value
        G[self.n2, self.n2] += self.value
        G[self.n3, self.n2] -= self.value
        G[self.n2, self.n3] -= self.value

class VoltageControlledVoltageSource(TwoPort):
    def __init__(self, n1, n0, n3, n2, value=0, name=None):
        super().__init__(n1, n0, n3, n2, value, name)

    def num_unknown_currents(self):
        return 1

    def simulate(self, _G, _B, _C, _D, _I, _E, _unknown_currents):
        idx = num_unknown_currents(_unknown_currents)
        unknown_currents.append(self)

        # TODO: Test that this code is indeed correct wrt polarity
        B[self.n3, idx] += 1
        B[self.n2, idx] -= 1
        C[idx, self.n3] += 1
        C[idx, self.n2] -= 1
        C[idx, self.n1] -= self.value
        C[idx, self.n0] += self.value

class CurrentControlledCurrentSource(TwoPort):
    def __init__(self, n1, n0, n3, n2, value=0, name=None):
        super().__init__(n1, n0, n3, n2, value, name)

    def num_unknown_currents(self):
        return 1

    def simulate(self, _G, _B, _C, _D, _I, _E, _unknown_currents):
        idx = num_unknown_currents(_unknown_currents)
        unknown_currents.append(self)

        # TODO: Test that this code is indeed correct wrt polarity
        B[self.n1, idx] += 1
        B[self.n0, idx] -= 1
        B[self.n3, idx] += self.value
        B[self.n2, idx] -= self.value
        C[idx, self.n1] += 1
        C[idx, self.n0] -= 1

class CurrentControlledVoltageSource(TwoPort):
    def __init__(self, n1, n0, n3, n2, value=0, name=None):
        super().__init__(n1, n0, n3, n2, value, name)

    def num_unknown_currents(self):
        return 2

    def simulate(self, _G, _B, _C, _D, _I, _E, _unknown_currents):
        idx = num_unknown_currents(_unknown_currents)
        unknown_currents.append(self)

        # TODO: Test that this code is indeed correct wrt polarity
        B[self.n1, idx] += 1
        B[self.n0, idx] -= 1
        B[self.n3, idx+1] += 1
        B[self.n2, idx+1] -= 1
        C[idx, self.n1] += 1
        C[idx, self.n0] -= 1
        C[idx+1, self.n3] += 1
        C[idx+1, self.n2] -= 1
        D[idx+1, idx] -= self.value # TODO



class OperationalAmplifier(TwoPort):
    def __init__(self, n1, n0, n3, n2, value=0, name=None):
        super().__init__(n1, n0, n3, n2, value, name)

    def num_unknown_currents(self):
        return 1

    def simulate(self, _G, _B, _C, _D, _I, _E, _unknown_currents):
        idx = num_unknown_currents(_unknown_currents)
        unknown_currents.append(self)

        B[self.n3, idx] += 1
        B[self.n2, idx] -= 1
        C[idx, self.n1] += 1
        C[idx, self.n0] -= 1

class IdealTransformer(TwoPort):
    def __init__(self, n1, n0, n3, n2, l1=0, l2=0, name=None):
        super().__init__(n1, n0, n3, n2, value=0, name=name)
        self.l1, self.l2 = l1, l2

    def num_unknown_currents(self):
        return 2

    def simulate(self, _G, _B, _C, _D, _I, _E, _unknown_currents):
        assert False
        pass


def num_nodes(components):
    return len(set(node for component in components for node in component.nodes()))

def num_unknown_currents(components):
    return sum(components.num_unknown_currents() for component in components)

def solve_mna(components):
    g_size = num_nodes(components)
    b_size = sum(1 for c in components if isinstance(c, VoltageSource))

    G = np.zeros((g_size, g_size))
    B = np.zeros((g_size, b_size))
    C = np.zeros((b_size, g_size))
    D = np.zeros((b_size, b_size))
    I = np.zeros(g_size + b_size)
    E = np.zeros(g_size + b_size)
    unknown_currents = []

    for component in components:
        component.stamp(G, B, C, D, I, E, unknown_currents)

    A = np.block([
        [G, B],
        [C, D]
    ])

    # NOTE: The number of independent KCLs is always one less than the number of nodes.
    # Any node may be chosen as *datum node* (ground node) and the solution will be the same.
    # I choose the ground node as the datum node, so I discard the first row and column of the matrix.
    return np.linalg.solve(A[1:, 1:], E[1:] - I[1:])  # Discard ground node
