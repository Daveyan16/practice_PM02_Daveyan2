from src.services.pricing_service import (
    Breakfast,
    Transfer,
    ServicePackage
)


def test_breakfast_price():

    breakfast = Breakfast()

    assert breakfast.get_price() == 15


def test_transfer_price():

    transfer = Transfer()

    assert transfer.get_price() == 30


def test_empty_package():

    package = ServicePackage("Empty")

    assert package.get_price() == 0


def test_package_with_breakfast():

    package = ServicePackage("Breakfast")

    package.add(Breakfast())

    assert package.get_price() == 15


def test_package_with_transfer():

    package = ServicePackage("Transfer")

    package.add(Transfer())

    assert package.get_price() == 30


def test_composite_package():

    package = ServicePackage("Combo")

    package.add(Breakfast())
    package.add(Transfer())

    assert package.get_price() == 45