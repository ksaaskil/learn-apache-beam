# Learn Apache Beam

```bash
$ pip install -r requirements.txt
```

or simply:

```bash
$ pip install apache-beam[gcp,aws]
```


Run example:

```bash
$ python -m apache_beam.examples.wordcount --output output/counts
```

This example reads from GCP bucket by default.

See example [wordcount_minimal.py](https://github.com/apache/beam/blob/master/sdks/python/apache_beam/examples/wordcount_minimal.py).