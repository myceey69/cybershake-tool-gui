import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import datetime
import models
import data_products
import filters
import query_constructor
import run_database_wrapper as db_wrap
import run_data_collector as data_collector
import utilities


# --- Globals ---
model_list = models.create_models()
dp_list = data_products.create_data_products()
filter_list = filters.create_filters()

# --- Tkinter Setup ---
root = tk.Tk()
root.title("CyberShake Data Access Tool")

frame = ttk.Frame(root, padding=10)
frame.grid(row=0, column=0, sticky="nsew")

# --- Variables ---
selected_model = tk.StringVar()
selected_product = tk.StringVar()
output_format = tk.StringVar(value="csv")
request_label = tk.StringVar(value=datetime.datetime.now().strftime("%H%M%S_%m%d%Y"))
output_dir = tk.StringVar(value=os.path.join(os.path.dirname(os.getcwd()), "output"))
event_file = tk.StringVar(value="")
debug_mode = tk.BooleanVar(value=False)
filter_widgets = []
selected_filters = []

# --- GUI Elements ---
tk.Label(frame, text="Request Label:").grid(row=0, column=0, sticky="e")
tk.Entry(frame, textvariable=request_label).grid(row=0, column=1)

tk.Label(frame, text="Model:").grid(row=1, column=0, sticky="e")
model_menu = ttk.Combobox(frame, textvariable=selected_model, state="readonly")
model_menu['values'] = [m.get_name() for m in model_list]
model_menu.grid(row=1, column=1)

tk.Label(frame, text="Data Product:").grid(row=2, column=0, sticky="e")
dp_menu = ttk.Combobox(frame, textvariable=selected_product, state="readonly")
dp_menu['values'] = [d.get_name() for d in dp_list]
dp_menu.grid(row=2, column=1)

def browse_event_file():
    path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if path:
        event_file.set(path)

tk.Label(frame, text="Event File (optional):").grid(row=3, column=0, sticky="e")
tk.Entry(frame, textvariable=event_file).grid(row=3, column=1)
tk.Button(frame, text="Browse", command=browse_event_file).grid(row=3, column=2)

tk.Label(frame, text="Output Format:").grid(row=4, column=0, sticky="e")
tk.OptionMenu(frame, output_format, "csv", "sqlite").grid(row=4, column=1, sticky="w")

tk.Label(frame, text="Output Directory:").grid(row=5, column=0, sticky="e")
tk.Entry(frame, textvariable=output_dir).grid(row=5, column=1)

tk.Checkbutton(frame, text="Debug Mode", variable=debug_mode).grid(row=6, column=1, sticky="w")

# --- Dynamic Filter Configuration ---
def build_filter_inputs():
    global filter_widgets, selected_filters
    for w in filter_widgets:
        w.destroy()
    filter_widgets.clear()
    selected_filters.clear()

    dp_name = selected_product.get()
    model_name = selected_model.get()
    model_obj = next((m for m in model_list if m.get_name() == model_name), None)
    dp_obj = next((d for d in dp_list if d.get_name() == dp_name), None)
    relevant_types = dp_obj.get_relevant_filters()

    row = 7
    for f in filter_list:
        if f.get_data_product() not in relevant_types:
            continue
        tk.Label(frame, text=f.get_name()).grid(row=row, column=0, sticky="e")
        mode = tk.StringVar(value="single")
        mode_menu = ttk.Combobox(frame, values=["single", "multiple", "range"], state="readonly", width=10)
        mode_menu.grid(row=row, column=1)
        mode_menu.set("single")
        entry = tk.Entry(frame)
        entry.grid(row=row, column=2)
        filter_widgets.append(entry)
        selected_filters.append((f, entry, mode_menu))
        row += 1

# --- Run Button ---
def run_all():
    model_obj = next((m for m in model_list if m.get_name() == selected_model.get()), None)
    dp_obj = next((d for d in dp_list if d.get_name() == selected_product.get()), None)
    query_filters = []
    for f, w, mode_menu in selected_filters:
        val = w.get()
        mode = mode_menu.get()
        if not val:
            continue
        try:
            if mode == "single":
                typed_val = f.get_type()(val)
                f.set_value(typed_val)
            elif mode == "multiple":
                vals = [f.get_type()(v.strip()) for v in val.split(",")]
                f.set_values(vals)
            elif mode == "range":
                min_v, max_v = val.split(",")
                f.set_value_range(f.get_type()(min_v.strip()), f.get_type()(max_v.strip()))
        except:
            continue
        query_filters.append(f)

    
    event_list = None
    if dp_obj.get_name() == "Seismograms" and event_file.get():
        event_list = []
        with open(event_file.get(), 'r') as fp:
            for line in fp:
                parts = line.strip().split(',')
                if len(parts) != 3:
                    continue  # skip malformed lines
                try:
                    src_id = int(parts[0])
                    rup_id = int(parts[1])
                    rv_id = int(parts[2])
                    event_list.append((src_id, rup_id, rv_id))
                except ValueError:
                    continue


    event_list = None

    query = query_constructor.construct_queries(model_obj, dp_obj, query_filters, event_list)

    input_dict = {
        "select": query.get_select_string(),
        "from": query.get_from_string(),
        "where": query.get_where_string(),
        "data_product": dp_obj.get_name()
    }
    if query.get_sort():
        input_dict["sort"] = query.get_sort()

    input_file = os.path.join(output_dir.get(), f"csdata.{request_label.get()}.query")
    with open(input_file, 'w') as f:
        for k, v in input_dict.items():
            f.write(f"{k} = {v}\n")

    config_file = os.path.join(os.getcwd(), "moment.cfg")
    config_dict = utilities.read_config(config_file)
    args_dict = {
        "input_filename": input_file,
        "output_filename": os.path.join(output_dir.get(), f"csdata.{request_label.get()}.data"),
        "config_filename": config_file,
        "output_format": output_format.get(),
    }
    result_set = db_wrap.execute_queries(config_dict, input_dict)
    db_wrap.write_results(result_set, args_dict, input_dict, config_dict)

   
    if dp_obj.get_name() == "Seismograms":
         db_wrap.write_url_file(args_dict, input_dict, config_dict, result_set)
         url_file = args_dict["output_filename"].replace(".data", ".urls")
         if os.path.exists(url_file):
             collector_args = {
                "input_filename": url_file,
                 "output_directory": output_dir.get(),
                 "temp_directory": os.path.join(os.getcwd(), "temp")
             }
             data_collector.retrieve_files(collector_args)
             data_collector.extract_rvs(collector_args)

    messagebox.showinfo("Success", "CyberShake data retrieval complete.")


# --- Bindings and Controls ---
tk.Button(frame, text="Configure Filters", command=build_filter_inputs).grid(row=6, column=2)
tk.Button(frame, text="Run Pipeline", command=run_all, bg="green", fg="white").grid(row=100, column=1, pady=10)

root.mainloop()