DS → Robot Topics
=================

The Driver Station is an NT4 client that publishes topics under ``/Dscomm/Control/`` for the robot to consume.

Control Topics
--------------

================================================== ====== ============================================= ======================================================
Topic                                              Type   Protobuf Type                                 Description
================================================== ====== ============================================= ======================================================
``/Dscomm/Control/ControlData``                    raw    ``mrc.proto.ProtobufControlData``              **Primary control message** -- robot state + joysticks + OpMode + GameData
``/Dscomm/Control/TeamNumber``                     integer                                               Team number
``/Dscomm/Control/MatchInfo``                       raw    ``mrc.proto.ProtobufMatchInfo``                Match name, number, type, replay
``/Dscomm/Control/RestartRobotCode``                boolean                                               Signal to restart user code
``/Dscomm/Control/RebootRobot``                     boolean                                               Signal to reboot the robot
``/Dscomm/Control/TimeZone``                        string                                                DS timezone name
``/Dscomm/Control/ResetEStop``                      boolean                                               Reset E-Stop latch
``/Dscomm/Control/JoystickDescriptors``              raw    ``mrc.proto.ProtobufJoystickDescriptors``      Connected joystick metadata
``/Dscomm/Control/DockedHeight``                    double                                                Charging station docked height
``/Dscomm/Control/RequireTeamNumberMatch``           boolean                                               Require team number verification
``/Dscomm/Control/UseWiFiStaticAddress``            boolean                                               Use static WiFi IP
================================================== ====== ============================================= ======================================================

OpMode Selection
-----------------

=========================================== ====== ============================================= ============================
Topic                                       Type   Protobuf Type                                 Description
=========================================== ====== ============================================= ============================
``/Dscomm/OpModeOptions``                   raw    ``mrc.proto.ProtobufAvailableOpModes``         Available operation modes
=========================================== ====== ============================================= ============================

The 2027 protocol replaces the fixed Teleop/Auto/Test mode bits with a flexible OpMode system. The DS publishes the list of available modes, and ``ControlData`` includes the currently selected mode.

Keyboard Topics (DS Internal)
------------------------------

These topics are used by the DS UI and are **never sent to the robot**:

=========================================== ====== ============================
Topic                                       Type   Description
=========================================== ====== ============================
``/Dscomm/Keyboard/EStopButtonPressed``      boolean E-Stop button state
``/Dscomm/Keyboard/AStopButtonPressed``      boolean **New in 2027** -- Auxiliary Stop
``/Dscomm/Keyboard/DisableButtonPressed``    boolean Disable button state
``/Dscomm/Keyboard/EnableButtonPressed``     boolean Enable button state
``/Dscomm/Keyboard/ReloadJoysticksButtonPressed`` boolean Reload joysticks trigger
``/Dscomm/Keyboard/ResetEstopButtonPressed`` boolean Reset E-Stop trigger
``/Dscomm/Keyboard/LostKeyboardPermissions`` boolean Keyboard permission lost
=========================================== ====== ============================

ControlData Details
-------------------

The ``ControlData`` topic is the single most important message. It replaces the old 8-byte UDP control packet with a Protobuf-encoded blob containing:

1. **ControlWord** (uint32) -- bitfield encoding robot control state
2. **MatchTime** (int32) -- match countdown in seconds
3. **Joysticks** (repeated ProtobufJoystickData) -- up to 6 joystick states
4. **CurrentOpMode** (ProtobufOpMode) -- selected operation mode
5. **GameData** (string) -- FMS game-specific message

ControlWord Bitfield (Inferred)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The exact bit assignments are not confirmed from static analysis alone. Based on the old protocol and DS behavior, the likely mapping is:

==== ====== =================== ===========================
Bit  Mask   Pre-2027 Equivalent Description
==== ====== =================== ===========================
0    0x01   Test                Test mode
1    0x02   Autonomous          Autonomous mode
2    0x04   Enabled             Robot enabled
3    0x08   FMS Attached        Connected to FMS
7    0x80   E-Stop              Emergency stop active
==== ====== =================== ===========================

2027 likely adds bits for A-Stop and other new features. Exact mapping needs live traffic capture to confirm.

Comparison to Pre-2027
^^^^^^^^^^^^^^^^^^^^^^

The old DS→Robot UDP packet was sent every 20ms to port 1110:

+--------------+--------+--------+
| Field        | Length | Type   |
+==============+========+========+
| Sequence Num | 2      | uint16 |
+--------------+--------+--------+
| Comm Version | 1      | uint8  |
+--------------+--------+--------+
| Control      | 1      | bitfield |
+--------------+--------+--------+
| Request      | 1      | bitfield |
+--------------+--------+--------+
| Alliance     | 1      | uint8  |
+--------------+--------+--------+
| Tags         | n      | TLV    |
+--------------+--------+--------+

In 2027, this is replaced by a single NT4 topic (``ControlData``) carrying a Protobuf blob. The NT4 server handles delivery -- no explicit sequence numbers or 20ms polling needed.

Robot-Side Namespace
---------------------

On the robot, MrcCommDaemon subscribes to ``/Dscomm/Control/*`` and republishes under ``/Netcomm/Control/*``. Robot code should use the ``/Netcomm/`` prefix:

===================================== ====================================
DS Publishes                          Robot Republishes
===================================== ====================================
``/Dscomm/Control/ControlData``       ``/Netcomm/Control/ControlData``
``/Dscomm/Control/MatchInfo``         ``/Netcomm/Control/MatchInfo``
``/Dscomm/Control/TimeZone``         ``/Netcomm/Control/TimeZone``
===================================== ====================================

DS-only topics (like ``TeamNumber``, ``RestartRobotCode``, ``RebootRobot``) are consumed by MrcCommDaemon directly and do not appear under ``/Netcomm/``.

Robot-Only Control Topics
^^^^^^^^^^^^^^^^^^^^^^^^^

=============================================== ====== ===========
Topic                                           Type   Description
=============================================== ====== ===========
``/Netcomm/Control/WatchdogActive``              boolean Watchdog keep-alive status
``/Netcomm/Control/GameSpecificMessage``         string  Game-specific message from FMS
``/Netcomm/Control/HasSetWallClock``              boolean Wall clock has been set from DS time
=============================================== ====== ===========
