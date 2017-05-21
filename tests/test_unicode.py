# coding: utf-8

import logging
import os
import shutil
import sys
import tempfile
import unittest

import pytest

import fiona


logging.basicConfig(stream=sys.stderr, level=logging.INFO)

class UnicodePathTest(unittest.TestCase):

    def setUp(self):
        tempdir = tempfile.mkdtemp()
        self.dir = os.path.join(tempdir, 'français')
        shutil.copytree('tests/data/', self.dir)

    def tearDown(self):
        shutil.rmtree(os.path.dirname(self.dir))

    def test_unicode_path(self):
        path = self.dir + '/coutwildrnp.shp'
        if sys.version_info < (3,):
            path = path.decode('utf-8')
        with fiona.open(path) as c:
            assert len(c) == 67

    def test_unicode_path_layer(self):
        path = self.dir
        layer = 'coutwildrnp'
        if sys.version_info < (3,):
            path = path.decode('utf-8')
            layer = layer.decode('utf-8')
        with fiona.open(path, layer=layer) as c:
            assert len(c) == 67

    def test_utf8_path(self):
        path = self.dir + '/coutwildrnp.shp'
        if sys.version_info < (3,):
            with fiona.open(path) as c:
                assert len(c) == 67

class UnicodeStringFieldTest(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    @pytest.mark.xfail(reason="OGR silently fails to convert strings")
    def test_write_mismatch(self):
        """TOFIX: OGR silently fails to convert strings"""
        # Details:
        #
        # If we tell OGR that we want a latin-1 encoded output file and
        # give it a feature with a unicode property that can't be converted
        # to latin-1, no error is raised and OGR just writes the utf-8
        # encoded bytes to the output file.
        #
        # This might be shapefile specific.
        #
        # Consequences: no error on write, but there will be an error
        # on reading the data and expecting latin-1.
        schema = {
            'geometry': 'Point',
            'properties': {'label': 'str', 'num': 'int'}}

        with fiona.open(os.path.join(self.tempdir, "test-write-fail.shp"),
                        'w', driver="ESRI Shapefile", schema=schema,
                        encoding='latin1') as c:
            c.writerecords([{
                'type': 'Feature',
                'geometry': {'type': 'Point', 'coordinates': [0, 0]},
                'properties': {
                    'label': '徐汇区',
                    'num': 0}}])

        with fiona.open(os.path.join(self.tempdir), encoding='latin1') as c:
            f = next(iter(c))
            # Next assert fails.
            self.assertEqual(f['properties']['label'], '徐汇区')

    def test_write_utf8(self):
        schema = {
            'geometry': 'Point',
            'properties': {'label': 'str', 'verit\xe9': 'int'}}
        with fiona.open(os.path.join(self.tempdir, "test-write.shp"),
                        "w", "ESRI Shapefile", schema=schema,
                        encoding='utf-8') as c:
            c.writerecords([{
                'type': 'Feature',
                'geometry': {'type': 'Point', 'coordinates': [0, 0]},
                'properties': {
                    'label': 'Ba\u2019kelalan', 'verit\xe9': 0}}])

        with fiona.open(os.path.join(self.tempdir), encoding='utf-8') as c:
            f = next(iter(c))
            self.assertEqual(f['properties']['label'], 'Ba\u2019kelalan')
            self.assertEqual(f['properties']['verit\xe9'], 0)

    def test_write_gb18030(self):
        """Can write a simplified Chinese shapefile"""
        schema = {
            'geometry': 'Point',
            'properties': {'label': 'str', 'num': 'int'}}
        with fiona.open(os.path.join(self.tempdir, "test-write-gb18030.shp"),
                        'w', driver="ESRI Shapefile", schema=schema,
                        encoding='gb18030') as c:
            c.writerecords([{
                'type': 'Feature',
                'geometry': {'type': 'Point', 'coordinates': [0, 0]},
                'properties': {'label': '徐汇区', 'num': 0}}])

        with fiona.open(os.path.join(self.tempdir), encoding='gb18030') as c:
            f = next(iter(c))
            self.assertEqual(f['properties']['label'], '徐汇区')
            self.assertEqual(f['properties']['num'], 0)
