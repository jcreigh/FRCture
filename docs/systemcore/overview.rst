Overview
========

The 2027 Protocol Overhaul
---------------------------

The 2027 FRC season introduces a **complete protocol break** from the pre-2027 DS <-> Robot communication. The old fixed-binary UDP packets are gone, replaced by **NT4 (NetworkTables 4) over WebSocket** with **MsgPack serialization**.

Pre-2027 Protocol (Legacy)
^^^^^^^^^^^^^^^^^^^^^^^^^^

==== ============ ===== =======================
Dir  Protocol     Port  Format
==== ============ ===== =======================
DS→R UDP          1110  Fixed binary with TLV tags
R→DS UDP          1150  Fixed binary with TLV tags
DS→R TCP          1740  Tagged binary (joystick descriptors, match info, game data)
DS <-> FMS UDP/TCP    Various Tagged binary
==== ============ ===== =======================

2027 Protocol
^^^^^^^^^^^^^

==== ============ ===== ==========================================
Dir  Protocol     Port  Format
==== ============ ===== ==========================================
DS <-> R WebSocket    5812  JSON text frames + MsgPack binary frames
DS <-> R UDP          TBD   Timesync + residual control (alongside NT4)
DS <-> FMS TCP (TLS)  Various Same tagged binary, with Kerberos/SPNEGO auth
==== ============ ===== ==========================================

The key insight: **all DS <-> Robot data is now exchanged as NT4 topics**. The DS is an NT4 client that publishes control topics and subscribes to status topics. The robot (SystemCore) runs an NT4 server.

Topic Namespace Split
----------------------

The most critical discovery from reverse engineering both sides: **the DS and robot use different topic prefixes for the same logical data**.

============================= ============================= ========
DS Side                       Robot Side                    Same?
============================= ============================= ========
``/Dscomm/Control/ControlData`` ``/Netcomm/Control/ControlData`` Yes
``/Dscomm/Control/MatchInfo``   ``/Netcomm/Control/MatchInfo``   Yes
``/Dscomm/Status/Battery``      ``/Netcomm/Status/Battery``      Yes
``/Dscomm/Status/CPU``          ``/Netcomm/Status/CPU``          Yes
``/Dscomm/Console/ConsoleLine`` ``/Netcomm/Console/ConsoleLine`` Yes
============================= ============================= ========

The ``MrcCommDaemon`` on the robot acts as a namespace bridge -- it subscribes to ``/Dscomm/`` topics from the DS and republishes them under ``/Netcomm/`` for local robot code, and vice versa. This was only discoverable by analyzing both the DS binary and the robot-side daemon.

Topics that only exist on one side:

- **DS-only**: ``TeamNumber``, ``RestartRobotCode``, ``RebootRobot``, ``ResetEStop``, ``TimeZone``, ``DockedHeight``, ``RequireTeamNumberMatch``, ``UseWiFiStaticAddress``, ``UdpConnAddr``, ``HasTcpConn``, ``RequestDisable``, ``StatusByte``
- **Robot-only**: ``WatchdogActive``, ``GameSpecificMessage``, ``HasSetWallClock``, ``/Netcomm/Modes/{Teleop,Auto,Test}OpModes``, ``/Netcomm/Reporting/*``

What's New in 2027
------------------

==================================== ============================================ =======================================================
Feature                              Topic                                        Description
==================================== ============================================ =======================================================
A-Stop                               ``/Dscomm/Keyboard/AStopButtonPressed``       New auxiliary stop button (separate from E-Stop)
Docked Height                        ``/Dscomm/Control/DockedHeight``             Docked/charging station height value
Team Number Match                    ``/Dscomm/Control/RequireTeamNumberMatch``   Stricter team verification
WiFi Static IP                       ``/Dscomm/Control/UseWiFiStaticAddress``      Static IP for WiFi connection
High Voltage Battery                 ``/Dscomm/Status/HighVoltageBattery``         HV battery monitoring
Multi-CAN Bus                        ``/Dscomm/Status/CanBusUtilizations``        Per-bus CAN utilization (SystemCore has 5 buses)
Resolved Teams                       ``/Dscomm/Status/ResolvedTeamNumbers``        mDNS-resolved team list
Op Modes                             ``/Dscomm/OpModeOptions``                    Available operation modes (replaces fixed Teleop/Auto/Test)
Watchdog                             ``/Dscomm/Status/WatchdogNotFed``            Robot watchdog state
Robot Code Uptime                    ``/Dscomm/Status/RobotCodeUpTime``            Time since user code started
Touchpad Data                        In ``ProtobufJoystickData``                   Touchpad/finger tracking for controllers
==================================== ============================================ =======================================================

Source Code
-----------

The DS networking core lives in ``mrccomm/allwpilib/``, a modified fork of the open-source `wpilibsuite/allwpilib <https://github.com/wpilibsuite/allwpilib>`_. Key paths::

  mrccomm/allwpilib/
  ├── wpinet/
  │   ├── DsClient.cpp              # DS-specific UDP/TCP control client
  │   ├── ParallelTcpConnector.cpp  # Concurrent TCP connection attempts
  │   ├── WebSocket.cpp             # WebSocket client implementation
  │   └── uv/Stream.cpp             # libuv stream wrapper
  ├── ntcore/
  │   ├── NetworkClient.cpp         # NT4 client
  │   ├── NetworkServer.cpp         # NT4 server
  │   ├── net/
  │   │   ├── ClientMessageQueue.hpp
  │   │   ├── WebSocketConnection.cpp
  │   │   ├── WireDecoder.cpp       # MsgPack decoder
  │   │   └── WireEncoder.cpp       # MsgPack encoder
  │   └── server/                   # Server-side handling
  └── datalog/
      ├── DataLog.cpp
      └── DataLogBackgroundWriter.cpp

**Note**: ``DsClient.cpp`` is **not** in the open-source allwpilib -- it's a mrccomm-specific addition handling the residual UDP timesync and control protocol.

The robot-side daemons (``RadioDaemon``, ``ExpansionHubDaemon``, ``PowerDistributionDaemon``) are open source at `github.com/wpilibsuite/scservices <https://github.com/wpilibsuite/scservices>`_. ``MrcCommDaemon`` itself is not open source.
