# testbed
Testing infrastructure for needlstk

1. Get VMware Fusion Pro for OS X (or equivalent for other platforms).
2. Get Mininet VM image from http://mininet.org (the native installations are flaky)
3. Launch VM image inside Fusion Pro; you will likely have to upgrade the image, meaning you can't use the upgraded image in an older version of Fusion Pro.
4. Install java, required for Spark: sudo apt-get install default-jdk default-jre
5. Get Spark Streaming from http://spark.apache.org/streaming/
6. Run the network word count example from here: http://spark.apache.org/docs/latest/streaming-programming-guide.html#a-quick-example As per http://stackoverflow.com/questions/31579204/spark-streaming-example-not-working-for-me-network-word-count-maybe-data-not you need to add --master=local[2] to get this to work on a virtual machine.
7. Get the In-band Network Telemetry demo from https://github.com/p4lang/ntf/tree/int-demo/apps/int
