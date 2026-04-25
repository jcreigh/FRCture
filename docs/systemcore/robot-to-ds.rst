Robot → DS Topics
=================

The robot (SystemCore/MrcCommDaemon) publishes status, console output, and joystick output topics that the DS subscribes to.

Status Topics
-------------

================================================== ====== ============================================= ======================================================
Topic                                              Type   Protobuf Type                                 Description
================================================== ====== ============================================= ======================================================
``/Dscomm/Status/UdpConnAddr``                     string                                                UDP connection address
``/Dscomm/Status/HasTcpConn``                      boolean                                               TCP (NT4 WebSocket) connection established
``/Dscomm/Status/HasUserCode``                      boolean                                               User robot code is deployed
``/Dscomm/Status/HasUserCodeReady``                boolean                                               User code is ready to run
``/Dscomm/Status/RequestDisable``                  boolean                                               Robot requests DS to disable it
``/Dscomm/Status/StatusByte``                      integer                                               Robot status bitfield
``/Dscomm/Status/CurrentOpModeTrace``               string                                                Human-readable current OpMode name
``/Dscomm/Status/AveragePacketTime``                double                                                Average packet round-trip time (ms)
``/Dscomm/Status/LostPackets``                      integer                                               Number of lost packets
``/Dscomm/Status/LoopDelta``                        double                                                Loop timing delta (ms)
``/Dscomm/Status/LoopTime``                         double                                                Robot loop time (ms)
``/Dscomm/Status/PacketTime``                       double                                                Most recent packet time (ms)
``/Dscomm/Status/IsSimulation``                    boolean                                               Running in simulation mode
``/Dscomm/Status/IsUsb``                            boolean                                               Connected via USB (not WiFi/Ethernet)
``/Dscomm/Status/UdpErrorCode``                    integer                                               UDP protocol error code
``/Dscomm/Status/Rtt``                              double                                                Measured round-trip time (ms)
``/Dscomm/Status/FmsTimes``                         raw                                                   FMS timing data (format unknown)
``/Dscomm/Status/JoystickOutputs``                 raw    ``mrc.proto.ProtobufJoystickOutputs``          Rumble/LED outputs to joysticks
``/Dscomm/Status/CPU``                             double                                                CPU utilization percentage
``/Dscomm/Status/Battery``                          double                                                Battery voltage
``/Dscomm/Status/HighVoltageBattery``               double                                                **New in 2027** -- HV battery reading
``/Dscomm/Status/FreeMemory``                      double                                                Free RAM (bytes)
``/Dscomm/Status/FreeStorage``                     double                                                Free disk space (bytes)
``/Dscomm/Status/RobotUpTime``                     integer                                               Time since robot boot (seconds)
``/Dscomm/Status/RobotCodeUpTime``                 integer                                               Time since user code started (seconds)
``/Dscomm/Status/WatchdogNotFed``                  boolean                                               **New in 2027** -- watchdog not being fed
``/Dscomm/Status/ResolvedTeamNumbers``             raw    ``mrc.proto.ProtobufResolvedTeamNumberSet``    mDNS-resolved team list
``/Dscomm/Status/CanBusUtilizations``              double[]                                              **New in 2027** -- per-bus CAN utilization
================================================== ====== ============================================= ======================================================

Console Topics
--------------

================================================== ====== ============================================= ============================
Topic                                              Type   Protobuf Type                                 Description
================================================== ====== ============================================= ============================
``/Dscomm/Console/ConsoleLine``                     raw    ``mrc.proto.ProtobufConsoleLineTimestamp``      Standard output line
``/Dscomm/Console/ErrorInfo``                       raw    ``mrc.proto.ProtobufErrorInfoTimestamp``        Error with details and call stack
``/Dscomm/Console/ProgramCrashInfo``                raw    ``mrc.proto.ProtobufProgramCrashInfoTimestamp`` User code crash report
================================================== ====== ============================================= ============================

Alert Topics
-------------

=========================================== ====== ===========
Topic                                       Type   Description
=========================================== ====== ===========
``/Dscomm/Alerts/``                         varies Alert notifications from robot to DS
=========================================== ====== ===========

Robot-Side Namespace
--------------------

MrcCommDaemon publishes under ``/Netcomm/`` and the DS subscribes under ``/Dscomm/``:

================================== ===================================
Robot Publishes                    DS Subscribes
================================== ===================================
``/Netcomm/Status/Battery``       ``/Dscomm/Status/Battery``
``/Netcomm/Status/CPU``           ``/Dscomm/Status/CPU``
``/Netcomm/Console/ConsoleLine``  ``/Dscomm/Console/ConsoleLine``
``/Netcomm/Outputs/JoystickOutputs`` ``/Dscomm/Status/JoystickOutputs``
================================== ===================================

Robot-Only Status Topics
^^^^^^^^^^^^^^^^^^^^^^^^

=============================================== ====== ============================================= ============================
Topic                                           Type   Protobuf Type                                 Description
=============================================== ====== ============================================= ============================
``/Netcomm/Modes/TeleopOpModes``                 raw    ``mrc.proto.ProtobufAvailableOpModes``         Available teleop modes
``/Netcomm/Modes/AutoOpModes``                   raw    ``mrc.proto.ProtobufAvailableOpModes``         Available autonomous modes
``/Netcomm/Modes/TestOpModes``                   raw    ``mrc.proto.ProtobufAvailableOpModes``         Available test modes
=============================================== ====== ============================================= ============================

Robot-Only Reporting Topics
^^^^^^^^^^^^^^^^^^^^^^^^^^^

=============================================== ====== ===========
Topic                                           Type   Description
=============================================== ====== ===========
``/Netcomm/Reporting/RequestVersions``           --     Request device firmware versions
``/Netcomm/Reporting/LibVersion``                --     FRC library version
=============================================== ====== ===========

Comparison to Pre-2027
----------------------

The old Robot→DS UDP packet was sent to port 1150:

+--------------+--------+---------+
| Field        | Length | Type    |
+==============+========+=========+
| Sequence Num | 2      | uint16  |
+--------------+--------+---------+
| Status       | 1      | bitfield|
+--------------+--------+---------+
| Trace        | 1      | uint8   |
+--------------+--------+---------+
| Battery      | 2      | uint16  |
+--------------+--------+---------+
| Tags         | n      | TLV     |
+--------------+--------+---------+

In 2027, each piece of data is a separate NT4 topic. The DS subscribes to the ones it needs. This is more flexible -- the robot can add new telemetry topics without the DS needing a parser update.
