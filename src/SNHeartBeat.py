#!/usr/bin/env python
# coding=utf-8

import time
import struct
import hashlib
import SNAttribute
from SNConstants import HBDefault, SNClient


class SNHeartBeat(object):

    def __init__(self, packet_id, timestamp, attribute_list, magic_num=0x534E):
        self.packet_id = packet_id
        self.timeflag = self.calc_timeflag(timestamp=timestamp)
        self.magic_num = magic_num
        self.attribute_list = attribute_list

        self._fmt_str = '>HHBB16s'

    @property
    def attributes_data(self):
        attributes_data = ''
        for attribute in self.attribute_list:
            attributes_data += attribute.digest()
        return attributes_data

    @property
    def length(self):
        return struct.calcsize(self._fmt_str) + len(self.attributes_data)

    @property
    def signature(self):
        salt = HBDefault['SIG_SALT']

        temp_data = struct.pack(self._fmt_str, self.magic_num,
                                self.length, self.packet_id,
                                self.timeflag, '\x00' * 16)
        temp_data += self.attributes_data

        m = hashlib.md5()
        m.update(temp_data)
        m.update(salt)

        return m.digest()

    @classmethod
    def calc_timeflag(cls, timestamp=int(time.time())):
        temp_num = (((timestamp * 0x343FD) + 0x269EC3) & 0xFFFFFFFF)
        timeflag = (temp_num >> 0x10) & 0xFF
        return timeflag

    def digest(self):
        ramdata = struct.pack(self._fmt_str, self.magic_num,
                              self.length, self.packet_id,
                              self.timeflag, self.signature)
        ramdata += self.attributes_data
        return ramdata

    def hexdigest(self):
        return self.digest().encode('hex')


class SNThunderProtocol(SNHeartBeat):

    def __init__(self, username, ipaddress, timestamp, version=SNClient['CLIENT_VERSION']):
        #timestamp = 1424526603
        attribute_list = [
            SNAttribute.CLIENT_IP_ADDRESS(ipaddress),
            SNAttribute.CLIENT_VERSION(version),
            SNAttribute.KEEPALIVE_DATA(
                SNAttribute.KEEPALIVE_DATA.get_keepalive_data(timestamp)),
            SNAttribute.KEEPALIVE_TIME(timestamp),
            SNAttribute.USER_NAME(username),
        ]
        super(SNThunderProtocol, self).__init__(
            packet_id=0x3, timestamp=timestamp, attribute_list=attribute_list)


class SNRegister_Bubble(SNHeartBeat):

    def __init__(self, bubble_id, ipaddress, username, timestamp):
        attribute_list = [
            SNAttribute.CLIENT_IP_ADDRESS(ipaddress),
            SNAttribute.USER_NAME(username)
        ]
        super(SNRegister_Bubble, self).__init__(
            packet_id=bubble_id, timestamp=timestamp, attribute_list=attribute_list)


if __name__ == '__main__':
    pass
