Program needs to be launched using sudo command (tracerout requires it).

If you don't have enough IP adresses you may uncomment firewallOn/firewallOf (but it's rare situation).

There are examples of usage attached.

myMain.py is version using one thread and due to that fact it's slow for many IPs.
main.py is multithread version and runs swiftly.