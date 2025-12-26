"""
Django 5 translation of a legacy PHP order insertion script.

The original snippet:
    $tab=$_SESSION['CMDCLT']; $nb=count($tab); if(empty($libCmd)) $libCmd="commande client du ".date('d-m-Y H:i');
    if($nb>0){
        if(!empty($datCmd) && $idClt>0){$opeMax=opeMaxClt($idClt); $soldClt=soldClt($idClt);
            if($opeMax==-1 || ($soldClt+$netCmd)<=$opeMax){
                $code=code("CMDCLT",$idUsers,4);
                $prodSelect=""; for($i=0;$i<$nb;$i++){if($i==0) $prodSelect=$tab[$i][0]; else $prodSelect.=",".$tab[$i][0];}
                $sql="INSERT INTO CMDCLT(idCC,idClt,idUsers,code,lib,remise,tva,datCmd,datPay,etat,dat, idMag, idPDV)
                VALUES('','$idClt','$idUsers','$code','$libCmd','$valRemise','$valTva','$datCmd','$datPay','0',CURRENT_TIMESTAMP,'$idMags', '$idPDVs') ";
                mysql_query($sql) or die("echec insert cmd"); $idCC=maxIdElem("CMDCLT",$idUsers,0,"idCC");
                if($idCC>0){
                    for($i=0; $i<$nb; $i++){
                        if($tab[$i][0]>0 && $tab[$i][1]>0){
                            $idProd = $tab[$i][0]; $qte = $tab[$i][1]; $pv = $tab[$i][2]; $commission = $tab[$i][3];
                            $sql="INSERT INTO DETAILCMDCLT(idDCC, idCC, idUsers, idProd, pv, commission, qte, etat, dat, idMag, idPDV) 
                            VALUES('', '$idCC', '$idUsers', '$idProd', '$pv', '$commission', '$qte', '1', CURRENT_TIMESTAMP,'$idMags', '$idPDVs')";
                            mysql_query($sql) or die("echec insert detail command clt");
                        }
                    }
                    if($montFact1==$montFact2 && $montFact1>0 && $montFact1<=$netCmd && in_array(11,$tabPU)){
                        $lib="reglement client (".$libCmd.")"; addCais(1,$idCC,$idUsers,$lib,$montFact1,1,1,1);
                        $sql="UPDATE CMDCLT SET etat=1 WHERE idCC=$idCC"; if($montFact1==$netCmd){ mysql_query($sql) or die("error update valid cmd");}
                    }
                    if($liv==1){
                        $code=code("LIVRAISON",$idUsers,4); if(empty($libLiv)) $libLiv="livraison du ".date('d-m-Y H:i')." (".$libCmd.")";
                        $sql="INSERT INTO LIVRAISON(idLiv,idClt,idCC,idUsers,code,lib,datLiv,remise,tva,etat,dat, idMag, idPDV)
                        VALUES('','$idClt','$idCC','$idUsers','$code','$libLiv','$datCmd','$remise','$tva','1',CURRENT_TIMESTAMP,'$idMags', '$idPDVs')";
                        mysql_query($sql) or die("echec insert livraison"); $idLiv=maxIdElem("LIVRAISON",$idUsers,1,"idLiv");
                        for($i=0;$i<$nb;$i++){
                            if($tab[$i][0]>0 && $tab[$i][1]>0){$idProd=$tab[$i][0]; $qte=$tab[$i][1]; $pv=$tab[$i][2];
                                $sql="INSERT INTO DETAILLIVRAISON(idDL,idLiv,idUsers,idProd,qte,pa,etat,dat, idMag, idPDV)
                                VALUES('','$idLiv','$idUsers','$idProd','$qte','$pv','1',CURRENT_TIMESTAMP,'$idMags', '$idPDVs')"; 
                                mysql_query($sql) or die("echec insert detail cmdclt");
                                $sql="UPDATE DETAILPROD SET qte=qte-$qte WHERE idMag=$idMags AND idProd=$idProd AND etat=1"; mysql_query($sql) or die("error update prod cmdclt");
                            }
                        }
                        $sql="UPDATE CMDCLT SET actif=1 WHERE idCC=$idCC AND actif=0"; mysql_query($sql) or die("error update prod cmdclt");
                    }
                    echo"reussi"; unset($_SESSION['CMDCLT']);
                }
            }else echo"exces";
        }else echo"vide";
    }else echo"noProd";

The module below exposes a Django 5-compatible view that mirrors the
behaviour in a safer, transactional way using the ORM instead of raw SQL.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, List

from django.conf import settings
from django.db import models, transaction
from django.db.models import F
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.views import View


class Client(models.Model):
    """Represents a customer."""

    name = models.CharField(max_length=255)
    credit_ceiling = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("-1"))
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))


class Magasin(models.Model):
    """Store or warehouse."""

    name = models.CharField(max_length=255)


class PointDeVente(models.Model):
    """Point of sale where the transaction occurred."""

    name = models.CharField(max_length=255)


class Produit(models.Model):
    """Product sold to the client."""

    name = models.CharField(max_length=255)


class DetailProd(models.Model):
    """Stock entry for a product in a store."""

    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    magasin = models.ForeignKey(Magasin, on_delete=models.PROTECT)
    qte = models.PositiveIntegerField(default=0)
    etat = models.BooleanField(default=True)


class CommandeClient(models.Model):
    """Client order header."""

    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    code = models.CharField(max_length=50)
    lib = models.CharField(max_length=255)
    remise = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    tva = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    dat_cmd = models.DateField()
    dat_pay = models.DateField(null=True, blank=True)
    etat = models.PositiveSmallIntegerField(default=0)
    actif = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    magasin = models.ForeignKey(Magasin, on_delete=models.PROTECT)
    point_de_vente = models.ForeignKey(PointDeVente, on_delete=models.PROTECT)


class DetailCommandeClient(models.Model):
    """Line item attached to a client order."""

    commande = models.ForeignKey(CommandeClient, on_delete=models.CASCADE, related_name="details")
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    pv = models.DecimalField(max_digits=12, decimal_places=2)
    commission = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    qte = models.PositiveIntegerField()
    etat = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)


class Livraison(models.Model):
    """Delivery header linked to a client order."""

    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    commande = models.ForeignKey(CommandeClient, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    code = models.CharField(max_length=50)
    lib = models.CharField(max_length=255)
    dat_liv = models.DateField()
    remise = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    tva = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    etat = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    magasin = models.ForeignKey(Magasin, on_delete=models.PROTECT)
    point_de_vente = models.ForeignKey(PointDeVente, on_delete=models.PROTECT)


class DetailLivraison(models.Model):
    """Delivery line item."""

    livraison = models.ForeignKey(Livraison, on_delete=models.CASCADE, related_name="details")
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    qte = models.PositiveIntegerField()
    pa = models.DecimalField(max_digits=12, decimal_places=2)
    etat = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)


class MouvementCaisse(models.Model):
    """Cash register movement used when the order is immediately settled."""

    reference = models.CharField(max_length=255)
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    commande = models.ForeignKey(CommandeClient, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)


@dataclass
class CartLine:
    produit_id: int
    qte: int
    pv: Decimal
    commission: Decimal = Decimal("0")


def generate_code(prefix: str, user_id: int, padding: int = 4) -> str:
    """Replicates the legacy `code()` helper with a timestamped slug."""

    suffix = timezone.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}-{str(user_id).zfill(padding)}-{suffix}"


class CreateClientOrderView(View):
    """
    Handle client order creation using Django 5.

    The logic mirrors the legacy PHP script:
    * Read cart lines from the session key ``CMDCLT``.
    * Validate client, available credit, and totals.
    * Create the order header, order lines, optional payment, and optional delivery.
    * Update stock quantities atomically.
    """

    def post(self, request: HttpRequest) -> JsonResponse:  # type: ignore[override]
        cart_lines = self._parse_cart(request.session.get("CMDCLT", []))
        if not cart_lines:
            return JsonResponse({"status": "error", "message": "noProd"}, status=400)

        lib_cmd = request.POST.get("libCmd") or f"commande client du {timezone.now():%d-%m-%Y %H:%M}"
        dat_cmd_raw = request.POST.get("datCmd")
        client_id = int(request.POST.get("idClt", 0))

        if not dat_cmd_raw or client_id <= 0:
            return JsonResponse({"status": "error", "message": "vide"}, status=400)

        client = Client.objects.get(pk=client_id)
        dat_cmd = timezone.datetime.fromisoformat(dat_cmd_raw).date()
        dat_pay = request.POST.get("datPay")
        remise = Decimal(request.POST.get("remise", "0"))
        tva = Decimal(request.POST.get("tva", "0"))
        payment_total = Decimal(request.POST.get("montFact1", "0"))
        payment_confirmation = Decimal(request.POST.get("montFact2", "0"))
        liv = request.POST.get("liv", "0") == "1"
        lib_liv = request.POST.get("libLiv")
        user = request.user
        magasin = Magasin.objects.get(pk=int(request.POST.get("idMag")))
        point_de_vente = PointDeVente.objects.get(pk=int(request.POST.get("idPDV")))
        payment_modes = {int(mode) for mode in request.POST.getlist("tabPU")}

        net_total = self._compute_net_total(cart_lines, remise, tva)
        if not self._has_credit(client, net_total):
            return JsonResponse({"status": "error", "message": "exces"}, status=400)

        with transaction.atomic():
            commande = CommandeClient.objects.create(
                client=client,
                user=user,
                code=generate_code("CMDCLT", user.id),
                lib=lib_cmd,
                remise=remise,
                tva=tva,
                dat_cmd=dat_cmd,
                dat_pay=timezone.datetime.fromisoformat(dat_pay).date() if dat_pay else None,
                etat=0,
                magasin=magasin,
                point_de_vente=point_de_vente,
            )

            self._create_order_lines(commande, cart_lines)

            if self._should_register_payment(payment_total, payment_confirmation, net_total, payment_modes):
                MouvementCaisse.objects.create(
                    reference=f"reglement client ({lib_cmd})",
                    montant=payment_total,
                    commande=commande,
                    user=user,
                )
                if payment_total == net_total:
                    commande.etat = 1
                    commande.save(update_fields=["etat"])

            if liv:
                livraison = self._create_delivery(commande, cart_lines, lib_cmd, lib_liv, tva, remise, dat_cmd)
                self._update_stock(cart_lines, magasin)
                commande.actif = True
                commande.save(update_fields=["actif"])

            request.session.pop("CMDCLT", None)

        return JsonResponse({"status": "ok", "message": "reussi", "commande_id": commande.id})

    @staticmethod
    def _parse_cart(raw_cart: Iterable) -> List[CartLine]:
        lines: List[CartLine] = []
        for raw in raw_cart:
            try:
                produit_id = int(raw[0])
                qte = int(raw[1])
                pv = Decimal(str(raw[2]))
                commission = Decimal(str(raw[3])) if len(raw) > 3 else Decimal("0")
            except (TypeError, ValueError, IndexError):
                continue
            if produit_id > 0 and qte > 0:
                lines.append(CartLine(produit_id=produit_id, qte=qte, pv=pv, commission=commission))
        return lines

    @staticmethod
    def _compute_net_total(cart_lines: Iterable[CartLine], remise: Decimal, tva: Decimal) -> Decimal:
        gross_total = sum(line.pv * line.qte for line in cart_lines)
        return gross_total - remise + tva

    @staticmethod
    def _has_credit(client: Client, net_total: Decimal) -> bool:
        ceiling = client.credit_ceiling
        if ceiling == -1:
            return True
        return (client.balance + net_total) <= ceiling

    @staticmethod
    def _should_register_payment(payment_total: Decimal, payment_confirmation: Decimal, net_total: Decimal, payment_modes: set[int]) -> bool:
        return payment_total == payment_confirmation and Decimal("0") < payment_total <= net_total and 11 in payment_modes

    @staticmethod
    def _create_order_lines(commande: CommandeClient, cart_lines: Iterable[CartLine]) -> None:
        for line in cart_lines:
            produit = Produit.objects.get(pk=line.produit_id)
            DetailCommandeClient.objects.create(
                commande=commande,
                produit=produit,
                pv=line.pv,
                commission=line.commission,
                qte=line.qte,
            )

    @staticmethod
    def _create_delivery(
        commande: CommandeClient,
        cart_lines: Iterable[CartLine],
        lib_cmd: str,
        lib_liv: str | None,
        tva: Decimal,
        remise: Decimal,
        dat_cmd,
    ) -> Livraison:
        user = commande.user
        code = generate_code("LIVRAISON", user.id)
        libelle = lib_liv or f"livraison du {timezone.now():%d-%m-%Y %H:%M} ({lib_cmd})"
        livraison = Livraison.objects.create(
            client=commande.client,
            commande=commande,
            user=user,
            code=code,
            lib=libelle,
            dat_liv=dat_cmd,
            remise=remise,
            tva=tva,
            magasin=commande.magasin,
            point_de_vente=commande.point_de_vente,
        )
        for line in cart_lines:
            produit = Produit.objects.get(pk=line.produit_id)
            DetailLivraison.objects.create(
                livraison=livraison,
                produit=produit,
                qte=line.qte,
                pa=line.pv,
            )
        return livraison

    @staticmethod
    def _update_stock(cart_lines: Iterable[CartLine], magasin: Magasin) -> None:
        for line in cart_lines:
            DetailProd.objects.filter(produit_id=line.produit_id, magasin=magasin, etat=True).update(qte=F("qte") - line.qte)
