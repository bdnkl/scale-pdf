"""Core PDF generation operations: scaling, 2-up, booklet, booklet-cut."""

import fitz  # Gehört zur Bibliothek PyMuPDF

from .i18n import tr
from .sizes import get_booklet_sheet_size_points, get_din_a_size_points, get_two_up_sheet_size_points


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
