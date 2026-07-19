"""Bilingual (German/English) message catalog and lookup helper."""

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
