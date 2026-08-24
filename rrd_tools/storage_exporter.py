import csv
import mysql.connector

from collections import defaultdict

from config import (
    DB_CONFIG,
    STORAGE_OUTPUT_CSV,
    ALL_PARTITIONS,
)


def normalize_storage_descr(descr):
    descr = descr.strip()

    if descr.upper().startswith(
        ("C:", "D:", "E:", "F:")
    ):
        return descr[:2].upper()

    return descr


def generate_csv(output_file):
    conn = None
    cursor = None

    try:
        conn = mysql.connector.connect(
            **DB_CONFIG
        )

        cursor = conn.cursor()

        query = """
        SELECT
            d.hostname,
            s.storage_descr,
            ROUND(
                (s.storage_used / s.storage_size) * 100,
                2
            ) AS usage_percent
        FROM storage s
        JOIN devices d
            ON d.device_id = s.device_id
        WHERE s.storage_size > 0
        ORDER BY
            d.hostname,
            s.storage_descr
        """

        cursor.execute(query)

        results = cursor.fetchall()

        data = defaultdict(dict)

        for hostname, partition, usage in results:
            normalized = normalize_storage_descr(
                partition
            )

            if normalized in ALL_PARTITIONS:
                data[hostname][normalized] = str(
                    usage
                )

        with open(
            output_file,
            mode="w",
            newline="\n"
        ) as file:

            writer = csv.writer(
                file,
                delimiter="\t"
            )

            header = [
                "Hostname",
                *ALL_PARTITIONS,
            ]

            writer.writerow(header)

            for hostname in sorted(data.keys()):
                row = [hostname]

                for partition in ALL_PARTITIONS:
                    row.append(
                        data[hostname].get(
                            partition,
                            "-"
                        )
                    )

                writer.writerow(row)

        print(
            f"✅ CSV berhasil dibuat: {output_file}"
        )

    except mysql.connector.Error as e:
        print(
            f"❌ Database error: {e}"
        )

    except OSError as e:
        print(
            f"❌ File error: {e}"
        )

    finally:
        if cursor is not None:
            cursor.close()

        if conn is not None and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    generate_csv(
        STORAGE_OUTPUT_CSV
    )