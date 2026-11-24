"""shelf list [--status STATUS]"""

from __future__ import annotations

import argparse

from shelf.models import STATUSES
from shelf.store import Store


def register(subparsers) -> None:
    parser = subparsers.add_parser("list", help="show the books on your shelf")
    parser.add_argument("--status", choices=STATUSES, help="show only books with this status")
    parser.set_defaults(handler=run)


def run(args: argparse.Namespace, store: Store) -> int:
    books = store.load()
    if args.status is not None:
        books = [book for book in books if book.status == args.status]
        if not books:
            print(f"No books with status {args.status}.")
            return 0
    if not books:
        print("Your shelf is empty. Add a book with: shelf add TITLE AUTHOR")
        return 0
    for book in books:
        print(book)
    return 0
