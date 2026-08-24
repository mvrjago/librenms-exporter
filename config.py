import os
from datetime import timedelta

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "dev-secret-key"
)

PERMANENT_SESSION_LIFETIME = timedelta(
    minutes=5
)

RRD_BASE_PATH = os.getenv(
    "RRD_BASE_PATH",
    "/opt/librenms-docker/compose/librenms/rrd"
)

RRD_OUTPUT_CSV = os.getenv(
    "RRD_OUTPUT_CSV",
    "cpu_combined.csv"
)

RRD_LOOKBACK_DAYS = int(
    os.getenv(
        "RRD_LOOKBACK_DAYS",
        "30"
    )
)

RRD_RESOLUTION = int(
    os.getenv(
        "RRD_RESOLUTION",
        "300"
    )
)

MEMORY_OUTPUT_CSV = os.getenv(
    "MEMORY_OUTPUT_CSV",
    "memory_combined.csv"
)

MEMORY_RRD_FILES = [
    "mempool-hrstorage-system-1.rrd",
    "mempool-hrstorage-system-5.rrd",
    "mempool-hrstorage-system-65536.rrd",
    "mempool-fortigate-system-0.rrd",
    "mempool-hrstorage-system-6.rrd",
    "mempool-hrstorage-system-7.rrd",
    "mempool-fortiweb-system-0.rrd",
    "mempool-hrstorage-system-4.rrd",
]

DB_CONFIG = {
    "host": os.getenv(
        "LIBRENMS_DB_HOST",
        "localhost"
    ),

    "port": int(
        os.getenv(
            "LIBRENMS_DB_PORT",
            "3306"
        )
    ),

    "user": os.getenv(
        "LIBRENMS_DB_USER",
        ""
    ),

    "password": os.getenv(
        "LIBRENMS_DB_PASSWORD",
        ""
    ),

    "database": os.getenv(
        "LIBRENMS_DB_NAME",
        ""
    ),
}

STORAGE_OUTPUT_CSV = os.getenv(
    "STORAGE_OUTPUT_CSV",
    "storage_combined.tsv"
)

LINUX_PARTITIONS = [
    "/",
    "/boot",
    "/home",
    "/home/jail/usr/share/terminfo",
    "/opt",
    "/snapshots",
    "/mnt/fde",
    "/mnt/fde-barman",
    "/mnt/fde-postgres",
    "/mnt/vg-eset",
    "/srv",
    "/tmp",
    "/usr",
    "/var",
    "/var/lib",
    "/var/log",
    "/var/log/audit",
    "/var/log/suricata",
    "/var/ossec",
    "/var/lib/wazuh-indexer",
    "/var/log/wazuh-indexer",
    "/var/lib/mysql",
    "/var/tmp",
]

WINDOWS_PARTITIONS = [
    "C:",
    "D:",
    "E:",
    "F:",
]

ALL_PARTITIONS = (
    LINUX_PARTITIONS +
    WINDOWS_PARTITIONS
)

APP_HOST = os.getenv(
    "APP_HOST",
    "0.0.0.0"
)

APP_PORT = int(
    os.getenv(
        "APP_PORT",
        "5000"
    )
)

APP_DEBUG = os.getenv(
    "APP_DEBUG",
    "false"
).lower() == "true"


EXPORT_TEMP_DIR = os.getenv(
    "EXPORT_TEMP_DIR",
    "/tmp"
)