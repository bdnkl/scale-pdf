import argparse
from pathlib import Path

import fitz  # Gehört zur Bibliothek PyMuPDF

DIN_A_SIZES_MM = {
    "A0": (841, 1189),
    "A1": (594, 841),
    "A2": (420, 594),
    "A3": (297, 420),
    "A4": (210, 297),
    "A5": (148, 210),
    "A6": (105, 148),
    "A7": (74, 105),
    "A8": (52, 74),
    "A9": (37, 52),
    "A10": (26, 37),
}

LANG_CHOICES = ("de", "en")

MESSAGES = {
    "de": {
        "err_two_up_a0": "2-seiten-pro-seite ist mit A0 nicht möglich, da es kein größeres DIN-A-Format gibt.",
        "ok_booklet": "Erfolgreich als Booklet (Basis {din}, komplett auf Grossbogen/A4 druckbar) gespeichert unter: {path}",
        "ok_booklet_cut": "Erfolgreich als Booklet-Cut (Basis {din}, 1 A5 pro A4 mit leerer Haelfte) gespeichert unter: {path}",
        "ok_two_up": "Erfolgreich im 2-seiten-pro-seite Modus auf Basis {din} skaliert und gespeichert unter: {path}",
        "ok_scaled": "Erfolgreich auf {din} skaliert und gespeichert unter: {path}",
        "prompt_invalid_din": "Ungueltiges DIN-Format. Bitte z.B. A5 oder A4 eingeben.",
        "prompt_invalid_float": "Bitte eine gueltige Zahl eingeben, z.B. 3 oder 2.5",
        "prompt_need_files": "Bitte mindestens eine PDF-Datei angeben.",
        "prompt_files_invalid": "Keine gueltigen Dateipfade erkannt. Bitte erneut eingeben.",
        "ui_title": "\n=== scale-pdf CLI UI ===",
        "ui_choose_mode": "Modus waehlen:",
        "ui_mode_1": "  1) Normales Skalieren - jede PDF-Seite wird auf das gewaehlte DIN-Format gezogen",
        "ui_mode_2": "  2) 2 Seiten pro Seite - zwei Quellseiten auf eine groessere Querformat-Seite",
        "ui_mode_3": "  3) Booklet - Broschueren-Reihenfolge; bei 2 mittleren Seiten mit Einlegeblatt",
        "ui_mode_4": "  4) Booklet-Cut - kein Booklet-Umsortieren; je Blatt nur halbe Seite zum Abschneiden",
        "ui_invalid_mode": "Bitte 1, 2, 3 oder 4 eingeben.",
        "prompt_din": "DIN-Format (A0-A10)",
        "prompt_mode": "Auswahl",
        "prompt_margin": "Innerer Rand je Halbseite in mm",
        "prompt_files": "PDF-Dateien (mehrere mit Komma trennen)",
        "prompt_lang": "Sprache / Language (de/en)",
        "err_opt_2up_combo": "--2-on-page kann nicht mit --booklet oder --booklet-cut kombiniert werden.",
        "err_opt_booklet_combo": "Bitte nur --booklet oder --booklet-cut verwenden, nicht beides.",
        "err_opt_margin": "--2-margin-mm darf nicht negativ sein.",
        "skip_invalid_pdf": "Uebersprungen (keine gueltige PDF-Datei): {path}",
        "err_processing_file": "Fehler bei {path}: {err}",
        "info_no_files_ui": "Keine Dateien angegeben. Starte interaktive CLI-Oberflaeche.",
        "argparse_desc": "Skaliert PDF-Dateien auf ein DIN-A-Format (A0-A10) und speichert sie als *_scaled.pdf im gleichen Ordner.",
        "argparse_epilog": (
            "Beispiele:\n"
            "  uv run .\\main.py --din A5 .\\datei.pdf\n"
            "  uv run .\\main.py --din A4 .\\a.pdf .\\b.pdf\n"
            "  uv run .\\main.py --din A5 --2-on-page .\\broschuere.pdf\n"
            "  uv run .\\main.py --din A5 --booklet .\\broschuere.pdf\n"
            "  uv run .\\main.py --din A5 --booklet-cut .\\broschuere.pdf"
        ),
    },
    "en": {
        "err_two_up_a0": "2-up is not possible with A0 because there is no larger DIN-A format.",
        "ok_booklet": "Saved successfully as booklet (base {din}, fully printable on larger sheet/A4): {path}",
        "ok_booklet_cut": "Saved successfully as booklet-cut (base {din}, one A5 per A4 with half left blank): {path}",
        "ok_two_up": "Saved successfully in 2-up mode based on {din}: {path}",
        "ok_scaled": "Saved successfully scaled to {din}: {path}",
        "prompt_invalid_din": "Invalid DIN format. Please enter e.g. A5 or A4.",
        "prompt_invalid_float": "Please enter a valid number, e.g. 3 or 2.5",
        "prompt_need_files": "Please provide at least one PDF file.",
        "prompt_files_invalid": "No valid file paths detected. Please try again.",
        "ui_title": "\n=== scale-pdf CLI UI ===",
        "ui_choose_mode": "Choose mode:",
        "ui_mode_1": "  1) Normal scaling - each page is stretched to the selected DIN format",
        "ui_mode_2": "  2) 2-up - place two source pages on one larger landscape page",
        "ui_mode_3": "  3) Booklet - booklet page order; uses insert sheet for 2 remaining middle pages",
        "ui_mode_4": "  4) Booklet-cut - no booklet reordering; half-page print per sheet for cutting",
        "ui_invalid_mode": "Please enter 1, 2, 3, or 4.",
        "prompt_din": "DIN format (A0-A10)",
        "prompt_mode": "Selection",
        "prompt_margin": "Inner margin per half page in mm",
        "prompt_files": "PDF files (separate multiple entries with commas)",
        "prompt_lang": "Language / Sprache (de/en)",
        "err_opt_2up_combo": "--2-on-page cannot be combined with --booklet or --booklet-cut.",
        "err_opt_booklet_combo": "Use either --booklet or --booklet-cut, not both.",
        "err_opt_margin": "--2-margin-mm must not be negative.",
        "skip_invalid_pdf": "Skipped (not a valid PDF file): {path}",
        "err_processing_file": "Error processing {path}: {err}",
        "info_no_files_ui": "No files provided. Starting interactive CLI UI.",
        "argparse_desc": "Scales PDF files to DIN-A format (A0-A10) and saves them as *_scaled.pdf in the same folder.",
        "argparse_epilog": (
            "Examples:\n"
            "  uv run .\\main.py --din A5 .\\file.pdf\n"
            "  uv run .\\main.py --din A4 .\\a.pdf .\\b.pdf\n"
            "  uv run .\\main.py --din A5 --2-on-page .\\brochure.pdf\n"
            "  uv run .\\main.py --din A5 --booklet .\\brochure.pdf\n"
            "  uv run .\\main.py --din A5 --booklet-cut .\\brochure.pdf"
        ),
    },
}


