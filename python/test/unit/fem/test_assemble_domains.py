# Copyright (C) 2019 Chris Richardson
#
# This file is part of DOLFINX (https://www.fenicsproject.org)
#
# SPDX-License-Identifier:    LGPL-3.0-or-later
"""Unit tests for assembly over domains"""

import numpy
import pytest
from petsc4py import PETSc

import dolfinx
import ufl


@pytest.fixture
def mesh():
    return dolfinx.generation.UnitSquareMesh(dolfinx.MPI.comm_world, 10, 10)


parametrize_ghost_mode = pytest.mark.parametrize("mode", [
    pytest.param(dolfinx.cpp.mesh.GhostMode.none,
                 marks=pytest.mark.skipif(condition=dolfinx.MPI.size(dolfinx.MPI.comm_world) > 1,
                                          reason="Unghosted interior facets fail in parallel")),
    pytest.param(dolfinx.cpp.mesh.GhostMode.shared_facet,
                 marks=pytest.mark.skipif(condition=dolfinx.MPI.size(dolfinx.MPI.comm_world) == 1,
                                          reason="Shared ghost modes fail in serial")),
    pytest.param(dolfinx.cpp.mesh.GhostMode.shared_vertex,
                 marks=pytest.mark.skipif(condition=dolfinx.MPI.size(dolfinx.MPI.comm_world) == 1,
                                          reason="Shared ghost modes fail in serial"))])


def test_assembly_dx_domains(mesh):
    V = dolfinx.FunctionSpace(mesh, ("CG", 1))
    u, v = ufl.TrialFunction(V), ufl.TestFunction(V)

    marker = dolfinx.MeshFunction("size_t", mesh, mesh.topology.dim, 0)
    values = marker.values
    # Mark first, second and all other
    # Their union is the whole domain
    values[0] = 111
    values[1] = 222
    values[2:] = 333

    dx = ufl.Measure('dx', subdomain_data=marker, domain=mesh)

    w = dolfinx.Function(V)
    with w.vector.localForm() as w_local:
        w_local.set(0.5)

    #
    # Assemble matrix
    #

    a = w * ufl.inner(u, v) * (dx(111) + dx(222) + dx(333))

    A = dolfinx.fem.assemble_matrix(a)
    A.assemble()
    norm1 = A.norm()

    a2 = w * ufl.inner(u, v) * dx

    A2 = dolfinx.fem.assemble_matrix(a2)
    A2.assemble()
    norm2 = A2.norm()

    assert norm1 == pytest.approx(norm2, 1.0e-12)

    #
    # Assemble vector
    #

    L = ufl.inner(w, v) * (dx(111) + dx(222) + dx(333))
    b = dolfinx.fem.assemble_vector(L)
    b.ghostUpdate(addv=PETSc.InsertMode.ADD, mode=PETSc.ScatterMode.REVERSE)

    L2 = ufl.inner(w, v) * dx
    b2 = dolfinx.fem.assemble_vector(L2)
    b2.ghostUpdate(addv=PETSc.InsertMode.ADD, mode=PETSc.ScatterMode.REVERSE)

    assert b.norm() == pytest.approx(b2.norm(), 1.0e-12)

    #
    # Assemble scalar
    #

    L = w * (dx(111) + dx(222) + dx(333))
    s = dolfinx.fem.assemble_scalar(L)
    s = dolfinx.MPI.sum(mesh.mpi_comm(), s)

    L2 = w * dx
    s2 = dolfinx.fem.assemble_scalar(L2)
    s2 = dolfinx.MPI.sum(mesh.mpi_comm(), s2)

    assert (s == pytest.approx(s2, 1.0e-12) and 0.5 == pytest.approx(s, 1.0e-12))


