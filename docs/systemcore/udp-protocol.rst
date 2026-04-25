UDP Residual Protocol
=====================

NT4 over WebSocket is the primary communication channel, but UDP still exists alongside it. This protocol handles timesync, lightweight control, and fallback connectivity.

Overview
--------

The UDP residual protocol is **not part of the open-source allwpilib**. It lives in ``mrccomm``-specific code -- specifically ``wpinet/DsClient.cpp`` on the DS side and the ``ncl::RobotConnection`` class on the robot side.

Known Error Strings
^^^^^^^^^^^^^^^^^^^

From binary analysis of both DS and robot:

=============================================== =======================================
String                                          Context
=============================================== =======================================
``"only V2 is supported"``                      Protocol version check
``"Invalid UDP Packet at index %d"``            Packet validation failure
``"Received UDP error packet at index %d with code %d"`` Error response from robot
``"Unknown Tag %d"``                            Unrecognized tag in packet
``"Invalid header CRC"``                        Header CRC mismatch
``"Invalid payload CRC"``                       Payload CRC mismatch
``"Failed to parse TimesyncServer"``            Timesync data parse failure
``"Mismatched TimesyncClient send time"``      Timesync round-trip mismatch
``"Failed to encode timesync client data"``     Encoding failure
``"client data not masked"``                    Masking validation failure
``"Control data not updating"``                 Stale control data
``"Error sending/receiving UDP packet %d"``     Socket error
``"Failed to bind to sim UDP port"``            Simulation mode bind failure
=============================================== =======================================

V2 Packet Structure (Inferred)
-------------------------------

From the error strings and code references, the UDP V2 packet has this structure::

  +----------------------------------------------+
  | Header                                        |
  |  - Version (V2)                               |
  |  - Packet index                               |
  |  - Header CRC                                 |
  +----------------------------------------------+
  | Payload                                       |
  |  - Tag-Length-Value data                      |
  |  - Payload CRC                                |
  +----------------------------------------------+

Header
^^^^^^

======== ===========
Field    Description
======== ===========
Version  Must be V2 (``"only V2 is supported"``)
Packet index Sequential packet number for ordering/dedup
Header CRC CRC over the header bytes
======== ===========

Payload
^^^^^^^

============ ===========
Field        Description
============ ===========
Tags         TLV-encoded data (timesync, control, status)
Payload CRC  CRC over the payload bytes
============ ===========

Both header and payload have **separate CRC checks** -- if either fails, the packet is discarded.

Tag Format
^^^^^^^^^^

Tags follow a Type-Length-Value structure. Known tag types exist (the ``"Unknown Tag %d"`` error indicates numeric tag IDs), but the exact tag definitions have not been determined from static analysis alone.

Timesync
--------

The UDP timesync is a separate mechanism from the NT4 WebSocket RTT ping/pong.

DS -> Robot (Timesync Client)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Sends client timestamp in the UDP payload
- Uses a **masking mechanism** (the ``"client data not masked"`` error confirms this)

Robot -> DS (Timesync Server)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Responds with server timestamp
- DS validates: ``"Mismatched TimesyncClient send time"`` -- the echoed client timestamp must match what was sent
- This allows the DS to measure RTT and calculate clock offset independently of the WebSocket RTT channel

UDP vs NT4 Roles
-----------------

================== ============ ============
Function           UDP          NT4 WebSocket
================== ============ ============
Control data       Fallback     Primary (``/Dscomm/Control/ControlData``)
Joystick data      --            Primary (in ProtobufControlData)
Status data        --            Primary (``/Dscomm/Status/*``)
Console output     --            Primary (``/Dscomm/Console/*``)
Timesync           Yes (dedicated) Yes (RTT ping/pong)
Connection detect  Yes (keep-alive) Yes (WebSocket)
================== ============ ============

The NT4 status topics ``/Dscomm/Status/UdpConnAddr`` and ``/Dscomm/Status/UdpErrorCode`` indicate that the DS reports the state of its UDP connection to the robot via NT4 -- the UDP channel is monitored alongside the WebSocket.

Comparison to Pre-2027
----------------------

The pre-2027 protocol used **only** UDP and TCP:

================================= ============================================
Pre-2027                          2027
================================= ============================================
UDP port 1110 (DS -> Robot control) NT4 topic ``/Dscomm/Control/ControlData``
UDP port 1150 (Robot -> DS status)  NT4 topics ``/Dscomm/Status/*``
TCP port 1740 (joystick/match)    NT4 topics + Protobuf blobs
UDP timesync (implicit)           Dedicated UDP timesync + NT4 RTT WebSocket
================================= ============================================

The old ports (1110, 1150, 1740) only appear in the simulation module code -- they are not used for real robot communication in 2027.

Open Questions
---------------

1. **Exact V2 packet binary layout** -- header field sizes, CRC algorithm, tag ID assignments
2. **Masking mechanism** -- how the ``"client data not masked"`` check works
3. **Packet index usage** -- how duplicates and ordering are handled
4. **Fallback behavior** -- when does the DS switch from NT4 to UDP-only?
5. **Tag definitions** -- what data each UDP tag ID carries

Answering these requires either live traffic capture or deeper decompilation of ``DsClient.cpp`` / ``ncl::RobotConnection``.
