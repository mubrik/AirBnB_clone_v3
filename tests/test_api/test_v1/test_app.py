#!/usr/bin/env python3
"""This is the test module for the web application"""
from api.v1 import app as app_mod
import unittest
from console import HBNBCommand
from unittest.mock import patch
from io import StringIO
from uuid import uuid4


class TestState(unittest.TestCase):
    """Test suite for the app"""

    def setUp(self):
        """Runs before each test case"""

        self.app = app_mod.create_app(None)
        self.app.config['TESTING'] = True

    def test_read_states_all(self):
        """Test the get request to /states endpoint"""

        with self.app.test_client() as client:
            response = client.get('/api/v1/states')
            self.assertEqual(response.status_code, 200)
            response_data = response.get_json()
            self.assertNotEqual(response_data, None)
            self.assertTrue(type(response_data) == list)

            for state in response_data:
                self.assertTrue(type(state) == dict)
                self.assertEqual(state.get('__class__'), "State")
                self.assertNotEqual(state.get('name'), "")

    def test_read_states_id(self):
        """Test get request to specific state"""

        with patch('sys.stdout', new=StringIO()) as fake_out:
            HBNBCommand().onecmd('create State name="foo"')
            state_id = fake_out.getvalue().strip()
            with self.app.test_client() as client:
                response = client.get('/api/v1/states/{}'.format(state_id))
                self.assertEqual(response.status_code, 200)
                response_data = response.get_json()
                self.assertNotEqual(response_data, None)
                self.assertTrue(type(response_data) == dict)
                self.assertEqual(response_data.get('name'), "foo")
                self.assertEqual(response_data.get('id'), state_id)

    def test_read_states_id_not_found(self):
        """Test get request to /states endpoint with invalid id"""

        with self.app.test_client() as client:
            response = client.get('/api/v1/states/{}'.format(uuid4()))
            self.assertEqual(response.status_code, 404)
            response_data = response.get_json()
            self.assertTrue(type(response_data) == dict)
            self.assertEqual(response_data.get('error'), 'Not found')

    def test_delete_state(self):
        """Test delete request to /states endpoint"""

        with patch('sys.stdout', new=StringIO()) as fake_out:
            HBNBCommand().onecmd('create State name="foo"')
            state_id = fake_out.getvalue().strip()

            with self.app.test_client() as client:
                response = client.get('/api/v1/states/{}'.format(state_id))
                self.assertEqual(response.status_code, 200)
                response = client.delete('/api/v1/states/{}'.format(state_id))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.get_json(), {})
                response = client.delete('/api/v1/states/{}'.format(state_id))
                self.assertEqual(response.status_code, 404)

    def test_delete_state_id_invalid(self):
        """Test delete request to /states endpoint with invalid id"""

        with self.app.test_client() as client:
            response = client.delete('/api/v1/states/{}'.format(uuid4()))
            self.assertEqual(response.status_code, 404)

    def test_create_state(self):
        """Test post request to /states endpoint"""
        with self.app.test_client() as client:
            response = client.post('/api/v1/states', json={"name": "foo"})
            self.assertEqual(response.status_code, 201)
            response_data = response.get_json()
            self.assertTrue(type(response_data) == dict)
            self.assertTrue(response_data.get('name') == 'foo')

    def test_create_state_invalid_type(self):
        """Test post request to /states endpoint with non json"""

        with self.app.test_client() as client:
            headers = {'Content-Type': 'text/plain'}
            response = client.post('/api/v1/states', data="a", headers=headers)
            self.assertTrue(response.status_code == 400)
            self.assertIn(b"Not a JSON", response.data)

    def test_create_state_invalid_attr(self):
        """Test post request to /states endpoint with invalid attribute"""

        with self.app.test_client() as client:
            response = client.post('/api/v1/states', json={"invalid": "foo"})
            self.assertTrue(response.status_code == 400)
            self.assertIn(b"Missing name", response.data)

    def test_update_state(self):
        """Test put request to /states endpoint"""

        with patch('sys.stdout', new=StringIO()) as fake_out:
            HBNBCommand().onecmd('create State name="foo"')
            state_id = fake_out.getvalue().strip()
            with self.app.test_client() as client:
                response = client.put('/api/v1/states/{}'.format(state_id),
                                      json={"name": "bar"})
                self.assertEqual(response.status_code, 200)
                response_data = response.get_json()
                self.assertTrue(type(response_data) == dict)
                self.assertEqual(response_data.get('name'), "bar")

    def test_update_state_invalid_id(self):
        """Test put request to /states endpoint with invalid id"""
        with self.app.test_client() as client:
            response = client.put('/api/v1/states/{}'.format(uuid4()),
                                  json={"name": "bar"})
            self.assertTrue(response.status_code == 404)


if __name__ == '__main__':
    unittest.main()
