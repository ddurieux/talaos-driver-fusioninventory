from flask import make_response, request, abort
from lxml import etree, objectify
from talaos_driver_fusioninventory.inventory import Inventory
import zlib
import gzip
import xmltodict


class Communication():

    def receive_xml(self, data, inv):
        data = self.get_compressed_xml(data)
        self.check_xml(data)
        xml_request = objectify.fromstring(data)
        if hasattr(xml_request, 'QUERY'):
            if xml_request.QUERY == 'PROLOG':
                # request an inventory
                em = objectify.ElementMaker(annotate=False)
                reply = em.REPLY(em.RESPONSE('SEND'), em.PROLOG_FREQ(24))
                return etree.tostring(reply, pretty_print=True)
            elif xml_request.QUERY == 'INVENTORY':
                # Inject inventory xml_request.CONTENT
                inventory = xmltodict.parse(data)
                inv.parse_inventory(inventory['REQUEST']['CONTENT'])
                em = objectify.ElementMaker(annotate=False)
                reply = em.REPLY()
                return etree.tostring(reply, pretty_print=True)
        return ''

    def get_compressed_xml(self, xmlcompressed):
        '''
        Determine if the XML is compressed
        '''
        if request.headers['Content-Type'] == 'application/x-compress-zlib':
            xml = zlib.decompress(xmlcompressed)
        elif request.headers['Content-Type'] == 'application/x-compress-gzip':
            xml = gzip.decompress(xmlcompressed)
        elif request.headers['Content-Type'] == 'application/xml':
            xml = xmlcompressed
        else:
            xml = xmlcompressed
        return xml

    def check_xml(self, xml):
        '''
        Check if the XML is valid
        '''
        try:
            return etree.fromstring(xml)
        except:
            self.error('XML invalid')

    def error(self, msg):
        print(msg)
        abort(make_response(msg, 400))
        pass
