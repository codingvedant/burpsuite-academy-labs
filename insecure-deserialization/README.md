# Insecure Deserialization

Exploiting how applications reconstruct objects from serialized data. When a server deserializes user-controllable input (like a session cookie), you can tamper with the serialized object to change attributes, inject different object types, or trigger gadget chains that execute arbitrary code.

The labs start with simple attribute modification in PHP serialized objects, move into data type manipulation and object injection, and progress to pre-built gadget chains in both PHP (PHPGGC) and Java (ysoserial).

[PortSwigger reference](https://portswigger.net/web-security/deserialization)

| # | Lab | Difficulty | Status |
|---|-----|-----------|--------|
| 1 | Modifying serialized objects | Apprentice | Solved |
| 2 | Modifying serialized data types | Practitioner | Solved |
| 3 | Using application functionality to exploit insecure deserialization | Practitioner | Solved |
| 4 | Arbitrary object injection in PHP | Practitioner | Solved |
| 5 | Exploiting Java deserialization with Apache Commons | Practitioner | Solved |
| 6 | Exploiting PHP deserialization with a pre-built gadget chain | Practitioner | Solved |
