#!/usr/bin/env python

import os
import re


def read_lines(the_file):
    with open(the_file, 'r') as f:
        return f.readlines()


dir_path = os.path.dirname(os.path.realpath(__file__))

bashprofile_path = os.path.join(dir_path, "bashprofile.sh")

lines = read_lines(bashprofile_path)


MAPPER = {}


def parse_group(rgx, text):
    match = re.search(rgx, text)
    # match.group() will throw an error if empty
    try:
        return match.groups()[0]
    except:
        return None


def is_category_name(text):
    """
    A category name looks like:
        # GIT*
        #GIT*
    """
    rgx = r"^\s*[#]\s*(.*?)[*]"
    return parse_group(rgx, text)


def is_category_name_ending_here(text):
    rgx = r"\s*[#]\s*END\s*"
    return bool(re.search(rgx, text))


def is_alias(text):
    rgx = r"""^alias """
    match = re.search(rgx, text)
    if match:
        name_rgx = r"^alias (.*?)[=]"
        name = parse_group(name_rgx, text)
        command_rgx = r"[=](.*?)\s+$"
        command_raw = parse_group(command_rgx, text)
        command_raw = command_raw.strip()
        command = command_raw[1:-1]
        return {'name': name, 'command': command}
    else:
        return None


def is_bash_function(text):
    rgx = r"""^(\w+)\s*[(][)]\s*[{]"""
    return parse_group(rgx, text)


def is_single_line_bash_function(text):
    rgx = r"""^\w+\s*[(][)]\s*[{](.*?)[}]"""
    group = parse_group(rgx, text)
    try:
        return group.strip()
    except:
        return None



def is_script(text):
    rgx = r"""[.](rb|py|sh)('|")\s*$"""
    return parse_group(rgx, text)


def is_filepath(text):
    rgx = r"""^(?P<name>\w+)[=]('|")(?P<path>.*?)('|")$"""
    match = re.search(rgx, text)
    if match:
        return {'name': match.group('name'), 'path': match.group('path')}
    return None


def gather_names_to_substitute(text):
    rgx = r"[$]\w+"
    matches = re.findall(rgx, text)
    return map(lambda x: x.replace('$', ''), matches)


def construct_full_filepath(text, filepaths_map):
    # substitutes all the $NAMEs and whatnot
    names = gather_names_to_substitute(text)
    for name in names:
        text = text.replace("$" + name, filepaths_map[name])
    return text

# def is_bash_var(text):
#     # rgx = r"""^(?P<name>\w+)[=]('|")(?P<path>.*?)('|")$"""
#     pass


def run_parsers():
    # they have no category, or no home
    orphaned_commands = []
    filepaths = []

    current_category = None

    parsers = [
        is_category_name,
        is_alias,
        is_bash_function,
        is_python_function,
        is_filepath,
        is_category_name_ending_here
    ]
