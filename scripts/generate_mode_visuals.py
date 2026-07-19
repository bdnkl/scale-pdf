from pathlib import Path

import fitz


OUT_DIR = Path("examples")
OUT_DIR.mkdir(exist_ok=True)


def draw_header(page, title, subtitle):
    page.insert_textbox(
        fitz.Rect(40, 20, 1160, 90),
        title,
        fontsize=32,
        fontname="helv",
        color=(0.1, 0.1, 0.1),
    )
    page.insert_textbox(
        fitz.Rect(40, 70, 1160, 130),
        subtitle,
        fontsize=16,
        fontname="helv",
        color=(0.25, 0.25, 0.25),
    )


def labeled_box(page, rect, label, fill, stroke=(0.2, 0.2, 0.2), fs=18):
    page.draw_rect(rect, color=stroke, fill=fill, width=1.5)
    page.insert_textbox(
        rect,
        label,
        fontsize=fs,
        fontname="helv",
        align=1,
        color=(0.05, 0.05, 0.05),
    )


def draw_arrow(page, x0, y0, x1, y1, label=None):
    page.draw_line(fitz.Point(x0, y0), fitz.Point(x1, y1), color=(0.3, 0.3, 0.3), width=2)
    # Small arrow head
    page.draw_line(fitz.Point(x1, y1), fitz.Point(x1 - 12, y1 - 8), color=(0.3, 0.3, 0.3), width=2)
    page.draw_line(fitz.Point(x1, y1), fitz.Point(x1 - 12, y1 + 8), color=(0.3, 0.3, 0.3), width=2)
    if label:
        page.insert_textbox(
            fitz.Rect((x0 + x1) / 2 - 90, (y0 + y1) / 2 - 18, (x0 + x1) / 2 + 90, (y0 + y1) / 2 + 18),
            label,
            fontsize=13,
            fontname="helv",
            align=1,
            color=(0.2, 0.2, 0.2),
        )


def export_page(page, out_path):
    pix = page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6), alpha=False)
    pix.save(out_path)


def visual_normal_scaling():
    doc = fitz.open()
    page = doc.new_page(width=1200, height=760)

    draw_header(
        page,
        "Mode 1: Normal scaling",
        "Each source page is scaled to exactly one target DIN page.",
    )

    left = fitz.Rect(80, 180, 480, 680)
    right = fitz.Rect(720, 180, 1120, 680)

    labeled_box(page, left, "Source page\n(A4)", fill=(0.87, 0.93, 1.0))
    labeled_box(page, right, "Output page\n(A5)", fill=(0.86, 0.97, 0.89))
    draw_arrow(page, 500, 430, 700, 430, "scale")

    export_page(page, OUT_DIR / "mode_normal_scaling.png")
    doc.close()


def visual_two_up():
    doc = fitz.open()
    page = doc.new_page(width=1200, height=820)

    draw_header(
        page,
        "Mode 2: 2-up",
        "Two source pages are placed on one larger landscape page.",
    )

    src1 = fitz.Rect(70, 200, 260, 650)
    src2 = fitz.Rect(300, 200, 490, 650)
    out = fitz.Rect(650, 170, 1140, 690)

    labeled_box(page, src1, "P1", fill=(0.87, 0.93, 1.0), fs=28)
    labeled_box(page, src2, "P2", fill=(0.87, 0.93, 1.0), fs=28)

    # Pale green = full half area (this is what stays visible as the margin).
    page.draw_rect(out, color=(0.2, 0.2, 0.2), fill=(0.85, 0.95, 0.85), width=1.5)
    split_x = (out.x0 + out.x1) / 2
    page.draw_line(fitz.Point(split_x, out.y0), fitz.Point(split_x, out.y1), color=(0.5, 0.5, 0.5), width=1)

    # Darker green = actual printable area after applying --2-margin-mm.
    margin = 18
    left_half = fitz.Rect(out.x0 + margin, out.y0 + margin, split_x - margin, out.y1 - margin)
    right_half = fitz.Rect(split_x + margin, out.y0 + margin, out.x1 - margin, out.y1 - margin)

    labeled_box(page, left_half, "P1", fill=(0.45, 0.75, 0.45), fs=24)
    labeled_box(page, right_half, "P2", fill=(0.45, 0.75, 0.45), fs=24)

    draw_arrow(page, 510, 430, 630, 430, "place both")

    # Callout sits below the sheet and points straight up into the pale green
    # margin strip at the bottom of the right half (well away from the P2 label).
    gap_target = fitz.Point(split_x + (out.x1 - split_x) / 2, out.y1 - margin / 2)
    callout = fitz.Rect(gap_target.x - 140, 715, gap_target.x + 140, 762)
    page.draw_rect(callout, color=(0.35, 0.35, 0.35), fill=(1.0, 0.98, 0.86), width=1.2)
    page.insert_textbox(
        callout,
        "--2-margin-mm\npale green = margin",
        fontsize=14,
        fontname="helv",
        align=1,
        color=(0.15, 0.15, 0.15),
    )
    draw_arrow(page, gap_target.x, 713, gap_target.x, gap_target.y + 4)

    page.insert_textbox(
        fitz.Rect(640, 775, 1140, 810),
        "Dark green = printable area; pale green = margin (0 by default).",
        fontsize=13,
        fontname="helv",
        align=1,
        color=(0.25, 0.25, 0.25),
    )

    export_page(page, OUT_DIR / "mode_2up.png")
    doc.close()


