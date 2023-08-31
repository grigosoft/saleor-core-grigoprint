from saleor.plugins.grigoprint.preventivo.models import Checkout, Preventivo, StatoPreventivo

def test_sequenza_preventivo(channel_USD):
    checkout1 = Checkout.objects.create(email="preventivo1@test.it", channel=channel_USD)
    preventivo1 = Preventivo.objects.create(checkout=checkout1)
    checkout2 = Checkout.objects.create(email="preventivo2@test.it", channel=channel_USD)
    preventivo2 = Preventivo.objects.create(checkout=checkout2, stato=StatoPreventivo.BOZZA)
    checkout3 = Checkout.objects.create(email="preventivo3@test.it", channel=channel_USD)
    preventivo3 = Preventivo.objects.create(checkout=checkout3)
    assert preventivo1.number == 1
    assert preventivo2.number == 2
    assert preventivo3.number == 3
    # torno indietro con gli anni cosi il prossimo riavvia la sequenza
    preventivo1.anno = 2000
    preventivo1.save()
    preventivo2.anno = 2000
    preventivo2.save()
    preventivo3.anno = 2000
    preventivo3.save()
    checkout4 = Checkout.objects.create(email="preventivo4@test.it", channel=channel_USD)
    preventivo4 = Preventivo.objects.create(checkout=checkout4)
    assert preventivo4.number == 1