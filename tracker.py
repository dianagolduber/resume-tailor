#!/usr/bin/env python3
"""
Job Application Tracker
Usage:
    python tracker.py add --company "Stripe" --role "PMM" --url "https://..."
    python tracker.py list
    python tracker.py list --status "Phone Screen"
    python tracker.py update 3 --status "Interview" --notes "Recruiter call Thursday 2pm"
    python tracker.py show 3
    python tracker.py stats
"""

import argparse
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path("/Users/didya/Projects/job-search/resume-tailor/applications.db")

STATUSES = ["Saved", "Applied", "Phone Screen", "Interview", "Offer", "Rejected", "Withdrawn"]

STATUS_COLORS = {
    "Saved":        "\033[90m",   # gray
    "Applied":      "\033[34m",   # blue
    "Phone Screen": "\033[33m",   # yellow
    "Interview":    "\033[35m",   # magenta
    "Offer":        "\033[32m",   # green
    "Rejected":     "\033[31m",   # red
    "Withdrawn":    "\033[90m",   # gray
}
RESET = "\033[0m"
BOLD  = "\033[1m"


def get_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            company     TEXT NOT NULL,
            role        TEXT NOT NULL,
            url         TEXT,
            status      TEXT NOT NULL DEFAULT 'Applied',
            resume_path TEXT,
            notes       TEXT,
            date_applied TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def cmd_add(args):
    conn = get_db()
    now = datetime.now().strftime("%Y-%m-%d")
    cur = conn.execute(
        """INSERT INTO applications (company, role, url, status, resume_path, notes, date_applied, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (args.company, args.role, args.url or "", args.status, args.resume or "", args.notes or "", now, now)
    )
    conn.commit()
    row_id = cur.lastrowid
    print(f"{BOLD}Added#{row_id}{RESET}  {args.company} — {args.role}  [{args.status}]")


def cmd_list(args):
    conn = get_db()
    query = "SELECT * FROM applications"
    params = []
    if args.status:
        query += " WHERE status = ?"
        params.append(args.status)
    query += " ORDER BY date_applied DESC, id DESC"
    rows = conn.execute(query, params).fetchall()

    if not rows:
        print("No applications found.")
        return

    # Header
    print(f"\n{BOLD}{'ID':<4} {'Date':<12} {'Company':<20} {'Role':<30} {'Status'}{RESET}")
    print("─" * 78)
    for r in rows:
        color = STATUS_COLORS.get(r["status"], "")
        print(f"{r['id']:<4} {r['date_applied']:<12} {r['company']:<20} {r['role']:<30} {color}{r['status']}{RESET}")
    print(f"\n{len(rows)} application(s)")


def cmd_update(args):
    conn = get_db()
    row = conn.execute("SELECT * FROM applications WHERE id = ?", (args.id,)).fetchone()
    if not row:
        print(f"No application with id {args.id}")
        sys.exit(1)

    updates = {}
    if args.status:
        if args.status not in STATUSES:
            print(f"Invalid status. Choose from: {', '.join(STATUSES)}")
            sys.exit(1)
        updates["status"] = args.status
    if args.notes is not None:
        updates["notes"] = args.notes
    if args.url:
        updates["url"] = args.url
    if args.resume:
        updates["resume_path"] = args.resume

    if not updates:
        print("Nothing to update. Use --status, --notes, --url, or --resume.")
        return

    updates["updated_at"] = datetime.now().strftime("%Y-%m-%d")
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    conn.execute(f"UPDATE applications SET {set_clause} WHERE id = ?", (*updates.values(), args.id))
    conn.commit()

    color = STATUS_COLORS.get(updates.get("status", row["status"]), "")
    status = updates.get("status", row["status"])
    print(f"{BOLD}Updated #{args.id}{RESET}  {row['company']} — {row['role']}  [{color}{status}{RESET}]")
    if args.notes:
        print(f"  Notes: {args.notes}")


def cmd_show(args):
    conn = get_db()
    row = conn.execute("SELECT * FROM applications WHERE id = ?", (args.id,)).fetchone()
    if not row:
        print(f"No application with id {args.id}")
        sys.exit(1)

    color = STATUS_COLORS.get(row["status"], "")
    print(f"\n{BOLD}#{row['id']} — {row['company']} / {row['role']}{RESET}")
    print(f"  Status:   {color}{row['status']}{RESET}")
    print(f"  Applied:  {row['date_applied']}")
    print(f"  Updated:  {row['updated_at']}")
    if row["url"]:
        print(f"  URL:      {row['url']}")
    if row["resume_path"]:
        print(f"  Resume:   {row['resume_path']}")
    if row["notes"]:
        print(f"  Notes:    {row['notes']}")


def cmd_stats(args):
    conn = get_db()
    rows = conn.execute("SELECT status, COUNT(*) as n FROM applications GROUP BY status").fetchall()
    total = conn.execute("SELECT COUNT(*) as n FROM applications").fetchone()["n"]

    if total == 0:
        print("No applications yet.")
        return

    print(f"\n{BOLD}Application Stats{RESET}")
    print("─" * 30)
    for r in rows:
        color = STATUS_COLORS.get(r["status"], "")
        bar = "█" * r["n"]
        print(f"  {color}{r['status']:<15}{RESET} {bar} {r['n']}")
    print("─" * 30)
    print(f"  {'Total':<15} {total}")

    # Response rate (anything past Applied)
    active = conn.execute(
        "SELECT COUNT(*) as n FROM applications WHERE status NOT IN ('Applied','Saved','Withdrawn')"
    ).fetchone()["n"]
    applied = conn.execute(
        "SELECT COUNT(*) as n FROM applications WHERE status != 'Saved'"
    ).fetchone()["n"]
    if applied > 0:
        rate = round(active / applied * 100)
        print(f"\n  Response rate: {rate}% ({active}/{applied} applications got a response)")


def main():
    parser = argparse.ArgumentParser(description="Job application tracker")
    sub = parser.add_subparsers(dest="command")

    # add
    p_add = sub.add_parser("add", help="Add a new application")
    p_add.add_argument("--company", required=True)
    p_add.add_argument("--role", required=True)
    p_add.add_argument("--url", default="")
    p_add.add_argument("--status", default="Applied", choices=STATUSES)
    p_add.add_argument("--notes", default="")
    p_add.add_argument("--resume", default="", help="Path to tailored resume file")

    # list
    p_list = sub.add_parser("list", help="List applications")
    p_list.add_argument("--status", help="Filter by status")

    # update
    p_update = sub.add_parser("update", help="Update an application")
    p_update.add_argument("id", type=int)
    p_update.add_argument("--status", choices=STATUSES)
    p_update.add_argument("--notes")
    p_update.add_argument("--url")
    p_update.add_argument("--resume")

    # show
    p_show = sub.add_parser("show", help="Show full details of one application")
    p_show.add_argument("id", type=int)

    # stats
    sub.add_parser("stats", help="Show application statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    {"add": cmd_add, "list": cmd_list, "update": cmd_update, "show": cmd_show, "stats": cmd_stats}[args.command](args)


if __name__ == "__main__":
    main()
