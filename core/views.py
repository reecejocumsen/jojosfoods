from re import template
from allauth.account.views import PasswordChangeView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView, CreateView, UpdateView, \
    DeleteView
from django.contrib.auth.models import User
from django.db.models import Q

import core.models
from . import models
from .context_processors import cart_processor
from .models import Item, UserHistory, Cart, OrderItem, Order

import cloudinary
import cloudinary.uploader

from .gmail import send_message, gmail_authenticate, create_message


def upload_to_cloudinary(img):
    ret = cloudinary.uploader.upload(img, use_filename=True)
    return ret['url']  # store this value


class ItemDeleteView(LoginRequiredMixin, DeleteView):
    model = Item
    success_url = '/accounts/account_details/my_products'
    template_name = "product_delete_confirmation.html"

    def dispatch(self, request, *args, **kwargs):
        """
        If the user trying to delete an item isn't the user who made it,
        throws PermissionError. This can 100% be changed to redirect to a
        "hey don't do that" page.
        """
        item = self.get_object()
        if item.sold_by.id != request.user.id:
            raise PermissionError("You do not have permission to edit that "
                                  "item!")
        else:
            return super().dispatch(request, *args, *kwargs)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.info(request, "Item successfully deleted!", extra_tags="alert-success")
        return super(ItemDeleteView, self).delete(request, *args, **kwargs)


class ItemCreateView(LoginRequiredMixin, CreateView):
    template_name = 'profile-page-add.html'
    model = Item
    fields = ['image', 'title', 'price', 'unit', 'quantity', 'category',
              'quality', 'description']

    def get_success_url(self):
        return '/accounts/account_details/my_products'

    def form_valid(self, form):
        url = upload_to_cloudinary(form.instance.image)
        form.instance.img_url = url
        form.instance.sold_by = self.request.user
        return super().form_valid(form)


class ItemUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "profile-page-update.html"
    model = Item
    fields = ['title', 'price', 'quantity', 'unit', 'category', 'quality',
              'description']

    def get_success_url(self):
        return '/accounts/account_details/my_products'

    def dispatch(self, request, *args, **kwargs):
        """
        If the user trying to edit an item isn't the user who made it,
        throws PermissionError. This can 100% be changed to redirect to a
        "hey don't do that" page.
        """
        item = self.get_object()
        if item.sold_by.id != request.user.id:
            raise PermissionError("You do not have permission to edit that "
                                  "item!")
        else:
            print("Good user!")
            self.success_url = '/product/' + str(item.id)
            return super().dispatch(request, *args, *kwargs)

    def form_valid(self, form):
        form.instance.sold_by = self.request.user
        return super().form_valid(form)


# super secret codes
# gone forever


def redirect_to_home(request):
    """
    When used as a function view, returns the user to the home page.
    """
    return redirect("/")


def home_view(request):
    """
    Function-based view to display different lists of items in the homepage.
    Replaces HomeView.
    """
    all_products = Item.objects.order_by('title')

    context = {
        'newest': Item.objects.order_by('-id')[0:5],
        'all_products': all_products
    }

    if request.user.is_authenticated:
        latest = UserHistory.objects.filter(user=request.user).order_by(
            '-last_viewed')

        recently_viewed = []
        if latest:
            for history_item in latest:
                item = Item.objects.filter(id=history_item.item.id)
                if len(item) != 0:
                    recently_viewed.append(item[0])
                else:
                    UserHistory.objects.get(item=history_item.item).delete()
        context['recently_viewed'] = recently_viewed
    return render(request, "home-page.html", context)


def recent_viewed(request):
    latest = UserHistory.objects.filter(user_id=request.user.id).order_by(
        '-last_viewed')
    context = {
        'latest': latest
    }
    return render(request, "recent.html", context)


