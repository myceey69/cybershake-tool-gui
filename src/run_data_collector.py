

import sys
import os
import argparse
import urllib.request
import timeit
import struct

# Add one directory level above to path to find imports
full_path = os.path.abspath(sys.argv[0])
path_add = os.path.dirname(os.path.dirname(full_path))
sys.path.append(path_add)

import utilities

debug = False

def make_abs_dir(folder_name):
    """Create absolute path to a directory one level above and ensure it exists."""
    abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', folder_name))
    os.makedirs(abs_path, exist_ok=True)
    return abs_path

def parse_args(argv):
    global debug
    parser = argparse.ArgumentParser(
        prog='Data Collector',
        description='Takes CyberShake data request URLs, retrieves them, and extracts desired results.'
    )
    parser.add_argument('-i', '--input-filename', dest='input_filename', action='store', default=None,
                        help="Path to file containing the URLs and variation IDs.")
    parser.add_argument('-o', '--output-directory', dest='output_directory', action='store', default=None,
                        help="Path to output directory to store files in.")
    parser.add_argument('-t', '--temp-directory', dest='temp_directory', action='store', default=".",
                        help="Path to temporary directory to store files before extraction.")
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False,
                        help='Turn on debug statements.')
    parser.add_argument('-v', '--version', dest='version', action='store_true', default=False,
                        help="Show version number and exit.")

    args = parser.parse_args(args=argv)
    args_dict = dict()

    if args.version:
        print("Version: %s" % utilities.get_version())
        sys.exit(utilities.ExitCodes.NO_ERROR)

    if args.input_filename is None:
        print("Path to input file must be provided, aborting.", file=sys.stderr)
        sys.exit(utilities.ExitCodes.MISSING_ARGUMENTS)

    args_dict['input_filename'] = args.input_filename

    # OUTPUT DIRECTORY (use seismograms if none provided)
    if args.output_directory:
        output_directory = os.path.abspath(args.output_directory)
    else:
        output_directory = make_abs_dir('seismograms')
    args_dict['output_directory'] = output_directory

    # TEMP DIRECTORY
    temp_directory = args.temp_directory or "."
    temp_directory = os.path.abspath(temp_directory)
    os.makedirs(temp_directory, exist_ok=True)
    args_dict['temp_directory'] = temp_directory

    if args.debug:
        debug = True

    return args_dict

def retrieve_files(args_dict):
    global debug
    input_file = args_dict['input_filename']
    local_filenames = []

    with open(input_file, 'r') as fp_in:
        data = fp_in.readlines()
        num_files = len(data)

        for i, line in enumerate(data):
            print("Downloading file %d of %d." % (i+1, num_files))
            url, rvs = line.strip().split()
            _, _, _, site_name, run_id, basename = url.split("/")

            local_directory = os.path.join(args_dict['temp_directory'], site_name, run_id)
            os.makedirs(local_directory, exist_ok=True)

            local_filename = os.path.join(local_directory, basename)
            local_filenames.append(local_filename)

            if debug:
                print("File URL: %s" % url)

            url_data = urllib.request.urlopen(url).read()
            with open(local_filename, 'wb') as fp_out:
                fp_out.write(url_data)

    return local_filenames

def extract_rvs(args_dict):
    input_file = args_dict['input_filename']
    output_directory = args_dict['output_directory']

    with open(input_file, 'r') as fp_in:
        data = fp_in.readlines()
        num_files = len(data)

        for i, line in enumerate(data):
            if i % 100 == 0:
                print("Extracting rupture variations from file %d of %d." % (i+1, num_files))

            url, rvs = line.strip().split()
            _, _, _, site_name, run_id, basename = url.split("/")
            rv_list = [int(rv) for rv in rvs.split(",")]

            local_rupture_directory = os.path.join(args_dict['temp_directory'], site_name, run_id)
            local_rupture_filename = os.path.join(local_rupture_directory, basename)

            sizeof_float = 4
            num_components = 2

            with open(local_rupture_filename, 'rb') as fp_rup_in:
                while rv_list:
                    header_str = fp_rup_in.read(56)
                    if header_str == b'':
                        break

                    rv = struct.unpack('i', header_str[32:36])[0]
                    nt = struct.unpack('i', header_str[40:44])[0]

                    if rv in rv_list:
                        rv_data = fp_rup_in.read(num_components * sizeof_float * nt)

                        filename_pieces = basename.split(".")[0].split("_")
                        source_id = int(filename_pieces[2])
                        rupture_id = int(filename_pieces[3])

                        local_rv_filename = os.path.join(
                            output_directory,
                            f"Seismogram_{site_name}_{run_id}_{source_id}_{rupture_id}_{rv}.grm"
                        )

                        with open(local_rv_filename, 'wb') as fp_out:
                            fp_out.write(header_str)
                            fp_out.write(rv_data)

                        rv_list.remove(rv)
                    else:
                        fp_rup_in.seek(num_components * sizeof_float * nt, 1)

                if rv_list:
                    print("Couldn't find rupture variation(s) %s in file %s, aborting." % (str(rv_list), local_rupture_filename), file=sys.stderr)
                    sys.exit(utilities.ExitCodes.FILE_PARSING_ERROR)

    print("Finished extracting rupture variations to %s." % output_directory)

def delete_temp_files(temp_directory, local_filenames):
    print("Removing temporary files from %s." % temp_directory)
    for f in local_filenames:
        if 'Seismogram' in f and f.endswith('.grm'):
            os.remove(f)

def run_main(argv):
    args_dict = parse_args(argv)
    local_filenames = retrieve_files(args_dict)
    extract_rvs(args_dict)
    delete_temp_files(args_dict['temp_directory'], local_filenames)

if __name__ == "__main__":
    run_main(sys.argv[1:])
    sys.exit(0)

