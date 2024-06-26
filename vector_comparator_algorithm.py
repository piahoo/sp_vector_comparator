# -*- coding: utf-8 -*-

"""
/***************************************************************************
 vectorComparator
                                 A QGIS plugin
 Ta wtyczka porównuje dwie warstwy wektorowe
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2024-03-15
        copyright            : (C) 2024 by Seweryn Piasecki
        email                : seweryn.piasecki@radom.lasy.gov.pl
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Seweryn Piasecki'
__date__ = '2024-03-15'
__copyright__ = '(C) 2024 by Seweryn Piasecki'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingMultiStepFeedback,
                       QgsProcessingParameterMapLayer,
                       QgsProcessingParameterBoolean,
                       QgsCoordinateReferenceSystem)
import processing
import os


class vectorComparatorAlgorithm(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterMapLayer('Warstwadruga', 'Warstwa A', defaultValue=None, types=[QgsProcessing.TypeVectorPolygon]))
        self.addParameter(QgsProcessingParameterMapLayer('Warstwapierwsza', 'Warstwa B', defaultValue=None, types=[QgsProcessing.TypeVectorPolygon]))
        self.addParameter(QgsProcessingParameterFeatureSink('RnaGeometriaADoB', 'Różna geometria A do B', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('RnaGeometriaBDoA', 'Różna geometria B do A', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('WarstwaAZaokrglona', 'Warstwa A (zaokrąglona)', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('WarstwaBZaokrglona', 'Warstwa B (zaokrąglona)', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Pełne rejestrowanie', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(14, model_feedback)
        results = {}
        outputs = {}

        # Przelicz układ współrzędnych warstwy A
        alg_params = {
            'INPUT': parameters['Warstwadruga'],
            'OPERATION': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:2180'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PrzeliczUkadWsprzdnychWarstwyA'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Przyciągnij punkty do siatki A
        alg_params = {
            'HSPACING': 0.01,
            'INPUT': outputs['PrzeliczUkadWsprzdnychWarstwyA']['OUTPUT'],
            'MSPACING': 0,
            'VSPACING': 0.01,
            'ZSPACING': 0,
            'OUTPUT': parameters['WarstwaAZaokrglona']
        }
        outputs['PrzycignijPunktyDoSiatkiA'] = processing.run('native:snappointstogrid', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['WarstwaAZaokrglona'] = outputs['PrzycignijPunktyDoSiatkiA']['OUTPUT']

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Ustaw styl Warstwa A
        alg_params = {
            'INPUT': outputs['PrzycignijPunktyDoSiatkiA']['OUTPUT'],
            'STYLE': os.path.dirname(__file__) + "/styles/poly_a.qml"
        }
        outputs['UstawStylWarstwaA'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Przelicz układ współrzędnych warstwy B
        alg_params = {
            'INPUT': parameters['Warstwapierwsza'],
            'OPERATION': '',
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:2180'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PrzeliczUkadWsprzdnychWarstwyB'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Wydobądź wierzchołki A
        alg_params = {
            'INPUT': outputs['PrzycignijPunktyDoSiatkiA']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['WydobdWierzchokiA'] = processing.run('native:extractvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Twórz indeks przestrzenny A
        alg_params = {
            'INPUT': outputs['WydobdWierzchokiA']['OUTPUT']
        }
        outputs['TwrzIndeksPrzestrzennyA'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Przyciągnij punkty do siatki B
        alg_params = {
            'HSPACING': 0.01,
            'INPUT': outputs['PrzeliczUkadWsprzdnychWarstwyB']['OUTPUT'],
            'MSPACING': 0,
            'VSPACING': 0.01,
            'ZSPACING': 0,
            'OUTPUT': parameters['WarstwaBZaokrglona']
        }
        outputs['PrzycignijPunktyDoSiatkiB'] = processing.run('native:snappointstogrid', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['WarstwaBZaokrglona'] = outputs['PrzycignijPunktyDoSiatkiB']['OUTPUT']

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Wydobądź wierzchołki B
        alg_params = {
            'INPUT': outputs['PrzycignijPunktyDoSiatkiB']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['WydobdWierzchokiB'] = processing.run('native:extractvertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Ustaw styl Warstwa B
        alg_params = {
            'INPUT': outputs['PrzycignijPunktyDoSiatkiB']['OUTPUT'],
            'STYLE': os.path.dirname(__file__) + "/styles/poly_b.qml"
        }
        outputs['UstawStylWarstwaB'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Twórz indeks przestrzenny B
        alg_params = {
            'INPUT': outputs['WydobdWierzchokiB']['OUTPUT']
        }
        outputs['TwrzIndeksPrzestrzennyB'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Wyodrębnij przestrzennie A
        alg_params = {
            'INPUT': outputs['TwrzIndeksPrzestrzennyB']['OUTPUT'],
            'INTERSECT': outputs['TwrzIndeksPrzestrzennyA']['OUTPUT'],
            'PREDICATE': [2],
            'OUTPUT': parameters['RnaGeometriaBDoA']
        }
        outputs['WyodrbnijPrzestrzennieA'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['RnaGeometriaBDoA'] = outputs['WyodrbnijPrzestrzennieA']['OUTPUT']

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Wyodrębnij przestrzennie B
        alg_params = {
            'INPUT': outputs['TwrzIndeksPrzestrzennyA']['OUTPUT'],
            'INTERSECT': outputs['TwrzIndeksPrzestrzennyB']['OUTPUT'],
            'PREDICATE': [2],
            'OUTPUT': parameters['RnaGeometriaADoB']
        }
        outputs['WyodrbnijPrzestrzennieB'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['RnaGeometriaADoB'] = outputs['WyodrbnijPrzestrzennieB']['OUTPUT']

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Ustaw styl warstwy B do A
        alg_params = {
            'INPUT': outputs['WyodrbnijPrzestrzennieA']['OUTPUT'],
            'STYLE': os.path.dirname(__file__) + "/styles/point_b.qml"
        }
        outputs['UstawStylWarstwyBDoA'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Ustaw styl warstwy A do B
        alg_params = {
            'INPUT': outputs['WyodrbnijPrzestrzennieB']['OUTPUT'],
            'STYLE': os.path.dirname(__file__) + "/styles/point_a.qml"
        }
        outputs['UstawStylWarstwyADoB'] = processing.run('native:setlayerstyle', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        return results

    def name(self):
        return 'Porównywacz'

    def displayName(self):
        return 'Porównywacz'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def shortHelpString(self):
        return """<html><body><h2>Opis algorytmu</h2>
