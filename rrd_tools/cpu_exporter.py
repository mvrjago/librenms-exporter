import os
import rrdtool
import csv

from statistics import mean
from datetime import datetime, timedelta

from config import (
    RRD_BASE_PATH,
    RRD_OUTPUT_CSV,
    RRD_LOOKBACK_DAYS,
    RRD_RESOLUTION,
)


def fetch_rrd_usage(rrd_file, ds_name, start_ts, end_ts):
    try:
        (start, end, step), ds_names, data = rrdtool.fetch(
            rrd_file,
            "AVERAGE",
            "--start",
            str(start_ts),
            "--end",
            str(end_ts),
            "--resolution",
            str(RRD_RESOLUTION),
        )

        if ds_name not in ds_names:
            print(f"⚠️ DS {ds_name} not found in {rrd_file}")
            return []

        idx = ds_names.index(ds_name)

        values = [
            row[idx]
            for row in data
            if row[idx] is not None
        ]

        return values

    except Exception as e:
        print(f"⚠️ Error parsing {rrd_file}: {e}")
        return []


def generate_csv(output_path, start_ts, end_ts):
    results = []

    for hostname in sorted(os.listdir(RRD_BASE_PATH)):
        host_path = os.path.join(RRD_BASE_PATH, hostname)

        if not os.path.isdir(host_path):
            continue

        core_files = sorted([
            f
            for f in os.listdir(host_path)
            if f.startswith("processor-hr-")
            and f.endswith(".rrd")
        ])

        core_data = []
        rrd_used = []

        if core_files:
            for fname in core_files:
                full_path = os.path.join(host_path, fname)

                usage = fetch_rrd_usage(
                    full_path,
                    "usage",
                    start_ts,
                    end_ts,
                )

                if usage:
                    core_data.append(usage)
                    rrd_used.append(fname)

        else:
            fortigate_rrd = os.path.join(
                host_path,
                "fortigate_cpu.rrd"
            )

            if os.path.exists(fortigate_rrd):
                usage = fetch_rrd_usage(
                    fortigate_rrd,
                    "LOAD",
                    start_ts,
                    end_ts,
                )

                if usage:
                    core_data.append(usage)
                    rrd_used.append("fortigate_cpu.rrd")

            fortiweb_rrd = os.path.join(
                host_path,
                "ucd_cpu.rrd"
            )

            if os.path.exists(fortiweb_rrd):
                usage = fetch_rrd_usage(
                    fortiweb_rrd,
                    "cpu",
                    start_ts,
                    end_ts,
                )

                if usage:
                    core_data.append(usage)
                    rrd_used.append("ucd_cpu.rrd")

        if not core_data:
            continue

        flat_values = [
            value
            for core in core_data
            for value in core
            if value is not None
        ]

        per_core_max = [
            max(core)
            for core in core_data
            if core
        ]

        per_core_min = [
            min(core)
            for core in core_data
            if core
        ]

        max_all = max(per_core_max) if per_core_max else 0.0
        min_all = min(per_core_min) if per_core_min else 0.0
        avg_all = mean(flat_values) if flat_values else 0.0

        results.append({
            "hostname": hostname,
            "rrd_files": ", ".join(rrd_used),
            "min": round(min_all, 2),
            "max": round(max_all, 2),
            "avg": round(avg_all, 2),
        })

    with open(output_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow([
            "Hostname",
            "RRD Files",
            "Min",
            "Max",
            "Avg",
        ])

        for row in results:
            writer.writerow([
                row["hostname"],
                row["rrd_files"],
                f"{row['min']:.2f}",
                f"{row['max']:.2f}",
                f"{row['avg']:.2f}",
            ])

    print(f"✅ Exported to {output_path}")


if __name__ == "__main__":
    end_time = int(datetime.now().timestamp())

    start_time = int(
        (
            datetime.now()
            - timedelta(days=RRD_LOOKBACK_DAYS)
        ).timestamp()
    )

    generate_csv(
        RRD_OUTPUT_CSV,
        start_time,
        end_time,
    )