"""
Generates a 3-D box mesh with variable numbers of elements for stellate ganglion in 3 directions.
"""

from __future__ import division
import math
from scaffoldmaker.meshtypes.scaffold_base import Scaffold_base
from scaffoldmaker.utils.eftfactory_tricubichermite import eftfactory_tricubichermite
from scaffoldmaker.utils.meshrefinement import MeshRefinement
from scaffoldmaker.utils import zinc_utils
from opencmiss.zinc.element import Element, Elementbasis
from opencmiss.zinc.field import Field
from opencmiss.zinc.node import Node


class MeshType_3d_box_stellate1(Scaffold_base):
    '''
    classdocs
    '''
    @staticmethod
    def getName():
        return '3D Box Stellate'

    @staticmethod
    def getDefaultOptions(parameterSetName='Default'):
        return {
            'Number of elements 1' : 1,
            'Number of elements 2' : 1,
            'Number of images': 2,
            'Length of cube 1': 12,
            'Length of cube 2': 6,
            'Length of cube 3': 15,
            'Thickness of image': 0.5,
            'Use cross derivatives' : False,
            'Refine' : False,
            'Refine number of elements 1' : 1,
            'Refine number of elements 2' : 1
        }
    @staticmethod
    def getOrderedOptionNames():
        return [
            'Number of elements 1',
            'Number of elements 2',
            'Number of images',
            'Length of cube 1',
            'Length of cube 2',
            'Length of cube 3',
            'Thickness of image',
            'Use cross derivatives',
            'Refine',
            'Refine number of elements 1',
            'Refine number of elements 2'
        ]
    @staticmethod
    def checkOptions(options):
        for key in [
            'Number of elements 1',
            'Number of elements 2',
            'Refine number of elements 1',
            'Refine number of elements 2']:
            if options[key] < 1:
                options[key] = 1
        for key in [
            'Length of cube 3']:
            if options [key] < 5:
                options[key] = 5


    @staticmethod
    def generateBaseMesh(region, options):
        """
        Generate the base tricubic Hermite mesh. See also generateMesh().
        :param region: Zinc region to define model in. Must be empty.
        :param options: Dict containing options. See getDefaultOptions().
        :return: None
        """
        elementsCount1 = options['Number of elements 1']
        elementsCount2 = options['Number of elements 2']
        elementsCount3 = options['Number of images'] * 2 - 1
        useCrossDerivatives = options['Use cross derivatives']
        cubeLength1 = options['Length of cube 1']
        cubeLength2 = options['Length of cube 2']
        cubeLength3 = options['Length of cube 3']
        thickness = options['Thickness of image']

        fm = region.getFieldmodule()
        fm.beginChange()
        coordinates = zinc_utils.getOrCreateCoordinateField(fm)

        nodes = fm.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_NODES)
        nodetemplate = nodes.createNodetemplate()
        nodetemplate.defineField(coordinates)
        nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_VALUE, 1)
        nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D_DS1, 1)
        nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D_DS2, 1)
        if useCrossDerivatives:
            nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D2_DS1DS2, 1)
        nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D_DS3, 1)
        if useCrossDerivatives:
            nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D2_DS1DS3, 1)
            nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D2_DS2DS3, 1)
            nodetemplate.setValueNumberOfVersions(coordinates, -1, Node.VALUE_LABEL_D3_DS1DS2DS3, 1)

        mesh = fm.findMeshByDimension(3)

        tricubichermite = eftfactory_tricubichermite(mesh, useCrossDerivatives)
        eft = tricubichermite.createEftBasic()

        elementtemplate = mesh.createElementtemplate()
        elementtemplate.setElementShapeType(Element.SHAPE_TYPE_CUBE)
        result = elementtemplate.defineField(coordinates, -1, eft)

        cache = fm.createFieldcache()

        # create nodes
        nodeIdentifier = 1
        distance = (cubeLength3 - ((elementsCount3 + 1) / 2) * thickness) / ((elementsCount3 - 1) / 2)
        #distance = (cubeLength3 - ((elementsCount3 - 1) / 2) * thickness) / ((elementsCount3 + 1) / 2)
        x = [0.0, 0.0, 0.0]
        dx_ds1 = [1.0 / elementsCount1, 0.0, 0.0]
        dx_ds2 = [0.0, 1.0 / elementsCount2, 0.0]
        dx_ds3 = [0.0, 0.0, 1.0 / elementsCount3]
        zero = [0.0, 0.0, 0.0]

        for n3 in range(elementsCount3+1):
            if n3 % 2 == 0:
                x[2] = (n3 * thickness + n3 * distance) / 2
                #x[2] = (n3 * distance + n3 * thickness) / 2
            else:
                 x[2] = ((n3 + 1) * thickness + (n3-1) * distance ) / 2
                 #x[2] = ((n3+1) * distance + (n3-1) * thickness) / 2
            for n2 in range(elementsCount2 + 1):
                x[1] = (n2 * cubeLength2) / elementsCount2
                for n1 in range(elementsCount1 + 1):
                    x[0] = (n1 * cubeLength1) / elementsCount1
                    node = nodes.createNode(nodeIdentifier, nodetemplate)
                    cache.setNode(node)
                    coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_VALUE, 1, x)
                    coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_D_DS1, 1, dx_ds1)
                    coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_D_DS2, 1, dx_ds2)
                    coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_D_DS3, 1, dx_ds3)
                    if useCrossDerivatives:
                        coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_D2_DS1DS2, 1, zero)
                        coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_D2_DS1DS3, 1, zero)
                        coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_D2_DS2DS3, 1, zero)
                        coordinates.setNodeParameters(cache, -1, Node.VALUE_LABEL_D3_DS1DS2DS3, 1, zero)
                    nodeIdentifier = nodeIdentifier + 1

        # create elements
        elementIdentifier = 1
        no2 = (elementsCount1 + 1)
        no3 = (elementsCount2 + 1)*no2
        for e3 in range(elementsCount3):
            for e2 in range(elementsCount2):
                for e1 in range(elementsCount1):
                    element = mesh.createElement(elementIdentifier, elementtemplate)
                    bni = e3*no3 + e2*no2 + e1 + 1
                    nodeIdentifiers = [ bni, bni + 1, bni + no2, bni + no2 + 1, bni + no3, bni + no3 + 1, bni + no2 + no3, bni + no2 + no3 + 1 ]
                    result = element.setNodesByIdentifier(eft, nodeIdentifiers)
                    elementIdentifier = elementIdentifier + 1

        fm.endChange()

    @classmethod
    def generateMesh(cls, region, options):
        """
        Generate base or refined mesh.
        :param region: Zinc region to create mesh in. Must be empty.
        :param options: Dict containing options. See getDefaultOptions().
        """
        if not options['Refine']:
            cls.generateBaseMesh(region, options)
            return

        refineElementsCount1 = options['Refine number of elements 1']
        refineElementsCount2 = options['Refine number of elements 2']

        baseRegion = region.createRegion()
        cls.generateBaseMesh(baseRegion, options)

        meshrefinement = MeshRefinement(baseRegion, region)
        meshrefinement.refineAllElementsCubeStandard3d(refineElementsCount1, refineElementsCount2, refineElementsCount3)
