"""Review fictional manufacturing-application incidents from a JSON file."""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

REQUIRED = ("id", "title", "application", "site", "reported_at", "status", "impact", "affected_areas", "safety_or_quality_impact", "summary", "evidence", "owner", "next_step")
OPEN_STATES = {"open", "monitoring", "waiting"}


def load_records(path: Path) -> list[dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except OSError as exc:
        raise ValueError(f"cannot read input: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    records = payload.get("incidents") if isinstance(payload, dict) else None
    if not isinstance(records, list) or not records:
        raise ValueError("input must contain a non-empty 'incidents' array")
    seen: set[str] = set()
    for index, record in enumerate(records, start=1):
        label = f"incident {index}"
        if not isinstance(record, dict):
            raise ValueError(f"{label}: expected an object")
        missing = [field for field in REQUIRED if field not in record]
        if missing:
            raise ValueError(f"{label}: missing fields: {', '.join(missing)}")
        ident = record["id"]
        if not isinstance(ident, str) or not ident.strip():
            raise ValueError(f"{label}: id must be a non-empty string")
        if ident in seen:
            raise ValueError(f"{label}: duplicate id {ident!r}")
        seen.add(ident)
        if record["status"] not in {"open", "monitoring", "waiting", "resolved"}:
            raise ValueError(f"{ident}: unsupported status {record['status']!r}")
        if record["impact"] not in {"stopped", "degraded", "minor"}:
            raise ValueError(f"{ident}: unsupported impact {record['impact']!r}")
        if not isinstance(record["affected_areas"], int) or record["affected_areas"] < 1:
            raise ValueError(f"{ident}: affected_areas must be a positive integer")
        if not isinstance(record["safety_or_quality_impact"], bool):
            raise ValueError(f"{ident}: safety_or_quality_impact must be true or false")
        try:
            datetime.fromisoformat(record["reported_at"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{ident}: reported_at must be an ISO-8601 date and time") from exc
        if not isinstance(record["evidence"], list) or not all(isinstance(item, str) for item in record["evidence"]):
            raise ValueError(f"{ident}: evidence must be an array of strings")
    return records


def assess(record: dict[str, Any]) -> tuple[str, str]:
    if record["status"] == "resolved":
        return "closed", "record is resolved"
    if record["impact"] == "stopped" or record["safety_or_quality_impact"]:
        return "critical", "production is stopped or safety/quality impact is flagged"
    if record["impact"] == "degraded" or record["affected_areas"] > 1:
        return "high", "production is degraded or multiple areas are affected"
    return "normal", "no elevated impact rule matched"


def order_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rank = {"critical": 0, "high": 1, "normal": 2, "closed": 3}
    def key(record: dict[str, Any]) -> tuple[int, str, str]:
        level, _ = assess(record)
        return (rank[level], record["reported_at"], record["id"])
    return sorted(records, key=key)


def build_report(records: list[dict[str, Any]]) -> dict[str, Any]:
    items = []
    for record in order_records(records):
        priority, reason = assess(record)
        items.append({"id": record["id"], "title": record["title"], "application": record["application"], "site": record["site"], "status": record["status"], "priority": priority, "priority_reason": reason, "owner": record["owner"], "next_step": record["next_step"]})
    counts = {level: sum(item["priority"] == level for item in items) for level in ("critical", "high", "normal", "closed")}
    return {"summary": {"total": len(items), "open": sum(record["status"] in OPEN_STATES for record in records), "by_priority": counts}, "incidents": items}


def show_record(records: list[dict[str, Any]], ident: str) -> dict[str, Any]:
    for record in records:
        if record["id"].casefold() == ident.casefold():
            priority, reason = assess(record)
            return {**record, "priority": priority, "priority_reason": reason}
    raise ValueError(f"incident not found: {ident}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review fictional manufacturing application incidents.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("queue", "show", "report"):
        cmd = sub.add_parser(name)
        cmd.add_argument("input", type=Path)
        if name == "show": cmd.add_argument("id")
        if name == "report": cmd.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        records = load_records(args.input)
        if args.command == "queue":
            print(json.dumps(build_report(records), ensure_ascii=False, indent=2))
        elif args.command == "show":
            print(json.dumps(show_record(records, args.id), ensure_ascii=False, indent=2))
        else:
            report = build_report(records)
            args.out.parent.mkdir(parents=True, exist_ok=True)
            if args.out.exists():
                raise ValueError(f"output already exists; choose a new path: {args.out}")
            args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"Report written: {args.out}")
        return 0
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
