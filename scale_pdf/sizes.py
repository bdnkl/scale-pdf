"""DIN-A paper size lookup and derived sheet size calculations."""

from .i18n import tr

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

POINTS_PER_MM = 2.83465


def get_din_a_size_points(din_format):
    mm_width, mm_height = DIN_A_SIZES_MM[din_format]

    # 1 mm entspricht exakt 2.83465 Points
    return mm_width * POINTS_PER_MM, mm_height * POINTS_PER_MM


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
