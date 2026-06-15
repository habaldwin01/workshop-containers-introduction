#!/usr/bin/env python3

import sys
import csv

try:
    csv_file_input = sys.argv[1]
    csv_file_output = sys.argv[1]
except ValueError:
    print("Please supply an input and output filename as first and second arguments")

counts = {}

with open(csv_file_input, newline="") as fp:
    reader = csv.DictReader(fp)
    for row in reader:
        if row["class"] not in counts:
            counts[row["class"]] = 0
        counts[row["class"]] += 1

with open(csv_file_output, "w") as fp:
    fieldnames = ["class", "count"]
    writer = csv.DictWriter(fp, fieldnames=fieldnames)
    writer.writeheader()

    for class_name in counts.keys():
        writer.writerow({"class": class_name, "count": counts[class_name]})

