from django.contrib.auth.models import User

from core.models import Cart


def cart_processor(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.filter(user=request.user)[0]
        except IndexError:
            cart = Cart.objects.create(user=request.user)
        total_cost = cart.total_cost

        return {'cart': cart.items.all(),
                'total_cost': total_cost,
                'cart_size': len(cart.items.all())}
    return {}
