Tutorial
========

This is a tutorial on how to use vegas-lattice.

First, we begin with a short physical and mathematical introduction to lattices.  Later, we explain how to write a descriptor (which is the basic file that vegas-lattice uses) and, in the end, we use said descriptor in a small simulation using the **bulk** command.


Scientific Background
---------------------

`Mathematically <https://en.wikipedia.org/wiki/Lattice_%28group%29>`_, one can consider lattices as subgroups of :math:`\mathbb{R}^n` formed by considering two linearly independent translations, but we will take a physical approach (and, for that , we will follow the `ALPS <http://alps.comp-phys.org/mediawiki/index.php/Tutorials:LatticeHOWTO:SimpleGraphs>`_ webpage's tutorial).

.. To-Do: finish writing the physical background, and adding illustrations.

Writing a descriptor: short example
-----------------------------------

A descriptor is a `JSON <http://www.w3schools.com/json/>`_ file which describes the atom kinds and interactions. As a first example, we will consider generating a grid graph of just 4 nodes (or atoms). 

.. To-Do: image of a small lattice with 4 colored nodes and a complete graph between them.

Writing a descriptor using *describe*
-------------------------------------

.. Structure:
    First of all, an introduction to the notion of translations and a couple
    images. Then, using a constructor to build a lattice, ...