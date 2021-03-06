import argparse
import logging
import re

from past.builtins import unicode

import apache_beam as beam

from apache_beam.options.pipeline_options import (
    PipelineOptions,
)

from apache_beam.io import ReadFromText, WriteToText


def main(argv=None):

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        dest="input",
        required=True,
        help="Input file to process.",
    )
    parser.add_argument(
        "--output",
        dest="output",
        required=True,
        help="Output location to write results to.",
    )
    known_args, pipeline_args = parser.parse_known_args(argv)

    options = PipelineOptions(pipeline_args)  # pipeline_options(pipeline_args)

    input_file = (
        known_args.input
    )  # For example: "gs://dataflow-samples/shakespeare/kinglear.txt"
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
