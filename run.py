#
# Author: devinengr
#

import glob, os, sys
from PyPDF2 import PdfReader, PdfWriter
import pdfkit
from fpdf import FPDF


# Command-line flags for wkhtmltopdf
wk_options = {
  "enable-local-file-access": None,
  "quiet": None,
}

# Instance variables
iteration = 0
pdfs_to_merge = []

# Command-line options
ARG_HELP = False
ARG_PATH = ""
ARG_SOURCE_EXT = "java"
ARG_SOURCE_ONLY = False
ARG_GRADLE_TEST_DIR = "test"
ARG_GRADLE_ONLY = False
ARG_GRADLE_SUM_VIEW = 1
ARG_COMBINE_PDFS = False
ARG_COMBINE_PDF_1 = ""
ARG_COMBINE_PDF_2 = ""
ARG_OUTPUT_DIR = "output"

# Help menu
HELP_MENU = """
FLAG                OPTIONS         SHORTCUT    DEFAULT
---------------------------------------------------------
--help                              -h
--path              [path]          -p          none

--source-ext        [ext]           -se         java
--source-only                       -so

--gradle-test-dir   [name]          -t          test
--gradle-only                       -go
--gradle-sum-view   <1|2>           -gv         1

--combine           [pdf1] [pdf2]   -c
"""


# def combine_pdf(path):
#     print('Fetching "' + path + '"')
#     pdf_writer = PdfWriter()
#     pdf_reader = PdfReader(path)
#     for page in pdf_reader.pages:
#         # Add each page to the writer object
#         pdf_writer.add_page(page)
#     # Write out the merged PDF
#     target_name = 'initial' + str(iteration) + '.pdf'
#     with open(target_name, 'wb') as out:
#         pdf_writer.write(out)
#     pdfs_to_merge.append(target_name)


def make_pdf_from_source(input: str, output: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Courier', size=10)    
    f = open(input, 'r')
    for l in f:
        pdf.write(4, l)
    pdf.output(output)


def fetch_and_append(input: str, type: str, method: str):
    global iteration
    iteration += 1
    print('Fetching ' + type +  ' ' + input + '"')
    output = type + str(iteration) + '.pdf'
    if (method == "pdfkit"):
        pdfkit.from_file(input, output, wk_options)
    elif (method == "src"):
        make_pdf_from_source(input, output)
    pdfs_to_merge.append(output)


def swap_gradle_view():
    replacements = {'.selected': '.temp_class_abc',}
    for i in range(3):
        if i == 1:
            replacements = {'.deselected': '.selected'}
        elif i == 2:
            replacements = {'.temp_class_abc': '.deselected'}
        lines = []
        name = ARG_PATH + '/build/reports/tests/' + ARG_GRADLE_TEST_DIR + '/css/base-style.css'
        with open(name) as infile:
            for line in infile:
                for src, target in replacements.items():
                    line = line.replace(src, target)
                lines.append(line)
        with open(name, 'w') as outfile:
            for line in lines:
                outfile.write(line)


def grab_checkstyle_reports():
    for filename in glob.iglob(ARG_PATH + '/build/reports/checkstyle/main.html', recursive=True):
        fetch_and_append(filename, "checkstyle", "pdfkit")


def grab_test_reports():
    swap_gradle_view()
    for filename in glob.iglob(ARG_PATH + '/build/reports/tests/' + ARG_GRADLE_TEST_DIR + '/index.html', recursive=True):
        fetch_and_append(filename, "test", "pdfkit")
    swap_gradle_view()
    for filename in glob.iglob(ARG_PATH + '/build/reports/tests/' + ARG_GRADLE_TEST_DIR + '/classes/**/*.html', recursive=True):
        fetch_and_append(filename, "test", "pdfkit")


def grab_source_code():
    global iteration
    # filename = 'src_diff.txt'
    for filename in glob.iglob(ARG_PATH + '/src/**/*.java', recursive=True):
        fetch_and_append(filename, "src", "src")


# https://realpython.com/pdf-python/#how-to-merge-pdfs
def merge_pdfs(paths, output):
    pdf_writer = PdfWriter()
    for path in paths:
        pdf_reader = PdfReader(path)
        for page in pdf_reader.pages:
            # Add each page to the writer object
            pdf_writer.add_page(page)
    # Write out the merged PDF
    with open(output, 'wb') as out:
        print('Merging PDFs...')
        pdf_writer.write(out)


def cleanup():
    print('Cleaning up...')
    for pdf in pdfs_to_merge:
        os.remove(pdf)


if __name__ == "__main__":
    if (len(sys.argv) < 3):
        print("Specify a path to the project (it should contain the Gradle build directory).")
        sys.exit(0)
    ARG_PATH = sys.argv[2]

    grab_test_reports()
    grab_checkstyle_reports()
    grab_source_code()
    merge_pdfs(pdfs_to_merge, 'output_final.pdf')
    cleanup()
    print('Done')
