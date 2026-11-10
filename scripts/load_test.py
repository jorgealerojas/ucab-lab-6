#!/usr/bin/env python3
"""Generador de carga acotado para observar el comportamiento del portal."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass


@dataclass(frozen=True)
class Sample:
    latency_ms: float
    status: int
    instance: str | None

    @property
    def successful(self) -> bool:
        return 200 <= self.status < 400


def percentile(values: list[float], percentile_value: float) -> float:
    """Calcula un percentil con interpolacion lineal."""
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = (len(ordered) - 1) * percentile_value / 100
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[lower]
    fraction = rank - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def summarize(samples: list[Sample], elapsed_seconds: float) -> dict[str, object]:
    latencies = [sample.latency_ms for sample in samples]
    successes = sum(sample.successful for sample in samples)
    instances = sorted({sample.instance for sample in samples if sample.instance})
    total = len(samples)
    return {
        "requests": total,
        "successful": successes,
        "errors": total - successes,
        "success_rate_pct": round(successes * 100 / total, 2) if total else 0.0,
        "throughput_rps": round(total / elapsed_seconds, 2) if elapsed_seconds else 0.0,
        "latency_avg_ms": round(statistics.fmean(latencies), 2) if latencies else 0.0,
        "latency_p50_ms": round(percentile(latencies, 50), 2),
        "latency_p95_ms": round(percentile(latencies, 95), 2),
        "instances_observed": instances,
    }


def request_once(url: str, timeout: float) -> Sample:
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
            status = response.status
            instance = data.get("instance")
    except urllib.error.HTTPError as error:
        status = error.code
        instance = None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        status = 0
        instance = None
    latency_ms = (time.perf_counter() - started) * 1_000
    return Sample(latency_ms=latency_ms, status=status, instance=instance)


def run_load(url: str, duration: int, concurrency: int, work_ms: int, timeout: float) -> tuple[list[Sample], float]:
    query = urllib.parse.urlencode({"ms": work_ms})
    target_url = f"{url.rstrip('/')}/work?{query}"
    stop_at = time.monotonic() + duration
    samples: list[Sample] = []
    lock = threading.Lock()

    def worker() -> None:
        local_samples: list[Sample] = []
        while time.monotonic() < stop_at:
            local_samples.append(request_once(target_url, timeout))
        with lock:
            samples.extend(local_samples)

    started = time.monotonic()
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(worker) for _ in range(concurrency)]
        for future in futures:
            future.result()
    return samples, time.monotonic() - started


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Genera trafico HTTP acotado y calcula indicadores del servicio."
    )
    parser.add_argument("--url", required=True, help="URL base entregada por el laboratorio")
    parser.add_argument("--duration", type=int, default=30, choices=range(5, 181), metavar="5-180")
    parser.add_argument("--concurrency", type=int, default=4, choices=range(1, 51), metavar="1-50")
    parser.add_argument("--work-ms", type=int, default=25, choices=range(0, 501), metavar="0-500")
    parser.add_argument("--timeout", type=float, default=5.0)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    samples, elapsed = run_load(
        args.url,
        args.duration,
        args.concurrency,
        args.work_ms,
        args.timeout,
    )
    print(json.dumps(summarize(samples, elapsed), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

