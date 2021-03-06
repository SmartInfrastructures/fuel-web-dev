# Copyright 2013 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from fuelmenu.common.errors import BadIPException
from fuelmenu.common.errors import NetworkException

import netaddr
import subprocess


def inSameSubnet(ip1, ip2, netmask_or_cidr):
    try:
        cidr1 = netaddr.IPNetwork("%s/%s" % (ip1, netmask_or_cidr))
        cidr2 = netaddr.IPNetwork("%s/%s" % (ip2, netmask_or_cidr))
        return cidr1 == cidr2
    except netaddr.AddrFormatError:
        return False


def getCidr(ip, netmask):
    try:
        ipn = netaddr.IPNetwork("%s/%s" % (ip, netmask))
        return str(ipn.cidr)
    except netaddr.AddrFormatError:
        return False


def getCidrSize(cidr):
    try:
        ipn = netaddr.IPNetwork(cidr)
        return ipn.size
    except netaddr.AddrFormatError:
        return False


def getNetwork(ip, netmask, additionalip=None):
    #Return a list excluding ip and broadcast IPs
    try:
        ipn = netaddr.IPNetwork("%s/%s" % (ip, netmask))
        ipn_list = list(ipn)
        #Drop broadcast and network ip
        ipn_list = ipn_list[1:-1]
        #Drop ip
        ipn_list[:] = [value for value in ipn_list if str(value) != ip]
        #Drop additionalip
        if additionalip:
            ipn_list[:] = [value for value in ipn_list if
                           str(value) != additionalip]

        return ipn_list
    except netaddr.AddrFormatError:
        return False


def range(startip, endip):
    #Return a list of IPs between startip and endip
    try:
        return set(netaddr.iter_iprange(startip, endip))
    except netaddr.AddrFormatError:
        raise BadIPException("Invalid IP address(es) specified.")


def intersects(range1, range2):
    #Returns true if any IPs in range1 exist in range2
    return range1 & range2


def netmaskToCidr(netmask):
    return sum([bin(int(x)).count('1') for x in netmask.split('.')])


def duplicateIPExists(ip, iface, arping_bind=False):
    """Checks for duplicate IP addresses using arping
    Don't use arping_bind unless you know what you are doing.

    :param ip: IP to scan for
    :param iface: Interface on which to send requests
    :param arping_bind: Bind to IP when probing (IP must be already assigned.)
    :returns: boolean
    """
    noout = open('/dev/null', 'w')
    if arping_bind:
        bind_ip = ip
    else:
        bind_ip = "0.0.0.0"
    no_dupes = subprocess.call(["arping", "-D", "-c3", "-w1", "-I", iface,
                               "-s", bind_ip, ip], stdout=noout, stderr=noout)
    return (no_dupes != 0)


def upIface(iface):
    noout = open('/dev/null', 'w')
    result = subprocess.call(["ifconfig", iface, "up"], stdout=noout,
                             stderr=noout)
    if result != 0:
        raise NetworkException("Failed to up interface {0}".format(iface))
