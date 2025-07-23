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
import config
import google.generativeai as genai
import matplotlib.pyplot as plt
import numpy as np

# --- Gemini API Setup ---
genai.configure(api_key=config.GEMINI_API_KEY)

chat_history = ["User: What are the models in the cybershake tool?",
    "AI: Study 22.12 Broadband and Study 22.12 Low Frequency."
    "User: What are the products in the cybershake tool?",
    "AI: Site Info, Seismograms, Intensity Measures, and Event Info."
    "User: What are the available site Info?",
    "AI: USC,PAS,LADT,LBP,WNGC,SABD,SBSM,FFI,CCP,SMCA,PTWN,PERR,GAVI,MBRD,PEDL,LBUT,ALIS,PACI,SLVW,ALP,OSI,PDE,MOP,LGU,WSS,HLL,LGB,COO,LAF,RPV,DLA,BRE,STG,PLS,OLI,RIO,CHN,TAB,PDU,SVD,FIL,LAPD,STNI,BVH,EMCH,SGRTT,CSDH,HUMC,SGCD,TRA,RHCH,MRSD,P14,P25,P24,P23,P22,P21,P20,P1,P2,P3,P4,P5,P6,P7,P8,P9,P10,P11,P12,P13,P15,P16,P17,P18,P19,s066,s070,s074,s078,s082,s151,s155,s159,s163,s167,s236,s240,s244,s248,s309,s313,s317,s321,s385,s389,s393,s397,s401,s470,s474,s478,s482,s486,s550,s554,s558,s562,s566,s632,s636,s640,s644,s648,s716,s720,s724,s728,s732,s022,s024,s026,s028,s030,s032,s034,s036,s038,s040,s064,s068,s072,s076,s080,s084,s109,s111,s113,s115,s117,s119,s121,s123,s125,s127,s153,s157,s161,s165,s169,s193,s195,s197,s199,s201,s203,s205,s207,s209,s211,s234,s238,s242,s246,s250,s271,s273,s275,s277,s279,s281,s283,s285,s287,s307,s311,s315,s319,s323,s345,s347,s349,s351,s353,s355,s357,s359,s361,s383,s387,s391,s395,s399,s403,s427,s429,s431,s433,s435,s437,s439,s441,s443,s445,s447,s472,s476,s480,s484,s488,s510,s512,s514,s516,s518,s520,s522,s524,s526,s528,s552,s556,s560,s564,s568,s591,s593,s595,s597,s599,s601,s603,s605,s607,s609,s634,s638,s642,s646,s650,s674,s676,s678,s680,s682,s684,s686,s688,s690,s692,s718,s722,s726,s730,s734,s758,s760,s762,s764,s766,s768,s770,s772,s774,s776,s778,s001,s003,s035,s043,s048,s071,s081,s145,s187,s228,s266,s292,s302,s328,s339,s344,s346,s348,s365,s366,s378,s380,s388,s410,s424,s451,s453,s465,s467,s491,s493,s505,s507,s531,s541,s545,s547,s586,s588,s624,s647,s660,s666,s668,s689,s710,s731,s765,s794,s795,PERR2,UCR,MRVY,GV03,GV05,BKBU,LBUT2,PIBU,NUEVO,PERRM,MKBD,GOPH,GLBT,PACI2,PBWL,LMAT,LPER,ACTN"
    
    ]

def ask_llm(prompt):
    
    lower_prompt = prompt.lower().strip()

    # Handle custom response
    if "what are the models" in lower_prompt:
        response = "Study 22.12 Broadband and Study 22.12 Low Frequency."
        chat_history.append(f"User: {prompt}")
        chat_history.append(f"AI: {response}")
        return response

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Format conversation history into a single prompt
        full_prompt = "\n".join(chat_history + [f"User: {prompt}"])
        
        response = model.generate_content(full_prompt)
        answer = response.text.strip()

        # Append new exchange to history
        chat_history.append(f"User: {prompt}")
        chat_history.append(f"AI: {answer}")

        return answer

    except Exception as e:
        return f"Error contacting Gemini LLM: {e}"


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
    if not dp_obj:
        return

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
                    continue
                try:
                    src_id = int(parts[0])
                    rup_id = int(parts[1])
                    rv_id = int(parts[2])
                    event_list.append((src_id, rup_id, rv_id))
                except ValueError:
                    continue

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

# --- LLM Query Popup ---
def open_llm_popup():
    popup = tk.Toplevel()
    popup.title("Ask CyberShake AI")

    tk.Label(popup, text="Ask a question about filters, models, or configuration:").pack()
    text_box = tk.Text(popup, height=5, width=60)
    text_box.pack()

    tk.Label(popup, text="LLM Response:").pack()
    response_box = tk.Text(popup, height=10, width=60, wrap="word")
    response_box.pack()

    def submit():
        question = text_box.get("1.0", tk.END).strip()
        if not question:
            return
        response = ask_llm(question)
        response_box.delete("1.0", tk.END)  # clear previous response
        response_box.insert(tk.END, response)

    tk.Button(popup, text="Submit", command=submit).pack(pady=5)

def read_and_plot_grm():
    # Ensure output folder exists
    out_dir = output_dir.get()
    if not os.path.exists(out_dir):
        messagebox.showerror("Directory Error", f"Output directory does not exist:\n{out_dir}")
        return

    # Open file dialog directly in output folder
    file_path = filedialog.askopenfilename(
        title="Select a .grm Seismogram File",
        initialdir=out_dir,
        filetypes=[("GRM Files", "*.grm"), ("All Files", "*.*")]
    )
    if not file_path:
        return

    try:
        # Read binary float32 data
        with open(file_path, 'rb') as f:
            data = np.fromfile(f, dtype=np.float32)

        if data.size == 0:
            messagebox.showwarning("Empty File", "The selected .grm file contains no data.")
            return

        # Plot
        plt.figure(figsize=(12, 5))
        plt.plot(data, color='midnightblue', linewidth=1)
        plt.title(f"Seismogram: {os.path.basename(file_path)}", fontsize=14, fontweight='bold')
        plt.xlabel("Sample Index (Time Steps)", fontsize=12)
        plt.ylabel("Amplitude (Ground Motion)", fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()

    except Exception as e:
        messagebox.showerror("Read Error", f"Failed to read file:\n{e}")



# --- Buttons ---
tk.Button(frame, text="Configure Filters", command=build_filter_inputs).grid(row=6, column=2)
tk.Button(frame, text="Run Pipeline", command=run_all, bg="green", fg="white").grid(row=100, column=1, pady=10)
tk.Button(frame, text="Ask AI", command=open_llm_popup, bg="blue", fg="white").grid(row=100, column=2, pady=10)
tk.Button(frame, text="Read Seismogram", command=read_and_plot_grm, bg="purple", fg="white").grid(row=102, column=1, pady=5)



root.mainloop()
