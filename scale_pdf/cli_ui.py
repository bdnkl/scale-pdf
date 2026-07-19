"""Small interactive CLI UI (prompts) for choosing mode, DIN format, and files."""

import argparse

from .i18n import LANG_CHOICES, tr
from .sizes import DIN_A_SIZES_MM


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
