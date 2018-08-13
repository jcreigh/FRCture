Dashboard
#########

*TODO: Based on LabVIEW Dashboard code. Need to actually listen and see if they are exact copies*

The Driver Station uses a variety of ports to communicate with any Dashboard software.
Either connects to these ports localhost or to them on the specified Remote Dashboard IP.

Control (UDP port 1164)
-----------------------

Simply a copy of the packets sent to the RoboRIO

Status (UDP port 1166)
----------------------

Simply a copy of the packets sent from the RoboRIO

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

   +--------+-------------------+
   | ID     | Tag               |
   +========+===================+
   | `0x00` | `Error Messages`_ |
   +--------+-------------------+
   | `0x04` | `Disable Counts`_ |
   +--------+-------------------+
   | `0x05` | `Rail Faults`_    |
   +--------+-------------------+
   | `0x07` | `Match Info`_     |
   +--------+-------------------+
   | `0x08` | `Robot IP`_       |
   +--------+-------------------+
   | `0x09` | `DB Mode`_        |
   +--------+-------------------+

.. _`error messages`:

Error Messages (``0x00``)
^^^^^^^^^^^^^^^^^^^^^^^^^

.. table::
   :widths: auto

   +---------+--------+--------+---------+
   | Field   | Length | Type   | Comment |
   +=========+========+========+=========+
   | Message | n      | string |         |
   +---------+--------+--------+---------+

.. _`disable counts`:

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

.. _`rail faults`:

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

.. _`match info`:

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

.. _`robot ip`:

Robot IP (``0x08``)
^^^^^^^^^^^^^^^^^^^

.. table::
   :widths: auto

   +-------+--------+--------------+---------+
   | Field | Length | Type         | Comment |
   +=======+========+==============+=========+
   | IP    | 4      | IPv4 Address |         |
   +-------+--------+--------------+---------+

.. _`db mode`:

DB Mode (``0x09``)
^^^^^^^^^^^^^^^^^^

.. table::
   :widths: auto

   +-------+--------+---------+---------+
   | Field | Length | Type    | Comment |
   +=======+========+=========+=========+
   | Mode  | 1      | `Mode`_ |         |
   +-------+--------+---------+---------+

Mode
""""

.. table::
   :widths: auto

   +-----------+------------+---------+
   | Field     | Mask       | Comment |
   +===========+============+=========+
   | Docked    | `.....x..` |         |
   +-----------+------------+---------+
   | Simulated | `.......x` |         |
   +-----------+------------+---------+

TCP Listening (port 1742)
-------------------------

The Driver Station listens on TCP port 1742 and sends the following JSON:

``{"robotIP":0,"dashboardiP":3232235818,"FMS Connected":false,"Robot Connected":false,"RobotCode":false}``

This is sent whenever one of the values changes.
