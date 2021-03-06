# -*- coding: utf-8 -*-

#    Copyright 2014 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from fuel_upgrade import utils

from fuel_upgrade.engines.docker_engine import DockerUpgrader
from fuel_upgrade.engines.host_system import HostSystemUpgrader
from fuel_upgrade.pre_upgrade_hooks.base import PreUpgradeHookBase

logger = logging.getLogger(__name__)


class AddKeystoneCredentialsHook(PreUpgradeHookBase):
    """Feature `Fuel master access control improvements`
    was introduced in 6.0 release [1].

    In this feature fuelmenu generates keystone credenitals
    and saves them in /etc/astute.yaml file.

    Before upgrade for this featuer we need to
    add new keystone credentials to the file.

    [1] https://blueprints.launchpad.net/fuel/+spec/
        access-control-master-node-improvments
    """

    #: This hook required only for docker and host system engines
    enable_for_engines = [DockerUpgrader, HostSystemUpgrader]

    #: New credentials
    keystone_config = {
        'keystone': {
            "nailgun_user": "nailgun",
            "nailgun_password": utils.generate_uuid_string(),
            "ostf_user": "ostf",
            "ostf_password": utils.generate_uuid_string(),
        }
    }

    def check_if_required(self):
        """Checks if it's required to run upgrade

        :returns: True - if it is required to run this hook
                  False - if it is not required to run this hook
        """
        is_required = not all(
            key in self.config.astute.get('keystone', {})
            for key in self.keystone_config['keystone'].keys())

        return is_required

    def run(self):
        """Adds default credentials to config file
        """
        self.update_astute_config(defaults=self.keystone_config)
