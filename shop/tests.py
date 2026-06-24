from django.test import TestCase
from django.urls import reverse
from .models import Category, MenuItem, Reservation


class CategoryModelTest(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Burgers", slug="burgers", order=1)

    def test_str(self):
        self.assertEqual(str(self.cat), "Burgers")

    def test_slug(self):
        self.assertEqual(self.cat.slug, "burgers")


class HomeViewTest(TestCase):
    def test_home_get(self):
        response = self.client.get(reverse("shop:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home/index.html")

    def test_home_context(self):
        response = self.client.get(reverse("shop:home"))
        self.assertIn("categories", response.context)
        self.assertIn("menu_items", response.context)
        self.assertIn("reservation_form", response.context)


class ReservationFormTest(TestCase):
    def test_valid_reservation(self):
        data = {
            "form_type":  "reservation",
            "full_name":  "Ali Valiyev",
            "phone":      "+998901234567",
            "email":      "ali@test.com",
            "guests":     "2",
            "date":       "2027-01-15",
            "time":       "19:00",
        }
        response = self.client.post(reverse("shop:home"), data)
        self.assertEqual(response.status_code, 302)   # redirect
        self.assertEqual(Reservation.objects.count(), 1)
