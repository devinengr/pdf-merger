import os, sys
from dataclasses import dataclass


# Misc options
TEMP_OUTPUT_DIR = "temp/"


# Command-line options
ARG_HELP = False
ARG_AGGREGATE_PDFS = False
ARG_PATH = ""
ARG_SOURCE_EXT = "java"
ARG_SOURCE_ONLY = False
ARG_GRADLE_TEST_DIR = "test"
ARG_GRADLE_ONLY = False
ARG_GRADLE_SUM_VIEW = 2
ARG_COMBINE_PDFS = False
ARG_PDFS_TO_COMBINE = []
ARG_OUTPUT_FILE = "out/out.pdf"


# Help menu
HELP_MENU = """
FLAG                OPTIONS         SHORT   DEFAULT         DESCRIPTION
----------------------------------------------------------------------------------
--help                              -h                      Shows this menu.

Required (choose 1):
--path              [path]          -p                      The path to the project (containing the build folder).
--combine           [pdf1] [pdf2]   -c                      Combine [pdf1] and [pdf2] into one PDF.

Optional:
--output            [file]          -o      out/out.pdf     Output file.

Can be used when --path is specified:
--source-ext        [ext]           -se     java            The file extension of the source code files to aggregate.
--source-only                       -so                     If set, only merges source code into a PDF.
--gradle-only                       -go                     If set, only merges Gradle reports into a PDF.
--gradle-test-dir   [dir]           -gd     test            The folder to use in [project dir]/build/reports/tests.
--gradle-sum-view   <1|2>           -gv     2               The view on the Gradle test summary page (see README).
"""


def parse_all():
    if (not parse_help()): return False
    if (not parse_path()): return False
    if (not parse_combine()): return False
    if (not parse_output_file()): return False
    if (not parse_source_ext()): return False
    if (not parse_source_only()): return False
    if (not parse_gradle_only()): return False
    if (not parse_gradle_test_dir()): return False
    if (not parse_gradle_sum_view()): return False
    return True


@dataclass
class Flag:
    occurrences: int
    options: list


def build_flag(*ids: str) -> Flag:
    count = 0
    add_options = False
    flag = Flag(0, [])
    for i in range(len(sys.argv)):
        if (sys.argv[i] in ids):
            count += 1
            add_options = True
        elif (count == 1):
            if (add_options):
                if (not sys.argv[i].startswith("-")):
                    flag.options.append(sys.argv[i])
                else:
                    add_options = False
    flag.occurrences = count
    return flag


def parse_help() -> bool:
    flag = build_flag("--help", "-h")
    if (flag.occurrences > 0):
        print(HELP_MENU)
        sys.exit()
    return True


def parse_path() -> bool:
    global ARG_AGGREGATE_PDFS
    global ARG_PATH
    path_flag = build_flag("--path", "-p")
    combine_flag = build_flag("--combine", "-c")
    if (path_flag.occurrences == 0 and combine_flag.occurrences == 1):
        return True
    if (path_flag.occurrences == 1 and combine_flag.occurrences == 0):
        if (len(path_flag.options) == 1):
            if (os.path.isdir(path_flag.options[0])):
                ARG_AGGREGATE_PDFS = True
                ARG_PATH = path_flag.options[0]
                return True
    return False


def parse_combine() -> bool:
    global ARG_COMBINE_PDFS
    global ARG_PDFS_TO_COMBINE
    combine_flag = build_flag("--combine", "-c")
    path_flag = build_flag("--path", "-p")
    if (combine_flag.occurrences == 0 and path_flag.occurrences == 1):
        return True
    if (combine_flag.occurrences == 1 and path_flag.occurrences == 0):
        if (len(combine_flag.options) > 1):
            for f in combine_flag.options:
                if (not os.path.isfile(f) or not f.endswith(".pdf")):
                    print("All files given must exist and be PDFs.")
                    return False
            ARG_COMBINE_PDFS = True
            ARG_PDFS_TO_COMBINE = combine_flag.options
            return True
    return False


def parse_output_file() -> bool:
    global ARG_OUTPUT_FILE
    output_flag = build_flag("--output", "-o")
    if (output_flag.occurrences == 0):
        return True
    if (output_flag.occurrences == 1):
        if (len(output_flag.options) == 1):
            dir = os.path.dirname(output_flag.options[0])
            if ((dir and os.access(dir, os.W_OK)) or ((not dir) and os.access(os.path.curdir, os.W_OK))):
                ARG_OUTPUT_FILE = output_flag.options[0]
                return True
            else:
                print("Files cannot be created in the chosen output location. Try another.")
    return False


def parse_source_ext() -> bool:
    global ARG_SOURCE_EXT
    ext_flag = build_flag("--source-ext", "-se")
    path_flag = build_flag("--path", "-p")
    if (ext_flag.occurrences == 0):
        return True
    if (path_flag.occurrences == 1 and ext_flag.occurrences == 1):
        if (len(ext_flag.options) == 1):
            ARG_SOURCE_EXT = ext_flag.options[0]
            return True
    return False


def parse_source_only() -> bool:
    global ARG_SOURCE_ONLY
    src_only_flag = build_flag("--source-only", "-so")
    gradle_only_flag = build_flag("--gradle-only", "-go")
    path_flag = build_flag("--path", "-p")
    if (src_only_flag.occurrences == 0):
        return True
    if (src_only_flag.occurrences == 1 and gradle_only_flag.occurrences == 1):
        return False
    if (path_flag.occurrences == 1 and src_only_flag.occurrences == 1):
        if (len(src_only_flag.options) == 0):
            ARG_SOURCE_ONLY = True
            return True
    return False


def parse_gradle_only() -> bool:
    global ARG_GRADLE_ONLY
    gradle_only_flag = build_flag("--gradle-only", "-go")
    src_only_flag = build_flag("--source-only", "-so")
    path_flag = build_flag("--path", "-p")
    if (gradle_only_flag.occurrences == 0):
        return True
    if (src_only_flag.occurrences == 1 and gradle_only_flag.occurrences == 1):
        return False
    if (path_flag.occurrences == 1 and gradle_only_flag.occurrences == 1):
        if (len(gradle_only_flag.options) == 0):
            ARG_GRADLE_ONLY = True
            return True
    return False


def parse_gradle_test_dir() -> bool:
    global ARG_GRADLE_TEST_DIR
    global ARG_PATH
    dir_flag = build_flag("--gradle-test-dir", "-gd")
    path_flag = build_flag("--path", "-p")
    if (dir_flag.occurrences == 0):
        return True
    if (path_flag.occurrences == 1 and dir_flag.occurrences == 1):
        if (len(dir_flag.options) == 1):
            path_full = ARG_PATH + "/build/reports/tests/" + dir_flag.options[0]
            if (os.path.isdir(path_full)):
                ARG_GRADLE_TEST_DIR = dir_flag.options[0]
                return True
            else:
                print("This is the determined location of the Gradle tests based on the options you provided:")
                print(path_full)
                print("It doesn't look like that folder exists. Double check the path to make sure.")
    return False


def parse_gradle_sum_view() -> bool:
    global ARG_GRADLE_SUM_VIEW
    view_flag = build_flag("--gradle-sum-view", "-gv")
    path_flag = build_flag("--path", "-p")
    if (view_flag.occurrences == 0):
        return True
    if (path_flag.occurrences == 1 and view_flag.occurrences == 1):
        if (len(view_flag.options) == 1):
            value = view_flag.options[0]
            if (value == str(1) or value == str(2)):
                ARG_GRADLE_SUM_VIEW = int(value)
                return True
    return False
