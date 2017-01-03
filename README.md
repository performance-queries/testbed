# testbed
Testing infrastructure for needlstk

1. Get VMware Fusion Pro for OS X (or equivalent for other platforms).
2. Get Mininet VM image from http://mininet.org (the native installations are flaky)
3. Get the In-band Network Telemetry demo from https://github.com/p4lang/ntf/tree/int-demo/apps/int
4. Get Spark Streaming from http://spark.apache.org/streaming/
http://stackoverflow.com/questions/31579204/spark-streaming-example-not-working-for-me-network-word-count-maybe-data-not
(Need to add --master=local[2] to get this to work on a virtual machine for some reason)
5. Launch VM image inside Fusion Pro; you will likely have to upgrade the image, meaning you can't use the upgraded image in an older version of Fusion Pro.
