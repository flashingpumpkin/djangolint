import os
from django.test import TestCase

from ..analyzers.db_backends import DB_BackendsAnalyzer
from ..parsers import Parser

from .base import TESTS_ROOT


class DB_BackendsAnalyzerTests(TestCase):

    def setUp(self):
        self.maxDiff = None
        self.example_project = os.path.join(TESTS_ROOT, 'example_project')
        self.code = Parser(self.example_project).parse()
        self.analyzer = DB_BackendsAnalyzer(self.code, self.example_project)

    def test_analyze(self):
        results = list(self.analyzer.analyze())
        self.assertEqual(len(results), 1)
        self.assertItemsEqual(results[0].source, [
            (30, False, "DATABASES = {"),
            (31, False, "    'default': {"),
            (32, True,  "        'ENGINE': 'django.db.backends.postgresql',"),
            (33, False, "        'NAME': 'project',"),
            (34, False, "    }"),
        ])
        self.assertItemsEqual(results[0].solution, [
            (30, False, "DATABASES = {"),
            (31, False, "    'default': {"),
            (32, True,  "        'ENGINE': 'django.db.backends.postgresql_psycopg2',"),
            (33, False, "        'NAME': 'project',"),
            (34, False, "    }"),
        ])