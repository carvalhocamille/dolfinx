// Automatically generated by FFC, the FEniCS Form Compiler, version 0.3.0.
// For further information, go to http://www/fenics.org/ffc/.
// Licensed under the GNU GPL Version 2.

#ifndef __P1TRI_H
#define __P1TRI_H

#include <dolfin/Mesh.h>
#include <dolfin/Cell.h>
#include <dolfin/Point.h>
#include <dolfin/Vector.h>
#include <dolfin/AffineMap.h>
#include <dolfin/FiniteElement.h>
#include <dolfin/FiniteElementSpec.h>

namespace dolfin
{
  
  class P1tri : public dolfin::FiniteElement
  {
  public:
  
    P1tri() : dolfin::FiniteElement(), tensordims(0), subelements(0)
    {
      // Element is scalar, don't need to initialize tensordims
  
      // Element is simple, don't need to initialize subelements
    }
  
    ~P1tri()
    {
      if ( tensordims ) delete [] tensordims;
      if ( subelements )
      {
        for (unsigned int i = 0; i < elementdim(); i++)
          delete subelements[i];
        delete [] subelements;
      }
    }
  
    inline unsigned int spacedim() const
    {
      return 3;
    }
  
    inline unsigned int shapedim() const
    {
      return 2;
    }
  
    inline unsigned int tensordim(unsigned int i) const
    {
      dolfin_error("Element is scalar.");
      return 0;
    }
  
    inline unsigned int elementdim() const
    {
      return 1;
    }
  
    inline unsigned int rank() const
    {
      return 0;
    }
  
    void nodemap(int nodes[], const Cell& cell, const Mesh& mesh) const
    {
      nodes[0] = cell.vertexID(0);
      nodes[1] = cell.vertexID(1);
      nodes[2] = cell.vertexID(2);
    }
  
    void pointmap(Point points[], unsigned int components[], const AffineMap& map) const
    {
      points[0] = map(0.000000000000000e+00, 0.000000000000000e+00);
      points[1] = map(1.000000000000000e+00, 0.000000000000000e+00);
      points[2] = map(0.000000000000000e+00, 1.000000000000000e+00);
      components[0] = 0;
      components[1] = 0;
      components[2] = 0;
    }
  
    void vertexeval(real values[], unsigned int vertex, const real x[], const Mesh& mesh) const
    {
      // FIXME: Temporary fix for Lagrange elements
      values[0] = x[vertex];
    }
  
    const FiniteElement& operator[] (unsigned int i) const
    {
      return *this;
    }
  
    FiniteElement& operator[] (unsigned int i)
    {
      return *this;
    }
  
    FiniteElementSpec spec() const
    {
      FiniteElementSpec s("Lagrange", "triangle", 1);
      return s;
    }
    
  private:
  
    unsigned int* tensordims;
    FiniteElement** subelements;
  
  };
  
}

#endif
