
from django.utils import timezone
from decimal import Decimal
from django.utils.text import slugify
from saleor.account.models import Address, Group, User
from saleor.channel.models import Channel
from django.conf import settings
from django.db import connection
from saleor.permission.enums import AccountPermissions, CheckoutPermissions, GiftcardPermissions, OrderPermissions, get_permissions
from saleor.permission.models import Permission
from saleor.plugins.grigoprint.permissions import GrigoprintPermissions
from saleor.shipping import ShippingMethodType
from saleor.shipping.models import ShippingMethod, ShippingMethodChannelListing, ShippingZone

from saleor.tax.models import TaxConfiguration
from saleor.warehouse import WarehouseClickAndCollectOption
from saleor.warehouse.models import Warehouse

from ...accountExtra.models import UserExtra

SUPER_USERS = [
    {"fname":"Antonio","lname":"Grigolini","email":"antonio@test.it", "rapp":False},
    {"fname":"Andrea","lname":"Olivo","email":"andrea@test.it", "rapp":False},
]
STAFF_USERS = [
    {"fname":"Giovanna","lname":"Lupatini","email":"giovanna@test.it", "rapp":False},
    {"fname":"Luciana","lname":"Viviani","email":"luciana@test.it", "rapp":False},
    {"fname":"Marcello","lname":"Grigolini","email":"marcello@test.it", "rapp":False},
    {"fname":"Dorothy","lname":"Rampoldi","email":"dorothy@test.it", "rapp":False},
]
RAPP_USERS = [
    {"fname":"Corbella","lname":"Raffaele","email":"raffaele@test.it", "rapp":True},
]


def create_staff_user(staff_password, data, superuser=True):
    email = data["email"]
    # Skip the email if it already exists
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = User.objects.create_user(
            first_name=data["fname"],
            last_name=data["lname"],
            email=email,
            is_active=True,
            is_staff=True,
            is_superuser = superuser,
            date_joined=timezone.get_current_timezone(),
        )
        user.set_password(staff_password)
        user.save()
        UserExtra(user=user, is_rappresentante=data["rapp"])
    # asegno permessi
    
    return user
def create_group(name, permissions, users):
    group, _ = Group.objects.get_or_create(name=name)
    group.permissions.add(*permissions)
    group.user_set.add(*users)
    return group
def create_permission_groups(staff_password):
    super_users = [create_staff_user(staff_password,user, True) for user in SUPER_USERS]
    group = create_group("Full Access", get_permissions(), super_users)
    yield f"Group: {group}"

    staff_users = [create_staff_user(staff_password,user, True) for user in STAFF_USERS]
    customer_support_codenames = [
        perm.codename
        for enum in [CheckoutPermissions, OrderPermissions, GiftcardPermissions]
        for perm in enum
    ]
    customer_support_codenames.append(AccountPermissions.MANAGE_USERS.codename)
    customer_support_permissions = Permission.objects.filter(
        codename__in=customer_support_codenames
    )
    group = create_group("Servizio Clienti", customer_support_permissions, staff_users)
    yield f"Group: {group}"
    rapp_users = [create_staff_user(staff_password,user, True) for user in RAPP_USERS]
    
    rappresentanti_codenames = [
        GrigoprintPermissions.IS_RAPPRESENTANTE.codename
    ]
    rappresentanti_permissions = Permission.objects.filter(
        codename__in=rappresentanti_codenames
    )
    group = create_group("Rappresentanti", rappresentanti_permissions, rapp_users)
    yield f"Group: {group}"

def create_channel(channel_name, currency_code, slug=None, country=None):
    if not slug:
        slug = slugify(channel_name)
    channel, _ = Channel.objects.get_or_create(
        slug=slug,
        defaults={
            "name": channel_name,
            "currency_code": currency_code,
            "is_active": True,
            "default_country": country,
        },
    )
    TaxConfiguration.objects.get_or_create(channel=channel)
    return f"Channel: {channel}"

def create_channels():
    yield create_channel(
        channel_name="Channel-IT",
        currency_code="EUR",
        slug=settings.DEFAULT_CHANNEL_SLUG,
        country="IT",
    )

def create_shipping_zone(shipping_methods_names, countries, shipping_zone_name):
    shipping_zone = ShippingZone.objects.get_or_create(
        name=shipping_zone_name, defaults={"countries": countries}
    )[0]
    shipping_methods = ShippingMethod.objects.bulk_create(
        [
            ShippingMethod(
                name=name,
                shipping_zone=shipping_zone,
                type=(
                    # ShippingMethodType.PRICE_BASED
                    # if random.randint(0, 1)
                    # else 
                    ShippingMethodType.WEIGHT_BASED
                ),
                minimum_order_weight=0,
                maximum_order_weight=None,
            )
            for name in shipping_methods_names
        ]
    )
    channels = Channel.objects.all()
    for channel in channels:
        ShippingMethodChannelListing.objects.bulk_create(
            [
                ShippingMethodChannelListing(
                    shipping_method=shipping_method,
                    price_amount=Decimal(0), # TODO prezzo spedizione
                    minimum_order_price_amount=Decimal(0),
                    maximum_order_price_amount=None,
                    channel=channel,
                    currency=channel.currency_code,
                )
                for shipping_method in shipping_methods
            ]
        )
    shipping_zone.channels.add(*channels)
    return "Shipping Zone: %s" % shipping_zone


def create_shipping_zones():
    european_countries = [
        "FR",
        "DE",
        "CH",
        "ES",
    ]
    yield create_shipping_zone(
        shipping_zone_name="Europe",
        countries=european_countries,
        shipping_methods_names=["DHL", "GLS"],
    )
    italia = [
        "IT"
    ]
    yield create_shipping_zone(
        shipping_zone_name="Italia",
        countries=european_countries,
        shipping_methods_names=["DHL", "GLS", "Registered priority", "DB Schenker"],
    )

def create_warehouse():
    address = Address(
        first_name="Ombrellificio Grigolini",
        last_name="",
        street_address_1="Loc. S.Antonio da Padova 2",
        city="Illasi",
        country="IT",
        country_area = "VR",
        postal_code = 37031,
    )
    address.save()
    channels = Channel.objects.all()
    for shipping_zone in ShippingZone.objects.all():
        shipping_zone_name = shipping_zone.name
        is_private = True, False
        cc_option = WarehouseClickAndCollectOption.LOCAL_STOCK
        warehouse, _ = Warehouse.objects.update_or_create(
            name=shipping_zone_name,
            slug=slugify(shipping_zone_name),
            defaults={
                "address": address,
                "is_private": is_private,
                "click_and_collect_option": cc_option,
            },
        )
        warehouse.shipping_zones.add(shipping_zone)
        warehouse.channels.add(*channels)