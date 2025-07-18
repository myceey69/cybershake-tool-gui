
import sys
import os
import argparse
import json
import datetime

#Add one directory level above to path to find imports


import query_constructor
import utilities
import filters
import data_products
import models

model_list = None
dp_list = None
filter_list = None

def parse_args(argv):
    parser = argparse.ArgumentParser(prog='Query Builder', description='Takes CyberShake data request and constructs database queries required to fulfill it.')
    parser.add_argument('-i', '--input-filename', dest='input_filename', action='store', default=None, help="Path to JSON file describing the data request.")
    parser.add_argument('-o', '--output-filename', dest='output_filename', action='store', default=None, help="Path to output file containing queries.")
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='Turn on debug statements.')
    parser.add_argument('-v', '--version', dest='version', action='store_true', default=False, help="Show version number and exit.")
    args = parser.parse_args(args=argv)
    if args.version==True:
        print("Version: %s" % utilities.get_version())
        sys.exit(utilities.ExitCodes.NO_ERROR)
    if args.input_filename is None:
        print("Path to input file must be provided, aborting.", file=sys.stderr)
        sys.exit(utilities.ExitCodes.MISSING_ARGUMENTS)
    input_filename = args.input_filename
    if args.output_filename is None:
        dt_tuple = datetime.datetime.now().timetuple()
        output_filename = "csdata.%02d%02d%02d_%02d%02d%04d.query" % (dt_tuple.tm_hour, dt_tuple.tm_min, dt_tuple.tm_sec, dt_tuple.tm_mon, dt_tuple.tm_mday, dt_tuple.tm_year)
    else:
        output_filename = args.output_filename
    return (input_filename, output_filename)
	
def load_data():
    global model_list, dp_list, filter_list
    model_list = models.create_models()
    if len(model_list)==0:
        print("No models available, aborting.", file=sys.stderr)
        sys.exit(utilities.ExitCodes.NO_MODELS)
    dp_list = data_products.create_data_products()
    if len(dp_list)==0:
        print("No data products available, aborting.", file=sys.stderr)
        sys.exit(utilities.ExitCodes.NO_DATAPRODUCTS)
    filter_list = filters.create_filters()
    if len(filter_list)==0:
        print("No filters available, aborting.", file=sys.stderr)
        sys.exit(utilities.ExitCodes.NO_FILTERS)

def parse_json(input_filename):
    try:
          fp_in = open(input_filename, 'r')
          json_dict = json.load(fp_in)
    except Exception as e:
          print("Error parsing JSON file %s, aborting." % input_filename)
          print(e)
          sys.exit(utilities.ExitCodes.FILE_PARSING_ERROR)
    model_name = json_dict['model']['name']
    for m in model_list:
        if m.get_name()==model_name:
            model_selected = m
            break
    dp_name = json_dict['products']['name']
    dp_selected = None
    for d in dp_list:
          if d.get_name()==dp_name:
                dp_selected = d
                break
    filters_selected = []
    for filt in json_dict['filters']:
          name = filt['name']
          params = filt['filter_params']
          values = filt['values']
          for f in filter_list:
                if f.get_name()==name:
                    selected_filt = f
                    #Update valid IM values based on model
                    if f.get_name()=='Intensity Measure Period':
                        #Update with periods from model
                        f.set_values_list(model_selected.get_periods())
                    if 'sort' in filt:
                        sort = filt['sort']
                        f.set_sort(sort)
                    if params==filters.FilterParams.SINGLE_VALUE:
                        if len(values)>1:
                            print("filter_params for the filter %s specifies %s, so only one value should be given in the 'values' field in the input file %s.  Aborting." % (f.get_name(), filters.FilterParams.get_text(params), input_filename))
                            sys.exit(utilities.ExitCodes.FILE_PARSING_ERROR)
                        selected_filt.set_value(values[0])
                    elif params==filters.FilterParams.MULTIPLE_VALUES:
                        if len(values)<2:
                            print("filter_params for the filter %s specifies %s, so there should be more than 1 values in the 'values' field in the input file %s.  Aborting." % (f.get_name(), filters.FilterParams.get_text(params), input_filename))
                            sys.exit(utilities.ExitCodes.FILE_PARSING_ERROR)
                        selected_filt.set_values(values)
                    elif params==filters.FilterParams.VALUE_RANGE:
                        if len(values)!=2:
                            print("filter_params for the filter %s specifies %s, so there should be exactly 2 values in the 'values' field in the input file %s.  Aborting." % (f.get_name(), filters.FilterParams.get_text(params), input_filename))
                            sys.exit(utilities.ExitCodes.FILE_PARSING_ERROR)
                        selected_filt.set_value_range(values[0], values[1])
                    filters_selected.append(selected_filt)
    event_list = None
    if 'event_list' in json_dict:
        #We specified a list of specific events
        event_list = []
        for e in json_dict['event_list']:
            event_list.append(e)
    if dp_selected is None:
          print("Couldn't find a valid data product in JSON file %s, aborting." % input_filename)
          sys.exit(utilities.ExitCodes.FILE_PARSING_ERROR)
    return (model_selected, dp_selected, filters_selected, event_list)

def write_queries(query, input_filename, output_filename, dp_name):
    with open(output_filename, 'w') as fp_out:
        distinct_string = ""
        if query.get_distinct()==True:
            distinct_string = "distinct"
        fp_out.write("select = %s %s\n" % (distinct_string, query.get_select_string()))
        fp_out.write("from = %s\n" % query.get_from_string())
        fp_out.write("where = %s\n" % query.get_where_string())
        if (query.get_sort()!=""):
            fp_out.write("sort = %s\n" % query.get_sort())
        fp_out.write("data_request_file = %s\n" % input_filename)
        fp_out.write("data_product = %s\n" % dp_name)
        fp_out.flush()
        fp_out.close()

def run_main(argv):
    (input_filename, output_filename) = parse_args(argv)
    load_data()
    (model_selected, dp_selected, filters_selected, event_list) = parse_json(input_filename)
    query = query_constructor.construct_queries(model_selected, dp_selected, filters_selected, event_list)
    write_queries(query, input_filename, output_filename, dp_selected.get_name())
    print("\nYour database queries were written to %s." % output_filename)

if __name__=="__main__":
    run_main(sys.argv[1:])
    sys.exit(0)