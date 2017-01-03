# testbed
Testing infrastructure for needlstk

1. Get VMware Fusion Pro for OS X (or equivalent for other platforms).
2. Get Mininet VM image from http://mininet.org (the native installations are flaky)
3. Launch VM image inside Fusion Pro; you will likely have to upgrade the image, meaning you can't use the upgraded image in an older version of Fusion Pro.
4. Install java, required for Spark: sudo apt-get install default-jdk default-jre
5. Get Spark Streaming from http://spark.apache.org/streaming/
6. Run the network word count example from here: http://spark.apache.org/docs/latest/streaming-programming-guide.html#a-quick-example As per http://stackoverflow.com/questions/31579204/spark-streaming-example-not-working-for-me-network-word-count-maybe-data-not you need to add --master=local[2] to get this to work on a virtual machine.
7. Get the In-band Network Telemetry demo from https://github.com/p4lang/ntf/tree/int-demo/apps/int

Notes:

1. Apparently java 7 is deprecated in Spark 2.0: http://spark.apache.org/releases/spark-release-2-0-0.html#deprecations I am not sure if this affects us, but is worth noting because the default-jre and jdk in Ubuntu 14.04 (the distro of the VM image) are version 7.

2. websockets needs --no-compile: https://github.com/aaugustin/websockets/issues/147

3. We need to modify the Makefile for the VXLAN-GPE driver to compile against headers from the 3.19.0-78-generic kernel. The kernel in the Mininet image is older and doesn't have udp_tunnel.h in its linux headers, which is required to compile this driver.
