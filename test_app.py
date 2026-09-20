import unittest
from unittest.mock import MagicMock, patch

from App import app


class TestApp(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    @patch('App.mysql')
    def test_add_contact(self, mock_mysql):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_mysql.connection = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (0,)
        mock_cursor.fetchall.return_value = []

        response = self.client.post('/add_contact', data={
            'fullname': 'Juan Pérez',
            'phone': '123456789',
            'email': 'juan@email.com',
            'url': 'https://ejemplo.com'
        }, follow_redirects=True)

        insert_call = mock_cursor.execute.call_args_list[0]
        self.assertIn('INSERT INTO contacts1(fullname, phone, email, url)', insert_call.args[0])
        self.assertEqual(
            insert_call.args[1],
            ('Juan Pérez', '123456789', 'juan@email.com', 'https://ejemplo.com')
        )
        mock_conn.commit.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Contacto guardado', response.data)

    @patch('App.mysql')
    def test_contacts_paginates_four_records(self, mock_mysql):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_mysql.connection = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (9,)
        mock_cursor.fetchall.return_value = []

        response = self.client.get('/contacts?page=2')

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            unittest.mock.call('SELECT * FROM contacts1 LIMIT %s OFFSET %s', (4, 4)),
            mock_cursor.execute.call_args_list
        )
        self.assertIn(b'P', response.data)


if __name__ == '__main__':
    unittest.main()
