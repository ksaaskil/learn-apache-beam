---
title: Getting started with Apache Beam for distributed data processing
description: Run your first big data processing job on Google cloud Dataflow with Apache Beam Python SDK
---

[MapReduce](https://research.google/pubs/pub62/) was revolutionary when it was first published in 2004. It provided a programming model suited for batch processing huge datasets with terabytes of data. MapReduce was built on three seemingly simple phases: map, sort, and reduce. It used the general-purpose [HDFS](https://hadoop.apache.org/docs/r1.2.1/hdfs_design.html) (Hadoop Distributed File System) file system for I/O and was therefore capable of processing almost any kind of data.

MapReduce jobs were notoriously tedious to write. High-level APIs such as [Hive](https://hive.apache.org/) and [Pig](https://pig.apache.org/) provided higher-level APIs wrapping MapReduce and made it a lot easier to get stuff done with MapReduce.

However, the MapReduce model had other shortcomings. For example, the stiff map-sort-reduce flow isn't optimal for every kind of job: the sort phase is often unnecessary and sometimes it would be much more useful to chain reducers directly without a new map-sort phase. MapReduce was also built for the kind of fault-tolerance that isn't really required outside Google scale: it insists on writing all intermediate state on HDFS, which makes processing slower. 

New frameworks and programming models such as [Apache Spark](https://spark.apache.org/), [Apache Tez](http://tez.apache.org/) and [Apache Flink](https://flink.apache.org/) emerged to address these short-comings. Spark does its best to keep data close to the executors or even in memory between tasks, which can speed things up a lot. Its dataset abstractions such as [resilient distributed dataset](https://spark.apache.org/docs/latest/rdd-programming-guide.html) (RDD) and [Dataset](https://spark.apache.org/docs/latest/sql-programming-guide.html) also made it a lot easier to reason about and write programs running in distributed setting.

[Apache Beam](https://beam.apache.org/) is yet another abstraction for massively parallel processing jobs. Beam allows declaring both batch and streaming jobs in unified fashion and they can run in any execution engine such as Spark, Flink, [Google Cloud Dataflow](https://cloud.google.com/dataflow/), [Apache Samza](https://samza.apache.org/), or [Twister 2](https://twister2.org//).

In this article, we'll declare a processing pipeline with Apache Beam Python SDK and execute the pipeline in Dataflow. Alternatively, you can execute the pipeline in your local machine.

## Setup

The code for the example can be found in the `wordcount/` folder of [this repository](https://github.com/ksaaskil/learn-apache-beam/tree/master/wordcount). To get started, move to the folder and install the requirements with

```bash
$ pip install -r requirements.txt
```

You'll probably want to create a virtual environment before running the command. You can also install Apache Beam Python SDK directly with `pip install apache-beam[gcp]`, where the `gcp` bundle includes everything required to use the Google Cloud Dataflow runner as execution engine.

### Google Cloud Setup

**Note: Running the pipeline will incur charges on your Google Cloud account. See [Dataflow pricing](https://cloud.google.com/dataflow/pricing). For me, running this pipeline multiple times incurred charges of $0.01 (covered by the free-tier credits).**

If you want to execute the pipeline in Dataflow, you'll need to execute the following steps:

1. Create a [Google Cloud](https://cloud.google.com/) account and a project within the account in the [console](https://console.cloud.google.com/).
1. [Install and setup](https://cloud.google.com/sdk/gcloud/) Google Cloud CLI if you want to manage resources from the command-line.
1. [Enable Dataflow API](https://cloud.google.com/apis/docs/getting-started#enabling_apis) as instructed here. You may also need to enable other APIs: you'll get detailed instructions when your pipeline fails.
1. Create a GCP bucket for writing output, preferably in the same [region](https://cloud.google.com/dataflow/docs/concepts/regional-endpoints) where you run Dataflow. To create bucket from the command line, run: `gsutil mb -p PROJECT_ID -c STANDARD -l REGION -b on gs://BUCKET_NAME`. Fill in project ID, region and bucket name here.
1. [Create a service account](https://cloud.google.com/docs/authentication/getting-started), download the JSON key and store it somewhere in your machine.

### Running the pipeline

The pipeline definition is located in [main.py](https://github.com/ksaaskil/learn-apache-beam/blob/master/wordcount/main.py). The file is almost identical to the [wordcount_minimal.py](https://github.com/apache/beam/blob/master/sdks/python/apache_beam/examples/wordcount_minimal.py) from Beam examples. We'll go through the pipeline code soon, but if you're in hurry, here are the details how to execute the pipeline first locally with the local execution engine ([DirectRunner](https://beam.apache.org/documentation/runners/direct/)) without Google Cloud account:

``bash
$ python main.py --runner DirectRunner --input gs://dataflow-samples/shakespeare/kinglear.txt --output output/counts
```

It should only take a few seconds to execute the pipeline. Check the output in `output/counts` folder:

```bash
$ cat output/counts-00000-of-00001 | head -n 5
KING: 243
LEAR: 236
DRAMATIS: 1
PERSONAE: 1
king: 65
```

To run the same script with [DataflowRunner](https://beam.apache.org/documentation/runners/dataflow/), writing output to the GCS bucket:

```bash
$ export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
$ export GCP_PROJECT=your-gcp-project-11111111
$ export GCP_BUCKET=your-gcp-bucket
$ export GCP_REGION=europe-west-1
$ python main.py --runner DataflowRunner --project ${GCP_PROJECT} --region=${GCP_REGION} --staging_location=gs://${GCP_BUCKET}/staging --temp_location gs://${GCP_BUCKET}/temp --job_name wordcount-job --input gs://dataflow-samples/shakespeare/kinglear.txt --output gs://${GCP_BUCKET}/output/counts
```

Running the pipeline in the cloud can take up to three minutes to finish.

### Understand the pipeline

The complete pipeline definition is here (without parsing arguments etc.):

```python
import re
from past.builtins import unicode

import apache_beam as beam

from apache_beam.options.pipeline_options import (
    PipelineOptions,
)

from apache_beam.io import ReadFromText, WriteToText

with beam.Pipeline(options=options) as p:

    # "A text file Read transform is applied to the Pipeline object itself,
    # and produces a PCollection as output. Each element in the output PCollection
    # represents one line of text from the input file."
    lines = p | ReadFromText(input_file)

    counts = (
        lines
        # "This transform splits the lines in PCollection<String>, where each element
        # is an individual word in Shakespeare’s collected texts. As an alternative,
        # it would have been possible to use a ParDo transform that invokes a DoFn
        # (defined in-line as an anonymous class) on each element that tokenizes the
        # text lines into individual words. The input for this transform is the PCollection
        # of text lines generated by the previous TextIO.Read transform. The ParDo transform
        # outputs a new PCollection, where each element represents an individual word in the text."
        | "Split"
        >> (
            beam.FlatMap(lambda x: re.findall(r"[A-Za-z\']+", x)).with_output_types(
                unicode
            )
        )
        | "PairWithOne" >> beam.Map(lambda x: (x, 1))
        | "GroupAndSum" >> beam.CombinePerKey(sum)
    )

    def format_result(word_count):
        (word, count) = word_count
        return "%s: %s" % (word, count)

    output = counts | "Format" >> beam.Map(format_result)
    output | WriteToText(output_file)
```

Let's start from the pipeline creation. The pipeline object is created with `options` specifying, for example, the configuration for the execution engine. The pipeline is used as a context manager `with beam.Pipeline(options=options) as p` so that it [can be executed at `__exit__`](https://github.com/apache/beam/blob/master/sdks/python/apache_beam/pipeline.py#L564).

We start the pipeline with [`ReadFromText`](https://github.com/apache/beam/blob/v2.26.0-RC00/sdks/python/apache_beam/io/textio.py#L516) from the `apache_beam.io` package:

```python
lines = p | ReadFromText(input_file)
```

`ReadFromText` returns a `PCollection`, which is Beam's term for the [dataset](https://cloud.google.com/dataflow/docs/concepts/beam-programming-model):

> A PCollection represents a potentially distributed, multi-element dataset that acts as the pipeline's data. Apache Beam transforms use PCollection objects as inputs and outputs for each step in your pipeline. A PCollection can hold a dataset of a fixed size or an unbounded dataset from a continuously updating data source.

`ReadFromText` itself is an `PTransform`:

> A transform represents a processing operation that transforms data. A transform takes one or more PCollections as input, performs an operation that you specify on each element in that collection, and produces one or more PCollections as output. A transform can perform nearly any kind of processing operation, including performing mathematical computations on data, converting data from one format to another, grouping data together, reading and writing data, filtering data to output only the elements you want, or combining data elements into single values.

In the Python SDK, transforms are chained with the vertical bar `|`. See [here](https://github.com/apache/beam/blob/v2.26.0-RC00/sdks/python/apache_beam/transforms/ptransform.py#L529) for the definition of `__or__`.

So now `lines` is a `PCollection` containing all lines in the input text file. Here are the next steps:

```python
counts = (
    lines
    | "Split"
    >> (
        beam.FlatMap(lambda x: re.findall(r"[A-Za-z\']+", x)).with_output_types(
            unicode
        )
    )
    | "PairWithOne" >> beam.Map(lambda x: (x, 1))
    | "GroupAndSum" >> beam.CombinePerKey(sum)
)
```

The bit-shift operator is [overridden](https://github.com/apache/beam/blob/v2.26.0-RC00/sdks/python/apache_beam/transforms/ptransform.py) by defining `__rrshift__` for `PTransform` to allow naming it. In the `"Split"` transform, each line is split into words. This collection of collections is flattened to a collection with `beam.FlatMap`. The `"PairWithOne"` transform maps every word to a tuple `(x, 1)`. The first item is the key and the second item is the value. The key-value pairs are then fed to the "GroupAndSum" transform, where all values are summed up by key. This is parallelized word count!

Finally, the output is formatted and written:

```python
def format_result(word_count):
    (word, count) = word_count
    return "%s: %s" % (word, count)

output = counts | "Format" >> beam.Map(format_result)
output | WriteToText(output_file)
```

The `"Format"` transform maps every `(word, count)` pair with the `format_result` function. The output is written to `output_file` with the [`WriteToText`](https://github.com/apache/beam/blob/v2.26.0-RC00/sdks/python/apache_beam/io/textio.py#L589) transform.

## Conclusion

That concludes my quick start for Apache Beam. It's a very promising project and there's a lot to learn. Please leave comments or questions if you have any, thanks a lot for reading!
