from scapy.all import *
from scapy.all import conf, orb, Packet, LenField, ByteField, XByteField, \
                      XShortField, FieldLenField, StrLenField, PacketListField


class Tag(Packet):
    @classmethod
    def dispatch_hook(cls, s=None, *_args, **_kwargs):
        if s is None:
            return conf.raw_layer
        tag_id = orb(s[2])

        if tag_id == 0x0a:
            return VersionInfo
        if tag_id == 0x0e:
            return GameData

    def guess_payload_class(self, payload):
        return conf.padding_layer


class VersionInfo(Tag):
    name = 'Tag - VersionInfo'

    fields_desc = [
        LenField("len", None),
        XByteField("tag", 0x0a),

        ByteField("type", None),
        XShortField("unknown", None),
        ByteField("id", None),
        FieldLenField("name_len", None, fmt='B', length_of='name'),
        StrLenField("name", None, length_from=lambda pkt:pkt.name_len),
        FieldLenField("ver_len", None, fmt='B', length_of='version'),
        StrLenField("version", None, length_from=lambda pkt:pkt.ver_len)
    ]


class RioToDsTcp(Packet):
    name = 'RIO to DS TCP Packet'
    fields_desc = [
        PacketListField('tags', [], Tag)
    ]

bind_layers(TCP, DsToRioTcp, dport=1740)
