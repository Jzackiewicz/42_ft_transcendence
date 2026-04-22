from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpassword',
            email='test@example.com'
        )

    def test_unauthenticated_request_is_blocked(self):
        response = self.client.get('/account/users/')
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")

    def test_login_with_wrong_credentials(self):
        response = self.client.post('/account/users/login/', {
            'username': 'wronguser',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], "Invalid credentials.")

    def test_login_success(self):
        response = self.client.post('/account/users/login/', {
            'username': 'testuser',
            'password': 'testpassword'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertIn('_auth_user_id', self.client.session)

    def test_access_protected_route_with_session(self):
        self.client.login(username='testuser', password='testpassword')
        
        response = self.client.get('/account/users/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)

    def test_logout_destroys_session(self):
        self.client.login(username='testuser', password='testpassword')
        
        logout_response = self.client.post('/account/users/logout/')
        self.assertEqual(logout_response.status_code, 204)
        
        protected_response = self.client.get('/account/users/')
        self.assertEqual(protected_response.status_code, 403)

    def test_login_missing_fields(self):
        response = self.client.post('/account/users/login/', {
            'username': 'testuser'
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)
