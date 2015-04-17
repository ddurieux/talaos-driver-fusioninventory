# flake8: noqa
from behave import *
from nose.tools import ok_, eq_, assert_equals, assert_not_equals
from pprint import pprint
import json
from talaos_inventory.app import Application


@given(u'the api backend is available')
def step_impl(context):
    ok_(context.client and context.application.db)

@given(u'I import the xml file "{xmlfile}"')
def step_impl(context, xmlfile):
    # send fusioninventory XML
    with open ("tests/features/data/" + xmlfile, "r") as myfile:
        xmldata=myfile.read().replace('\n', '')
    response = context.client.post('/fusioninventory/xml',
                                   data=xmldata
                                  )
    eq_(response.status_code, 200)

    # ensure this asset type has been sucessfully created
#    response = context.client.get('/asset_type?where={{"name":"{}"}}'.format(asset_type))
#    eq_(response.status_code, 200)
#    result = json.loads(response.data.decode())
#    eq_(len(result['_items']), 1)


@when(u'I am looking for asset types "{asset_type}"')
def step_impl(context,asset_type):
    # retrieve the asset_type id
    response = context.client.get('/asset_type?where={{"name":"{}"}}'.format(asset_type))
    assert_equals(response.status_code, 200)
    result = json.loads(response.data.decode())
    assert_equals(len(result['_items']), 1)
    asset_type_id = result['_items'][0]['id']

    # search
    response = context.client.get('/asset?where={{"asset_type_id":"{}"}}'.format(asset_type_id))
    assert_equals(response.status_code, 200)
    result = json.loads(response.data.decode())
    context.result = result


@then(u'I must retrieve a list of "{nb:d}" asset')
def step_impl(context, nb):
    ok_(context.result and context.result['_meta'])
    assert_equals(context.result['_meta']['total'], nb)


@when(u'I am looking for all assets in database')
def step_impl(context):
    response = context.client.get('/asset')
    assert_equals(response.status_code, 200)
    result = json.loads(response.data.decode())
    context.result = result
