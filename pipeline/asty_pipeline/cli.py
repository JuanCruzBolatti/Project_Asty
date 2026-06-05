import argparse

from asty_pipeline.lanus.build import build_lanus


def main():

    parser = argparse.ArgumentParser(
        description="Asty Pipeline CLI"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Command to execute"
    )

    # Build Lanús
    build_parser = subparsers.add_parser(
        "build-lanus",
        help="Build Lanús dataset"
    )

    build_parser.add_argument(
        "--year",
        type=int,
        required=True,
    )

    build_parser.add_argument(
        "--quarter",
        type=int,
        required=True,
        choices=[1, 2, 3, 4],
    )

    build_parser.add_argument(
        "--force-download",
        action="store_true",
    )

    args = parser.parse_args()

    if args.command == "build-lanus":

        build_lanus(
            year=args.year,
            quarter=args.quarter,
            force_download=args.force_download
        )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()