def tr(lang, key, **kwargs):
    language = lang if lang in MESSAGES else "de"
    template = MESSAGES[language][key]
    if kwargs:
        return template.format(**kwargs)
    return template


def get_din_a_size_points(din_format):
    mm_width, mm_height = DIN_A_SIZES_MM[din_format]

    # 1 mm entspricht exakt 2.83465 Points
    return mm_width * 2.83465, mm_height * 2.83465


def get_two_up_sheet_size_points(din_format, lang="de"):
    din_number = int(din_format[1:])

    if din_number == 0:
        raise ValueError(tr(lang, "err_two_up_a0"))

    parent_format = f"A{din_number - 1}"
    parent_width, parent_height = get_din_a_size_points(parent_format)

    # Querformat nutzen: z.B. A4 quer für 2x A5 hochkant
    return parent_height, parent_width


def get_booklet_sheet_size_points(din_format, lang="de"):
    return get_two_up_sheet_size_points(din_format, lang)


def _place_page(target_page, target_rect, source_doc, source_page_index):
    if source_page_index is None:
        return

    target_page.show_pdf_page(
        target_rect,
        source_doc,
        source_page_index,
        keep_proportion=False,
    )


def inset_rect(rect, margin_points):
    if margin_points <= 0:
        return rect

    # Margin darf nie größer als die halbe Breite/Höhe sein.
    max_margin = min(rect.width / 2, rect.height / 2)
    safe_margin = min(margin_points, max_margin)
    return fitz.Rect(
        rect.x0 + safe_margin,
        rect.y0 + safe_margin,
        rect.x1 - safe_margin,
        rect.y1 - safe_margin,
    )


