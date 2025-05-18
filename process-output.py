#!/usr/bin/env python3

import os
import sys

import argparse
import logging
import itertools

import inspect
import types
from pathlib import Path
from typing import Iterable

import polars as pl


def directory_exists(path: str) -> bool:
    return Path(path).is_dir()


def get_processing_functions() -> list[tuple[str, types.FunctionType]]:
    current_module = inspect.getmodule(inspect.currentframe())
    functions = inspect.getmembers(current_module, inspect.isfunction)

    processing_function_prefix = "process_"
    processing_functions = filter(
        lambda x: x[0].startswith(processing_function_prefix), functions
    )
    stripped_prefixes_from_name = map(
        lambda x: (x[0].replace(processing_function_prefix, ""), x[1]),
        processing_functions,
    )
    return list(stripped_prefixes_from_name)


def get_all_files_in_dir(dir: str) -> list[str]:
    file_paths = []

    for file in os.listdir(dir):
        file_path = os.path.join(dir, file)
        if os.path.isfile(file_path):
            file_paths.append(file_path)

    return file_paths


def get_all_files_with_prefix_in_dir(dir: str, prefix: str) -> list[str]:
    return list(
        filter(lambda x: x.split("/")[-1].startswith(prefix), get_all_files_in_dir(dir))
    )


def parse_duration(line: str) -> int:
    """
    Parses the time, returns as nanoseconds
    """
    multiplier = None

    duration = line.split()[1]
    unit: str = duration[-2]
    if unit == "u":
        multiplier = 1000
    elif unit == "m":
        multiplier = 1000 * 1000
    else:
        if duration[-2].isnumeric() and duration[-1] == "s":
            multiplier = 1000 * 1000 * 1000
        else:
            raise Exception(f"Could not parse {duration}, unknown unit: {unit}.")

    value_float: float = float(duration[:-2])

    return int(value_float * multiplier)


def read_compressors_output_as_df(file: str) -> pl.DataFrame:
    lines = []

    with open(file, "r") as f:
        lines = f.readlines()

    lines = list(
        map(
            lambda x: float(x.split(";")[1]),
            filter(
                lambda x: "GREPTAG" in x,
                lines,
            ),
        )
    )

    return pl.DataFrame(
        {
            "kernel": ["decompression", "decompression_query"],
            "duration_ms": [lines[0], lines[1]],
            "compression_ratio": [lines[-1], lines[-1]],
        }
    )


def duplicate_each(collection: Iterable, repeat_n_times: int) -> list:
    return [x for x in collection for _ in range(repeat_n_times)]


def add_sample_run_column(df: pl.DataFrame, n_samples: int) -> pl.DataFrame:
    assert df.height % n_samples == 0, "Number of samples is not divisible by n_samples"
    n_unique_kernels = df.height // n_samples
    return df.with_columns(
        pl.Series("sample_run", list(range(1, n_samples + 1)) * n_unique_kernels),
    )


def convert_compressors_file_to_df(file: str) -> pl.DataFrame:
    params = os.path.basename(file).split("-")
    is_double = params[2] == "double"

    df = read_compressors_output_as_df(file)
    df = df.with_columns(
        pl.lit("f64" if is_double else "f32").alias("data_type"),
        pl.lit(f"fpcompressor-{params[3]}").alias("compressor"),
        pl.lit(params[4]).alias("file"),
        pl.lit(params[5]).alias("n_vecs"),
        pl.lit(int(params[5]) * 1024 * (int(is_double) + 1) * 4).alias("n_bytes"),
        pl.lit(params[6]).alias("sample_run"),
        pl.lit(None).alias("avg_bits_per_value"),
        pl.lit(None).alias("avg_exceptions_per_vector"),
        pl.lit(0).alias("return_code"),
    )

    return df


def collect_files_into_df(
    input_dir: str, prefix: str, convertor_lambda
) -> pl.DataFrame:
    files = get_all_files_with_prefix_in_dir(input_dir, prefix)
    return pl.concat(map(convertor_lambda, files))


def process_compressors(input_dir: str) -> tuple[str, pl.DataFrame]:
    df = collect_files_into_df(
        input_dir, "fpcompressor-decompress", convert_compressors_file_to_df
    )

    desired_order = [
        "return_code",
        "avg_bits_per_value",
        "avg_exceptions_per_vector",
        "kernel",
        "compressor",
        "file",
        "n_bytes",
        "duration_ms",
        "compression_ratio",
        "data_type",
        "n_vecs",
        "sample_run"
    ]

    df = df.select(desired_order)

    return "fpcompressors.csv", df


def main(args):
    assert directory_exists(args.input_dir)
    assert directory_exists(args.output_dir)

    for default_name, df in args.processing_function(args.input_dir):
        df.write_csv(os.path.join(args.output_dir, default_name))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="program")

    processing_functions = {func[0]: func[1] for func in get_processing_functions()}
    parser = argparse.ArgumentParser(prog="program")

    parser.add_argument(
        "processing_function",
        type=str,
        choices=list(processing_functions.keys()) + ["all"],
        help="function to execute",
    )
    parser.add_argument(
        "input_dir",
        type=str,
        help="directory_to_read_results_from",
    )
    parser.add_argument(
        "output_dir",
        default=None,
        type=str,
        help="directory_to_write_results_to",
    )

    parser.add_argument(
        "-ll",
        "--logging-level",
        type=int,
        default=logging.INFO,
        choices=[logging.CRITICAL, logging.ERROR, logging.INFO, logging.DEBUG],
        help=f"logging level to use: {logging.CRITICAL}=CRITICAL, {logging.ERROR}=ERROR, {logging.INFO}=INFO, "
        + f"{logging.DEBUG}=DEBUG, higher number means less output",
    )

    args = parser.parse_args()
    logging.basicConfig(level=args.logging_level)  # filename='program.log',
    logging.info(
        f"Started {os.path.basename(sys.argv[0])} with the following args: {args}"
    )

    if args.processing_function == "all":
        args.processing_function = lambda in_dir: list(
            func(in_dir) for func in processing_functions.values()
        )
    else:
        string_value = args.processing_function
        args.processing_function = lambda in_dir: [
            processing_functions[string_value](in_dir)
        ]
    main(args)
