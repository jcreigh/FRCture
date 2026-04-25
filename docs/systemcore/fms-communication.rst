FMS Communication
=================

Communication with the Field Management System (FMS) is only present in the **Windows build** of the DS. The macOS and Linux builds lack the FMS module entirely.

Platform Differences
--------------------

========= ======================= ====================== ===================================================
Platform  Authentication          TLS                    API
========= ======================= ====================== ===================================================
Windows   SSPI Negotiate (Kerberos/SPNEGO) Schannel  ``AcquireCredentialsHandle``, ``InitializeSecurityContext``, ``EncryptMessage``, ``DecryptMessage``
macOS     GSS/Kerberos           Apple Network framework ``gss_init_sec_context``, ``gss_accept_sec_context``, ``gss_acquire_cred_with_password``
Linux     GSS/Kerberos (MIT/Heimdal) OpenSSL?          Not analyzed
========= ======================= ====================== ===================================================

The Windows build is the only one with a full FMS connection handler. On macOS and Linux, the FMS-related .NET types are not present in the binary.

FMS Connection Handler (Windows)
---------------------------------

Classes
^^^^^^^

========================= =======================================
Class                     Purpose
========================= =======================================
``FmsConnectionHandler``   Main FMS connection lifecycle
``DatagramConnectionHandler`` UDP datagram processing
``NegotiateAuthenticationPal`` SSPI Negotiate auth wrapper
``CertificateValidationPal`` TLS certificate validation
``SslStreamContext``       TLS stream state
``ChallengeResponse``      FMS challenge-response protocol
========================= =======================================

Key Methods
^^^^^^^^^^^

=============================== =======================================
Method                          Purpose
=============================== =======================================
``ConnectAsync``                Initiate FMS TCP connection
``HandleFmsConnection``         Process FMS connection
``HandleFmsDataConnection``     Process FMS data channel
``HandleUdpData``               Parse incoming UDP from FMS
``SendUdpReply``                Send UDP response to FMS
``HandleTcpTag``                Process FMS TCP tag
``HandleStationCheck``          Verify alliance station
``CheckChangedTeamNumber``      Detect team number change
``IsValidChallenge``            Validate FMS challenge
``GenerateResponse``            Generate challenge response
``WriteChallengeResponseAsync`` Send challenge response
=============================== =======================================

Authentication
--------------

SSPI Negotiate (Windows)
^^^^^^^^^^^^^^^^^^^^^^^^

The FMS uses SSPI Negotiate authentication, which tries Kerberos first and falls back to NTLM:

1. ``AcquireCredentialsHandle`` -- acquire Negotiate credentials
2. ``InitializeSecurityContext`` -- generate auth token (possibly multiple rounds)
3. ``CompleteAuthToken`` -- finalize if needed
4. ``DeleteSecurityContext`` -- cleanup

The challenge-response flow is:

1. FMS sends a challenge over TCP
2. DS validates with ``IsValidChallenge``
3. DS generates response with ``GenerateResponse``
4. DS sends response with ``WriteChallengeResponseAsync``

GSS/Kerberos (macOS)
^^^^^^^^^^^^^^^^^^^^

Uses the standard GSS-API:

- ``gss_init_sec_context`` -- initiate security context
- ``gss_accept_sec_context`` -- accept (for testing)
- ``gss_acquire_cred_with_password`` -- acquire credentials
- ``gss_verify_mic`` / ``gss_get_mic`` -- message integrity

TLS
---

Windows (Schannel)
^^^^^^^^^^^^^^^^^^

- ``SchannelCred`` -- Schannel credential configuration
- ``SecPkgContext_StreamSizes`` -- stream size negotiation
- ``SecPkgContext_ApplicationProtocol`` -- ALPN support
- ``EncryptMessage`` / ``DecryptMessage`` -- TLS record encryption

macOS (Apple Network)
^^^^^^^^^^^^^^^^^^^^^

- ``nw_protocol_copy_tls_definition`` -- TLS protocol definition
- ``sec_protocol_options_*`` -- TLS options configuration
- ``SecCertificate*`` / ``SecIdentity*`` / ``SecTrust*`` -- certificate handling

No FMS-specific TLS server certificates are embedded in the DS binary -- certificate validation is dynamic via ``CertificateValidationPal``.

FMS Control Data
-----------------

Topic: ``/FMSInfo/FMSControlData``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

========= ===== ========================================================
Property  Type  Description
========= ===== ========================================================
Type      numeric (integer)
Encoding  Odd values = robot enabled, even values = disabled (``value % 2 == 1`` -> enabled)
========= ===== ========================================================

Fallback Enable Topics
^^^^^^^^^^^^^^^^^^^^^^

The DS checks multiple topics to determine if the robot should be enabled:

=============================================== ====== ===========
Topic                                           Type   Description
=============================================== ====== ===========
``/FMSInfo/FMSControlData``                      integer Primary FMS control
``/DriverStation/Enabled``                       boolean Direct enable
``NT:/AdvantageKit/DriverStation/Enabled``       boolean AdvantageKit enable
``DS:enabled``                                   boolean Internal enable flag
``/DSLog/Status/DSDisabled``                     boolean **Inverted** -- true means disabled
``RobotEnable``                                  boolean Generic enable
=============================================== ====== ===========

FMS -> DS Protocol
------------------

The FMS communicates with the DS using the same tagged binary format as the pre-2027 protocol.

UDP (FMS -> DS)
^^^^^^^^^^^^^^^

======== ===========
Field    Description
======== ===========
Control  Robot enable/disable, E-Stop, mode
Alliance Station Red/Blue, position 1-3
Tournament Level Practice, qualification, elimination
Date    Match time sync
======== ===========

TCP (FMS -> DS)
^^^^^^^^^^^^^^

======== ==================== ===========
Tag ID  Tag                  Description
======== ==================== ===========
--       Version              Protocol version exchange
``0x14`` Event Code          FMS event code
``0x19`` Station Info        Alliance station assignment + status
``0x1a`` Challenge Question  Authentication challenge
``0x1c`` Game Data           Game-specific data
======== ==================== ===========

TCP (DS -> FMS)
^^^^^^^^^^^^^^^

======== ==================== ===========
Tag ID  Tag                  Description
======== ==================== ===========
--       Version              Protocol version
``0x15`` Usage Report        Software/hardware usage data
``0x16`` Log Data            DS log entries
``0x17`` Error and Event Data Error reports
``0x18`` Team Number        Team identification
``0x1b`` Challenge Response  Authentication response
``0x1c`` DS Ping            Keep-alive
======== ==================== ===========

Data Logging
------------

============================================ ====== ============================
File                                         Format Description
============================================ ====== ============================
``FIRST_DS_FMS_{event}_{match}_{station}({team})_{timestamp}.wpilog`` WPILog FMS session logs (Windows only)
``FIRST_DS_{timestamp}.wpilog``              WPILog Regular DS logs (all platforms)
============================================ ====== ============================

Code Signing
------------

The Windows DS binary is signed with a Microsoft-verified code signing certificate:

========= ==================================
Property  Value
========= ==================================
Signer    Thad House (WPILib developer)
Key       3072-bit RSA
Hash      SHA-384
Validity  3 days (Apr 25-28, 2026) -- alpha build
========= ==================================

No FMS-specific TLS server certificates are embedded -- dynamic validation only.
