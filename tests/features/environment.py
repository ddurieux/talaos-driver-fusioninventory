from talaos_inventory.app import Application
from talaos_driver_fusioninventory.inventory import Inventory
from pprint import pprint  # noqa
import importlib


def before_feature(context, feature):
    context.application = Application()
    context.application.initialize(False, 'install')
    context.application.install()

    driver = "talaos_driver_fusioninventory"
    if importlib.find_loader(driver):
        print("load", driver)
        new_driver = __import__(driver, globals(), locals(),
                                ['driver'], 0)
        new_driver.driver.load(context.application.app, context.application.db)

    context.client = context.application.app.test_client()


def before_scenario(context, scenario):
    context.application.db.drop_all()
    context.application.install()
    inv = Inventory()
    inv.get_settings_from_ini(context.application.db)
