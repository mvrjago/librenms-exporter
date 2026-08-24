import os
import csv

import rrdtool

from statistics import mean
from datetime import datetime, timedelta

from config import (
    RRD_BASE_PATH,
    RRD_LOOKBACK_DAYS,
    MEMORY_OUTPUT_CSV,
    MEMORY_RRD_FILES,
)


def find_rrd_file(host_path):
    for filename in MEMORY_RRD_FILES:
        full_path = os.path.join(host_path, filename)

        if os.path.exists(full_path):
            return full_path

    return None


def generate_csv(output_path, start_ts, end_ts):
    hosts = [
        hostname
        for hostname in os.listdir(RRD_BASE_PATH)
        if os.path.isdir(
            os.path.join(RRD_BASE_PATH, hostname)
        )
    ]

    results = []

    for hostname in sorted(hosts):
        host_path = os.path.join(
            RRD_BASE_PATH,
            hostname
        )

        rrd_file = find_rrd_file(host_path)

        if not rrd_file:
            print(
                f"⚠️ Skip {hostname}: "
                "No preferred RRD file found"
            )
            continue

        try:
            (
                (start_rrd, end_rrd, step),
                ds_names,
                data,
            ) = rrdtool.fetch(
                rrd_file,
                "AVERAGE",
                "--start",
                str(start_ts),
                "--end",
                str(end_ts),
            )

        except Exception as e:
            print(
                f"⚠️ Skip {hostname}: "
                f"RRDTool error: {e}"
            )
            continue

        ds_names = tuple(ds_names)

        if "used" not in ds_names or "free" not in ds_names:
            print(
                f"⚠️ Skip {hostname}: "
                f"DS fields not found: {ds_names}"
            )
            continue

        idx_used = ds_names.index("used")
        idx_free = ds_names.index("free")

        percent_used_list = []

        for row in data:
            used = row[idx_used]
            free = row[idx_free]

            if used is None or free is None:
                continue

            total = used + free

            if total <= 0:
                continue

            percent_used = (used / total) * 100

            percent_used_list.append(
                percent_used
            )

        if not percent_used_list:
            print(
                f"⚠️ Skip {hostname}: "
                "No valid data points"
            )
            continue

        min_used = min(percent_used_list)
        max_used = max(percent_used_list)
        avg_used = mean(percent_used_list)

        results.append({
            "hostname": hostname,
            "min_used": round(min_used, 2),
            "max_used": round(max_used, 2),
            "avg_used": round(avg_used, 2),
        })

    with open(
        output_path,
        "w",
        newline=""
    ) as csvfile:

        fieldnames = [
            "Hostname",
            "Min Used (%)",
            "Max Used (%)",
            "Avg Used (%)",
        ]

        writer = csv.DictWriter(
            csvfile,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for row in results:
            writer.writerow({
                "Hostname": row["hostname"],
                "Min Used (%)": row["min_used"],
                "Max Used (%)": row["max_used"],
                "Avg Used (%)": row["avg_used"],
            })

    print(
        f"✅ Memory report exported to {output_path}"
    )


if __name__ == "__main__":
    end_time = int(
        datetime.now().timestamp()
    )

    start_time = int(
        (
            datetime.now()
            - timedelta(days=RRD_LOOKBACK_DAYS)
        ).timestamp()
    )

    generate_csv(
        MEMORY_OUTPUT_CSV,
        start_time,
        end_time,
    )