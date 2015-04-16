import os
from configparser import ConfigParser
import ast
import talaos_inventory.models.assets as assets
from eve.methods.post import post_internal
from sqlalchemy.sql import and_, or_
import time


class Inventory():

    def parse_inventory(self, data):
        '''
        parse inventory and insert into db
        '''
        start_time = time.time()
        # add computer asset
        computer = {}
        computer['serialnumber'] = data['BIOS']['SSN']
        computer['uuid'] = data['HARDWARE']['UUID']
        computer['manufacturer'] = data['BIOS']['SMANUFACTURER']
        computer['name'] = data['HARDWARE']['NAME']
        asset_id = self.add_asset_parent(computer, 'COMPUTER')

        db_values = self.db.session.query(
            assets.AssetAsset
        ).with_entities(
            assets.AssetAsset.asset_right
        ).filter(
            assets.AssetAsset.asset_left == asset_id
        ).all()
        result_db = [r[0] for r in db_values]
        # Split list to have less than 1000 elements for the next query
        assets_db_sub = [result_db[i:i + 900] for i in range(
            0,
            len(result_db),
            900)]

        properties = {}
        if len(assets_db_sub) > 0:
            for assets_db in assets_db_sub:
                db_values = self.db.session.query(
                    assets.AssetProperty
                ).with_entities(
                    assets.AssetProperty.asset_id,
                    assets.AssetProperty.property_name_id
                ).filter(
                    assets.AssetProperty.asset_id.in_(assets_db)
                ).all()
                for i, (asset_id, property_name_id) in enumerate(db_values):
                    if asset_id not in properties:
                        properties[asset_id] = set()
                    properties[asset_id].add(property_name_id)

        assets_ids = []
        assets_id = []
        for item in data:
            if type(data[item]) is list:
                for dataitem in data[item]:
                    assets_id.append(
                        self.add_asset(
                            dataitem, item, properties
                        )
                    )
            else:
                assets_id.append(
                    self.add_asset(
                        data[item], item, properties
                    )
                )
        for i in assets_id:
            if i > 0 and i not in assets_ids:
                assets_ids.append(i)
        # link assets to this computer asset
        self.parent_links(asset_id, assets_ids)
        print("--- %s seconds ---" % (time.time() - start_time))

    def add_asset(self, data, nodename, properties):
        if nodename in self.mapping_local_inventory:
            property_name_ids = set()
            property_name_bis = self.db.session.query(
                assets.PropertyName
            ).with_entities(
                assets.PropertyName.id,
                assets.PropertyName.asset_type_property_id
            )
            clauses = []
            prop = {}
            for name in data:
                if name in self.mapping_local_inventory[nodename]:
                    value = str(data[name])
                    if len(value) > 250:
                        value = str(data[name])[:250]
                    clauses.append(and_(
                        assets.PropertyName.name == value,
                        assets.PropertyName.asset_type_property_id == self.
                        mapping_local_inventory[nodename][name]
                    ))
                    prop[self.mapping_local_inventory[nodename][name]] = value

            property_name_bis = property_name_bis.filter(or_(*clauses))
            property_name_db = property_name_bis.all()
            for i, (id, atp_id) in enumerate(property_name_db):
                if atp_id in prop:
                    property_name_ids.add(id)
                    del prop[atp_id]
            if len(prop) == 0:
                for asset_id in properties:
                    if properties[asset_id] == property_name_ids:
                        del properties[asset_id]
                        return asset_id

            for id in prop:
                input = {
                    'name': prop[id],
                    'asset_type_property_id': id
                }
                propertyname = post_internal('property_name', input)
                property_name_ids.add(propertyname[0]['_id'])

            # if we are here, we must add new asset
            input = {
                'asset_type_id': self.mapping_asset_type[nodename]
            }
            asset = post_internal('asset', input)
            asset_id = asset[0]['_id']
            for id in property_name_ids:
                input = {
                    'asset_id': asset_id,
                    'property_name_id': id
                }
                post_internal('asset_property', input)
            return asset_id
        return 0

    def add_asset_parent(self, data, nodename):
        if nodename in self.mapping_local_inventory:
            property_name_ids = []
            search_asset_property = True
            property_name_bis = self.db.session.query(
                assets.PropertyName
            ).with_entities(
                assets.PropertyName.id,
                assets.PropertyName.asset_type_property_id
            )
            clauses = []
            properties = {}
            for name in data:
                if name in self.mapping_local_inventory[nodename]:
                    value = str(data[name])
                    if len(value) > 250:
                        value = str(data[name])[:250]
                    key = self.mapping_local_inventory[nodename][name]
                    clauses.append(and_(
                        assets.PropertyName.name == value,
                        assets.PropertyName.asset_type_property_id == key
                    ))
                    properties[key] = value

            property_name_bis = property_name_bis.filter(or_(*clauses))
            property_name_db = property_name_bis.all()
            for i, (id, atp_id) in enumerate(property_name_db):
                if atp_id in properties:
                    property_name_ids.append(id)
                    del properties[atp_id]
            for id in properties:
                search_asset_property = False
                input = {
                    'name': properties[id],
                    'asset_type_property_id': id
                }
                propertyname = post_internal('property_name', input)
                print(propertyname)
                property_name_ids.append(propertyname[0]['_id'])

            if search_asset_property:
                args = []
                i = 0
                for id in property_name_ids:
                    if i == 0:
                        args.append(self.db.session.query(
                            assets.AssetProperty
                        ).with_entities(
                            assets.AssetProperty.asset_id,
                        ).filter(
                            assets.AssetProperty.property_name_id == id
                        ))
                    else:
                        args[(i - 1)] = args[(i - 1)].subquery()

                        args.append(self.db.session.query(
                            assets.AssetProperty
                        ).with_entities(
                            assets.AssetProperty.asset_id,
                        ).filter(
                            assets.AssetProperty.asset_id == args[(i - 1)].
                            c.asset_id,
                            assets.AssetProperty.property_name_id == id
                        ))
                    i = i + 1
                for fields in args[(i - 1)]:
                    return fields.asset_id
            # if we are here, we must add new asset
            input = {
                'asset_type_id': self.mapping_asset_type[nodename]
            }
            asset = post_internal('asset', input)
            asset_id = asset[0]['_id']
            for id in property_name_ids:
                input = {
                    'asset_id': asset_id,
                    'property_name_id': id
                }
                post_internal('asset_property', input)
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
            if id not in children:
                input = {
                    'asset_left': parent_id,
                    'asset_right': id
                }
                post_internal('asset_asset', input)

    def get_settings_from_ini(self, db):
        self.db = db
        settings_filenames = [
            '/etc/talaos_inventory/driver_fusioninventory.ini',
            os.path.abspath('./docs/driver_fusioninventory.ini')
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
            asset_type = db.session.query(
                assets.AssetType
            ).filter_by(
                name=data[key]
            ).first()
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
                asset_type_property = db.session.query(
                    assets.AssetTypeProperty
                ).filter_by(
                    name=data[key][prop],
                    asset_type_id=self.mapping_asset_type[key]
                ).first()
                if asset_type_property is not None:
                    self.mapping_local_inventory[key][prop] = \
                        asset_type_property.id
                else:
                    assettypeproperty = assets.AssetTypeProperty()
                    assettypeproperty.name = data[key][prop]
                    assettypeproperty.asset_type_id = \
                        self.mapping_asset_type[key]
                    db.session.add(assettypeproperty)
                    db.session.commit()
                    self.mapping_local_inventory[key][prop] = \
                        assettypeproperty.id
