import argparse
import logging
import os
import re

from past.builtins import unicode

import apache_beam as beam

from apache_beam.options.pipeline_options import (
    PipelineOptions,
    GoogleCloudOptions,
    StandardOptions,
    SetupOptions,
)

from apache_beam.io import ReadFromText, WriteToText


def pipeline_options() -> PipelineOptions:
    # from dotenv import load_dotenv
    # load_dotenv()

    # GOOGLE_CLOUD_PROJECT = os.getenv("GCP_PROJECT", None)
    # GCP_BUCKET = os.getenv("GCP_BUCKET", None)
    # GCP_REGION = os.getenv("GCP_REGION", None)
    options = PipelineOptions()
    # gcp_options = options.view_as(GoogleCloudOptions)
    # gcp_options.project = GOOGLE_CLOUD_PROJECT
    # gcp_options.job_name = "wordcount-minimal"
    # gcp_options.staging_location = f"gs://{GCP_BUCKET}/staging"
    # gcp_options.temp_location = f"gs://{GCP_BUCKET}/temp"
    # gcp_options.region = GCP_REGION
    # options.view_as(StandardOptions).runner = "DataflowRunner"
    # gcp_options.view_as(SetupOptions).save_main_session = True
    return options


def main(argv=None):

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        dest="input",
        default="gs://dataflow-samples/shakespeare/kinglear.txt",
        help="Input file to process.",
    )
    parser.add_argument(
        "--output",
        dest="output",
        # CHANGE 1/6: The Google Cloud Storage path is required
        # for outputting the results.
        # default='gs://YOUR_OUTPUT_BUCKET/AND_OUTPUT_PREFIX',
        required=True,
        help="Output location to write results to.",
    )
    known_args, pipeline_args = parser.parse_known_args(argv)
    pipeline_args.extend(
        [
            # Change this to DataflowRunner to
            # run your pipeline on the Google Cloud Dataflow Service.
            "--runner=DirectRunner",
            # Project ID is required in order to
            # run your pipeline on the Google Cloud Dataflow Service.
            "--project=SET_YOUR_PROJECT_ID_HERE",
            # The Google Cloud region (e.g. us-central1)
            # is required in order to run your pipeline on the Google Cloud
            # Dataflow Service.
            "--region=SET_REGION_HERE",
            # Google Cloud Storage path is required for staging local
            # files.
            "--staging_location=gs://YOUR_BUCKET_NAME/AND_STAGING_DIRECTORY",
            # Google Cloud Storage path is required for temporary
            # files.
            "--temp_location=gs://YOUR_BUCKET_NAME/AND_TEMP_DIRECTORY",
            "--job_name=your-wordcount-job",
        ]
    )

    options = PipelineOptions(pipeline_args)  # pipeline_options(pipeline_args)

    input_file = known_args.input  # "gs://dataflow-samples/shakespeare/kinglear.txt"
    output_file = known_args.output

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


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    main()