def item_view(request, pk):
    """
    Function-based view of a particular item listing.
    """
    this_item = Item.objects.get(id=pk)
    if request.user.is_authenticated:
        if UserHistory.objects.filter(user=request.user,
                                      item_id=this_item):
            UserHistory.objects.filter(user=request.user,
                                       item=this_item).update(
                last_viewed=timezone.now())
        else:
            all_viewed = UserHistory.objects.filter(
                user=request.user).order_by('-last_viewed')
            if len(all_viewed) == 5:
                latest = all_viewed.earliest('last_viewed')
                UserHistory.objects.filter(user=latest.user,
                                           item=latest.item).delete()
            UserHistory.objects.create(user=request.user,
                                       item=this_item)

    context = {
        "item": this_item,
    }
    return render(request, "product-details.html", context)


def account_details(request):
    """
    Function-based view of account details, including password change and
    logout option.
    """
    context = {
        "user": request.user,
    }
    return render(request, "profile-page.html", context)


def my_products(request):
    """
    Function-based view of a user's products.
    """
    context = {
        "products": Item.objects.filter(sold_by=request.user)
    }
    return render(request, "profile-page-products.html", context)


def profile_public(request, pk):
    """
    Public profile view, including items for sale and general account details.
    """
    user = User.objects.get(id=pk)
    items = Item.objects.filter(sold_by_id=user.pk)
    find_in = dict(core.models.CATEGORY_CHOICES)
    print(find_in)
    categories = items.order_by().values_list('category').distinct()

    context = {
        "this_user": user,
        "items_for_sale": items,
    }

    # if 'upload_btn' in request.POST:
    #    img = request.FILES['product_image']
    #    upload_to_cloudinary(img)

    return render(request, "profile-user-page.html", context)


class GradingView(TemplateView):
    """
    Template-based view for the grading page.
    """
    template_name = 'grading.html'


def contact_seller_item_view(request, pk):
    this_item = Item.objects.get(id=pk)
    print(request.user)
    context = {
        "item": this_item,
        "order": 0
    }

    print(this_item.sold_by.email)

    info = 'A user would like to contact you about your product: ' + this_item.title + '\n'
    if request.user.is_anonymous:
        sender = '\n\nThis message was sent by an anonymous user'
    else:
        sender = '\n\nTo reply to this please contact ' + request.user.email

    if 'send_email' in request.POST and request.POST['email_title'] and \
            request.POST['email_body']:
        service = gmail_authenticate()
        message = create_message('contactjojosfoods@gmail.com',
                                 this_item.sold_by.email,
                                 info + request.POST['email_title'],
                                 request.POST['email_body'] + sender)
        send_message(service, message)

    return render(request, "contact-seller-page.html", context)


def contact_seller_order_view(request, pk):
    this_order = Order.objects.get(id=pk)
    if this_order.buyer.id != request.user.id:
        raise PermissionError("You do not have permission to contact the seller"
                              " about this!")
    else:

        context = {
            "item": 0,
            "order": this_order,
        }

        info = 'A user would like to contact you about their order: Order #' + \
               str(this_order.id) + '\n'
        sender = '\n\nTo reply to this please contact ' + request.user.email

        if 'send_email' in request.POST and request.POST['email_title'] and \
                request.POST['email_body']:
            service = gmail_authenticate()
            message = create_message('contactjojosfoods@gmail.com',
                                     this_order.seller.email,
                                     info + request.POST['email_title'],
                                     request.POST['email_body'] + sender)
            send_message(service, message)

        return render(request, "contact-seller-page.html", context)


def profile_page_order_history(request):
    orders = Order.objects.filter(buyer=request.user).order_by('-ordered_date')
    context = {
        'orders': orders
    }
    return render(request, 'profile-page-order-history.html', context)


def profile_page_sales_history(request):
    orders = Order.objects.filter(seller=request.user)
    context = {
        'orders': orders
    }
    return render(request, 'profile-page-sales-history.html', context)


def profile_page_order_details_buyer(request, pk):
    # if you've come here because you're getting an IndexError, it's supposed
    # to happen. One day I will fix this.
    order = Order.objects.filter(id=pk)[0]

    if order.buyer.id != request.user.id:
        raise PermissionError("You do not have permission to view this order!")
    else:

        context = {
            'is_seller': 0,
            'order': order,
            'order_items': order.items.all(),
            'status': int(order.status)
        }
        return render(request, 'profile-page-order-details.html', context)


