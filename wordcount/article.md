---
title: Run your first big data processing job on Google Dataflow with Apache Beam Python SDK
description: 

---

[MapReduce](https://research.google/pubs/pub62/) was revolutionary when it was first published in 2004. It provided a programming model suited for batch processing huge datasets with terabytes of data. MapReduce was built on three seemingly simple phases: map, sort, and reduce. It used the general-purpose [HDFS](https://hadoop.apache.org/docs/r1.2.1/hdfs_design.html) (Hadoop Distributed File System) file system for I/O and was therefore capable of processing almost any kind of data.

MapReduce jobs were notoriously tedious to write. High-level APIs such as [Hive](https://hive.apache.org/) and [Pig](https://pig.apache.org/) provided higher-level APIs wrapping MapReduce and made it a lot easier to get stuff done with MapReduce.

However, the MapReduce model had other shortcomings. For example, the stiff map-sort-reduce flow isn't optimal for every kind of job: the sort phase is often unnecessary and sometimes it would be much more useful to chain reducers directly without a new map-sort phase. MapReduce was also built for the kind of fault-tolerance that isn't really required outside Google scale: it insists on writing all intermediate state on HDFS, which makes processing slower. 

New frameworks and programming models such as [Apache Spark](https://spark.apache.org/), [Apache Tez](http://tez.apache.org/) and [Apache Flink](https://flink.apache.org/) emerged to address these short-comings. Spark does its best to keep data close to the executors or even in memory between tasks, which can speed things up a lot. Its dataset abstractions such as [resilient distributed dataset](https://spark.apache.org/docs/latest/rdd-programming-guide.html) (RDD) and [Dataset](https://spark.apache.org/docs/latest/sql-programming-guide.html) also made it a lot easier to reason about and write programs running in distributed setting.
