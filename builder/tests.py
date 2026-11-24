from django.test import TestCase
from django.contrib.auth.models import User
from .models import Portfolio
class PortfolioTests(TestCase):
    def test_slug_created(self):
        u=User.objects.create_user(username="test",password="Pass12345!")
        p=Portfolio.objects.create(user=u,title="Demo Portfolio")
        self.assertTrue(p.slug.startswith("demo-portfolio"))
