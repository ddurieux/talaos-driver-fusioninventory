import os
from configparser import ConfigParser
import ast
import talaos_inventory.models.assets as assets
from lxml import objectify


class Inventory():

    def parse_inventory(self, data):
        '''
        parse inventory and insert into db
        data is a xml
        '''
        assets_ids = []
        assets_id = []
        for item in data.iterchildren():
            assets_id.append(self.add_asset(item))
        for i in assets_id:
            if i > 0 and i not in assets_ids:
                assets_ids.append(i)
        # add computer asset
        computer = objectify.Element("COMPUTER")
        computer.serialnumber = data.BIOS.SSN
        computer.uuid = data.HARDWARE.UUID
        computer.manufacturer = data.BIOS.SMANUFACTURER
        computer.name = data.HARDWARE.NAME
        asset_id = self.add_asset(computer)
        # link assets to this computer asset
        self.parent_links(asset_id, assets_ids)

    def add_asset(self, data):
        if data.tag in self.mapping_local_inventory:
            property_name_ids = []
            search_asset_property = True
            for v in data.iterchildren():
                name = (str(v)[:250]) if len(str(v)) > 250 else str(v)
                property_name = self.db.session.query(
                    assets.PropertyName
                ).with_entities(
                    assets.PropertyName.id
                ).filter_by(
                    name=name,
                    asset_type_property_id=self.mapping_local_inventory[data.tag][v.tag]
                ).first()
                if property_name is not None:
                    property_name_ids.append(property_name.id)
                else:
                    search_asset_property = False
                    propertyname = assets.PropertyName()
                    propertyname.name=name
                    propertyname.asset_type_property_id=self.mapping_local_inventory[data.tag][v.tag]
                    self.db.session.add(propertyname)
                    self.db.session.commit()
                    property_name_ids.append(propertyname.id)
            if search_asset_property:
                prepQuery = self.db.session.query(
                    assets.AssetProperty
                ).with_entities(
                    assets.AssetProperty.asset_id
                ).filter(
                    getattr(
                        assets.AssetProperty,
                        'property_name_id'
                    ).in_(property_name_ids)
                )
                db_values = prepQuery.first()
                if db_values is not None:
                    return db_values.asset_id
            # if we are here, we must add new asset
            print('Create new asset ' + data.tag)
            asset = assets.Asset()
            asset.asset_type_id = self.mapping_asset_type[data.tag]
            self.db.session.add(asset)
            self.db.session.commit()
            asset_id = asset.id
            for id in property_name_ids:
                assetproperty = assets.AssetProperty()
                assetproperty.asset_id = asset_id
                assetproperty.property_name_id = id
                self.db.session.add(assetproperty)
                self.db.session.commit()
            return asset_id
        return 0

    def parent_links(self, parent_id, children_ids):
        query = self.db.session.query(assets.AssetAsset)
        prepQuery = query.with_entities(assets.AssetAsset.asset_right).filter(
            getattr(
                assets.AssetAsset,
                'asset_left'
            ) == parent_id)
        db_values = prepQuery.all()
        children = [r[0] for r in db_values]
        for id in children_ids:
            if not id in children:
                asset_asset = assets.AssetAsset()
                asset_asset.asset_left = parent_id
                asset_asset.asset_right = id
                self.db.session.add(asset_asset)
                self.db.session.commit()

    def get_settings_from_ini(self, db):
        self.db = db
        settings = {}
        settings_filenames = [
            '/etc/talaos_inventory/driver_fusioninventory.ini',
            os.path.abspath('./driver_fusioninventory.ini')
        ]
        # Define some variables available
        defaults = {
            '_cwd': os.getcwd()
        }
        config = ConfigParser(defaults=defaults)
        config.read(settings_filenames)
        at = ast.literal_eval(config.get('MAPPING', 'asset_type'))
        self.structure_asset_type(db, at)
        li = ast.literal_eval(config.get('MAPPING', 'local_inventory'))
        self.structure_properties(db, li)

    def structure_asset_type(self, db, data):
        self.mapping_asset_type = {}
        for key in data:
            asset_type = db.session.query(assets.AssetType).filter_by(name=data[key]).first()
            if asset_type is not None:
                self.mapping_asset_type[key] = asset_type.id
            else:
                assettype = assets.AssetType(name=data[key])
                db.session.add(assettype)
                db.session.commit()
                self.mapping_asset_type[key] = assettype.id

    def structure_properties(self, db, data):
        self.mapping_local_inventory = {}
        for key in data:
            self.mapping_local_inventory[key] = {}
            for prop in data[key]:
                asset_type_property = db.session.query(assets.AssetTypeProperty).filter_by(name=data[key][prop]).first()
                if asset_type_property is not None:
                    self.mapping_local_inventory[key][prop] = asset_type_property.id
                else:
                    assettypeproperty = assets.AssetTypeProperty()
                    assettypeproperty.name = data[key][prop]
                    assettypeproperty.asset_type_id = self.mapping_asset_type[key]
                    db.session.add(assettypeproperty)
                    db.session.commit()
                    self.mapping_local_inventory[key][prop] = assettypeproperty.id