def create_booklet_pdf(input_path, output_path, din_format, lang="de"):
    doc = fitz.open(input_path)
    new_doc = fitz.open()

    sheet_width, sheet_height = get_booklet_sheet_size_points(din_format, lang)
    left_rect = fitz.Rect(0, 0, sheet_width / 2, sheet_height)
    right_rect = fitz.Rect(sheet_width / 2, 0, sheet_width, sheet_height)

    source_indices = list(range(doc.page_count))

    # Eine Einlage hat Vorder- und Rückseite, daher auf gerade Seitenzahl auffüllen.
    while len(source_indices) % 2 != 0:
        source_indices.append(None)

    left = 0
    right = len(source_indices) - 1

    # Außenseiten als klassische Booklet-Bögen (A(n-1)-Querformat) erzeugen.
    while (right - left + 1) > 2:
        front_left = source_indices[right]
        front_right = source_indices[left]
        left += 1
        right -= 1

        front_page = new_doc.new_page(width=sheet_width, height=sheet_height)
        _place_page(front_page, left_rect, doc, front_left)
        _place_page(front_page, right_rect, doc, front_right)

        back_left = source_indices[left]
        back_right = source_indices[right]
        left += 1
        right -= 1

        back_page = new_doc.new_page(width=sheet_width, height=sheet_height)
        _place_page(back_page, left_rect, doc, back_left)
        _place_page(back_page, right_rect, doc, back_right)

    # Bleiben 2 mittlere Seiten übrig, als Einlegeblatt auf A4 ausgeben
    # (pro Seite nur eine Hälfte bedruckt, andere Hälfte leer zum Schneiden).
    if (right - left + 1) == 2:
        insert_front = new_doc.new_page(width=sheet_width, height=sheet_height)
        _place_page(
            insert_front,
            right_rect,
            doc,
            source_indices[left],
        )

        insert_back = new_doc.new_page(width=sheet_width, height=sheet_height)
        _place_page(
            insert_back,
            left_rect,
            doc,
            source_indices[left + 1],
        )

    new_doc.save(output_path)
    new_doc.close()
    doc.close()

    print(tr(lang, "ok_booklet", din=din_format, path=output_path))


def create_booklet_cut_pdf(input_path, output_path, din_format, lang="de"):
    doc = fitz.open(input_path)
    new_doc = fitz.open()

    sheet_width, sheet_height = get_booklet_sheet_size_points(din_format, lang)
    left_rect = fitz.Rect(0, 0, sheet_width / 2, sheet_height)
    right_rect = fitz.Rect(sheet_width / 2, 0, sheet_width, sheet_height)

    source_indices = list(range(doc.page_count))

    # Für Vorder-/Rückseite pro A5-Blatt sind Paare nötig.
    while len(source_indices) % 2 != 0:
        source_indices.append(None)

    for i in range(0, len(source_indices), 2):
        front_index = source_indices[i]
        back_index = source_indices[i + 1]

        # Vorderseite: Inhalt rechts, links leer (zum späteren Abschneiden).
        front_page = new_doc.new_page(width=sheet_width, height=sheet_height)
        _place_page(front_page, right_rect, doc, front_index)

        # Rückseite: Inhalt links, rechts leer, sodass nach Duplexdruck
        # Vorder-/Rückseite desselben A5-Blattes entstehen.
        back_page = new_doc.new_page(width=sheet_width, height=sheet_height)
        _place_page(back_page, left_rect, doc, back_index)

    new_doc.save(output_path)
    new_doc.close()
    doc.close()

    print(tr(lang, "ok_booklet_cut", din=din_format, path=output_path))


def scale_pdf_to_din_ax(input_path, output_path, din_format, two_on_page=False, two_on_page_margin_mm=0.0, lang="de"):
    # 1. Original-PDF öffnen
    doc = fitz.open(input_path)
    new_doc = fitz.open()

    if two_on_page:
        # 2-up: Ausgabeseite ist das nächstgrößere DIN-A-Format im Querformat
        sheet_width, sheet_height = get_two_up_sheet_size_points(din_format, lang)
        left_rect = fitz.Rect(0, 0, sheet_width / 2, sheet_height)
        right_rect = fitz.Rect(sheet_width / 2, 0, sheet_width, sheet_height)

        margin_points = two_on_page_margin_mm * 2.83465
        left_rect = inset_rect(left_rect, margin_points)
        right_rect = inset_rect(right_rect, margin_points)

        # Jeweils zwei Quellseiten auf eine Ausgabeseite setzen
        for page_index in range(0, doc.page_count, 2):
            new_page = new_doc.new_page(width=sheet_width, height=sheet_height)

            # Vollständige Halbseiten-Ausnutzung durch Dehnen auf das Halbfeld
            new_page.show_pdf_page(left_rect, doc, page_index, keep_proportion=False)

            if page_index + 1 < doc.page_count:
                new_page.show_pdf_page(right_rect, doc, page_index + 1, keep_proportion=False)

            # Dünner grauer Trennstrich in der Mitte
            split_x = sheet_width / 2
            new_page.draw_line(
                fitz.Point(split_x, 0),
                fitz.Point(split_x, sheet_height),
                color=(0.7, 0.7, 0.7),
                width=0.5,
            )
    else:
        # 2. Zielmaße (DIN A0-A10) von Millimeter in Punkte (Points) umrechnen
        target_width, target_height = get_din_a_size_points(din_format)
        target_rect = fitz.Rect(0, 0, target_width, target_height)

        # 3. Jede Seite auf das gewünschte DIN-A-Format skalieren
        for page in doc:
            # Neue leere Seite im Ziel-Format erstellen
            new_page = new_doc.new_page(width=target_width, height=target_height)
            
            # Inhalt der alten Seite auf die Ziel-Größe skalieren und platzieren
            new_page.show_pdf_page(target_rect, doc, page.number)

    # 4. Das neue skalierte PDF speichern
    new_doc.save(output_path)
    new_doc.close()
    doc.close()

    if two_on_page:
        print(tr(lang, "ok_two_up", din=din_format, path=output_path))
    else:
        print(tr(lang, "ok_scaled", din=din_format, path=output_path))


