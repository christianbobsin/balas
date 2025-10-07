import os
import csv
import numpy as np

def append_inference_report(arena_size, macs, inference_times_us, report_filepath):
    """
    Appends inference performance data to a CSV file with average and standard deviation.

    Args:
        arena_size (int): Arena size in bytes.
        macs (int): Number of multipl-accumulate operations.
        inference_times_us (list[int]): List of inference times in microseconds.
        report_filepath (str): Path to the CSV report file.
    """
    file_exists = os.path.exists(report_filepath)

    avg_time = np.mean(inference_times_us)
    std_time = np.std(inference_times_us)

    with open(report_filepath, mode="a", newline="") as f:
        writer = csv.writer(f)
        # Write header only if the file didn't exist
        if not file_exists:
            writer.writerow(["arena_size", "macs", "avg_inference_us", "std_inference_us"])

        writer.writerow([arena_size, macs, avg_time, std_time])