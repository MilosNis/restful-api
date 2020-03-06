from unittest.mock import patch
from django.test import TestCase
from django.core.management import call_command
from django.db.utils import OperationalError


class TestCommands(TestCase):

    def test_wait_for_db_ready(self):
        """Test for command wait_for_db when database is connected"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 1)

    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        """Testing command wait_for_db when
        after 5 OperationalError in sixth time returns True"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
