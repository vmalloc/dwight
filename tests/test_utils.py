from unittest import TestCase

from dwight_chroot import Environment

class EnvironmentTestCase(TestCase):
    def setUp(self):
        super(EnvironmentTestCase, self).setUp()
        self.environment = Environment()
    
