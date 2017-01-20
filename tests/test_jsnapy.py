# content of test_expectation.py
import pytest
from jnpr.jsnapy import SnapAdmin
from pprint import pprint
from jnpr.junos import Device
import yaml

test_parameters = {}

def pytest_generate_tests(metafunc):
    global test_parameters


    ## Add function to search for testfile in local directory

    ## Open test file
    jsnap_test_conf_file = open("jsnap_test.yaml")
    jsnap_test_conf_file = yaml.load(jsnap_test_conf_file)

    param = []
    for device in jsnap_test_conf_file['hosts']:
        for test in jsnap_test_conf_file['tests']:
            test_name = device['device'] + '/' + str(device['port']) + '/' + test
            #test_name = test_name.replace('.', '_')
            param.append(test_name)

            test_parameters[test_name] = {}
            test_parameters[test_name]['device'] = device
            test_parameters[test_name]['test_file'] = test

    metafunc.parametrize("jsnap_test_name",param)

def test_valid_string(jsnap_test_name):
    global test_parameters


    try:
        dev = Device(test_parameters[jsnap_test_name]['device']['device'],
                     user=test_parameters[jsnap_test_name]['device']['username'],
                     password=test_parameters[jsnap_test_name]['device']['passwd'],
                     port=test_parameters[jsnap_test_name]['device']['port'],
                     gather_facts=False).open()

    except Exception as err:
        msg = 'unable to connect to {0}: {1}'.format(
            test_parameters[jsnap_test_name]['device']['device'],
            str(err))
        assert 0
        # --- UNREACHABLE ---

    ## Open test file
    #try:
    #jsnap_test_file = open(test_parameters[jsnap_test_name]['test_file'])

    config_data = {'tests': [test_parameters[jsnap_test_name]['test_file']]}

    js = SnapAdmin()
    snapValue = js.snapcheck(data=config_data, dev=dev)

    if isinstance(snapValue, (list)):
        for snapCheck in snapValue:
            total_test = int(snapCheck.no_passed) + int(snapCheck.no_failed)
        percentagePassed = (int(snapCheck.no_passed) * 100 ) / total_test

    assert percentagePassed == 100

# js = SnapAdmin()
#
# config_data = """
# hosts:
#   - device: 10.209.16.204
#     username : demo
#     passwd: demo123
# tests:
#   - test_exists.yml
#   - test_contains.yml
#   - test_is_equal.yml
# """
#
# snapchk = js.snapcheck(config_data, "pre")
# for val in snapchk:
#     print "Tested on", val.device
#     print "Final result: ", val.result
#     print "Total passed: ", val.no_passed
#     print "Total failed:", val.no_failed
#     pprint(dict(val.test_details))
