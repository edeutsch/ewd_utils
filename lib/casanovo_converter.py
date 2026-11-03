#!/usr/bin/env python3
import sys
def eprint(*args, **kwargs): print(*args, file=sys.stderr, **kwargs)

#### Import some standard modules
import os
import argparse
import os.path
import timeit
import re
import gzip


####################################################################################################
#### Casanovo Converter class
class CasanovoConverter:


    ####################################################################################################
    #### Constructor
    def __init__(self, input_file=None, output_file=None, verbose=None):

        #### Set verbosity
        if verbose is None:
            verbose = 0
        self.verbose = verbose

        #### Store parameters
        self.input_file = input_file
        self.output_file = output_file


    ####################################################################################################
    #### Convert
    def convert(self, input_file, output_file, verbose=None):

        if verbose is not None:
            self.verbose = verbose

        if input_file:
            self.input_file = input_file
        if output_file:
            self.output_file = output_file

        #### Set up information
        t0 = timeit.default_timer()
        stats = { 'n_psms': 0 }
        self.psms = []

        #### Show information
        if self.verbose >= 1:
            eprint(f"INFO: Reading PSMs in input file {self.input_file}")
            progress_intro = False

        #### If the pepXML is gzipped, then open with zlib, else a plain open
        if self.input_file.endswith('.gz'):
            infile = gzip.open(self.input_file)
        else:
            infile = open(self.input_file, 'rb')

        outfile = open(self.output_file, 'w')

        #### Read psms from the file
        for line in infile:
            if not line.startswith('PSM'):
                continue
            columns = line.strip().split("\t")
            sequence = columns[1]
            score = columns[8]
            modifications = columns[9]
            charge = columns[11]
            experimental_mz = columns[12]
            theoretical_mz = columns[13]
            scan_id = columns[14]
            match = re.search(r"scan=(\d+)", scan_id)
            if match:
                scan_number = match.group(1)
            else:
                scan_number = '-1'
            proforma = columns[20]

            #### Update counters and print progress
            stats['n_psms'] += 1
            if self.verbose >= 1:
                if stats['n_psms']/5000 == int(stats['n_psms']/5000):
                    if not progress_intro:
                        eprint("INFO: Reading psms.. ", end='')
                        progress_intro = True
                    eprint(f"{stats['n_psms']}.. ", end='', flush=True)

            row = [ scan_number, str(charge), str(round(experimental_mz, 4)), str(round(theoretical_mz, 4)), str(round(score, 4)), proforma ]
            outfile.write("\t".join(row) + "\n")


        infile.close()
        outfile.close()
        if self.verbose >= 1:
            eprint('')

        #### Print final timing information
        t1 = timeit.default_timer()
        print(f"INFO: Read {stats['n_psms']} psms from {self.pepxml_file}")

        if self.verbose >= 1:
            print(f"INFO: Elapsed time: {t1-t0}")
            print(f"INFO: Processed {stats['n_psms']/(t1-t0)} psms per second")


####################################################################################################
#### For command-line usage
def main():

    argparser = argparse.ArgumentParser(description='Converts a Casanovo mzTab file into a BenchSubmit file')
    argparser.add_argument('--min_psm_probability', action='store', default=0.90, help='Minimum PSM (PeptideProphet or iProphet) probability to accept')
    argparser.add_argument('--verbose', action='count', help='If set, print more information about ongoing processing' )
    argparser.add_argument('--output_file', action='store', help='Output filename')
    argparser.add_argument('input_file', type=str, help='Filename of Casanovo mzTab file to convert')
    params = argparser.parse_args()

    #### Set verbose
    verbose = params.verbose
    if verbose is None:
        verbose = 0

    #### Ensure that the input_file is really there before starting work
    input_file = params.input_file
    if not os.path.isfile(input_file):
        print(f"ERROR: File '{input_file}' not found or not a file")
        return

    #### Ensure that the output_file is specified
    output_file = params.output_file
    if output_file is None:
        print(f"ERROR: Output file must be specified")
        return
    if input_file == output_file:
        print(f"ERROR: Input file and output file must not be the same")
        return

    #### Load the relevant search result information from the pepXML file
    converter = CasanovoConverter()
    converter.convert(input_file, output_file, verbose=verbose)


#### For command line usage
if __name__ == "__main__": main()
