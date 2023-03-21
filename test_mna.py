from mna import *

import sympy as sym


def sym_solve_mna(circuit):
    return map(sym.Matrix, solve_mna(circuit, zeros=lambda x: sym.Matrix(np.zeros(x)), block=sym.BlockMatrix,
                                     return_populated_system=True))

def test_num_unknown_currents():
    assert num_unknown_currents([VoltageSource(1, 0, 1)]) == 1
    assert num_unknown_currents([VoltageSource(1, 0, 1), VoltageSource(1, 0, 1)]) == 2

def test_num_nodes():
    assert num_nodes([VoltageSource(1, 0, 1)]) == 2
    assert num_nodes([Resistor(1, 0), Resistor(10, 0)]) == 3
    assert num_nodes([Resistor(i, 0) for i in range(50)]) == 50
    assert num_nodes([VoltageSource(i, 0) for i in range(50) if i % 2 == 0]) == 25


def test_bassman_tonestack_resistors_only():
    bassman_tonestack_2 = [
        VoltageSource(1, 0, 1),
        Resistor(1, 2, 1),
        Resistor(1, 3, 1),
        Resistor(2, 3, 1),
        Resistor(3, 4, 1),
        Resistor(2, 4, 1),
        Resistor(4, 0, 1),
    ]

    assert num_nodes(bassman_tonestack_2) == 5
    assert np.allclose(solve_mna(bassman_tonestack_2), np.array([1, 3 / 4, 3 / 4, 1 / 2, -1 / 2]))

    bassman_tonestack_2 = [
        VoltageSource(1, 0, 1),
        Resistor(1, 2, 1),
        Resistor(1, 3, 2),
        Resistor(2, 3, 3),
        Resistor(3, 4, 4),
        Resistor(2, 4, 5),
        Resistor(4, 0, 6),
    ]
    assert num_nodes(bassman_tonestack_2) == 5
    assert np.allclose(solve_mna(bassman_tonestack_2), np.array([1, 44 / 47, 85 / 94, 63 / 94, -21 / 188]))


def test_simple_circuit():
    components = [
        VoltageSource(1, 0, 1),
        Resistor(1, 2, 1),
        Resistor(1, 3, 1),
        Resistor(2, 3, 1),
        Resistor(3, 4, 1),
        Resistor(2, 4, 1),
        Resistor(4, 0, 1),
    ]
    assert num_nodes(components) == 5
    assert np.allclose(solve_mna(components), np.array([1, 3 / 4, 3 / 4, 1 / 2, -1 / 2]))


def test_simple_circuit_2():
    r1, r2, r3, r4, r5, v1 = sym.symbols('r1, r2, r3, r4, r5, v1')
    hd5_1 = [
        VoltageSource(1, 0, v1),
        Resistor(1, 2, r1),
        Resistor(1, 3, r2),
        Resistor(2, 3, r3),
        Resistor(2, 0, r4),
        Resistor(3, 0, r5),
    ]

    assert num_nodes(hd5_1) == 4
    assert num_unknown_currents(hd5_1) == 1

    g1, g2, g3, g4, g5 = 1 / r1, 1 / r2, 1 / r3, 1 / r4, 1 / r5
    A_hand = sym.Matrix([
        [g1 + g2, -g1, -g2, 1],
        [-g1, g1 + g3 + g4, -g3, 0],
        [-g2, -g3, g2 + g3 + g5, 0],
        [1, 0, 0, 0]
    ])
    E_hand = sym.Matrix([0, 0, 0, v1])

    A, E = sym_solve_mna(hd5_1)

    assert A == A_hand
    assert E == E_hand


