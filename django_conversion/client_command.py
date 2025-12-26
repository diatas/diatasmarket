"""
Django 5 translation of a legacy PHP client command workflow.

The original PHP script:
    - Consumes a ``CMDCLT`` session cart and request parameters to create a customer
      command (``CMDCLT``) along with detail lines.
    - Optionally records a payment when the invoice values match.
    - Optionally generates a delivery record and adjusts inventory.

This module provides a single ``create_client_command`` view function that mirrors
those behaviors using Django ORM patterns, transactional integrity, and explicit
response codes.
"""
from __future__ import annotations

from decimal import Decimal
from typing import List, Sequence, Tuple

from django.db import models, transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST


# --- Domain models ---------------------------------------------------------
# These mirror the tables from the PHP snippet. Field names follow the original
# schema for easier traceability while adopting Django conventions.


class Client(models.Model):
    name = models.CharField(max_length=255)


class Magasin(models.Model):
    label = models.CharField(max_length=255)


class PointDeVente(models.Model):
    label = models.CharField(max_length=255)


class CommandeClient(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    user_id = models.IntegerField()
    code = models.CharField(max_length=32)
    lib = models.CharField(max_length=255)
    remise = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    dat_cmd = models.DateTimeField()
    dat_pay = models.DateTimeField(null=True, blank=True)
    etat = models.BooleanField(default=False)
    actif = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    magasin = models.ForeignKey(Magasin, on_delete=models.PROTECT)
    point_de_vente = models.ForeignKey(PointDeVente, on_delete=models.PROTECT)


class Produit(models.Model):
    name = models.CharField(max_length=255)


class DetailCommandeClient(models.Model):
    commande = models.ForeignKey(CommandeClient, on_delete=models.CASCADE)
    user_id = models.IntegerField()
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    pv = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2)
    qte = models.PositiveIntegerField()
    etat = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    magasin = models.ForeignKey(Magasin, on_delete=models.PROTECT)
    point_de_vente = models.ForeignKey(PointDeVente, on_delete=models.PROTECT)