def profile_page_order_details_seller(request, pk):
    # if you've come here because you're getting an IndexError, it's supposed
    # to happen. One day I will fix this.
    order = Order.objects.filter(id=pk)[0]
    if order.seller.id != request.user.id:
        raise PermissionError("You do not have permission to view this order!")
    else:
        options = list(models.ORDER_STATUS_OPTIONS)
        options.sort()
        options.remove(options[0])
        context = {
            'is_seller': 1,
            'order': order,
            'order_items': order.items.all(),
            'status_options': options,
            'status': int(order.status)
        }
        return render(request, 'profile-page-order-details.html', context)


def order_update(request, pk):
    if request.method == 'POST':
        new_status = request.POST['status']
        order = Order.objects.filter(id=pk)[0]
        if request.user == order.seller:
            order.status = new_status
            order.save()
            messages.info(request, "Order successfully updated!", extra_tags="alert-info")
            return redirect("/accounts/sales_history/details/{0}".format(pk))
    raise PermissionError("You do not have permission to update this order!")


def readd_quantity(order):
    for oi in order.items.all():
        item = oi.item
        item.quantity = item.quantity + oi.quantity
        item.save()


def cancel_order(request, pk):
    order = Order.objects.filter(id=pk)[0]
    if request.user == order.seller:
        order.status = -1
        order.save()
        messages.info(request, "Order successfully cancelled.", extra_tags="alert-info")

        info = 'Order #' + str(order.id) + ' has been cancelled'
        sender = 'Please contact the seller at ' + order.seller.email + ' with any further questions.'

        service = gmail_authenticate()
        message = create_message('contactjojosfoods@gmail.com',
                                 order.buyer.email, info, sender)
        send_message(service, message)
        readd_quantity(order)
        return redirect("/accounts/sales_history")


def team_page_view(request):
    return render(request, 'team-page.html')


def category_view(request, pk):
    """
    Public profile view, including items for sale and general account details.
    """

    categories = {
        1: ('M', 'Meat'),
        2: ('D', 'Dairy'),
        3: ('E', 'Eggs'),
        4: ('F', 'Fruit'),
        5: ('V', 'Vegetables'),
        6: ('L', 'Legumes and Nuts'),
        7: ('H', 'Herbs'),
        8: ('O', 'Other')
    }
    items = Item.objects.filter(category__contains=categories[pk][0])
    print(items)
    context = {
        "category": categories[pk][1],
        "all_products": items
    }

    return render(request, "product_category.html", context)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "profile-page-edit.html"
    model = User
    fields = ['username', 'first_name', 'last_name', 'email']

    def get_success_url(self):
        return '/accounts/account_details'

    def dispatch(self, request, *args, **kwargs):
        print('aaaaa')
        self.user = request.user
        return super().dispatch(request, *args, *kwargs)

    def form_valid(self, form):
        return super().form_valid(form)

    def get_object(self):
        return get_object_or_404(User, pk=self.user.id)


class ContactUsView(TemplateView):
    """
    Template-based view for the contact us page.
    """
    template_name = 'contact-us-page.html'

    def post(self, request):
        if 'send_email' in request.POST and request.POST['email_title'] and \
                request.POST['email_body']:
            service = gmail_authenticate()
            message = create_message('contactjojosfoods@gmail.com',
                                     'alexpatapan@gmail.com',
                                     request.POST['email_title'],
                                     request.POST['email_body'])
            send_message(service, message)

        return render(request, self.template_name)


class TAndCView(TemplateView):
    """
    Template-based view for T&C
    """
    template_name = "terms-condition.html"


class PrivacyView(TemplateView):
    """
    Template-based view for Privacy Policy
    """
    template_name = "privacy-policy.html"


class CustomPasswordChangeView(PasswordChangeView):
    success_url = '/accounts/password/change/success'


class PasswordChangeSuccessView(TemplateView):
    template_name = "password_change_success.html"


class PurchaseSuccessView(TemplateView):
    template_name = "success.html"

    def post(self, request):
        if 'order-submitted' in request.POST:
            # reduce quantity of everything in cart
            reduce_item_quantity(request)
            split_into_orders(request)

        return render(request, self.template_name)


