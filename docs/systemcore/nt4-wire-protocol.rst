NT4 Wire Protocol
==================

All DS <-> Robot data exchange happens over NT4, which runs on WebSocket. This document covers the exact binary format.

Connection
----------

The DS connects to the robot's NT4 server at::

  ws://<host>:5812/nt/<clientId>

The path **must** match ``/nt/<clientId>`` -- the server validates this.

WebSocket Subprotocols
^^^^^^^^^^^^^^^^^^^^^^

The client sends two subprotocol options during the WebSocket handshake:

=============================================== ========================================
Subprotocol                                     Purpose
=============================================== ========================================
``v4.1.networktables.first.wpi.edu``            **Main data channel** -- carries all NT4 topic data
``rtt.networktables.first.wpi.edu``             **RTT measurement channel** -- dedicated round-trip-time pings only
=============================================== ========================================

If the server doesn't recognize the protocol version, it responds with ``"unsupported protocol version"`` and disconnects.

The DS opens **two WebSocket connections**:

1. **Data WS** (``v4.1.networktables.first.wpi.edu``) -- carries publish/subscribe/topic data
2. **RTT WS** (``rtt.networktables.first.wpi.edu``) -- sends RTT pings every 250ms, no topic data

Frame Types
-----------

==== ===== = =======================================
Code Type  Purpose
==== ===== = =======================================
0x1  Text  JSON control messages (publish, subscribe, announce, etc.)
0x2  Binary MsgPack-encoded topic value updates
==== ===== = =======================================

Text Frame Format (JSON)
------------------------

Text frames contain a JSON array of method call objects::

  [
    {"method": "<method_name>", "params": {<params>}},
    {"method": "<method_name>", "params": {<params>}}
  ]

Multiple methods can be batched in a single text frame.

Client → Server Methods
^^^^^^^^^^^^^^^^^^^^^^^

``publish`` -- Publish a new topic::

  {
    "method": "publish",
    "params": {
      "name": "/Dscomm/Control/TeamNumber",
      "type": "integer",
      "pubuid": 42,
      "properties": {}
    }
  }

====== ====== ===========
Param  Type   Description
====== ====== ===========
name   string Full topic path
type   string NT4 type string (e.g. ``"double"``, ``"raw"``, ``"mrc.proto.ProtobufControlData"``)
pubuid int    Unique publisher ID (client-assigned)
properties object Topic properties (e.g. ``{"persistent": true}``)
====== ====== ===========

``unpublish`` -- Stop publishing::

  {"method": "unpublish", "params": {"pubuid": 42}}

``subscribe`` -- Subscribe to topics::

  {
    "method": "subscribe",
    "params": {
      "subuid": 7,
      "topics": ["/Dscomm/Status/Battery", "/Dscomm/Status/CPU"],
      "options": {"periodic": 0.02, "prefix": false}
    }
  }

====== ====== ===========
Param  Type   Description
====== ====== ===========
subuid int    Unique subscriber ID (client-assigned)
topics string[] Topic paths or prefixes (if ``prefix: true``)
options object See below
====== ====== ===========

Subscribe Options:

========= ====== ======= ===========
Key       Type   Default Description
========= ====== ======= ===========
periodic  number --       Minimum publish interval in seconds
all       bool   false   Subscribe to all topics
topicsonly bool  false   Only receive announcements, no values
prefix    bool   false   ``topics`` array contains prefixes, match all subtopics
========= ====== ======= ===========

``unsubscribe`` -- Unsubscribe::

  {"method": "unsubscribe", "params": {"subuid": 7}}

``setproperties`` -- Update topic properties::

  {
    "method": "setproperties",
    "params": {
      "name": "/Dscomm/Control/TeamNumber",
      "update": {"persistent": true}
    }
  }

Server → Client Methods
^^^^^^^^^^^^^^^^^^^^^^^

``announce`` -- New topic available::

  {
    "method": "announce",
    "params": {
      "name": "/Dscomm/Status/Battery",
      "id": 15,
      "type": "double",
      "properties": {},
      "pubuid": 3
    }
  }

========= ====== ===========
Param     Type   Description
========= ====== ===========
name      string Full topic path
id        int    **Server-assigned topic ID** -- used in binary frames
type      string NT4 type string
properties object Topic properties
pubuid    int?   Publisher ID (optional, absent if no active publisher)
========= ====== ===========

``unannounce`` -- Topic removed::

  {"method": "unannounce", "params": {"name": "/Dscomm/Status/Battery", "id": 15}}

``properties`` -- Properties updated::

  {
    "method": "properties",
    "params": {
      "name": "/Dscomm/Status/Battery",
      "update": {"persistent": true},
      "ack": true
    }
  }

