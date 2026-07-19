"""Argument parsing, validation, and per-file processing for scale-pdf."""

import argparse
from pathlib import Path

from .cli_ui import run_cli_ui
from .i18n import LANG_CHOICES, tr
from .paths import build_booklet_output_path, build_output_path
from .pdf_ops import create_booklet_cut_pdf, create_booklet_pdf, scale_pdf_to_din_ax
from .sizes import DIN_A_SIZES_MM


def validate_options(two_on_page, booklet, booklet_cut, two_margin_mm, lang="de"):
    if two_on_page and (booklet or booklet_cut):
        raise ValueError(tr(lang, "err_opt_2up_combo"))
    if booklet and booklet_cut:
        raise ValueError(tr(lang, "err_opt_booklet_combo"))
    if two_margin_mm < 0:
        raise ValueError(tr(lang, "err_opt_margin"))


def process_files(args):
    had_error = False

    for file_arg in args.files:
        input_path = Path(file_arg).expanduser().resolve()

        if not input_path.exists() or input_path.suffix.lower() != ".pdf":
            print(tr(args.lang, "skip_invalid_pdf", path=input_path))
            had_error = True
            continue

        if args.booklet or args.booklet_cut:
            output_path = build_booklet_output_path(input_path, args.din, signature=args.booklet_cut)
        else:
            output_path = build_output_path(input_path, args.din, two_on_page=args.two_on_page)

        try:
            if args.booklet:
                create_booklet_pdf(
                    str(input_path),
                    str(output_path),
                    args.din,
                    lang=args.lang,
                )
            elif args.booklet_cut:
                create_booklet_cut_pdf(
                    str(input_path),
                    str(output_path),
                    args.din,
                    lang=args.lang,
                )
            else:
                scale_pdf_to_din_ax(
                    str(input_path),
                    str(output_path),
                    args.din,
                    two_on_page=args.two_on_page,
                    two_on_page_margin_mm=args.two_margin_mm,
                    lang=args.lang,
                )
        except Exception as exc:
            print(tr(args.lang, "err_processing_file", path=input_path, err=exc))
            had_error = True

    return had_error


def build_arg_parser():
    parser = argparse.ArgumentParser(
        description=tr("de", "argparse_desc"),
        epilog=tr("de", "argparse_epilog"),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--lang",
        choices=LANG_CHOICES,
        default="de",
        help="Output language: de (default) or en",
    )
    parser.add_argument(
        "--ui",
        action="store_true",
        help="Startet eine kleine interaktive CLI-Oberfläche mit Modus-Auswahl und Eingabehilfen.",
    )
    parser.add_argument(
        "--din",
        default="A5",
        type=str.upper,
        choices=DIN_A_SIZES_MM.keys(),
        help="Ziel-DIN-Format (Standard: A5)",
    )
    parser.add_argument(
        "--2-on-page",
        "--2",
        dest="two_on_page",
        action="store_true",
        help=(
            "Setzt jeweils 2 Quellseiten auf 1 Ausgabeseite mit Trennstrich. "
            "Die Ausgabeseite wird dabei das nächstgrößere DIN-Format im Querformat "
            "(z.B. DIN A5 -> DIN A4 quer)."
        ),
    )
    parser.add_argument(
        "--2-margin-mm",
        dest="two_margin_mm",
        type=float,
        default=0.0,
        help=(
            "Innerer weißer Rand pro Halbseite im 2-on-page-Modus in Millimetern "
            "(z.B. 3.0)."
        ),
    )
    parser.add_argument(
        "--booklet",
        action="store_true",
        help=(
            "Klassisches Booklet: links letzte/rechts erste Seite, dann Rückseite usw. "
            "Bei Rest von 2 Seiten wird automatisch ein Einlegeblatt als halb bedrucktes A4-Blatt erzeugt "
            "(z.B. bei 6 Seiten: 2x A4 beidseitig, davon 1 Blatt als Einlage)."
        ),
    )
    parser.add_argument(
        "--booklet-cut",
        action="store_true",
        help=(
            "Schnittmodus ohne Booklet-Umsortierung: pro A4 nur eine Hälfte bedruckt, "
            "andere Hälfte leer zum Abschneiden. Vorder-/Rückseite bilden direkt ein A5-Blatt "
            "(Seite 1/2, 3/4, ...), kein Einlegeblatt-Layout."
        ),
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="PDF-Datei(en), z.B. per Drag-and-Drop auf das Skript oder in die Konsole ziehen",
    )
    return parser


def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.lang == "en":
        parser.description = tr("en", "argparse_desc")
        parser.epilog = tr("en", "argparse_epilog")

    if args.ui or not args.files:
        if not args.ui and not args.files:
            print(tr(args.lang, "info_no_files_ui"))
        args = run_cli_ui(default_lang=args.lang)

    try:
        validate_options(
            two_on_page=args.two_on_page,
            booklet=args.booklet,
            booklet_cut=args.booklet_cut,
            two_margin_mm=args.two_margin_mm,
            lang=args.lang,
        )
    except ValueError as exc:
        parser.error(str(exc))

    had_error = process_files(args)

    if had_error:
        raise SystemExit(1)
