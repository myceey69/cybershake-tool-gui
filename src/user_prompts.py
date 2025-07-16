import sys
import os

# Add one directory level above to path to find imports
full_path = os.path.abspath(sys.argv[0])
path_add = os.path.dirname(os.path.dirname(full_path))
sys.path.append(path_add)

import data_products
import filters
import utilities


def validate_input(user_input, max_ok_val):
    try:
        input_int = int(user_input)
    except ValueError:
        print('"%s" is not a valid selection.' % user_input)
        return -1
    if input_int < 1 or input_int > max_ok_val:
        print('"%s" is not a valid selection.' % user_input)
        return -2
    return input_int

def choose_model(model_list):
    print("\n======== Choose CyberShake Model ========")
    selected_model = None
    while True:
        print(" LF = Low Frequency   |   BB = BroadBand\n")
        for i, m in enumerate(model_list):
            print("\t%d) %s" % ((i+1), m.get_name()))
        model_choice = input("\nWhich model do you want to use? ")
        model_choice_int = validate_input(model_choice, len(model_list))
        if model_choice_int > 0:
            selected_model = model_list[model_choice_int-1]
            break
    print("You have selected %s.\n" % (selected_model.get_name()))
    return selected_model

def choose_data_product(dp_list):
    print("\n\n\n======== Choose Data Product ========")
    selected_dp = None
    while True:
        print("These are the available data products:\n")
        for i, d in enumerate(dp_list):
            print("\t%d) %s" % ((i+1), d.get_name()))
        dp_choice = input("\nWhich data product do you want to retrieve? ")
        dp_choice_int = validate_input(dp_choice, len(dp_list))
        if dp_choice_int > 0:
            selected_dp = dp_list[dp_choice_int-1]
            break
    print("You have selected %s." % (selected_dp.get_name()))
    return selected_dp

def choose_filter_value(filter):
    print(f"\n\n\n======== Set Filter Values for '{filter.get_name()}' ========")
    while True:
        print("How do you want to specify value(s) for the %s filter?\n" % (filter.get_name()))
        print("%d) Specify single value." % filters.FilterParams.SINGLE_VALUE)
        print("%d) Specify multiple values." % filters.FilterParams.MULTIPLE_VALUES)
        max_filter_val = filters.FilterParams.MULTIPLE_VALUES
        if filter.is_numeric():
            print("%d) Specify a range of values." % filters.FilterParams.VALUE_RANGE)
            max_filter_val = filters.FilterParams.VALUE_RANGE
        max_filter_val += 1
        print("%d) Show valid values for this filter." % (max_filter_val))
        value_type_choice = input("\nHow do you want to specify filter values? ")
        value_type_choice_int = validate_input(value_type_choice, max_filter_val)
        if value_type_choice_int == max_filter_val:
            try:
                (min_val, max_val) = filter.get_range()
                print("Valid values are between [%f, %f]." % (min_val, max_val))
                continue
            except:
                pass
            try:
                vals_list = filter.get_values_list()
                print("Valid values are %s" % ', '.join([str(v) for v in vals_list]))
                continue
            except:
                pass
            print("Valid values are numbers." if filter.is_numeric() else "Valid values are strings.")
            continue
        elif value_type_choice_int >= 0:
            break
    # Handle value input
    # ... (unchanged logic)
    if value_type_choice_int == filters.FilterParams.SINGLE_VALUE:
        while True:
            input_string = "What value do you want to use? "
            if filter.get_units():
                input_string = f"What value do you want to use (units {filter.get_units()})? "
            value = input(input_string)
            try:
                value_obj = filter.get_type()(value)
            except ValueError:
                if filter.get_name() == "Intensity Measure Period" and (value == "PGA" or value == "PGV"):
                    value_obj = str(value)
                else:
                    print("%s filter requires values of type %s." % (filter.get_name(), str(filter.get_type())))
                    continue
            if filter.set_value(value_obj) != 0:
                continue
            break
    elif value_type_choice_int == filters.FilterParams.MULTIPLE_VALUES:
        exit_loop = False
        while not exit_loop:
            input_string = "What values (comma-separated) do you want to use? "
            if filter.get_units():
                input_string = f"What values (comma-separated) do you want to use (units {filter.get_units()})? "
            values = input(input_string)
            pieces = values.split(',')
            value_list = []
            good_input = True
            for p in pieces:
                try:
                    value_obj = filter.get_type()(p.strip())
                except ValueError:
                    if filter.get_name() == "Intensity Measure Period" and (p.strip() == "PGA" or p.strip() == "PGV"):
                        print(f"Cannot mix {p.strip()} with other intensity measures.")
                        good_input = False
                        break
                    else:
                        print("%s filter requires values of type %s." % (filter.get_name(), filter.get_type().__name__))
                        good_input = False
                        break
                value_list.append(value_obj)
            if good_input:
                if filter.set_values(value_list) != 0:
                    continue
                else:
                    exit_loop = True
    elif value_type_choice_int == filters.FilterParams.VALUE_RANGE:
        while True:
            print("\n======== Set the Range ========")
            input_string = "What range do you want to use? Specify as min, max: "
            if filter.get_units():
               
                input_string = f"What range do you want to use? Specify as min, max (units {filter.get_units()}): "
            values = input(input_string)
            pieces = values.split(",")
            if len(pieces) != 2:
                print("'%s' isn't in min, max format." % values)
                continue
            (min_val, max_val) = pieces
            try:
                min_obj = filter.get_type()(min_val)
                max_obj = filter.get_type()(max_val)
            except ValueError:
                print("%s filter requires values of type %s." % (filter.get_name(), str(filter.get_type())))
                continue
            if filter.set_value_range(min_obj, max_obj) != 0:
                continue
            break
    return filter

