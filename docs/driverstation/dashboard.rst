Dashboard
#########

*TODO: Based on LabVIEW Dashboard code. Need to actually listen and see if they are exact copies*

The Driver Station uses a variety of ports to communicate with any Dashboard software.
Either connects to these ports localhost or to them on the specified Remote Dashboard IP.

.. _dashboard_control:

Control (UDP port 1164)
-----------------------

Simply a copy of the packets sent to the RoboRIO

.. _dashboard_status:

Status (UDP port 1166)
----------------------

Simply a copy of the packets sent from the RoboRIO

.. _dashboard_tcp:

TCP (port 1741)
---------------

**Might have the other tags, but at least have the `Robot IP` and `DB Mode` tags special**

.. table::
   :widths: auto

   +-------+--------+--------+------------------------------------+
   | Field | Length | Type   | Comment                            |
   +=======+========+========+====================================+
   | Size  | 2      | uint16 | Including ID                       |
   +-------+--------+--------+------------------------------------+
   | ID    | 1      | uint8  | See table below (only of Size > 0) |
   +-------+--------+--------+------------------------------------+
   | Tags  | n      |        | Depends on tag type                |
   +-------+--------+--------+------------------------------------+

.. table::
   :widths: auto

   +--------+--------------------------------------------------+
   | ID     | Tag                                              |
   +========+==================================================+
   | `0x00` | :ref:`Error Messages <dashboard_error_messages>` |
   +--------+--------------------------------------------------+
   | `0x04` | :ref:`Disable Counts <dashboard_disable_counts>` |
   +--------+--------------------------------------------------+
   | `0x05` | :ref:`Rail Faults <dashboard_rail_faults>`       |
   +--------+--------------------------------------------------+
   | `0x07` | :ref:`Match Info <dashboard_match_info>`         |
   +--------+--------------------------------------------------+
   | `0x08` | :ref:`Robot IP <dashboard_robot_ip>`             |
   +--------+--------------------------------------------------+
   | `0x09` | :ref:`DB Mode <dashboard_db_mode>`               |
   +--------+--------------------------------------------------+

.. _dashboard_error_messages:

Error Messages (``0x00``)
^^^^^^^^^^^^^^^^^^^^^^^^^

.. table::
   :widths: auto

   +---------+--------+--------+---------+
   | Field   | Length | Type   | Comment |
   +=========+========+========+=========+
   | Message | n      | string |         |
   +---------+--------+--------+---------+

.. _dashboard_disable_counts:

Disable Counts (``0x04``)
^^^^^^^^^^^^^^^^^^^^^^^^^

.. table::
   :widths: auto

   +-------+--------+--------+---------+
   | Field | Length | Type   | Comment |
   +=======+========+========+=========+
   | Comms | 2      | uint16 |         |
   +-------+--------+--------+---------+
   | 12V   | 2      | uint16 |         |
   +-------+--------+--------+---------+

.. _dashboard_rail_faults:

Rail Faults (``0x05``)
^^^^^^^^^^^^^^^^^^^^^^

.. table::
   :widths: auto

   +-------+--------+--------+---------+
   | Field | Length | Type   | Comment |
   +=======+========+========+=========+
   | 6V    | 2      | uint16 |         |
   +-------+--------+--------+---------+
   | 5V    | 2      | uint16 |         |
   +-------+--------+--------+---------+
   | 3.3V  | 2      | uint16 |         |
   +-------+--------+--------+---------+

.. _dashboard_match_info:

Match Info (``0x07``)
^^^^^^^^^^^^^^^^^^^^^

.. table::
   :widths: auto

   +---------------+--------+--------+------------------------------------------------------------+
   | Field         | Length | Type   | Comment                                                    |
   +===============+========+========+============================================================+
   | Competition   | 1 + n  | string |                                                            |
   +---------------+--------+--------+------------------------------------------------------------+
   | Match Type    | 1      |        | 0: "None", 1: Practice, 2: Qualifications, 3: Eliminations |
   +---------------+--------+--------+------------------------------------------------------------+
   | Match Number  | 2      | uint16 |                                                            |
   +---------------+--------+--------+------------------------------------------------------------+
   | Replay Number | 1      | uint8  |                                                            |
   +---------------+--------+--------+------------------------------------------------------------+

.. _dashboard_robot_ip:

Robot IP (``0x08``)
^^^^^^^^^^^^^^^^^^^

.. table::
   :widths: auto

   +-------+--------+--------------+---------+
   | Field | Length | Type         | Comment |
   +=======+========+==============+=========+
   | IP    | 4      | IPv4 Address |         |
   +-------+--------+--------------+---------+

.. _dashboard_db_mode:

DB Mode (``0x09``)
^^^^^^^^^^^^^^^^^^

.. table::
   :widths: auto

   +-------+--------+------------------------------+---------+
   | Field | Length | Type                         | Comment |
   +=======+========+==============================+=========+
   | Mode  | 1      | :ref:`Mode <dashboard_mode>` |         |
   +-------+--------+------------------------------+---------+

.. _dashboard_mode:

Mode
""""

.. table::
   :widths: auto

   +-----------+--------------+---------+
   | Field     | Mask         | Comment |
   +===========+==============+=========+
   | Docked    | ``.....x..`` |         |
   +-----------+--------------+---------+
   | Simulated | ``.......x`` |         |
   +-----------+--------------+---------+

.. _dashboard_tcp_listening:

TCP Listening (port 1742)
-------------------------

The Driver Station listens on TCP port 1742 and sends the following JSON:

``{"robotIP":0,"dashboardiP":3232235818,"FMS Connected":false,"Robot Connected":false,"RobotCode":false}``

This is sent whenever one of the values changes.
