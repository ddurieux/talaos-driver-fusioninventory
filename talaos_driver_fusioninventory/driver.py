from talaos_driver_fusioninventory.communication import Communication
from talaos_driver_fusioninventory.inventory import Inventory
from flask import request


def load(app, db):
    inv = Inventory()
    inv.get_settings_from_ini(db)

    @app.route("/fusioninventory/xml", methods=['POST'])
    def loadxml():
        com = Communication()
        return com.receive_xml(request.data, inv)
