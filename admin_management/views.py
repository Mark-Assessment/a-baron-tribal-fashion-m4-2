from django.shortcuts import (render, get_object_or_404,
                              redirect, reverse)
from profiles.models import UserAccount, RetailAccount
from products.models import Product
from checkout.models import OrderLineItem, Order
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required, user_passes_test


@login_required
@user_passes_test(lambda u: u.is_superuser)
def management_dashboard(request):
    account = get_object_or_404(UserAccount, user=request.user)
    products = Product.objects.all()
    template = 'admin_management/management_dashboard.html'
    context = {
        'account': account,
        'products': products
    }
    return render(request, template, context=context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def remove_tribal_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    items = OrderLineItem.objects.filter(product=product)
    if items:
        messages.error(request, 'An order exists with this item')
        return redirect(reverse('management_dashboard'))
    else:
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect(reverse('management_dashboard'))


@login_required
@user_passes_test(lambda u: u.is_superuser)
def retailer_requests(request):
    requests = UserAccount.objects.all()
    template = 'admin_management/retailer_requests.html'
    context = {
        'requests': requests
    }
    return render(request, template, context=context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def approve_retailer(request, request_user_id):
    requests = UserAccount.objects.all()
    current_request = get_object_or_404(UserAccount, pk=request_user_id)
    if request.method == 'POST':
        account = get_object_or_404(UserAccount, pk=request_user_id)
        account.retailer = True
        account.retailer_requested = False
        account.save()
        user_email = account.user.email
        subject = render_to_string(
            "retailer_response_email/retailer_response_subject.txt",
            {'retailer': account})
        body = render_to_string(
            "retailer_response_email/retailer_response_body_approved.txt",
            {'retailer': account,
             'contact_email': settings.DEFAULT_FROM_EMAIL})
        send_mail(
            subject=subject,
            message=body,
            recipient_list=[user_email],
            from_email=settings.DEFAULT_FROM_EMAIL,
        )
        return redirect(reverse('retailer_requests'))
    template = 'admin_management/retailer_request.html'
    context = {
        'requests': requests,
        'current_request': current_request
    }
    return render(request, template, context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def decline_retailer(request, request_user_id):
    account = get_object_or_404(UserAccount, pk=request_user_id)
    account.retailer_requested = False
    account.save()
    user_email = account.user.email
    subject = render_to_string(
            "retailer_response_email/retailer_response_subject.txt",
            {'retailer': account})
    body = render_to_string(
            "retailer_response_email/retailer_response_body_declined.txt",
            {'retailer': account,
             'contact_email': settings.DEFAULT_FROM_EMAIL})
    send_mail(
        subject=subject,
        message=body,
        recipient_list=[user_email],
        from_email=settings.DEFAULT_FROM_EMAIL,
        )
    return redirect(reverse('retailer_requests'))


@login_required
@user_passes_test(lambda u: u.is_superuser)
def premium_cancel_requests(request):
    requests = RetailAccount.objects.all()
    template = 'admin_management/premium_cancel_requests.html'
    context = {
        'requests': requests
    }
    return render(request, template, context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def approve_cancelation(request, retailer_id):
    requests = RetailAccount.objects.all()
    retailer = get_object_or_404(RetailAccount, pk=retailer_id)
    if request.method == 'POST':
        retailer.subscribed = False
        retailer.cancel_subscription = False
        retailer.save()
        return redirect(reverse('premium_cancel_requests'))
    template = 'admin_management/premium_cancel_request.html'
    context = {
        'retailer': retailer,
        'requests': requests
    }
    return render(request, template, context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def order_cancel_requests(request):
    orders = Order.objects.all()
    template = 'admin_management/order_cancellations.html'
    context = {
        'orders': orders
    }
    return render(request, template, context)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def order_cancellation(request, order_number):
    orders = Order.objects.all()
    items_ordered = OrderLineItem.objects.all()
    current_request = None
    product = None
    order_num = ''
    for order in orders:
        if order.order_number == order_number:
            current_request = order

    if request.method == 'POST':
        order_num = current_request.order_number
        for item in items_ordered:
            if item.order == current_request:
                product = item.product
                product.stock_quantity = product.stock_quantity + item.quantity
                product.save()
        customer_email = current_request.email
        subject = render_to_string(
            "order_cancellation_email/order_cancellation_subject.txt",
            {'order': current_request})
        body = render_to_string(
            "order_cancellation_email/order_cancellation_body.txt",
            {'order': current_request,
             'contact_email': settings.DEFAULT_FROM_EMAIL})
        send_mail(
            subject=subject,
            message=body,
            recipient_list=[customer_email],
            from_email=settings.DEFAULT_FROM_EMAIL,
        )
        current_request.delete()
        messages.success(request, f'Order with order number {order_num}\
             has been cancelled successfully.')
        return redirect(reverse('order_cancel_requests'))

    template = 'admin_management/order_cancellation.html'
    context = {
        'orders': orders,
        'current_request': current_request,
        'items': items_ordered
    }
    return render(request, template, context)
