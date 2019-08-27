Watchdog
========

The FPGA has a watchdog which, when fed properly, enables all the outputs on
the robot (e.g. PWM, Relays, CAN (albeit, indirectly), etc).

.. DANGER::
   Manually feeding the watchdog bypasses all the built in safeties preventing
   the robot from moving. Do not manually feed the watchdog on a robot that has
   any chance of injuring someone.


Feeding
-------

The 2019 FPGA watchdog was updated to be slightly obfuscated, but is still based
on a single byte challenge-response, so still has the same problem.

1. Write ``0xb007`` to ``SysWatchdog.Command``
2. Read from ``SysWatchdog.Challenge`` (4 bytes as of 2019)
3. Apply the following deobfuscation to the challenge:

.. code-block:: c

   uint32_t swapped = obfuscated;

   swapped = ((swapped >> 1) & (0x55555555)) | ((swapped & (0x55555555)) << 1);
   // Swap consecutive pairs
   swapped = ((swapped >> 2) & (0x33333333)) | ((swapped & (0x33333333)) << 2);
   // Swap nibbles
   swapped = ((swapped >> 4) & (0x0f0f0f0f)) | ((swapped & (0x0f0f0f0f)) << 4);

   // XOR outer bytes of swapped with inner bytes of original obfuscated challenge
   challenge = ( (swapped >> 24) ^ (obfuscated >> 16) ^ (obfuscated >> 8) ^ swapped ) & 0xff;

4. The official code combines the response with random data to reobfuscate it.
   The result is that the lower two bytes XORed together produce the response. 

.. code-block:: c

  response = 0xcc | ((0xcc ^ responses[challenge]) << 8) 

.. NOTE::

   This can be any byte (``0xcc`` used above) other than ``0x00``. Using ``0x00`` will
   cause the watchdog to die when the response is ``0x00``. This is what
   lead to FIRST to release a late build season image, since the original didn't check.
   
   When enabled, every 20ms there's a :math:`\frac{1}{256}` chance for the (lower byte of the)
   random obfuscation number to be 0, and a :math:`\frac{1}{256}` chance for the response to be 0.
   When both were 0 (on average, every 21.8 minutes), the watchdog would die.

5. Write the response to ``SysWatchdog.Command``
6. Write ``0xfeed`` to ``SysWatchdog.Command`` and go to step 2

To stop feeding, one should write ``0xdead`` to ``SysWatchdog.Command``

Challenge-response
------------------

The challenge-response is a single byte in 2019, just obfuscated, so simply
intercepting, deobfuscating, and recording all the proper responses is trivial.

The current responses are:

.. code-block:: c

   uint8_t responses[256] = {
    118, 154, 243,  85,  81,  32, 153, 216, 137, 123,  26,  45, 165,  28, 100,   2, 
    168, 234,  61, 231, 155, 250, 248,  74,  58, 230, 246,  69,  77, 163,   7,  52, 
    106, 239, 240,  64, 188, 147, 254,   5, 126, 138, 121, 113, 229, 179,  49, 161, 
    109,  57,  27,  18,  86, 148, 195,  55, 222, 211, 117, 210, 104,   3, 226,  67, 
    209, 217, 177,  12, 219, 101,  73, 145,  99, 164, 215, 214,  94,  78,  17,   0, 
    169, 225, 245, 119,  53, 157, 224, 107, 212,  51, 218,  63,   8, 174, 252,  96, 
    184, 223, 105,  38, 129,  82,  92, 134, 194,  80, 102,  48, 146,  36, 204, 242, 
    238, 253, 130,  40, 152, 182,  70, 178, 247,  84, 187, 235, 208,  42, 202,  71, 
     23,  54, 141, 175, 180,  20,  89,  29,  97, 108, 221, 156, 206, 236, 189, 143, 
      9,  30, 125,  35,  87, 144, 159,  90, 114, 191, 139,   6, 201, 171, 228, 213, 
     15,  65, 232,  50,  79, 150, 220, 133, 116, 181, 185,  16, 190,  91, 200,  47, 
    197, 203,  68,  21,  43, 167, 199, 241, 142, 255, 183, 158, 122, 251,  59, 176, 
     39,   1, 192,  83, 124,  37, 115, 132, 128,  22, 244, 249,  93,  46, 227,  11, 
    149, 172, 196, 136, 193, 207,  76,  13, 162,  19, 170,  10,  66, 131,  44, 110, 
     75,  31, 103,  33,  56, 198, 140, 120, 166,  72,  98,  95, 127, 112, 160,  25, 
     34, 186, 173, 135,  88,  14,   4, 237,  62,  24, 233,  60, 111, 205, 151,  41
   };

