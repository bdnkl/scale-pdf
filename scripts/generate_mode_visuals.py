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
    page = doc.new_page(width=1200, height=760)

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

    page.draw_rect(out, color=(0.2, 0.2, 0.2), fill=(0.95, 0.98, 0.9), width=1.5)
    split_x = (out.x0 + out.x1) / 2
    page.draw_line(fitz.Point(split_x, out.y0), fitz.Point(split_x, out.y1), color=(0.5, 0.5, 0.5), width=1)

    # Simulate optional --2-margin-mm by shrinking printable area.
    margin = 18
    left_half = fitz.Rect(out.x0 + margin, out.y0 + margin, split_x - margin, out.y1 - margin)
    right_half = fitz.Rect(split_x + margin, out.y0 + margin, out.x1 - margin, out.y1 - margin)

    # Reference border (full half area without margin).
    page.draw_rect(fitz.Rect(out.x0, out.y0, split_x, out.y1), color=(0.7, 0.7, 0.7), width=0.8)
    page.draw_rect(fitz.Rect(split_x, out.y0, out.x1, out.y1), color=(0.7, 0.7, 0.7), width=0.8)

    labeled_box(page, left_half, "P1", fill=(0.75, 0.9, 0.75), fs=24)
    labeled_box(page, right_half, "P2", fill=(0.75, 0.9, 0.75), fs=24)

    draw_arrow(page, 510, 430, 630, 430, "place both")

    # Clear margin callout outside the content area.
    callout = fitz.Rect(820, 120, 1170, 180)
    page.draw_rect(callout, color=(0.35, 0.35, 0.35), fill=(1.0, 0.98, 0.86), width=1.2)
    page.insert_textbox(
        callout,
        "--2-margin-mm\nadds inner white space",
        fontsize=16,
        fontname="helv",
        align=1,
        color=(0.15, 0.15, 0.15),
    )
    # Arrow points to the actual gap between gray border and green printable area.
    page.draw_line(fitz.Point(915, 180), fitz.Point(975, 230), color=(0.35, 0.35, 0.35), width=2.2)
    page.draw_line(fitz.Point(975, 230), fitz.Point(960, 227), color=(0.35, 0.35, 0.35), width=2.2)
    page.draw_line(fitz.Point(975, 230), fitz.Point(968, 216), color=(0.35, 0.35, 0.35), width=2.2)

    page.insert_textbox(
        fitz.Rect(640, 700, 1140, 740),
        "Output: A(n-1) landscape. Gray border = full half area; green area = with optional margin.",
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