Binary Frame Format (MsgPack)
-----------------------------

Binary frames carry topic value updates using MsgPack encoding. Each value is a 4-element MsgPack array::

  [topic_id, timestamp, type_code, value]

========= ====== ===========
Element   Type   Description
========= ====== ===========
topic_id  int    Server-assigned topic ID from ``announce``
timestamp int64  Microseconds since epoch. **0 = use server's current time**
type_code uint8  See type codes table below
value     varies MsgPack-encoded value, format depends on type_code
========= ====== ===========

Multiple values can be packed into a single binary frame.

Type Codes
^^^^^^^^^^

==== ====== =============================== ==========================================
Code Type   MsgPack Encoding                 Example
==== ====== =============================== ==========================================
0    Boolean mpack_write_bool                ``[5, 1700000000000000, 0, true]``
1    Double  mpack_write_double (64-bit)     ``[10, 1700000000000000, 1, 12.6]``
2    Integer mpack_write_int (int64)         ``[3, 1700000000000000, 2, 42]``
3    Float   mpack_write_float (32-bit)       
4    String  mpack_write_str                 ``[12, 1700000000000000, 4, "hello"]``
5    Raw/Binary mpack_write_bin              ``[3, 1700000000000000, 5, <bytes>]``
16   Bool Array mpack_start_array + N × bool  ``[20, 0, 16, [true, false, true]]``
17   Double Array mpack_start_array + N × dbl ``[7, 0, 17, [1.1, 2.2, 3.3]]``
18   Int Array mpack_start_array + N × int64  ``[9, 0, 18, [1, 2, 3]]``
19   Float Array mpack_start_array + N × flt  
20   String Array mpack_start_array + N × str 
==== ====== =============================== ==========================================

**Note on type code 5 (Raw)**: Used for two purposes -- NT_RPC (remote procedure calls) and NT_RAW (arbitrary binary data like Protobuf-encoded structs). All complex Dscomm topics (ControlData, JoystickData, MatchInfo, etc.) are encoded as type 5 with Protobuf content.

Timesync (RTT Ping/Pong)
------------------------

NT4 includes a built-in round-trip time measurement protocol.

Ping (Client → Server)::

  MsgPack: [-1, 0, 2, <client_time_us>]

- ``topic_id = -1`` (special value for RTT)
- ``timestamp = 0``
- ``type_code = 2`` (integer)
- ``value = client's current time in microseconds``

Pong (Server → Client)::

  MsgPack: [-1, <server_time_us>, <original_type_code>, <original_value>]

The server echoes the original ``type_code`` and ``value`` back, with the server's timestamp filled in.

Client Calculation::

  rtt = now - original_client_time
  rtt2 = rtt / 2
  serverTimeOffset = server_time + rtt2 - now

The client keeps the **minimum observed RTT/2**. The offset is set on the first measurement and only updated when a smaller RTT is observed.

Timing Constants
^^^^^^^^^^^^^^^^

========================== ======= ===========
Constant                   Value   Description
========================== ======= ===========
RTT_PERIOD_MS_V41          250ms   RTT ping interval on dedicated RTT WebSocket
RTT_PERIOD_MS_V40          1000ms  RTT ping interval on shared data WebSocket (v4.0 only)
TIMEOUT_MS_V41             1000ms  Connection timeout for v4.1
TIMEOUT_MS_V40             5000ms  Connection timeout for v4.0
kRttIntervalMs             3000ms  Full RTT measurement interval
NetworkPing::kPingIntervalMs 200ms   Network-level ping interval
NetworkPing::kPingTimeoutMs  1000ms  Network ping timeout
========================== ======= ===========

Connection Lifecycle
--------------------

1. **WebSocket Connect** -- Client opens WS to ``ws://<host>:5812/nt/<clientId>`` with subprotocol ``v4.1.networktables.first.wpi.edu``
2. **Server Announces** -- Server sends ``announce`` messages for all existing topics
3. **Client Subscribes** -- Client sends ``subscribe`` for topics it wants to receive
4. **Client Publishes** -- Client sends ``publish`` for topics it wants to send
5. **Data Exchange** -- Binary frames carry value updates; text frames carry control messages
6. **Disconnect** -- WebSocket closes; all subscriptions and publications are cleaned up

**Important**: The client must wait for ``announce`` messages before sending binary value updates for a topic -- the topic ID is server-assigned and only known after announcement.

Persistent Storage
------------------

The NT4 server stores persistent topic data in ``/nt/persistent.json``. Only topics with the ``persistent: true`` property are saved.
