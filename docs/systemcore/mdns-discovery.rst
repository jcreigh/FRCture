mDNS Discovery
===============

The DS and robot find each other on the network using mDNS/DNS-SD (Multicast DNS / DNS Service Discovery).

Service Types
-------------

========================= ======================================= ===========================
Service Type              Purpose                                 Used By
========================= ======================================= ===========================
``_SystemCore._tcp``      Primary SystemCore discovery             2027 DS
``_SystemCoreConsole._tcp`` Console/terminal service               Web terminal
``_networktables._tcp``   NT4 server discovery                    Any NT4 client
========================= ======================================= ===========================

.. note::
   The beta image also advertises ``_ni._tcp`` and ``_ni-rt._tcp`` for roboRIO backward compatibility, and uses the ``roboRIO-{team}-FRC`` hostname pattern. These are confirmed to be **removed in the full release**.

Team Number Resolution
----------------------

The DS resolves the robot's address using the team number:

1. DS constructs the expected hostname: ``SystemCore-{team}-FIRST``
2. DS queries mDNS for ``_SystemCore._tcp``
3. DS matches the resolved host against the expected team number
4. DS connects to NT4 server on port 5812

The topic ``/Dscomm/Status/ResolvedTeamNumbers`` contains the full list of mDNS-resolved teams that the DS found on the network, encoded as ``mrc.proto.ProtobufResolvedTeamNumberSet``.

Team Number Mismatch
^^^^^^^^^^^^^^^^^^^^

The topic ``/Dscomm/Control/RequireTeamNumberMatch`` controls whether the DS strictly verifies the team number. When enabled, the DS will refuse to connect to a robot that doesn't match the configured team number.

Network Responder
-----------------

The SystemCore also runs a ``networkresponder`` binary that provides a separate discovery protocol:

=========== =====================================================
API Version Behavior
=========== =====================================================
V1         Binds to a **single IP address** -- for directed discovery
V2         Binds to **all interfaces** -- for broadcast discovery
=========== =====================================================

This is the Limelight auto-configuration protocol, separate from mDNS.

Network Interfaces
------------------

The SystemCore has multiple network interfaces, and mDNS operates on all of them:

========== =================== ================ =====
Interface  Protocol            IP Range         mDNS?
========== =================== ================ =====
``usb0``   ECM (macOS/Linux)   ``172.27.{0-15}.x`` Yes
``usb1``   RNDIS (Windows)     ``172.26.{0-15}.x`` Yes
``wlan0``  WiFi AP             ``172.30.0.x``    Yes
``eth0``   Ethernet            DHCP client      Yes
========== =================== ================ =====

The DS can discover the robot over any of these paths simultaneously.

DHCP Subnet Mapping
^^^^^^^^^^^^^^^^^^^

The USB DHCP ranges are team-number-aware -- 16 subnets of 11 addresses each:

=========== ==================== ===============
Interface  Subnet Range          Team Mapping
=========== ==================== ===============
``usb0``   ``172.27.{0-15}.21-31`` Team number determines which /24 subnet
``usb1``   ``172.26.{0-15}.21-31`` Same mapping, different /16
=========== ==================== ===============

Each subnet hands out addresses ``.21`` through ``.31`` (11 per subnet) with a 1-hour DHCP lease. No gateway or DNS is advertised -- this is a point-to-point link.

IRQ Affinity
------------

The SystemCore pins eth0's interrupt to CPU core 2 via ``smp_affinity``::

  echo 2 > "/proc/irq/$ETH/smp_affinity"

On the PREEMPT_RT kernel, this ensures deterministic latency for Ethernet interrupts -- important when the robot is on a competition field network with the FMS.
