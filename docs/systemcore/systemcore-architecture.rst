SystemCore Architecture
========================

The SystemCore is the robot-side counterpart to the DS. It runs on a Raspberry Pi Compute Module 5 with a custom Limelight OS image (Buildroot, PREEMPT_RT kernel 6.6.64-rt47).

Network Interfaces
------------------

========== ======================= ================ =======
Interface  Purpose                IP Range         mDNS?
========== ======================= ================ =======
``usb0``   ECM USB network to DS  ``172.27.{0-15}.x`` Yes
``usb1``   RNDIS USB network to DS ``172.26.{0-15}.x`` Yes
``wlan0``  WiFi access point      ``172.30.0.1/24`` Yes
``eth0``   Ethernet               DHCP client      Yes
``can_s0``-``can_s4`` CAN FD buses N/A              N/A
========== ======================= ================ =======

USB gadget mode provides both ECM and RNDIS simultaneously over a single USB cable -- ECM for macOS/Linux, RNDIS for Windows.

WiFi Access Point
^^^^^^^^^^^^^^^^^

========= ====================
Setting   Value
========= ====================
SSID      ``SYSTEMCORE``
Password  ``PASSWORD``
Mode      5GHz 802.11ac
Security  WPA2-PSK (CCMP)
DHCP      ``172.30.0.21-31``
Max clients 10
========= ====================

CAN Bus Configuration
--------------------

The SystemCore has **5 CAN FD buses** via MCP2518FD controllers on SPI:

======== ====== =========== ======= ====== =====================================
CAN Bus  SPI    CS Pin       INT Pin Osc    Device Tree Overlay
======== ====== =========== ======= ====== =====================================
``can_s0`` SPI2  CS0=GPIO0   GPIO22  40MHz ``sc-mcp2518-can0-spi2``
``can_s1`` SPI2  CS1=GPIO24  GPIO26  40MHz ``sc-mcp2518-can1-spi2``
``can_s2`` SPI3  CS0=GPIO27  GPIO9   40MHz ``sc-mcp2518-can2-spi3`` (BETA)
``can_s3`` SPI1  CS0=GPIO25  GPIO17  40MHz ``sc-mcp2518-can3-spi1-beta``
``can_s4`` SPI1  CS1=GPIO18  GPIO8   40MHz ``sc-mcp2518-can4-spi1-beta``
======== ====== =========== ======= ====== =====================================

All buses run at 1 Mbps CAN FD with ``txqueuelen=1000``. Per-bus utilization is published to the DS via the ``/Dscomm/Status/CanBusUtilizations`` topic.

Protocol Services
-----------------

===================== ======================================= ======================================================================
Service               Binary                                  Description
===================== ======================================= ======================================================================
``mrccomm.service``   ``/usr/bin/MrcCommDaemon`` (4.5MB)       NT4 server (port 5812) + UDP control protocol + ``/Dscomm/`` <-> ``/Netcomm/`` namespace bridge
``robot.service``     ``/home/systemcore/robotCommand``        User code runner (waits for CAN interfaces)
``radiodaemon.service`` ``/usr/bin/RadioDaemon`` (4.1MB)     NT4 client for FRC field radio link quality. **Stub -- not yet implemented.** `Open source <https://github.com/wpilibsuite/scservices>`__
``expansionhubdaemon.service`` ``/usr/bin/ExpansionHubDaemon`` (4.1MB) REV Expansion Hub (RHSP). `Open source <https://github.com/wpilibsuite/scservices>`__
``powerdistribution.service`` ``/usr/bin/PowerDistributionDaemon`` (3.9MB) PDH/PDP monitoring, publishes ``/pd/`` NT4 topics. `Open source <https://github.com/wpilibsuite/scservices>`__
===================== ======================================= ======================================================================

Other services on the SystemCore (CAN bus setup, DHCP, WiFi AP, hardware monitoring, package management, OTA updates) handle system administration and are not directly involved in the DS <-> Robot protocol.

``can_heartbeat`` Kernel Module
-------------------------------

The ``can_heartbeat`` module is a custom out-of-tree kernel module that bridges CAN bus data to sysfs. ``MrcCommDaemon`` reads from:

- ``/sys/kernel/can_heartbeat/controldata`` -- CAN heartbeat control data
- ``/sys/kernel/can_heartbeat/matchinfo`` -- CAN heartbeat match info
- ``/sys/kernel/can_heartbeat/enabledro`` -- robot enabled state (read by ``iodaemon`` for the status LEDs)

This is how MrcCommDaemon obtains CTRE device status and CAN bus health information for DS communication.

mDNS Services
-------------

========================= =======================================
Service                   Purpose
========================= =======================================
``_SystemCore._tcp``      Primary SystemCore discovery
``_SystemCoreConsole._tcp`` Console/terminal service
``_networktables._tcp``   NT4 server discovery
========================= =======================================

.. note::
   The beta image also advertises ``_ni._tcp`` and ``_ni-rt._tcp`` for roboRIO backward compatibility, and uses the ``roboRIO-{team}-FRC`` hostname pattern. These are confirmed to be **removed in the full release**.
