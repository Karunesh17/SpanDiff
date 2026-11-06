# Platform verification matrix

This matrix reports only checks actually run in the current workspace.

| Capability | Windows / Python 3.12 | Linux | Docker Desktop |
| --- | --- | --- | --- |
| Editable package install | Verified | Not run | Not applicable |
| Workspace paths containing spaces | Verified | Not run | Not run |
| Subprocess cancellation | Verified | Not run | Not run |
| Port collision handling | Verified | Not run | Not run |
| Compose integration | Not run | Not run | Not run |

SD-37 is not complete because the contract requires Linux and Docker Desktop
verification. No unsupported platform is advertised by this document.
