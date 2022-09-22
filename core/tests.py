from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import Item, Category, OrderItem, Order, Profile, Payment
# Create your tests here.
from rest_framework.test import APIClient
User = get_user_model()

class EcommerceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="linn@gmail.com", password="man")
        self.cat = Category.objects.create(choice="clothes")
        self.payment = Payment.objects.create(status="successful", amount=234, tx_ref="tx_ref",
                                              tansaction_id="tansaction_id", user=self.user, flw_ref="flw_ref")
        self.item = Item.objects.create(description="linn@gmail.com", price=122, title="rice",
                            picture = "http://localhost:8000/media/picture/logoconel.jpeg",
                            category=self.cat)
        self.order_item = OrderItem.objects.create(item=self.item, quantity=2,
                                               user=self.user)
        self.order = Order.objects.create(ref_code="ref_code", payment=self.payment,
                                              billing_address="tansaction_id", user=self.user)
        self.order.cart.add(self.order_item)



    def test_user_created(self):
        self.assertEqual(self.user.email, "linn@gmail.com")

    def get_client(self):
        client = APIClient()
        client.login(email=self.user.email, password="man")
        return client

    def test_profile_created(self):
        self.assertEqual(self.user.profile.id, 1)
        self.assertEqual(self.user, self.user)

    def test_create_products(self):
        self.item1 = Item.objects.create(description="linn@gmail.com", price=122, title="rice")
        self.item2 = Item.objects.create(description="ligmail.com", price=344,title="beans")
        self.assertNotEqual(self.item1, self.item2)

    def test_product_list(self):
        client = self.get_client()
        response = client.get("/api/products-list")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 4)

    def test_order(self):
        client = self.get_client()
        response = client.get("/api/all-order-summary")
        self.assertEqual(response.status_code, 200)
        print(response.json())





