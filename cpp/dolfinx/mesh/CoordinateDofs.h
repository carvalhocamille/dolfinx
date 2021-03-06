// Copyright (C) 2018 Chris N. Richardson
//
// This file is part of DOLFINX (https://www.fenicsproject.org)
//
// SPDX-License-Identifier:    LGPL-3.0-or-later

#pragma once

#include <Eigen/Dense>
#include <memory>
#include <vector>

namespace dolfinx
{
namespace graph
{
template <typename T>
class AdjacencyList;
}

namespace mesh
{

/// CoordinateDofs contains the connectivity from MeshEntities to the
/// geometric points which make up the mesh.

class CoordinateDofs
{
public:
  /// Constructor
  /// @param point_dofs Array containing point dofs for each entity
  CoordinateDofs(
      const Eigen::Ref<const Eigen::Array<std::int32_t, Eigen::Dynamic,
                                          Eigen::Dynamic, Eigen::RowMajor>>&
          point_dofs);

  /// Copy constructor
  CoordinateDofs(const CoordinateDofs& topology) = default;

  /// Move constructor
  CoordinateDofs(CoordinateDofs&& topology) = default;

  /// Destructor
  ~CoordinateDofs() = default;

  /// Copy assignment
  CoordinateDofs& operator=(const CoordinateDofs& topology) = default;

  /// Move assignment
  CoordinateDofs& operator=(CoordinateDofs&& topology) = default;

  /// Get the entity points associated with cells (const version)
  /// @return Connections from cells to points
  graph::AdjacencyList<std::int32_t>& entity_points();

  /// Get the entity points associated with cells (const version)
  /// @return Connections from cells to points
  const graph::AdjacencyList<std::int32_t>& entity_points() const;

private:
  // AdjacencyList<std::int32_t> from cells to points
  std::shared_ptr<graph::AdjacencyList<std::int32_t>> _coord_dofs;
};
} // namespace mesh
} // namespace dolfinx
