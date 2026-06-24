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
        response = self.client.get('/api/account/profiles/me/')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], "Authentication credentials were not provided.")


    def test_login_with_username_succeeds(self):
        response = self.client.post('/api/account/users/login/', {
            'identifier': 'testuser',
            'password': 'testpassword',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertIn('_auth_user_id', self.client.session)


    def test_login_with_email_succeeds(self):
        response = self.client.post('/api/account/users/login/', {
            'identifier': 'test@example.com',
            'password': 'testpassword',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertIn('_auth_user_id', self.client.session)


    def test_login_with_email_is_case_insensitive(self):
        response = self.client.post('/api/account/users/login/', {
            'identifier': 'TEST@EXAMPLE.COM',
            'password': 'testpassword',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')

    def test_login_with_username_is_case_insensitive(self):
        response = self.client.post('/api/account/users/login/', {
            'identifier': 'TESTUSER',
            'password': 'testpassword',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], 'testuser')


    def test_login_with_unknown_identifier_returns_401(self):
        response = self.client.post('/api/account/users/login/', {
            'identifier': 'ghost@nowhere.com',
            'password': 'whatever',
        })

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], "Invalid credentials.")


    def test_login_with_wrong_password_returns_401(self):
        response = self.client.post('/api/account/users/login/', {
            'identifier': 'testuser',
            'password': 'wrongpassword',
        })

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], "Invalid credentials.")

    def test_login_missing_password_returns_400(self):
        response = self.client.post('/api/account/users/login/', {
            'identifier': 'testuser',
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)

    def test_login_missing_identifier_returns_400(self):
        response = self.client.post('/api/account/users/login/', {
            'password': 'testpassword',
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn('identifier', response.data)


    def test_access_protected_route_with_session(self):
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get('/api/account/profiles/me/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['username'], 'testuser')


    def test_logout_destroys_session(self):
        self.client.login(username='testuser', password='testpassword')

        logout_response = self.client.post('/api/account/users/logout/')
        self.assertEqual(logout_response.status_code, 204)

        protected_response = self.client.get('/api/account/profiles/me/')
        self.assertEqual(protected_response.status_code, 401)


    def test_register_rejects_username_containing_at_sign(self):
        # Without this rule, someone could register username="alice@bar.com"
        # and shadow another user's email at login time.
        response = self.client.post('/api/account/users/register/', {
            'username': 'alice@bar.com',
            'email': 'alice@bar.com',
            'password': 'somepassword',
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.data)


    def test_register_accepts_clean_username(self):
        # Regression guard: the new validator must not reject normal usernames.
        response = self.client.post('/api/account/users/register/', {
            'username': 'alice',
            'email': 'alice@bar.com',
            'password': 'somepassword',
        })

        self.assertEqual(response.status_code, 201)
