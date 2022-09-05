from django.test import TestCase, Client
from http import HTTPStatus


class AboutURLTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_template(self):
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(
                    HTTPStatus(response.status_code).phrase,
                    'OK',
                    f'Проблема с отображением страницы {address}'
                )