def purchase_success(request):
    reduce_item_quantity(request)
    split_into_orders(request)
    empty_cart(request)
    messages.info(request, mark_safe("Order placed! To find this order later, check your <a class='alert-link' href='/accounts/order_history'>Order History</a>."), extra_tags="alert-success")
    return redirect("/")


def reduce_item_quantity(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.filter(user=request.user)[0]
        except IndexError:
            cart = Cart.objects.create(user=request.user)

        for item in cart.items.all():
            item_model = Item.objects.get(id=item.item.id)

            new_quantity = item_model.quantity - OrderItem.objects.get(
                id=item.id).quantity

            item_model.quantity = new_quantity
            item_model.save()


def split_into_orders(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.filter(user=request.user)[0]
        except IndexError:
            cart = Cart.objects.create(user=request.user)

        cart_by_seller = dict()

        sellers = cart.items.all().values_list('sold_by').distinct()
        for seller in sellers:
            user_id = seller[0]
            actual_seller = User.objects.get(id=user_id)
            items_by_seller = cart.items.all().filter(sold_by=actual_seller)
            cart_by_seller[actual_seller] = items_by_seller
        print(cart_by_seller)
        for seller in cart_by_seller.keys():
            order = Order.objects.create(buyer=request.user, seller=seller)
            order.items.set(cart_by_seller[seller])
            print(order.items.all())
            order.save()


#
#  CART MANAGEMENT TIME
#
def checkout(request):
    """
    Function-based view of a user's cart.
    """

    def queryset_cost(queryset):
        qs_cost = 0
        for item in queryset.all():
            qs_cost = qs_cost + item.total_item_price
        return qs_cost

    context = cart_processor(request)
    cart = context.get('cart')

    if cart:
        cart_by_seller = dict()
        cost_by_seller = dict()

        sellers = cart.values_list('sold_by').distinct()
        for seller in sellers:
            user_id = seller[0]
            actual_seller = User.objects.get(id=user_id)
            items_by_seller = cart.filter(sold_by=actual_seller)
            cost = queryset_cost(items_by_seller)
            cart_by_seller[actual_seller] = items_by_seller
            cost_by_seller[actual_seller] = cost

        context['sorted_cart'] = cart_by_seller
        context['sorted_cost'] = cost_by_seller

    return render(request, "payment-page.html", context)


def empty_cart(request):
    try:
        cart = Cart.objects.filter(user=request.user)[0]
    except IndexError:
        cart = Cart.objects.create(user=request.user)
    cart.empty()


def add_to_cart(request, pk):
    last_page = request.META.get('HTTP_REFERER', '/')
    try:
        num = int(request.POST['quantity'])
    except KeyError:
        num = 1

    this_item = Item.objects.get(id=pk)
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.filter(user=request.user)[0]
        except IndexError:
            cart = Cart.objects.create(user=request.user)
        if this_item.sold_by != request.user:
            if not cart.add_to_cart(this_item, int(num)):
                messages.info(request, message="There aren't enough of that "
                                               "item available for you to place"
                                               " this order.", extra_tags="alert-danger")

        else:
            messages.info(request,
                          message="You can't order items you're selling!", extra_tags="alert-danger")
    return redirect(last_page)


def remove_from_cart(request, oi_id):
    last_page = request.META.get('HTTP_REFERER', '/')
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.filter(user=request.user)[0]
        except IndexError:
            cart = Cart.objects.create(user=request.user)
            return redirect(last_page)
        try:
            oi = OrderItem.objects.get(id=oi_id)
            if cart.contains_order_item(oi):
                cart.remove_order_item(oi)
        except OrderItem.DoesNotExist:
            pass

    return redirect(last_page)


def search(request):
    if request.method == "GET":
        query = request.GET.get('q')
        print("Query made:", query)

        if query is not None and query != "":
            lookups = Q(title__icontains=query) | Q(category__icontains=query)

            results = Item.objects.filter(lookups).distinct()
            print(results)
            context = {
                'results': results
            }
            print(context)
            return render(request, 'search_results.html', context)
    return render(request, 'search_results.html')