<p>Algorytm porównuje dwie warstwy wektorowe i jako wynik tworzy dwie warstwy punktowe z różniącymi się węzłami. Warstwy przed porównaniem przeliczane są do EPSG:2180. Węzły przed porównaniem są zaokrąglane przez przyciągniecie do siatki 0,01 m x 0,01 m.</p>
<h2>Parametry wejściowe</h2>
<h3>Warstwa A</h3>
<p>Pierwsza warstwa do porównania</p>
<h3>Warstwa B</h3>
<p>Druga warstwa do porównania</p>
<h3>Różna geometria A do B</h3>
<p>Węzły warstwy A nie występujące w warstwie B</p>
<h3>Różna geometria B do A</h3>
<p>Węzły warstwy B nie występujące w warstwie A</p>
<h3>Warstwa A (zaokrąglona)</h3>
<p></p>
<h3>Warstwa B (zaokrąglona)</h3>
<p></p>
<h3>Pełne rejestrowanie</h3>
<p></p>
<h2>Wyniki</h2>
<h3>Różna geometria A do B</h3>
<p>Węzły warstwy A nie występujące w warstwie B</p>
<h3>Różna geometria B do A</h3>
<p>Węzły warstwy B nie występujące w warstwie A</p>
<h3>Warstwa A (zaokrąglona)</h3>
<p></p>
<h3>Warstwa B (zaokrąglona)</h3>
<p></p>
<br><p align="right">Autor algorytmu: Seweryn Piasecki</p><p align="right">Autor pomocy: Seweryn Piasecki</p><p align="right">Wersja algorytmu: 0.7</p></body></html>"""

    def createInstance(self):
        return vectorComparatorAlgorithm()
