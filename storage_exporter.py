#!/usr/bin/env python3
import os
import shutil
import time
import logging
import argparse
from prometheus_client import start_http_server, Gauge, REGISTRY, PROCESS_COLLECTOR, PLATFORM_COLLECTOR

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

DISK_TOTAL = Gauge("cephfs_disk_total_bytes", "Total disk space of the CephFS mountpoint", ["mountpoint"])
DISK_USED = Gauge("cephfs_disk_used_bytes", "Used disk space of the CephFS mountpoint", ["mountpoint"])
DISK_FREE = Gauge("cephfs_disk_free_bytes", "Free disk space of the CephFS mountpoint", ["mountpoint"])
DISK_USAGE_RATIO = Gauge("cephfs_disk_usage_ratio", "Used fraction of CephFS disk space (0–1)", ["mountpoint"])
MOUNT_UP = Gauge("cephfs_mount_up", "1 if the CephFS mountpoint is accessible, 0 otherwise", ["mountpoint"])


def collect(mountpoint: str) -> None:
    if not os.path.ismount(mountpoint):
        log.warning("Mountpoint %s is not mounted", mountpoint)
        MOUNT_UP.labels(mountpoint=mountpoint).set(0)
        for metric in (DISK_TOTAL, DISK_USED, DISK_FREE, DISK_USAGE_RATIO):
            metric.labels(mountpoint=mountpoint).set(0)
        return

    try:
        usage = shutil.disk_usage(mountpoint)
    except OSError as exc:
        log.error("Failed to read disk usage for %s: %s", mountpoint, exc)
        MOUNT_UP.labels(mountpoint=mountpoint).set(0)
        for metric in (DISK_TOTAL, DISK_USED, DISK_FREE, DISK_USAGE_RATIO):
            metric.labels(mountpoint=mountpoint).set(0)
        return

    MOUNT_UP.labels(mountpoint=mountpoint).set(1)
    DISK_TOTAL.labels(mountpoint=mountpoint).set(usage.total)
    DISK_USED.labels(mountpoint=mountpoint).set(usage.used)
    DISK_FREE.labels(mountpoint=mountpoint).set(usage.free)
    ratio = usage.used / usage.total if usage.total > 0 else 0.0
    DISK_USAGE_RATIO.labels(mountpoint=mountpoint).set(ratio)

    log.debug(
        "mountpoint=%s total=%d used=%d free=%d ratio=%.4f",
        mountpoint, usage.total, usage.used, usage.free, ratio,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Prometheus exporter for CephFS disk usage")
    parser.add_argument("--mountpoint", default="/mnt/cephfs", help="CephFS mountpoint to monitor")
    parser.add_argument("--port", type=int, default=9857, help="Port to expose metrics on")
    parser.add_argument("--interval", type=int, default=60, help="Scrape interval in seconds")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Remove default process/platform collectors to keep the output focused
    REGISTRY.unregister(PROCESS_COLLECTOR)
    REGISTRY.unregister(PLATFORM_COLLECTOR)

    start_http_server(args.port)
    log.info("Exporter started on :%d — monitoring %s every %ds", args.port, args.mountpoint, args.interval)

    while True:
        collect(args.mountpoint)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