def choose_filters(filter_list, selected_dp, selected_model):
    print("\n\n\n======== Apply Filters ========")
    selected_filters = []
    remaining_filter_list = []
    filter_dps = selected_dp.get_relevant_filters()
    for f in filter_list:
        if f.get_name() == 'Intensity Measure Period':
            f.set_values_list(selected_model.get_periods())
        if f.get_data_product() in filter_dps:
            remaining_filter_list.append(f)
    while True:
        #print("\n======== Apply Filters ========\n")
        print("Available filters:\n")
        for i, f in enumerate(remaining_filter_list):
            print("\t%d) %s" % ((i+1), f.get_name()))
        print("\t%d) Done adding filters" % (len(remaining_filter_list)+1))
        filt_choice = input("\nWhich filter would you like to add next? ")
        filt_choice_int = validate_input(filt_choice, len(remaining_filter_list)+1)
        if filt_choice_int > 0:
            if filt_choice_int == len(remaining_filter_list)+1:
                break
            selected_filt = remaining_filter_list[filt_choice_int-1]
            if selected_filt in selected_filters:
                print("You've already selected the %s filter." % selected_filt.get_name())
                continue
            selected_filt = choose_filter_value(selected_filt)
            selected_filters.append(selected_filt)
            remaining_filter_list.remove(selected_filt)
            for s in selected_filt.get_required_filters():
                if s in selected_filters:
                    continue
                print("\nRequired filter '%s' also selected." % s.get_name())
                s = choose_filter_value(s)
                selected_filters.append(s)
                remaining_filter_list.remove(s)
    return selected_filters

def choose_sort_order(sort_item):
    while True:
        print(f"\nYou've chosen to sort on {sort_item.get_name()}.\n")
        print("\n\t1) Ascending order")
        print("\t2) Descending order")
        order_choice = input("\nWhat order do you want to sort in? ")
        order_choice_int = validate_input(order_choice, 2)
        if order_choice_int > 0:
            sort_item.set_sort(1 if order_choice_int == 1 else -1)
            break

def choose_sort(selected_filters):
    print("\n\n\n======== (Optional) Sort Results ========")
    while True:
        do_sort_choice = input("Would you like to sort your results (y/n)? ")
        if do_sort_choice.lower() == 'n':
            return
        elif do_sort_choice.lower() == 'y':
            break
        else:
            print("'%s' is not a valid option." % do_sort_choice)
    while True:
        print("\nYou can sort by:\n")
        for i, f in enumerate(selected_filters):
            print("\t%d) %s" % ((i+1), f.get_name()))
        sort_choice = input("\nWhich filter to sort on? ")
        sort_choice_int = validate_input(sort_choice, len(selected_filters))
        if sort_choice_int > 0:
            sort_item = selected_filters[sort_choice_int-1]
            choose_sort_order(sort_item)
            break

def get_user_input(model_list, dp_list, filter_list, input_event_filename=None):
    print("\n\n")
    print("|===========================================|")
    print("|Welcome to the CyberShake Data Access tool.|")
    print("|===========================================|\n")
    selected_model = choose_model(model_list)
    selected_dp = choose_data_product(dp_list)

    event_list = None
    if input_event_filename is not None:
        event_list = []
        try:
            with open(input_event_filename, 'r', encoding='utf-8-sig') as fp_in:
                data = fp_in.readlines()
                for line in data:
                    pieces = line.strip().split(",")
                    if len(pieces) < 3:
                        print("Error: CSV format should be <src id>,<rup id>,<rup var id>", file=sys.stderr)
                        sys.exit(utilities.ExitCodes.FILE_PARSING_ERROR)
                    event_list.append((int(pieces[0]), int(pieces[1]), int(pieces[2])))
        except Exception as e:
            print("Error reading file %s: %s" % (input_event_filename, e), file=sys.stderr)
            sys.exit(utilities.ExitCodes.BAD_FILE_PATH)
        if len(event_list) > utilities.MAX_EVENT_LIST_LENGTH:
            print("Too many events in file: %d" % len(event_list), file=sys.stderr)
            sys.exit(utilities.ExitCodes.FILE_PARSING_ERROR)
        filter_list = [f for f in filter_list if f.get_data_product() != filters.FilterDataProducts.EVENTS]

    selected_filters = choose_filters(filter_list, selected_dp, selected_model)

    if selected_filters:
        choose_sort(selected_filters)

    print("\n======== Summary of Your Request ========")
    print("Model:\n\t%s" % selected_model.get_name())
    print("\nData product:\n\t%s" % selected_dp.get_name())
    print("\nFilters:")
    if not selected_filters:
        print("\tNone")
        print("\n=========================================")
    else:
        for s in selected_filters:
            if s.get_sort() < 0:
                print(f"\t{s.get_filter_string()}, sort descending")
            elif s.get_sort() > 0:
                print(f"\t{s.get_filter_string()}, sort ascending")
            else:
                print(f"\t{s.get_filter_string()}")

    if event_list is not None:
        print("\nEvents specified in file:")
        for e in event_list:
            print("\tSrc %d, Rup %d, RV %d" % (e[0], e[1], e[2]))

    return (selected_model, selected_dp, selected_filters, event_list)
    print("\n=========================================")
