from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import map
from builtins import zip
from builtins import str

import collections
import itertools
import json
import random

import click
import numpy

from .lattice import Atom
from .lattice import Interaction
from .lattice import Lattice
from .lattice import Locator
from .lattice import NanoParticle


# Python2 compatibility
from future import standard_library
standard_library.install_aliases()


def get_spin(site, spins):
    return random.choice(numpy.atleast_1d(spins[site.atom.kind]))


@click.group()
def cli():
    '''
    Some generators for grid graph based nanostructures, this program would
    generate samples from descriptor files using linear time algorithms which
    are much faster than those based on checking distances between points
    '''
    pass


@cli.command()
@click.argument('descriptor', type=click.File('r'))
@click.option('--shape', default=(1, 1, 1),
              help='shape of the lattice')
@click.option('--pbc', default=(True, True, True),
              help='use periodic boundary conditions')
@click.option('--lattice-params', default=(1.0, 1.0, 1.0),
              help='lattice parameters for the atoms in the descriptor')
def bulk(descriptor, shape, pbc, lattice_params):

    data = json.load(descriptor)
    atoms = [Atom(**kw) for kw in data['atoms']]
    vertices = [Interaction(**kw) for kw in data['interactions']]
    spins = data['material']['spins']
    exchanges = data['material']['exchanges']
    latt = Lattice(atoms, shape, pbc, vertices)

    lsites = []
    linteractions = []

    unitcell = numpy.eye(3) * lattice_params
    locator = Locator(unitcell, crystal_coords=False)

    for site in latt.sites():
        lsites.append(site)
        for interaction in latt.interactions_for(site):
            linteractions.append(interaction)

    click.echo("{}\t{}\t{}\t{}".format(len(lsites), len(linteractions), 2, 0))
    click.echo("A\nB")
    for site in lsites:
        px, py, pz = tuple(locator.locate(site))
        click.echo(
            "{id}\t{px}\t{py}\t{pz}\t{spin}\t0.0\t0.0\t0.0\t0.0\t{kind}".format(
                id=latt.index(site),
                px=px, py=py, pz=pz,
                spin=get_spin(site, spins),
                kind=site.atom.kind
            ))

    for source, target, vertex in linteractions:
        click.echo('{source}\t{target}\t{exchange}'.format(
            source=latt.index(source),
            target=latt.index(target),
            exchange=exchanges[vertex.kind]
            ))


@cli.command()
@click.argument('descriptor', type=click.File('r'))
@click.option('--diameter', default=5,
              help='Diameter of the nanoparticle')
@click.option('--lattice-params', default=(1.0, 1.0, 1.0),
              help='lattice parameters for the atoms in the descriptor')
def nanoparticle(descriptor, diameter, lattice_params):

    data = json.load(descriptor)
    atoms = [Atom(**kw) for kw in data['atoms']]
    vertices = [Interaction(**kw) for kw in data['interactions']]
    spins = data['material']['spins']
    exchanges = data['material']['exchanges']
    unitcell = numpy.eye(3) * lattice_params
    locator = Locator(unitcell, crystal_coords=False)
    shape = (diameter, ) * 3
    pbc = (False, ) * 3

    latt = NanoParticle(locator, diameter*4, atoms, shape, pbc, vertices)

    lsites = []
    linteractions = []
    new_ids = {}

    for idx, site in enumerate(latt.sites()):
        lsites.append(site)
        new_ids[latt.index(site)] = idx
        for interaction in latt.interactions_for(site):
            linteractions.append(interaction)

    click.echo("{}\t{}\t{}\t{}".format(len(lsites), len(linteractions), 2, 0))
    click.echo("A\nB")

    for site in lsites:
        px, py, pz = tuple(locator.locate(site))
        click.echo(
            "{id}\t{px}\t{py}\t{pz}\t{spin}\t0.0\t0.0\t0.0\t0.0\t{kind}".format(
                id=new_ids[latt.index(site)],
                px=px, py=py, pz=pz,
                spin=get_spin(site, spins),
                kind=site.atom.kind
            ))

    for source, target, vertex in linteractions:
        click.echo('{source}\t{target}\t{exchange}'.format(
            source=new_ids[latt.index(source)],
            target=new_ids[latt.index(target)],
            exchange=exchanges[vertex.kind]
            ))


@cli.command()
@click.argument('sites', type=click.File('r'))
@click.argument('descriptor', type=click.File('w'), default="-")
@click.option('--shape', default=(1.0, 1.0, 1.0),
              help='Shape of the unitcell (default: a=b=c=1)')
@click.option('--cut', default=1.0,
              help='Neighbor cutoff radius (default: 1.0)')
def describe(sites, descriptor, shape, cut):
    '''
    Generates a descriptor file from a site list file, the site list file format
    should be a plain text file with the following format:

        <x> <y> <z> <kind>

    the kind parameter is taked in as a string, and the identifiers of the sites
    are generated according to the order in which this file is presented,
    furthermore, you should include the lattice parameters in x y and z for
    the unit cell.

    If DESCRIPTOR is specified and writable, the json representation of the
    descriptor file will be written there, otherwise the standard output will
    be used.
    '''
    points = numpy.loadtxt(sites, usecols=(0, 1, 2))
    # Rewind the file handle
    sites.seek(0, 0)
    labels = numpy.loadtxt(sites, usecols=(3, ), dtype=str)
    labels = [l[2:-1] for l in labels]
    images = map(numpy.array, itertools.product((-1, 0, 1), repeat=3))

    expanded = []
    for image in images:
        imaged = points + shape * image
        for site, kind, uuid in zip(imaged, labels, itertools.count(0)):
            expanded.append({
                'site': site,
                'kind': kind,
                'image': image,
                'id': uuid,
            })

    norm = numpy.linalg.norm
    interactions = []
    for uuid, site in enumerate(points):
        for other in expanded:
            dis = norm(site - other['site'])
            is_real = (other['image'] == (0, 0, 0, )).all()
            if dis < cut and (not is_real or uuid != other['id']):
                interactions.append(collections.OrderedDict([
                    ('source', uuid),
                    ('target', other['id']),
                    ('delta', [str(i) for i in other['image']]),
                    ('type', labels[uuid] + other['kind']),
                ]))

    atoms = [{'kind': kind, 'site': list(site), 'id': uuid}
             for kind, site, uuid in zip(labels, points, itertools.count(0))]
    json.dump({'atoms': atoms, 'interactions': interactions},
              descriptor, indent=2)


if __name__ == '__main__':
    cli()
