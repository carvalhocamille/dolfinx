// Copyright (C) 2019 Chris Richardson
//
// This file is part of DOLFIN (https://www.fenicsproject.org)
//
// SPDX-License-Identifier:    LGPL-3.0-or-later

#include "ElementDofMap.h"
#include <cstdlib>
#include <dolfin/mesh/CellType.h>

using namespace dolfin;
using namespace dolfin::fem;

//-----------------------------------------------------------------------------
ElementDofMap::ElementDofMap(const ufc_dofmap& dofmap,
                             const mesh::CellType& cell_type)
{
  _cell_dimension
      = dofmap.num_element_support_dofs + dofmap.num_global_support_dofs;

  // Copy over number of dofs per entity
  std::copy(dofmap.num_entity_dofs, dofmap.num_entity_dofs + 4,
            _num_entity_dofs);

  // Fill entity dof indices
  for (unsigned int dim = 0; dim < 4; ++dim)
  {
    unsigned int num_entities = cell_type.num_entities(dim);
    _entity_dofs[dim].resize(num_entities);
    for (unsigned int i = 0; i < num_entities; ++i)
    {
      _entity_dofs[dim][i].resize(_num_entity_dofs[dim]);
      dofmap.tabulate_entity_dofs(_entity_dofs[dim][i].data(), dim, i);
    }
  }

  // Fill all subdofmaps
  for (int i = 0; i < dofmap.num_sub_dofmaps; ++i)
  {
    ufc_dofmap* sub_dofmap = dofmap.create_sub_dofmap(i);
    sub_dofmaps.push_back(
        std::make_unique<ElementDofMap>(*sub_dofmap, cell_type));
    std::free(sub_dofmap);
  }

  // Get sizes of all sub_dofmaps
  std::vector<int> sub_dofmap_sizes;
  for (const auto& dm : sub_dofmaps)
    sub_dofmap_sizes.push_back(dm->_cell_dimension);
}
//-----------------------------------------------------------------------------
std::vector<int> ElementDofMap::tabulate_entity_dofs(unsigned int dim,
                                                     unsigned int i) const
{
  assert(dim < _entity_dofs.size());
  assert(i < _entity_dofs[dim].size());

  return _entity_dofs[dim][i];
}