def test_circuit_resistor_voltage_source():
    g1, g2, g3, g4, v1, v2 = 1 / 4, 1 / 12, 1 / 2, 1 / 3, 2, 3
    hd2_2 = [
        VoltageSource(1, 0, v1),
        VoltageSource(3, 0, v2),
        Resistor(1, 2, 1 / g1),
        Resistor(2, 3, 1 / g2),
        Resistor(2, 4, 1 / g3),
        Resistor(4, 0, 1 / g4)
    ]
    assert num_nodes(hd2_2) == 5

    hd2_2_direct = np.linalg.solve(np.array([
        [g1, -g1, 0, 0, 1, 0],
        [-g1, g1 + g2 + g3, -g2, -g3, 0, 0],
        [0, -g2, g2, 0, 0, 1],
        [0, -g3, 0, g3 + g4, 0, 0],
        [1, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
    ]), np.array([0, 0, 0, 0, v1, v2]))
    assert np.allclose(solve_mna(hd2_2), hd2_2_direct)


def test_current_source_resistor_galore():
    hd2_4 = [
        CurrentSource(2, 0, 3),
        CurrentSource(1, 0, -1),
        CurrentSource(3, 0, -2),
        CurrentSource(5, 0, 4),
        CurrentSource(4, 0, 2),
        Resistor(1, 0, 1),
        Resistor(1, 3, 1 / 2),
        Resistor(1, 2, 1),
        Resistor(2, 3, 1 / 3),
        Resistor(2, 4, 1 / 2),
        Resistor(3, 0, 1),
        Resistor(3, 4, 1),
        Resistor(3, 5, 1 / 3),
        Resistor(4, 5, 1 / 2),
        Resistor(5, 0, 1 / 2),
    ]
    assert num_nodes(hd2_4) == 6

    i1, i2, i3, i4, i5 = 3, -1, -2, 4, 2
    g1, g2, g3, g4, g5, g6, g7, g8, g9, g10 = 1, 2, 1, 3, 2, 1, 1, 3, 2, 2

    hd2_4_direct = np.linalg.solve(np.array([
        [g1 + g2 + g3, -g3, -g2, 0, 0],
        [-g3, g3 + g4 + g5, -g4, -g5, 0],
        [-g2, -g4, g2 + g4 + g6 + g7 + g8, -g7, -g8],
        [0, -g5, -g7, g5 + g7 + g9, -g9],
        [0, 0, -g8, -g9, g8 + g9 + g10],
    ]), np.array([i2, i1, i3, i5, i4]))

    assert np.allclose(solve_mna(hd2_4), hd2_4_direct)


def test_op_adder_circuit():
    hd3_3 = [
        ResistiveVoltageSource(1, 0, 1, 1),
        ResistiveVoltageSource(2, 0, 1, 1),
        ResistiveVoltageSource(2, 0, 1, 1),
        Resistor(1, 3, 1),
        OperationalAmplifier(2, 1, 3, 0)
    ]
    g1 = g2 = g3 = g4 = v1 = v2 = v3 = 1
    hd3_3_direct = np.linalg.solve(np.array([
        [g4, 0, -g4, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 0],
        [-g4, 0, g4, 0, 0, 0, 1],
        [1, 0, 0, -1 / g3, 0, 0, 0],
        [0, 1, 0, 0, -1 / g1, 0, 0],
        [0, 1, 0, 0, 0, -1 / g2, 0],
        [-1, 1, 0, 0, 0, 0, 0]
    ]), np.array([0, 0, 0, v1, v2, v3, 0]))
    print(solve_mna(hd3_3), np.array(hd3_3_direct).astype(float).T)
    assert num_nodes(hd3_3) == 4
    assert np.allclose(solve_mna(hd3_3), np.array(hd3_3_direct).astype(float).T)


def test_resistive_voltage_source():
    volt_source = [
        VoltageSource(1, 0, 1),
        Resistor(1, 2, 1),
        Resistor(2, 3, 1),
    ]
    resistive_volt_source = [
        ResistiveVoltageSource(1, 0, 1, 1),
        Resistor(1, 2, 1),
    ]
    assert np.allclose(solve_mna(volt_source)[1:], solve_mna(resistive_volt_source))


def test_vcvs():
    r1, r2, r3, mu, i1 = sym.symbols('r1, r2, r3, mu, i1')
    hd3_4 = [
        CurrentSource(1, 0, i1),
        Resistor(1, 0, r1),
        Resistor(1, 2, r2),
        Resistor(2, 0, r3),
        VoltageControlledVoltageSource(1, 0, 2, 1, mu)
    ]

    assert num_nodes(hd3_4) == 3
    assert num_unknown_currents(hd3_4) == 1

    A_hand = sym.Matrix([
        [1 / r1 + 1 / r2, -1 / r2, -1],
        [-1 / r2, 1 / r2 + 1 / r3, 1],
        [-1 - mu, 1, 0]
    ])
    E_hand = sym.Matrix([i1, 0, 0])

    A, E = sym_solve_mna(hd3_4)

    assert A == A_hand
    assert E == E_hand


def test_ccvs():
    pass


def test_cccs():
    r1, r2, r3, r4, mu, i1, v1 = sym.symbols('r1, r2, r3, r4, mu, i1, v1')
    hd5_2 = [
        CurrentControlledCurrentSource(1, 4, 1, 0, mu),
        VoltageSource(1, 4, v1),
        CurrentSource(2, 0, i1),
        Resistor(1, 2, r1),
        Resistor(4, 3, r2),
        Resistor(2, 3, r3),
        Resistor(3, 0, r4)
    ]

    assert num_nodes(hd5_2) == 5
    assert num_unknown_currents(hd5_2) == 2

    g1, g2, g3, g4 = 1 / r1, 1 / r2, 1 / r3, 1 / r4
    A_hand = sym.Matrix([
        [g1, -g1, 0, 0, -mu + 1],
        [-g1, g1 + g3, -g3, 0, 0],
        [0, -g3, g2 + g3 + g4, -g2, 0],
        [0, 0, -g2, g2, -1],
        [1, 0, 0, -1, 0],
    ])
    E_hand = sym.Matrix([0, i1, 0, 0, v1])

    A, E = sym_solve_mna(hd5_2)

    assert A == A_hand
    assert E == E_hand


def test_non_planar_circuit():
    r1, r2, r3, r4, v1, i1 = sym.symbols('r1, r2, r3, r4, v1, i1')
    circuit = [
        Resistor(1, 0, r1),
        ResistiveVoltageSource(1, 0, volt=v1, resistance=r3),
        Resistor(1, 2, r2),
        Resistor(2, 0, r4),
        CurrentSource(0, 2, i1)
    ]

    assert num_nodes(circuit) == 3
    assert num_unknown_currents(circuit) == 1

    A_hand = sym.Matrix([
        [1 / r1 + 1 / r2, -1 / r2, 1],
        [-1 / r2, 1 / r2 + 1 / r4, 0],
        [1, 0, -r3]
    ])
    E_hand = sym.Matrix([0, -i1, v1])

    A, E = sym_solve_mna(circuit)

    assert A == A_hand
    assert E == E_hand


def test_vccs():
    r1, r2, r3, r4, mu = sym.symbols('r1 r2 r3 r4 mu')
    hd4_1 = [
        Resistor(1, 0, r1 + r2),
        Resistor(1, 0, r3),
        Resistor(1, 2, r4),
        VoltageControlledCurrentSource(1, 0, 2, 0, mu),
        CurrentSource(2, 0, 1)
    ]

    assert num_nodes(hd4_1) == 3
    assert num_unknown_currents(hd4_1) == 0

    A_hand = sym.Matrix([
        [1 / (r1 + r2) + 1 / r3 + 1 / r4, -1 / r4],
        [-1 / r4 - mu, 1 / r4]
    ])
    E_hand = sym.Matrix([0, 1])

    A, E = sym_solve_mna(hd4_1)

    assert A_hand == A and E_hand == E


def test_op_amp():
    v_in = 42
    hd3_1 = [
        VoltageSource(1, 0, v_in),
        OperationalAmplifier(1, 2, 3, 0),
        Resistor(2, 0, 10e3),
        Resistor(2, 3, 10e3),
        Resistor(3, 4, 2e3),
        Resistor(4, 0, 8e3),
        Resistor(5, 0, 10e3),
        OperationalAmplifier(4, 5, 6, 0),
        Resistor(5, 6, 10e3),
    ]

    assert num_nodes(hd3_1) == 7
    assert np.allclose(solve_mna(hd3_1), v_in * np.array([1.0, 1.0, 2.0, 1.6, 1.6, 16 / 5, 0.0, - 3.0e-04, -1.6e-04]))


def test_op_amp2():
    r1, r2, r3, r4, r5, r6, vin = sym.symbols('r1, r2, r3, r4, r5, r6, vin')
    hd3_2 = [
        VoltageSource(1, 0, vin),
        Resistor(1, 2, r1),
        Resistor(2, 4, r2),
        Resistor(2, 3, r3),
        Resistor(3, 4, r4),
        Resistor(4, 5, r5),
        Resistor(5, 0, r6),
        OperationalAmplifier(5, 3, 4, 0),
    ]
    assert num_nodes(hd3_2) == 6
    assert num_unknown_currents(hd3_2) == 2

    g1, g2, g3, g4, g5, g6 = 1 / r1, 1 / r2, 1 / r3, 1 / r4, 1 / r5, 1 / r6

    A_hand = sym.Matrix([
        [g1, -g1, 0, 0, 0, 1, 0],
        [-g1, g1 + g2 + g3, -g3, -g2, 0, 0, 0],
        [0, -g3, g3 + g4, -g4, 0, 0, 0],
        [0, -g2, -g4, g2 + g4 + g5, -g5, 0, 1],
        [0, 0, 0, -g5, g5 + g6, 0, 0],
        [1, 0, 0, 0, 0, 0, 0],
        [0, 0, -1, 0, 1, 0, 0],
    ])
    E_hand = sym.Matrix([0, 0, 0, 0, 0, vin, 0])

    A, E = sym_solve_mna(hd3_2)

    assert A_hand == A and E_hand == E