def visual_booklet():
    doc = fitz.open()
    page = doc.new_page(width=1300, height=860)

    draw_header(
        page,
        "Mode 3: Booklet",
        "Booklet reordering, plus automatic insert sheet if 2 middle pages remain.",
    )

    # Example mapping for 6 pages: [6|1], [2|5], insert [ |3], [4| ]
    slots = [
        (fitz.Rect(70, 190, 610, 360), "Sheet 1 Front: [6 | 1]"),
        (fitz.Rect(690, 190, 1230, 360), "Sheet 1 Back:  [2 | 5]"),
        (fitz.Rect(70, 430, 610, 600), "Insert Front:   [  | 3]"),
        (fitz.Rect(690, 430, 1230, 600), "Insert Back:    [4 |  ]"),
    ]

    for rect, label in slots:
        page.draw_rect(rect, color=(0.2, 0.2, 0.2), fill=(0.95, 0.91, 0.82), width=1.5)
        split_x = (rect.x0 + rect.x1) / 2
        page.draw_line(fitz.Point(split_x, rect.y0), fitz.Point(split_x, rect.y1), color=(0.45, 0.45, 0.45), width=1)
        page.insert_textbox(
            fitz.Rect(rect.x0 + 10, rect.y0 + 10, rect.x1 - 10, rect.y1 - 10),
            label,
            fontsize=19,
            fontname="helv",
            align=1,
            color=(0.1, 0.1, 0.1),
        )

    page.insert_textbox(
        fitz.Rect(70, 660, 1230, 820),
        "This mode prepares folding order. If exactly two middle pages are left,\n"
        "the script creates an insert sheet with half-page printing automatically.",
        fontsize=15,
        fontname="helv",
        align=1,
        color=(0.25, 0.25, 0.25),
    )

    export_page(page, OUT_DIR / "mode_booklet.png")
    doc.close()


def visual_booklet_cut():
    doc = fitz.open()
    page = doc.new_page(width=1300, height=860)

    draw_header(
        page,
        "Mode 4: Booklet-cut",
        "No booklet reordering. Pairwise printing for cutting: 1/2, 3/4, 5/6 ...",
    )

    rows = [
        (fitz.Rect(90, 190, 1210, 320), "Sheet A: front [ | 1]  back [2 | ]"),
        (fitz.Rect(90, 360, 1210, 490), "Sheet B: front [ | 3]  back [4 | ]"),
        (fitz.Rect(90, 530, 1210, 660), "Sheet C: front [ | 5]  back [6 | ]"),
    ]

    for rect, text in rows:
        page.draw_rect(rect, color=(0.2, 0.2, 0.2), fill=(0.87, 0.94, 0.98), width=1.5)
        page.insert_textbox(
            fitz.Rect(rect.x0 + 15, rect.y0 + 15, rect.x1 - 15, rect.y1 - 15),
            text,
            fontsize=23,
            fontname="helv",
            align=1,
            color=(0.08, 0.08, 0.08),
        )

    page.insert_textbox(
        fitz.Rect(90, 700, 1210, 820),
        "Use this when you want simple duplex pairs per cut sheet,\n"
        "not a folded booklet order.",
        fontsize=15,
        fontname="helv",
        align=1,
        color=(0.25, 0.25, 0.25),
    )

    export_page(page, OUT_DIR / "mode_booklet_cut.png")
    doc.close()


def main():
    visual_normal_scaling()
    visual_two_up()
    visual_booklet()
    visual_booklet_cut()
    print(f"Created visuals in: {OUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
