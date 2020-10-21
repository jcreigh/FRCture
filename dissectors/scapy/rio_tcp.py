from scapy.all import *
from scapy.all import conf, orb, Packet, LenField, ByteField, XByteField, \
                      XShortField, FieldLenField, StrLenField, PacketListField
import struct


class Tag(Packet):
    fields_desc = [
        LenField('len', None),
        XByteField('tag', None),
        StrLenField('data', '', length_from=lambda pkt:pkt.len - 1)
    ]

    @classmethod
    def dispatch_hook(cls, s=None, *_args, **_kwargs):
        if s is None:
            return conf.raw_layer
        tag_id = orb(s[2])

        if tag_id == 0x00:
            return RadioEvent
        elif tag_id == 0x01:
            return UsageReport
        elif tag_id == 0x04:
            return DisableFaults
        elif tag_id == 0x05:
            return RailFaults
        elif tag_id == 0x0a:
            return VersionInfo
        elif tag_id == 0x0b:
            return ErrorMessage
        elif tag_id == 0x0c:
            return StdOut
        else:
            return Tag

    def guess_payload_class(self, payload):
        return conf.padding_layer

    def post_build(self, p, pay):
        if self.len is None:
            p = struct.pack('>H', len(p) - 2) + p[2:]
        return p + pay


class RadioEvent(Tag):
    name = 'Tag - RadioEvent'

    fields_desc = [
        LenField('len', None),
        XByteField('tag', 0x00),
        StrLenField('message', None, length_from=lambda pkt:pkt.len - 1)
    ]


class UsageReport(Tag):
    name = 'Tag - UsageReport'

    fields_desc = [
        LenField('len', None),
        XByteField('tag', 0x01),
        XByteField('unknown', None),
        StrLenField('data', None, length_from=lambda pkt:pkt.len - 2)
    ]


class DisableFaults(Tag):
    name = 'Tag - DisableFaults'

    fields_desc = [
        LenField('len', None),
        XByteField('tag', 0x04),
        ShortField('comms', 0),
        ShortField('volts12', 0)
    ]


class RailFaults(Tag):
    name = 'Tag - RailFaults'

    fields_desc = [
        LenField('len', None),
        XByteField('tag', 0x05),
        ShortField('volts6', 0),
        ShortField('volts5', 0),
        ShortField('volts3_3', 0)
    ]


class VersionInfo(Tag):
    name = 'Tag - VersionInfo'

    fields_desc = [
        LenField('len', None),
        XByteField('tag', 0x0a),

        ByteField('type', None),
        XShortField('unknown', None),
        ByteField('id', None),
        FieldLenField('name_len', None, fmt='B', length_of='name'),
        StrLenField('name', None, length_from=lambda pkt:pkt.name_len),
        FieldLenField('ver_len', None, fmt='B', length_of='version'),
        StrLenField('version', None, length_from=lambda pkt:pkt.ver_len)
    ]


class ErrorMessage(Tag):
    name = 'Tag - ErrorMessage'

    fields_desc = [
        LenField('len', None),
        XByteField('tag', 0x0b),
        IEEEFloatField('timestamp', 0.0),
        ShortField('seqnum', 0),
        ShortField('unknown', 1),
        SignedIntField('code', 0),
        FlagsField('flag', 0, 8, ['error', 'isLVCode', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7']),
        FieldLenField('details_len', None, fmt='H', length_of='details'),
        StrLenField('details', '', length_from=lambda pkt:pkt.details_len),
        FieldLenField('location_len', None, fmt='H', length_of='location'),
        StrLenField('location', '', length_from=lambda pkt:pkt.location_len),
        FieldLenField('callstack_len', None, fmt='H', length_of='callstack'),
        StrLenField('callstack', '', length_from=lambda pkt:pkt.callstack_len)
    ]


class StdOut(Tag):
    name = 'Tag - StdOut'

    fields_desc = [
        LenField('len', None),
        XByteField('tag', 0x0b),
        IEEEFloatField('timestamp', 0.0),
        ShortField('seqnum', 0),
        StrLenField('message', '', length_from=lambda pkt:pkt.len - 7),
    ]



class RioToDsTcp(Packet):
    name = 'RIO to DS TCP Packet'
    fields_desc = [
        PacketListField('tags', [], Tag)
    ]

bind_layers(TCP, RioToDsTcp, sport=1740)
