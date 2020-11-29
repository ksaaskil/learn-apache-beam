# Learn Apache Beam

## Setup

```bash
$ pip install -r requirements.txt
```

Run example from built-in [examples](https://github.com/apache/beam/blob/master/sdks/python/apache_beam/examples/) to see everything works:

```bash
$ python -m apache_beam.examples.wordcount --output output/counts
```

This example reads from a public GCP bucket by default.

See example [wordcount_minimal.py](https://github.com/apache/beam/blob/master/sdks/python/apache_beam/examples/wordcount_minimal.py).

## Google Cloud setup

Note: Running the pipeline will incur charges on your Google Cloud account. See [Dataflow pricing](https://cloud.google.com/dataflow/pricing).

1. Create a Google Cloud account and a project
1. [Install and setup](https://cloud.google.com/sdk/gcloud/) Google Cloud CLI if you want to manage resources from the command-line
1. [Enable Dataflow API](https://cloud.google.com/apis/docs/getting-started#enabling_apis)
1. Create a GCP bucket for writing output, preferably in the same [region](https://cloud.google.com/dataflow/docs/concepts/regional-endpoints) where you run Dataflow. To create bucket from the command line, run: `gsutil mb -p PROJECT_ID -c STANDARD -l REGION -b on gs://BUCKET_NAME`. Fill in project ID, region and bucket name here.
1. [Create a service account](https://cloud.google.com/docs/authentication/getting-started) and download the JSON key

## Local wordcount example with Google Cloud Dataflow

First, fill in the values in `.env` file, following `.env.example`.

Run the example:

```bash
$ python wordcount_minimal.py --requirements_file requirements-workers.txt
```

Specifying the `requirements-workers.txt` is required so that cloud workers know which packages are required.

## Alternative run

```bash
$ export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
$ python main.py --runner DataflowRunner --project ${GCP_PROJECT} --region=europe-west1 --staging_location=gs://${GCP_BUCKET}/staging --temp_location gs://${GCP_BUCKET}/temp --job_name wordcount-job
```
