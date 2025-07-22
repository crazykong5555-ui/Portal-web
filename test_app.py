import unittest
from unittest.mock import patch, MagicMock
from App import app

class TestApp(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    @patch('App.mysql')
    def test_add_contact(self, mock_mysql):
        # Mock de la conexión y cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_mysql.connection = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Importante: mock de fetchall() para que no falle al cargar contactos luego del redirect
        mock_cursor.fetchall.return_value = []

        # Simular POST al formulario
        response = self.client.post('/add_contact', data={
            'fullname': 'Juan Pérez',
            'phone': '123456789',
            'email': 'juan@email.com',
            'url': 'https://ejemplo.com'
        }, follow_redirects=True)

        # Verificar que el método correcto fue llamado
        self.assertIn(
            ('INSERT INTO contacts1(fullname, phone, email, url) VALUES (%s, %s, %s, %s)',
             ('Juan Pérez', '123456789', 'juan@email.com', 'https://ejemplo.com')),
            mock_cursor.execute.call_args_list
        )
        mock_conn.commit.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Guardado exitoso del contacto', response.data)

if __name__ == '__main__':
    unittest.main()
