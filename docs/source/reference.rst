API Reference
=============

This is an API reference for the vegas-lattice package.


The lattice module
------------------

.. automodule:: vlattice.lattice
  :members: Atom, Site, Vertex, Locator, Lattice, NanoParticle, DepletedLattice

Example
*******

.. testsetup:: *

  from vlattice.lattice import Atom


.. doctest::

  >>> atom = Atom((0, 0, 0), 'Co', 0)
  >>> print(atom.kind)
  Co


.. doctest::

  >>> from vlattice.lattice import Atom
  >>> atom = Atom((0, 0, 0), 'Co', 0)
  >>> print(atom.kind)
  Co
  >>> print(atom.id)
  0


The material module
-------------------

.. automodule:: vlattice.material
  :members:


The scripts module
------------------

.. automodule:: vlattice.scripts
  :members: cli
