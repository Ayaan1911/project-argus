"""
ai_layer/scraper/run_scraper.py
=================================
CLI entry point for the Argus web scraper.

Runs the Playwright scraper for all target cities and saves results
to ai_layer/datasets/listings_dataset.json. Falls back to BS4Scraper
if Playwright is not installed.

Usage:
    # From the backend/ directory:
    python -m ai_layer.scraper.run_scraper
    python -m ai_layer.scraper.run_scraper --city mumbai
    python -m ai_layer.scraper.run_scraper --city mumbai --city delhi
    python -m ai_layer.scraper.run_scraper --max-pages 3
    python -m ai_layer.scraper.run_scraper --scraper bs4
    python -m ai_layer.scraper.run_scraper --dry-run

Options:
    --city        City to scrape (can be repeated). Defaults to all in config.CITIES.
    --max-pages   Max listing pages per city. Defaults to config.MAX_PAGES.
    --scraper     Scraper backend: 'playwright' (default) or 'bs4'.
    --dry-run     Print resolved config and exit without scraping.
    --output      Override dataset output path.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Ensure the backend/ directory is on sys.path when run as a script
_BACKEND_DIR = Path(__file__).resolve().parents[3]  # backend/../..  → project root
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

# Also ensure backend/ itself is on path (for `from ai_layer import ...` imports)
_BACKEND = Path(__file__).resolve().parents[2]  # ai_layer/ → backend/
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from ai_layer.config import CITIES, DATASET_PATH, LOG_PREFIX, MAX_PAGES
from ai_layer.scraper.dataset_manager import DatasetManager


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="argus-scraper",
        description="Project Argus — Web Scraper for Rental Listing Dataset Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m ai_layer.scraper.run_scraper
  python -m ai_layer.scraper.run_scraper --city bangalore --max-pages 3
  python -m ai_layer.scraper.run_scraper --scraper bs4 --city mumbai
  python -m ai_layer.scraper.run_scraper --dry-run
        """,
    )
    parser.add_argument(
        "--city",
        action="append",
        dest="cities",
        metavar="CITY",
        help="City to scrape (repeat for multiple). Defaults to all cities in config.py.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=MAX_PAGES,
        metavar="N",
        help=f"Max listing pages per city per platform (default: {MAX_PAGES}).",
    )
    parser.add_argument(
        "--scraper",
        choices=["playwright", "bs4"],
        default="playwright",
        help="Scraper backend to use (default: playwright).",
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="PATH",
        help=f"Override dataset output path (default: {DATASET_PATH}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print resolved config and exit without scraping.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default: INFO).",
    )
    return parser.parse_args()


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
        datefmt="%H:%M:%S",
        level=getattr(logging, level),
    )


def _dry_run(args: argparse.Namespace, target_cities: list[str]) -> None:
    """Print the resolved configuration and exit."""
    output_path = Path(args.output).resolve() if args.output else Path(DATASET_PATH).resolve()
    print(f"""
╔══════════════════════════════════════════════════╗
║         Project Argus — Scraper Dry Run          ║
╠══════════════════════════════════════════════════╣
  Scraper backend : {args.scraper}
  Cities          : {', '.join(target_cities)}
  Max pages       : {args.max_pages}
  Output dataset  : {output_path}
  Log level       : {args.log_level}
╚══════════════════════════════════════════════════╝
""")


def _run_playwright(cities: list[str], dataset_manager: DatasetManager, max_pages: int) -> dict:
    """Launch Playwright scraper, fall back to BS4 on error."""
    try:
        from ai_layer.scraper.playwright_scraper import PlaywrightScraper
        scraper = PlaywrightScraper()
        return asyncio.run(scraper.run(cities=cities, dataset_manager=dataset_manager, max_pages=max_pages))
    except ImportError:
        print(
            f"\n{LOG_PREFIX} ⚠  Playwright not installed.\n"
            "  Install with: pip install playwright && playwright install chromium\n"
            f"{LOG_PREFIX} Falling back to BS4 scraper …\n"
        )
        return _run_bs4(cities, dataset_manager, max_pages)
    except Exception as err:
        print(f"\n{LOG_PREFIX} ⚠  Playwright error: {err}\n{LOG_PREFIX} Falling back to BS4 …\n")
        return _run_bs4(cities, dataset_manager, max_pages)


def _run_bs4(cities: list[str], dataset_manager: DatasetManager, max_pages: int) -> dict:
    from ai_layer.scraper.bs4_scraper import BS4Scraper
    scraper = BS4Scraper()
    return scraper.run(cities=cities, dataset_manager=dataset_manager, max_pages=max_pages)


def main() -> None:
    args = _parse_args()
    _configure_logging(args.log_level)

    target_cities = args.cities if args.cities else CITIES

    if args.dry_run:
        _dry_run(args, target_cities)
        return

    output_path = Path(args.output).resolve() if args.output else None
    dm = DatasetManager(path=output_path)

    print(f"\n{LOG_PREFIX} Starting scraper — cities: {target_cities}, max_pages: {args.max_pages}")
    print(f"{LOG_PREFIX} Dataset → {dm.dataset_path}\n")

    if args.scraper == "playwright":
        metrics = _run_playwright(target_cities, dm, args.max_pages)
    else:
        metrics = _run_bs4(target_cities, dm, args.max_pages)

    print(f"\n## Scraper Metrics\n")
    print(f"pages_scraped:      {metrics.get('pages_scraped', 0)}")
    print(f"listings_found:     {metrics.get('listings_found', 0)}")
    print(f"duplicates_skipped: {metrics.get('duplicates_skipped', 0)}")
    print(f"errors:             {metrics.get('errors', 0)}")

    print(f"\n{LOG_PREFIX} ✅  Done. Total listings in dataset: {dm.total()}")
    print(f"{LOG_PREFIX} Saved to: {dm.dataset_path}\n")


if __name__ == "__main__":
    main()
