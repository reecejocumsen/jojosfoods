from datetime import datetime

from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import User

CATEGORY_CHOICES = {
    ('F', 'Fruit'),
    ('V', 'Vegetables'),
    ('H', 'Herbs'),
    ('D', 'Dairy'),
    ('M', 'Meat'),
    ('E', 'Eggs'),
    ('L', 'Legumes and Nuts'),
    ('O', 'Other')
}

QUALITY_CHOICES = {
    ('A+', 'A+'),
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('U', 'Unrated')
}

UNIT_CHOICES = {
    ('kg', 'kilograms'),
    ('g', 'grams'),
    ('L', 'litres'),
    ('mL', 'millilitres'),
    ('dozen', 'dozen'),
}


class Item(models.Model):
    id = models.AutoField(primary_key=True)
    sold_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    unit = models.CharField(choices=UNIT_CHOICES, max_length=5, default="kg")
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=1,
                                default='O')
    quality = models.CharField(choices=QUALITY_CHOICES, max_length=2,
                               default='U')
    img_url = models.URLField()
    image = models.ImageField(null=True)
    description = models.CharField(blank=True, null=True, max_length=200)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={'id': self.id})


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    sold_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    @property
    def total_item_price(self):
        return self.quantity*self.item.price


class Cart(models.Model):
    user = models.OneToOneField(User, primary_key=True,
                                on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem, blank=True)

    @property
    def total_cost(self):
        cost = 0
        for item in self.items.all():
            cost = cost + item.total_item_price
        return cost

    def __str__(self):
        return self.user.username + "'s cart"

    def is_empty(self):
        return len(self.items.all()) == 0

    def add_to_cart(self, item, add_this_many):
        if self.contains_item(item):
            order_item = self.items.all().get(item=item)
            if order_item.quantity + add_this_many > item.quantity:
                return False
            order_item.quantity += add_this_many
            order_item.save()
            return True
        else:
            if add_this_many > item.quantity:
                return False
            else:
                order_item = OrderItem.objects.create(sold_by=item.sold_by,
                                                      ordered=False, item=item,
                                                      quantity=add_this_many)
                self.items.add(order_item)
                return True

    def contains_item(self, check_item):
        return len(self.items.all().filter(item=check_item)) > 0

    def contains_order_item(self, check_order_item):
        return len(self.items.all().filter(id=check_order_item.id)) > 0

    def empty(self):
        for item in self.items.all():
            self.items.remove(item)

    def remove_item(self, remove_this):
        if self.contains_item(remove_this):
            id_to_remove = self.items.all().get(item=remove_this).id
            OrderItem.objects.filter(id=id_to_remove).delete()

    def remove_order_item(self, remove_this):
        if self.contains_order_item(remove_this):
            OrderItem.objects.filter(id=remove_this.id).delete()


ORDER_STATUS_OPTIONS = {
    (0, 'Placed'),
    (1, 'Confirmed by seller'),
    (2, 'In transit'),
    (3, 'Delivered'),
    (-1, 'Cancelled')
}


# store all user's items for a particular order
class Order(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    buyer = models.ForeignKey(User, related_name="buyer", null=True, on_delete=models.SET_NULL, default=User.objects.all()[0].pk)
    seller = models.ForeignKey(User, related_name="seller", null=True, on_delete=models.SET_NULL, default=User.objects.all()[0].pk)
    items = models.ManyToManyField(OrderItem)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=ORDER_STATUS_OPTIONS, default=0)

    def __str__(self):
        return "Order #" + str(self.id) + " (" + str(self.seller) + " -> " + str(self.buyer) + ")"

    @property
    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.total_item_price
        return total

    @property
    def get_full_status(self):
        print(self.status)
        for status_option in list(ORDER_STATUS_OPTIONS):
            if int(self.status) == status_option[0]:
                print("status ", status_option[1])
                return status_option[1]


class UserHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    item = models.ForeignKey(Item, unique=False, on_delete=models.CASCADE, null=True)
    last_viewed = models.DateTimeField(default=datetime.now())


class Shop(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    orders = models.ManyToManyField(Order)
