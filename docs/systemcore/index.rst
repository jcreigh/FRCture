SystemCore / 2027 Protocol
==========================

The 2027 FRC season introduces a complete protocol overhaul. The old fixed-binary UDP packets (documented in :doc:`/driverstation/index`) are replaced by **NT4 (NetworkTables 4) over WebSocket** with **MsgPack serialization**.

.. warning::
   This documentation is derived from static binary analysis and has not been validated against live traffic. Some details (particularly UDP V2 packet layout and ControlWord bit assignments) are inferred and may be incorrect.

.. toctree::
   :maxdepth: 2

   overview
   nt4-wire-protocol
   ds-to-robot
   robot-to-ds
   protobuf-schemas
   udp-protocol
   mdns-discovery
   fms-communication
   systemcore-architecture
