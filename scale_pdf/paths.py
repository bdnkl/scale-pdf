"""Output file path builders for the different scaling/booklet modes."""


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
