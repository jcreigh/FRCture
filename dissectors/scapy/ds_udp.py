from scapy.all import conf, orb, bind_layers, UDP, Packet, Field, FlagsField, \
                      ByteEnumField, ShortField, LenField, ByteField, \
                      XByteField, FieldLenField, StrLenField, IntField, \
                      PacketListField, SignedShortField, FieldListField, \
                      SignedByteField, IEEEFloatField, raw


# bolb


class Tag(Packet):
    @classmethod
    def dispatch_hook(cls, s=None, *_args, **_kwargs):
        if s is None:
            return conf.raw_layer
        tag_id = orb(s[1])

        if tag_id == 0x07:
            return Countdown
        elif tag_id == 0x0c:
            return Joystick
        elif tag_id == 0x0f:
            return Date
        elif tag_id == 0x10:
            return Timezone

        return UnknownTag

    def guess_payload_class(self, payload):
        return conf.padding_layer

    def post_build(self, p, pay):
        if self.len is None:
            p = bytes([len(p) - 1]) + p[1:]
        return p + pay


class UnknownTag(Tag):
    fields_desc = [
        LenField('len', None, fmt='B'),
        XByteField('tag', None),
        StrLenField('data', None, length_from=lambda pkt:pkt.len - 1)
    ]


class ButtonsField(Field):
    __slots__ = ['count_from']
    islist = 1

    def __init__(self, name, default, count_from=None):  # noqa: E501
        Field.__init__(self, name, default)
        self.count_from = count_from

    def getfield(self, pkt, s):
        btn_count = self.count_from(pkt)
        len_pkt = ((btn_count - 1) // 8 + 1) if btn_count else 0
        return s[len_pkt:], self.m2i(pkt, s[:len_pkt])

    def addfield(self, pkt, s, val):
        return s + self.i2m(pkt, val)

    def m2i(self, pkt, x):
        buttons = []
        btn_count = self.count_from(pkt)
        byte_len = ((btn_count - 1) // 8 + 1) if btn_count else 0
        for i in range(0, btn_count):
            buttons.append(bool(x[byte_len - 1 - i // 8] >> (i % 8) & 1))
        return buttons

    def i2m(self, pkt, x):
        byte_len = ((len(x) - 1) // 8 + 1) if len(x) else 0
        out = [0] * byte_len
        for i in range(0, len(x)):
            out[byte_len - 1 - i // 8] |= int(x[i]) << (i % 8)
        return raw(out)

    def i2repr(self, pkt, val):
        if val is None:
            return repr(val)
        return str.join('', ['0' if not x else '1' for x in val])

    def i2count(self, pkt, val):
        return len(val)

    def i2len(self, pkt, val):
        btn_count = len(val)
        return (btn_count // 8 + 1) if btn_count else 0


class Countdown(Tag):  # 0x07
    fields_desc = [
        LenField('len', None, fmt='B'),
        XByteField('tag', None),
        IEEEFloatField('countdown', 0.0)
    ]


class Joystick(Tag):  # 0x0c

    fields_desc = [
        LenField('len', None, fmt='B'),
        XByteField('tag', 0x0c),

        FieldLenField('axis_count', None, fmt='B', count_of='axes'),
        FieldListField('axes', [], SignedByteField('', None), count_from=lambda pkt:pkt.axis_count),
        FieldLenField('button_count', None, fmt='B', count_of='buttons'),
        ButtonsField('buttons', [], count_from=lambda pkt:pkt.button_count),
        FieldLenField('pov_count', None, fmt='B', length_of='povs'),
        FieldListField('povs', [], SignedShortField('', None), count_from=lambda pkt:pkt.pov_count)
    ]


class Date(Tag):  # 0x0f
    fields_desc = [
        LenField('len', None, fmt='B'),
        XByteField('tag', None),
        IntField('microseconds', None),
        ByteField('second', None),
        ByteField('minute', None),
        ByteField('hour', None),
        ByteField('day', None),
        ByteField('month', None),
        ByteField('year', None),
    ]


class Timezone(Tag):  # 0x10
    fields_desc = [
        LenField('len', None, fmt='B'),
        XByteField('tag', None),
        StrLenField('tz', None, length_from=lambda pkt:pkt.len - 1)
    ]


class DsToRioUdp(Packet):
    name = 'DS to RIO UDP Packet'
    fields_desc = [
        ShortField('seq_num', None),
        ByteField('comm_ver', 0),

        FlagsField('control', 0, 8, ['test', 'auton', 'enabled',
                                     'fms_connected', 'reserved4',
                                     'reserved5', 'reserved6', 'estop']),

        FlagsField('request', 0, 8, ['reserved0', 'reserved1',
                                     'restart_code', 'reboot_rio',
                                     'reserved4', 'reserved5', 'reserved6',
                                     'reserved7']),

        ByteEnumField('alliance', None, ['red_0', 'red_1', 'red_2',
                                         'blue_0', 'blue_1', 'blue_2']),

        PacketListField('tags', [], Tag)
    ]


bind_layers(UDP, DsToRioUdp, dport=1110)
bind_layers(UDP, DsToRioUdp, dport=1115)