def test_assembly_ds_domains(mesh):
    V = dolfinx.FunctionSpace(mesh, ("CG", 1))
    u, v = ufl.TrialFunction(V), ufl.TestFunction(V)

    marker = dolfinx.MeshFunction("size_t", mesh, mesh.topology.dim - 1, 0)

    def bottom(x):
        return numpy.isclose(x[1], 0.0)

    def top(x):
        return numpy.isclose(x[1], 1.0)

    def left(x):
        return numpy.isclose(x[0], 0.0)

    def right(x):
        return numpy.isclose(x[0], 1.0)

    marker.mark(bottom, 111)
    marker.mark(top, 222)
    marker.mark(left, 333)
    marker.mark(right, 444)

    ds = ufl.Measure('ds', subdomain_data=marker, domain=mesh)

    w = dolfinx.Function(V)
    with w.vector.localForm() as w_local:
        w_local.set(0.5)

    #
    # Assemble matrix
    #

    a = w * ufl.inner(u, v) * (ds(111) + ds(222) + ds(333) + ds(444))

    A = dolfinx.fem.assemble_matrix(a)
    A.assemble()
    norm1 = A.norm()

    a2 = w * ufl.inner(u, v) * ds

    A2 = dolfinx.fem.assemble_matrix(a2)
    A2.assemble()
    norm2 = A2.norm()

    assert norm1 == pytest.approx(norm2, 1.0e-12)

    #
    # Assemble vector
    #

    L = ufl.inner(w, v) * (ds(111) + ds(222) + ds(333) + ds(444))
    b = dolfinx.fem.assemble_vector(L)
    b.ghostUpdate(addv=PETSc.InsertMode.ADD, mode=PETSc.ScatterMode.REVERSE)

    L2 = ufl.inner(w, v) * ds
    b2 = dolfinx.fem.assemble_vector(L2)
    b2.ghostUpdate(addv=PETSc.InsertMode.ADD, mode=PETSc.ScatterMode.REVERSE)

    assert b.norm() == pytest.approx(b2.norm(), 1.0e-12)

    #
    # Assemble scalar
    #

    L = w * (ds(111) + ds(222) + ds(333) + ds(444))
    s = dolfinx.fem.assemble_scalar(L)
    s = dolfinx.MPI.sum(mesh.mpi_comm(), s)

    L2 = w * ds
    s2 = dolfinx.fem.assemble_scalar(L2)
    s2 = dolfinx.MPI.sum(mesh.mpi_comm(), s2)

    assert (s == pytest.approx(s2, 1.0e-12) and 2.0 == pytest.approx(s, 1.0e-12))


@parametrize_ghost_mode
def xtest_assembly_dS_domains(mode):
    N = 10
    mesh = dolfinx.UnitSquareMesh(dolfinx.MPI.comm_world, N, N, ghost_mode=mode)
    one = dolfinx.Constant(mesh, 1)
    val = dolfinx.fem.assemble_scalar(one * ufl.dS)
    val = dolfinx.MPI.sum(mesh.mpi_comm(), val)
    assert val == pytest.approx(2 * (N - 1) + N * numpy.sqrt(2), 1.0e-7)


@parametrize_ghost_mode
def test_additivity(mode):
    mesh = dolfinx.UnitSquareMesh(dolfinx.MPI.comm_world, 12, 12, ghost_mode=mode)
    V = dolfinx.FunctionSpace(mesh, ("CG", 1))

    f1 = dolfinx.Function(V)
    f2 = dolfinx.Function(V)
    f3 = dolfinx.Function(V)
    with f1.vector.localForm() as f1_local:
        f1_local.set(1.0)
    with f2.vector.localForm() as f2_local:
        f2_local.set(2.0)
    with f3.vector.localForm() as f3_local:
        f3_local.set(3.0)
    j1 = ufl.inner(f1, f1) * ufl.dx(mesh)
    j2 = ufl.inner(f2, f2) * ufl.ds(mesh)
    j3 = ufl.inner(ufl.avg(f3), ufl.avg(f3)) * ufl.dS(mesh)

    # Assemble each scalar form separately
    J1 = dolfinx.MPI.sum(mesh.mpi_comm(), dolfinx.fem.assemble_scalar(j1))
    J2 = dolfinx.MPI.sum(mesh.mpi_comm(), dolfinx.fem.assemble_scalar(j2))
    J3 = dolfinx.MPI.sum(mesh.mpi_comm(), dolfinx.fem.assemble_scalar(j3))

    # Sum forms and assemble the result
    J12 = dolfinx.MPI.sum(mesh.mpi_comm(), dolfinx.fem.assemble_scalar(j1 + j2))
    J13 = dolfinx.MPI.sum(mesh.mpi_comm(), dolfinx.fem.assemble_scalar(j1 + j3))
    J23 = dolfinx.MPI.sum(mesh.mpi_comm(), dolfinx.fem.assemble_scalar(j2 + j3))
    J123 = dolfinx.MPI.sum(mesh.mpi_comm(), dolfinx.fem.assemble_scalar(j1 + j2 + j3))

    # Compare assembled values
    assert (J1 + J2) == pytest.approx(J12)
    assert (J1 + J3) == pytest.approx(J13)
    assert (J2 + J3) == pytest.approx(J23)
    assert (J1 + J2 + J3) == pytest.approx(J123)