def build_output_path(input_path, din_format, two_on_page=False):
    if two_on_page:
        suffix = f"scaled_2up_{din_format.lower()}"
    elif din_format != "A5":
        suffix = f"scaled_{din_format.lower()}"
    else:
        suffix = "scaled"

    return input_path.with_name(f"{input_path.stem}_{suffix}.pdf")


def build_booklet_output_path(input_path, din_format, signature=False):
    if signature:
        return input_path.with_name(f"{input_path.stem}_scaled_booklet_cut_{din_format.lower()}.pdf")
    return input_path.with_name(f"{input_path.stem}_scaled_booklet_{din_format.lower()}.pdf")


def _prompt_text(prompt, default=None):
    if default is None:
        suffix = ""
    else:
        suffix = f" [{default}]"

    value = input(f"{prompt}{suffix}: ").strip()
    if value:
        return value
    return default


def _prompt_din_format(lang, default="A5"):
    while True:
        din_format = _prompt_text(tr(lang, "prompt_din"), default=default)
        if din_format is None:
            din_format = default
        din_format = din_format.upper()

        if din_format in DIN_A_SIZES_MM:
            return din_format

        print(tr(lang, "prompt_invalid_din"))


def _prompt_float(lang, prompt, default=0.0):
    while True:
        raw = _prompt_text(prompt, default=str(default))
        try:
            return float(raw)
        except (TypeError, ValueError):
            print(tr(lang, "prompt_invalid_float"))


def _prompt_files(lang):
    while True:
        raw = _prompt_text(tr(lang, "prompt_files"))
        if not raw:
            print(tr(lang, "prompt_need_files"))
            continue

        files = [part.strip().strip('"').strip("'") for part in raw.split(",") if part.strip()]
        if files:
            return files

        print(tr(lang, "prompt_files_invalid"))


def run_cli_ui(default_lang="de"):
    selected_lang = _prompt_text(tr(default_lang, "prompt_lang"), default=default_lang)
    if selected_lang is None:
        selected_lang = default_lang
    selected_lang = selected_lang.lower()
    if selected_lang not in LANG_CHOICES:
        selected_lang = default_lang

    print(tr(selected_lang, "ui_title"))
    print(tr(selected_lang, "ui_choose_mode"))
    print(tr(selected_lang, "ui_mode_1"))
    print(tr(selected_lang, "ui_mode_2"))
    print(tr(selected_lang, "ui_mode_3"))
    print(tr(selected_lang, "ui_mode_4"))

    mode = _prompt_text(tr(selected_lang, "prompt_mode"), default="1")
    while mode not in {"1", "2", "3", "4"}:
        print(tr(selected_lang, "ui_invalid_mode"))
        mode = _prompt_text(tr(selected_lang, "prompt_mode"), default="1")

    din_format = _prompt_din_format(selected_lang, default="A5")

    two_on_page = mode == "2"
    booklet = mode == "3"
    booklet_cut = mode == "4"
    two_margin_mm = 0.0

    if two_on_page:
        two_margin_mm = _prompt_float(selected_lang, tr(selected_lang, "prompt_margin"), default=0.0)

    files = _prompt_files(selected_lang)

    return argparse.Namespace(
        din=din_format,
        two_on_page=two_on_page,
        two_margin_mm=two_margin_mm,
        booklet=booklet,
        booklet_cut=booklet_cut,
        files=files,
        lang=selected_lang,
        ui=True,
    )


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


def main():
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


if __name__ == "__main__":
    main()
