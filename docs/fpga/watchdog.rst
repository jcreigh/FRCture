Watchdog
========

The FPGA has a watchdog which, when fed properly, enables all the outputs on
the robot (e.g. CAN, PWM, Relays, etc).

.. DANGER::
   Manually feeding the watchdog bypasses all the built in safeties preventing
   the robot from moving. Do not manually feed the watchdog on a robot that has
   any chance of injuring someone.


Feeding
-------

1. Send ``b007`` to ``SysWatchdog.Command``
2. Read from ``SysWatchdog.Challenge``
3. Bitwise OR the proper response with ``a300`` and write it to 
   ``SysWatchdog.Command``
4. Write ``feed`` to ``SysWatchdog.Command`` and go to step 2

To stop feeding, one should write ``dead`` to ``SysWatchdog.Command``

Challenge-response
------------------

The challenge-response is a single byte as of 2018, so simply intercepting and
recording all the proper responses is trivial. The current responses are:

.. code-block:: c

   uint8_t responses[256] = {
      215, 146, 240,  69,  60,  49, 178,  31,  50, 191, 242,  14, 110, 175,  34, 103,
      156, 180,  94,  96, 222,   2,  57,  81, 122,  71,   3, 166,  75,  35,  19, 251,
       58, 155, 149, 117, 184,  27, 158, 248,  51, 159,  98,  87,   4, 154,  73, 213,
      224,  47,  61,  54, 205,   8,  10,  29, 171, 241,  40,  77,  21, 217, 247, 208,
       70, 229,  32, 136,  72, 121, 218, 109,   1,  83, 144, 226, 127,  12, 253, 186,
      227,  88, 129, 199, 172, 124,  20, 200, 177,  84,  13,  53, 243, 120,  17, 161,
      115,  65, 255, 167,  15, 138,   7, 165, 249, 195,  97, 236, 219, 250, 235, 196,
      210,   0, 231,  25, 151, 118, 201, 147, 176, 246,  56, 169,  82, 188,  42, 232,
       28,  33,  67,  24, 148, 174,  66, 203, 193,  36, 206, 207, 157, 181, 113, 202,
      107,  93, 220, 101, 140, 131, 160,  41,  37, 239, 102,  18,  39,  90,  62, 112,
       26, 244,  48,  63,  76,  22, 111,  16,  91,  80, 162, 105, 152, 142, 108, 212,
      125, 153, 163, 106, 100, 192, 204, 128, 116, 233, 179, 164,  89, 170, 228,  45,
      238, 221, 143,  99,   9,   5,  44, 123, 234, 183, 145,  23,  46, 114, 190,  92,
      137, 198,  55, 135,  68, 254, 252, 173,  86,  74,  64,  79, 209, 141, 130, 168,
      230, 104, 187, 194, 182, 139, 150, 223, 134, 119, 189, 245,  85,  52,  95, 214,
      132, 133, 216,  11,  43,  78,  30, 237, 211,  59,   6, 126,  38, 185, 225, 197
   };