class Livraison(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    commande = models.ForeignKey(CommandeClient, on_delete=models.CASCADE)
    user_id = models.IntegerField()
    code = models.CharField(max_length=32)
    lib = models.CharField(max_length=255)
    dat_liv = models.DateTimeField()
    remise = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    etat = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    magasin = models.ForeignKey(Magasin, on_delete=models.PROTECT)
    point_de_vente = models.ForeignKey(PointDeVente, on_delete=models.PROTECT)


class DetailLivraison(models.Model):
    livraison = models.ForeignKey(Livraison, on_delete=models.CASCADE)
    user_id = models.IntegerField()
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    qte = models.PositiveIntegerField()
    pa = models.DecimalField(max_digits=10, decimal_places=2)
    etat = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    magasin = models.ForeignKey(Magasin, on_delete=models.PROTECT)
    point_de_vente = models.ForeignKey(PointDeVente, on_delete=models.PROTECT)


# --- Domain helpers --------------------------------------------------------


def ope_max_client(client_id: int) -> int:
    """Return the maximum allowed operation amount for the client.

    A value of ``-1`` mirrors the PHP behavior and means no limit.
    Replace this stub with real business logic.
    """

    return -1


def client_balance(client_id: int) -> Decimal:
    """Return the client's outstanding balance."""

    return Decimal("0")


def generate_code(prefix: str, user_id: int, width: int) -> str:
    """Mimic the PHP ``code`` helper that produced an incremental code."""

    suffix = str(user_id).rjust(width, "0")
    return f"{prefix}-{suffix}-{timezone.now().strftime('%Y%m%d%H%M%S')}"


def add_cash_entry(type_id: int, command_id: int, user_id: int, lib: str, amount: Decimal) -> None:
    """Persist a cash register entry.

    Replace this stub with calls to your actual accounting layer.
    """

    # Implement integration with your caisse model here.
    return None


# --- Conversion of the PHP workflow ---------------------------------------


@require_POST
@transaction.atomic
def create_client_command(request):
    """Create a client command based on the PHP snippet's control flow.

    Expected request payload keys mirror the PHP variables:
    - ``datCmd``, ``datPay``
    - ``idClt`` (client id), ``idUsers`` (current user id)
    - ``idMags`` (store), ``idPDVs`` (point of sale)
    - ``valRemise``, ``valTva``, ``netCmd``
    - ``montFact1``, ``montFact2``, ``tabPU`` (list of payment modes)
    - ``liv`` (1 to trigger delivery), ``libLiv`` (optional delivery label)

    The ``CMDCLT`` session entry should be a sequence of tuples like
    ``(product_id, quantity, price, commission)``.
    """

    cart: Sequence[Tuple[int, int, Decimal, Decimal]] = request.session.get("CMDCLT", [])
    if not cart:
        return JsonResponse({"status": "error", "code": "noProd"}, status=400)

    lib_cmd = request.POST.get("libCmd") or f"commande client du {timezone.now():%d-%m-%Y %H:%M}"
    dat_cmd_raw = request.POST.get("datCmd")
    dat_pay_raw = request.POST.get("datPay")
    id_clt = int(request.POST.get("idClt", 0))
    id_users = int(request.POST.get("idUsers", 0))
    id_mags = int(request.POST.get("idMags", 0))
    id_pdvs = int(request.POST.get("idPDVs", 0))

    if not dat_cmd_raw or id_clt <= 0:
        return JsonResponse({"status": "error", "code": "vide"}, status=400)

    dat_cmd = timezone.make_aware(timezone.datetime.fromisoformat(dat_cmd_raw))
    dat_pay = (
        timezone.make_aware(timezone.datetime.fromisoformat(dat_pay_raw)) if dat_pay_raw else None
    )

    net_cmd = Decimal(request.POST.get("netCmd", "0"))
    val_remise = Decimal(request.POST.get("valRemise", "0"))
    val_tva = Decimal(request.POST.get("valTva", "0"))

    if not cart:
        return JsonResponse({"status": "error", "code": "vide"}, status=400)

    ope_max = ope_max_client(id_clt)
    sold_clt = client_balance(id_clt)
    if ope_max != -1 and (sold_clt + net_cmd) > ope_max:
        return JsonResponse({"status": "error", "code": "exces"}, status=400)

    client = Client.objects.get(pk=id_clt)
    magasin = Magasin.objects.get(pk=id_mags)
    point_de_vente = PointDeVente.objects.get(pk=id_pdvs)

    command = CommandeClient.objects.create(
        client=client,
        user_id=id_users,
        code=generate_code("CMDCLT", id_users, 4),
        lib=lib_cmd,
        remise=val_remise,
        tva=val_tva,
        dat_cmd=dat_cmd,
        dat_pay=dat_pay,
        magasin=magasin,
        point_de_vente=point_de_vente,
    )

    detail_rows: List[DetailCommandeClient] = []
    for product_id, quantity, pv, commission in cart:
        if product_id > 0 and quantity > 0:
            produit = Produit.objects.get(pk=product_id)
            detail_rows.append(
                DetailCommandeClient(
                    commande=command,
                    user_id=id_users,
                    produit=produit,
                    pv=Decimal(pv),
                    commission=Decimal(commission),
                    qte=quantity,
                    magasin=magasin,
                    point_de_vente=point_de_vente,
                )
            )
    DetailCommandeClient.objects.bulk_create(detail_rows)

    mont_fact1 = Decimal(request.POST.get("montFact1", "0"))
    mont_fact2 = Decimal(request.POST.get("montFact2", "0"))
    tab_pu = {int(value) for value in request.POST.getlist("tabPU")}

    if (
        mont_fact1 == mont_fact2
        and mont_fact1 > 0
        and mont_fact1 <= net_cmd
        and 11 in tab_pu
    ):
        lib = f"reglement client ({lib_cmd})"
        add_cash_entry(1, command.pk, id_users, lib, mont_fact1)
        command.etat = mont_fact1 == net_cmd
        command.save(update_fields=["etat"])

    liv = int(request.POST.get("liv", 0))
    if liv == 1:
        lib_liv = request.POST.get("libLiv") or f"livraison du {timezone.now():%d-%m-%Y %H:%M} ({lib_cmd})"
        livraison = Livraison.objects.create(
            client=client,
            commande=command,
            user_id=id_users,
            code=generate_code("LIVRAISON", id_users, 4),
            lib=lib_liv,
            dat_liv=dat_cmd,
            remise=val_remise,
            tva=val_tva,
            magasin=magasin,
            point_de_vente=point_de_vente,
        )

        detail_liv_rows: List[DetailLivraison] = []
        for product_id, quantity, pv, _commission in cart:
            if product_id > 0 and quantity > 0:
                produit = Produit.objects.get(pk=product_id)
                detail_liv_rows.append(
                    DetailLivraison(
                        livraison=livraison,
                        user_id=id_users,
                        produit=produit,
                        qte=quantity,
                        pa=Decimal(pv),
                        magasin=magasin,
                        point_de_vente=point_de_vente,
                    )
                )
                # Inventory adjustments would normally happen through a service
                # layer; add the necessary hooks here when integrating.
        DetailLivraison.objects.bulk_create(detail_liv_rows)

        command.actif = True
        command.save(update_fields=["actif"])

    request.session.pop("CMDCLT", None)
    return JsonResponse({"status": "ok", "id": command.pk, "code": command.code})
