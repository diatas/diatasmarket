"""
Django 5 view that reproduces the PHP order creation flow from the prompt.

The code assumes existing Django models representing customer orders, order lines,
stock details, and deliveries. Replace the placeholder imports with the actual
models and helper functions in your project.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from django.db import models, transaction
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

# Import your concrete models/helpers instead of these placeholders.
from orders.models import (
    CustomerCommand,
    CustomerCommandLine,
    Delivery,
    DeliveryLine,
    ProductStock,
)
from orders.services import add_cash_entry, generate_code, get_client_balance, get_client_operation_limit


@dataclass
class CartLine:
    """Represents a line in the session cart.

    Attributes:
        product_id: Identifier of the product being purchased.
        quantity: Number of units ordered.
        unit_price: Sale price for the product.
        commission: Commission amount associated with the sale.
    """

    product_id: int
    quantity: int
    unit_price: float
    commission: float


@require_POST
@transaction.atomic
def create_customer_order(request: HttpRequest):
    """
    Create a customer order from the session cart.

    This is a direct translation of the provided PHP code. It keeps the control
    flow identical while using Django 5 features like transactions, ORM queries,
    and HTTP helpers. The view responds with simple JSON status markers to match
    the original echo statements.
    """

    cart: list[list[int | float]] = request.session.get("CMDCLT", [])
    if not cart:
        return JsonResponse({"status": "noProd"}, status=400)

    lib_cmd = request.POST.get(
        "libCmd",
        f"commande client du {timezone.localtime().strftime('%d-%m-%Y %H:%M')}",
    )
    dat_cmd = request.POST.get("datCmd")
    dat_pay = request.POST.get("datPay")
    customer_id = int(request.POST.get("idClt", "0"))
    user_id = int(request.POST.get("idUsers", "0"))
    discount_value = float(request.POST.get("valRemise", "0"))
    vat_value = float(request.POST.get("valTva", "0"))
    net_amount = float(request.POST.get("netCmd", "0"))
    first_payment = float(request.POST.get("montFact1", "0"))
    second_payment = float(request.POST.get("montFact2", "0"))
    payment_modes = [int(mode) for mode in request.POST.getlist("tabPU[]", [])]
    deliver_now = request.POST.get("liv") == "1"
    lib_delivery = request.POST.get(
        "libLiv",
        f"livraison du {timezone.localtime().strftime('%d-%m-%Y %H:%M')} ({lib_cmd})",
    )
    store_id = int(request.POST.get("idMags", "0"))
    pos_id = int(request.POST.get("idPDVs", "0"))

    if not dat_cmd or customer_id <= 0:
        return JsonResponse({"status": "vide"}, status=400)

    operation_limit = get_client_operation_limit(customer_id)
    client_balance = get_client_balance(customer_id)

    if not (operation_limit == -1 or (client_balance + net_amount) <= operation_limit):
        return JsonResponse({"status": "exces"}, status=400)

    # Create the order header.
    order_code = generate_code("CMDCLT", user_id, 4)
    order = CustomerCommand.objects.create(
        customer_id=customer_id,
        user_id=user_id,
        code=order_code,
        label=lib_cmd,
        discount=discount_value,
        vat=vat_value,
        order_date=dat_cmd,
        payment_date=dat_pay,
        status=0,
        created_at=timezone.now(),
        store_id=store_id,
        point_of_sale_id=pos_id,
    )

    lines: Iterable[CartLine] = (
        CartLine(
            product_id=int(item[0]),
            quantity=int(item[1]),
            unit_price=float(item[2]),
            commission=float(item[3]),
        )
        for item in cart
        if len(item) >= 4 and int(item[0]) > 0 and int(item[1]) > 0
    )

    for line in lines:
        CustomerCommandLine.objects.create(
            order=order,
            user_id=user_id,
            product_id=line.product_id,
            unit_price=line.unit_price,
            commission=line.commission,
            quantity=line.quantity,
            status=1,
            created_at=timezone.now(),
            store_id=store_id,
            point_of_sale_id=pos_id,
        )

    if (
        first_payment == second_payment
        and first_payment > 0
        and first_payment <= net_amount
        and 11 in payment_modes
    ):
        payment_label = f"reglement client ({lib_cmd})"
        add_cash_entry(1, order.id, user_id, payment_label, first_payment, 1, 1, 1)
        if first_payment == net_amount:
            order.status = 1
            order.save(update_fields=["status"])

    if deliver_now:
        delivery_code = generate_code("LIVRAISON", user_id, 4)
        delivery = Delivery.objects.create(
            customer_id=customer_id,
            order=order,
            user_id=user_id,
            code=delivery_code,
            label=lib_delivery,
            delivery_date=dat_cmd,
            discount=discount_value,
            vat=vat_value,
            status=1,
            created_at=timezone.now(),
            store_id=store_id,
            point_of_sale_id=pos_id,
        )

        for line in cart:
            if len(line) < 2 or int(line[0]) <= 0 or int(line[1]) <= 0:
                continue

            product_id = int(line[0])
            quantity = int(line[1])
            unit_price = float(line[2]) if len(line) > 2 else 0.0

            DeliveryLine.objects.create(
                delivery=delivery,
                user_id=user_id,
                product_id=product_id,
                quantity=quantity,
                purchase_price=unit_price,
                status=1,
                created_at=timezone.now(),
                store_id=store_id,
                point_of_sale_id=pos_id,
            )

            ProductStock.objects.filter(
                store_id=store_id, product_id=product_id, status=1
            ).update(quantity=models.F("quantity") - quantity)

        CustomerCommand.objects.filter(id=order.id, is_active=False).update(is_active=True)

    request.session.pop("CMDCLT", None)
    return JsonResponse({"status": "reussi", "order_id": order.id})
