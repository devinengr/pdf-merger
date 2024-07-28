#
# Author: devinengr
#

import glob, os, sys
from PyPDF2 import PdfReader, PdfWriter
import pdfkit
from fpdf import FPDF
import parser


# Command-line flags for wkhtmltopdf
wk_options = {
  "enable-local-file-access": None,
  "quiet": None,
}


# Instance variables
iteration = 0
pdfs_to_merge = []


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
    output = parser.TEMP_OUTPUT_DIR + '/' + type + str(iteration) + '.pdf'
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
        name = parser.ARG_PATH + '/build/reports/tests/' + parser.ARG_GRADLE_TEST_DIR + '/css/base-style.css'
        with open(name) as infile:
            for line in infile:
                for src, target in replacements.items():
                    line = line.replace(src, target)
                lines.append(line)
        with open(name, 'w') as outfile:
            for line in lines:
                outfile.write(line)


def swap_gradle_view_if_preferred():
    if (parser.ARG_GRADLE_SUM_VIEW == 2):
        swap_gradle_view()


def grab_checkstyle_reports():
    for filename in glob.iglob(parser.ARG_PATH + '/build/reports/checkstyle/main.html', recursive=True):
        fetch_and_append(filename, "checkstyle", "pdfkit")


def grab_test_reports():
    swap_gradle_view_if_preferred()
    for filename in glob.iglob(parser.ARG_PATH + '/build/reports/tests/' + parser.ARG_GRADLE_TEST_DIR + '/index.html', recursive=True):
        fetch_and_append(filename, "test", "pdfkit")
    swap_gradle_view_if_preferred()
    for filename in glob.iglob(parser.ARG_PATH + '/build/reports/tests/' + parser.ARG_GRADLE_TEST_DIR + '/classes/**/*.html', recursive=True):
        fetch_and_append(filename, "test", "pdfkit")


def grab_source_code():
    global iteration
    for filename in glob.iglob(parser.ARG_PATH + '/**/*.' + parser.ARG_SOURCE_EXT, recursive=True):
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


def parse_arguments():
    if (not parser.parse_all()):
        print("There was an issue parsing the command. Use '--help' or '-h' for usage info.")
        sys.exit()


def create_output_directories():
    out_dir = os.path.dirname(parser.ARG_OUTPUT_FILE)
    temp_dir = os.path.dirname(parser.TEMP_OUTPUT_DIR)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    if temp_dir:
        os.makedirs(temp_dir, exist_ok=True)


def perform_aggregate():
    if (not parser.ARG_SOURCE_ONLY):
        grab_test_reports()
        grab_checkstyle_reports()
    if (not parser.ARG_GRADLE_ONLY):
        grab_source_code()
    merge_pdfs(pdfs_to_merge, parser.ARG_OUTPUT_FILE)
    cleanup()


def perform_combine():
    merge_pdfs(parser.ARG_PDFS_TO_COMBINE, parser.ARG_OUTPUT_FILE)


if __name__ == "__main__":
    parse_arguments()
    create_output_directories()
    if (parser.ARG_AGGREGATE_PDFS):
        perform_aggregate()
    elif (parser.ARG_COMBINE_PDFS):
        perform_combine()
    print('Done')
