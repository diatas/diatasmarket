"""
Django 5 translation of the legacy PHP order creation snippet.

This module defines ORM models and a view that reproduce the behavior of the
original code while following Django conventions. The view expects to receive
POST data similar to the PHP script and uses the ``CMDCLT`` session key to
collect the cart items.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, List

from django.db import models, transaction
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST


class Client(models.Model):
    ope_max = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("-1"))
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))


class User(models.Model):
    username = models.CharField(max_length=150)


class CommandeClient(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    code = models.CharField(max_length=32)
    lib = models.CharField(max_length=255)
    remise = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    tva = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    dat_cmd = models.DateTimeField()
    dat_pay = models.DateTimeField(null=True, blank=True)
    etat = models.BooleanField(default=False)
    dat = models.DateTimeField(default=timezone.now)
    id_mag = models.IntegerField()
    id_pdv = models.IntegerField()
    actif = models.BooleanField(default=False)
    net_cmd = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))


class DetailCommandeClient(models.Model):
    commande = models.ForeignKey(CommandeClient, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    produit_id = models.IntegerField()
    pv = models.DecimalField(max_digits=12, decimal_places=2)
    commission = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    qte = models.PositiveIntegerField()
    etat = models.BooleanField(default=True)
    dat = models.DateTimeField(default=timezone.now)
    id_mag = models.IntegerField()
    id_pdv = models.IntegerField()


class Livraison(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    commande = models.ForeignKey(CommandeClient, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    code = models.CharField(max_length=32)
    lib = models.CharField(max_length=255)
    dat_liv = models.DateTimeField()
    remise = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    tva = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    etat = models.BooleanField(default=True)
    dat = models.DateTimeField(default=timezone.now)
    id_mag = models.IntegerField()
    id_pdv = models.IntegerField()


class DetailLivraison(models.Model):
    livraison = models.ForeignKey(Livraison, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    produit_id = models.IntegerField()
    qte = models.PositiveIntegerField()
    pa = models.DecimalField(max_digits=12, decimal_places=2)
    etat = models.BooleanField(default=True)
    dat = models.DateTimeField(default=timezone.now)
    id_mag = models.IntegerField()
    id_pdv = models.IntegerField()


class DetailProduit(models.Model):
    produit_id = models.IntegerField()
    id_mag = models.IntegerField()
    qte = models.IntegerField(default=0)
    etat = models.BooleanField(default=True)


@dataclass
class CartItem:
    produit_id: int
    quantity: int
    prix_vente: Decimal
    commission: Decimal


def generate_code(prefix: str, user_id: int, width: int = 4) -> str:
    """Generate an alphanumeric code similar to the legacy ``code`` helper."""
    return f"{prefix}-{user_id}-{timezone.now():%Y%m%d%H%M%S}"[-width:]


def parse_cart(cart_data: Iterable[List]) -> List[CartItem]:
    items: List[CartItem] = []
    for raw in cart_data:
        produit_id, qte, pv, commission = raw
        items.append(
            CartItem(
                produit_id=int(produit_id),
                quantity=int(qte),
                prix_vente=Decimal(str(pv)),
                commission=Decimal(str(commission)),
            )
        )
    return items


@require_POST
@transaction.atomic
def create_client_order(request: HttpRequest) -> JsonResponse:
    """
    Django 5 implementation of the PHP order creation workflow.

    Expected POST keys: ``idClt``, ``idUsers``, ``datCmd``, ``datPay``,
    ``valRemise``, ``valTva``, ``netCmd``, ``idMags``, ``idPDVs``, ``liv``,
    ``montFact1``, ``montFact2``, ``tabPU`` and optional ``libCmd`` or ``libLiv``.
    """

    session_cart = request.session.get("CMDCLT", [])
    cart_items = parse_cart(session_cart)
    lib_cmd = request.POST.get("libCmd") or f"commande client du {timezone.now():%d-%m-%Y %H:%M}"

    if not cart_items:
        return JsonResponse({"status": "noProd"}, status=400)

    dat_cmd_raw = request.POST.get("datCmd")
    try:
        dat_cmd = timezone.make_aware(timezone.datetime.fromisoformat(dat_cmd_raw)) if dat_cmd_raw else None
    except ValueError:
        dat_cmd = None

    id_clt = int(request.POST.get("idClt", 0))
    user_id = int(request.POST.get("idUsers", 0))

    if not dat_cmd or id_clt <= 0:
        return JsonResponse({"status": "vide"}, status=400)

    client = Client.objects.select_for_update().get(pk=id_clt)
    user = User.objects.get(pk=user_id)
    net_cmd = Decimal(request.POST.get("netCmd", "0"))

    if client.ope_max != Decimal("-1") and (client.balance + net_cmd) > client.ope_max:
        return JsonResponse({"status": "exces"}, status=400)

    code_cmd = generate_code("CMDCLT", user_id, 4)

    commande = CommandeClient.objects.create(
        client=client,
        user=user,
        code=code_cmd,
        lib=lib_cmd,
        remise=Decimal(request.POST.get("valRemise", "0")),
        tva=Decimal(request.POST.get("valTva", "0")),
        dat_cmd=dat_cmd,
        dat_pay=request.POST.get("datPay"),
        net_cmd=net_cmd,
        id_mag=int(request.POST.get("idMags", 0)),
        id_pdv=int(request.POST.get("idPDVs", 0)),
    )

    detail_rows = [
        DetailCommandeClient(
            commande=commande,
            user=user,
            produit_id=item.produit_id,
            pv=item.prix_vente,
            commission=item.commission,
            qte=item.quantity,
            id_mag=commande.id_mag,
            id_pdv=commande.id_pdv,
        )
        for item in cart_items
        if item.produit_id > 0 and item.quantity > 0
    ]
    DetailCommandeClient.objects.bulk_create(detail_rows)

    mont_fact1 = Decimal(request.POST.get("montFact1", "0"))
    mont_fact2 = Decimal(request.POST.get("montFact2", "0"))
    tab_pu = request.POST.getlist("tabPU")

    if mont_fact1 == mont_fact2 and Decimal("0") < mont_fact1 <= net_cmd and "11" in tab_pu:
        commande.etat = True
        commande.save(update_fields=["etat"])
        # Place-holder: addCais equivalent would be implemented here.

    if request.POST.get("liv") == "1":
        code_liv = generate_code("LIVRAISON", user_id, 4)
        lib_liv = request.POST.get("libLiv") or f"livraison du {timezone.now():%d-%m-%Y %H:%M} ({lib_cmd})"
        remise = Decimal(request.POST.get("valRemise", "0"))
        tva = Decimal(request.POST.get("valTva", "0"))
        livraison = Livraison.objects.create(
            client=client,
            commande=commande,
            user=user,
            code=code_liv,
            lib=lib_liv,
            dat_liv=dat_cmd,
            remise=remise,
            tva=tva,
            id_mag=commande.id_mag,
            id_pdv=commande.id_pdv,
        )

        liv_details = []
        for item in cart_items:
            if item.produit_id <= 0 or item.quantity <= 0:
                continue
            liv_details.append(
                DetailLivraison(
                    livraison=livraison,
                    user=user,
                    produit_id=item.produit_id,
                    qte=item.quantity,
                    pa=item.prix_vente,
                    id_mag=commande.id_mag,
                    id_pdv=commande.id_pdv,
                )
            )

            DetailProduit.objects.filter(
                id_mag=commande.id_mag,
                produit_id=item.produit_id,
                etat=True,
            ).update(qte=models.F("qte") - item.quantity)

        DetailLivraison.objects.bulk_create(liv_details)
        CommandeClient.objects.filter(pk=commande.pk, actif=False).update(actif=True)

    request.session.pop("CMDCLT", None)
    return JsonResponse({"status": "reussi", "idCC": commande.pk})
