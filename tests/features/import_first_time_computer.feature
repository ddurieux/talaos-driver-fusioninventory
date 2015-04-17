Feature: import a fusioninventory computer from XML

  Background:
    Given the api backend is available
    And I import the xml file "portdavid.xml"

  Scenario: Import computer from XML
        When I am looking for all assets in database
        Then I must retrieve a list of "1964" asset

        When I am looking for asset types "computer"
        Then I must retrieve a list of "1" asset

        When I am looking for asset types "accesslog"
        Then I must retrieve a list of "1" asset

        When I am looking for asset types "bios"
        Then I must retrieve a list of "0" asset

        When I am looking for asset types "operatingsystem"
        Then I must retrieve a list of "1" asset

        When I am looking for asset types "antivirus"
        Then I must retrieve a list of "0" asset

        When I am looking for asset types "battery"
        Then I must retrieve a list of "1" asset

        When I am looking for asset types "controller"
        Then I must retrieve a list of "16" asset

        When I am looking for asset types "cpu"
        Then I must retrieve a list of "1" asset

        When I am looking for asset types "drive"
        Then I must retrieve a list of "34" asset

        When I am looking for asset types "env"
        Then I must retrieve a list of "26" asset

        When I am looking for asset types "input"
        Then I must retrieve a list of "0" asset

        When I am looking for asset types "licenseinfo"
        Then I must retrieve a list of "0" asset

        When I am looking for asset types "local_group"
        Then I must retrieve a list of "3" asset

        When I am looking for asset types "local_user"
        Then I must retrieve a list of "46" asset

        When I am looking for asset types "logical_volume"
        Then I must retrieve a list of "0" asset

        When I am looking for asset types "memory"
        Then I must retrieve a list of "2" asset

        When I am looking for asset types "monitor"
        Then I must retrieve a list of "0" asset

        When I am looking for asset types "network"
        Then I must retrieve a list of "17" asset

        When I am looking for asset types "physical_volume"
        Then I must retrieve a list of "0" asset

        When I am looking for asset types "port"
        Then I must retrieve a list of "25" asset

        When I am looking for asset types "printer"
        Then I must retrieve a list of "0" asset

        When I am looking for asset types "process"
        Then I must retrieve a list of "159" asset

        When I am looking for asset types "slot"
        Then I must retrieve a list of "5" asset

        When I am looking for asset types "software"
        Then I must retrieve a list of "1622" asset

        When I am looking for asset types "user"
        Then I must retrieve a list of "1" asset

        When I am looking for asset types "storage"
        Then I must retrieve a list of "1" asset

        When I am looking for asset types "sound"
        Then I must retrieve a list of "1" asset

        When I am looking for asset types "virtualmachine"
        Then I must retrieve a list of "1" asset

        When I am looking for asset types "volume_group"
        Then I must retrieve a list of "0" asset
