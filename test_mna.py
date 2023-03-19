from mna import *


def test_num_nodes():
    assert num_nodes([VoltageSource(1, 0, value=1)]) == 2
    assert num_nodes([Resistor(1, 0), Resistor(10, 0)]) == 3
    assert num_nodes([Resistor(i, 0) for i in range(50)]) == 50
    assert num_nodes([VoltageSource(i, 0) for i in range(50) if i % 2 == 0]) == 25


def test_bassman_tonestack_resistors_only():
    bassman_tonestack_2 = [
        VoltageSource(1, 0, value=1),
        Resistor(1, 2, value=1),
        Resistor(1, 3, value=2),
        Resistor(2, 3, value=3),
        Resistor(3, 4, value=4),
        Resistor(2, 4, value=5),
        Resistor(4, 0, value=6),
    ]
    assert np.allclose(solve_mna(bassman_tonestack_2), np.array([1, 44 / 47, 85 / 94, 63 / 94, -21 / 188]))


def test_simple_circuit():
    components = [
        VoltageSource(1, 0, value=1),
        Resistor(1, 2, value=1),
        Resistor(1, 3, value=1),
        Resistor(2, 3, value=1),
        Resistor(3, 4, value=1),
        Resistor(2, 4, value=1),
        Resistor(4, 0, value=1),
    ]
    assert num_nodes(components) == 5
    assert np.allclose(solve_mna(components), np.array([1, 3 / 4, 3 / 4, 1 / 2, -1 / 2]))


def test_circuit_resistor_voltage_source():
    hd2_2 = [
        VoltageSource(1, 0, value=2),
        VoltageSource(3, 0, value=3),
        Resistor(1, 2, value=4),
        Resistor(2, 3, value=12),
        Resistor(2, 4, value=2),
        Resistor(4, 0, value=3)
    ]
    assert num_nodes(hd2_2) == 5

    g1, g2, g3, g4, v1, v2 = 1 / 4, 1 / 12, 1 / 2, 1 / 3, 2, 3
    hd2_2_direct = sym.Matrix([
        [g1, -g1, 0, 0, 1, 0],
        [-g1, g1 + g2 + g3, -g2, -g3, 0, 0],
        [0, -g2, g2, 0, 0, 1],
        [0, -g3, 0, g3 + g4, 0, 0],
        [1, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
    ]).LUsolve(sym.Matrix([0, 0, 0, 0, v1, v2]))
    assert np.allclose(solve_mna(hd2_2), np.array(hd2_2_direct).astype(float).T)


def test_current_source_resistor_galore():
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
    assert num_nodes(hd2_4) == 6

    i1, i2, i3, i4, i5 = 3, -1, -2, 4, 2
    g1, g2, g3, g4, g5, g6, g7, g8, g9, g10 = 1, 2, 1, 3, 2, 1, 1, 3, 2, 2

    hd2_4_direct = sym.Matrix([
        [g1 + g2 + g3, -g3, -g2, 0, 0],
        [-g3, g3 + g4 + g5, -g4, -g5, 0],
        [-g2, -g4, g2 + g4 + g6 + g7 + g8, -g7, -g8],
        [0, -g5, -g7, g5 + g7 + g9, -g9],
        [0, 0, -g8, -g9, g8 + g9 + g10],
    ]).LUsolve(sym.Matrix([i2, i1, i3, i5, i4]))

    assert np.allclose(solve_mna(hd2_4), np.array(hd2_4_direct).astype(float).T)