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
from PIL import Image, ImageTk
import webview

# --- Gemini API Setup ---
genai.configure(api_key=config.GEMINI_API_KEY)

chat_history = [
    "User: What are the models in the cybershake tool?",
    "AI: Study 22.12 Broadband and Study 22.12 Low Frequency.",
    "User: What are the products in the cybershake tool?",
    "AI: Site Info, Seismograms, Intensity Measures, and Event Info."
]

def ask_llm(prompt):
    lower_prompt = prompt.lower().strip()
    if "what are the models" in lower_prompt:
        response = "Study 22.12 Broadband and Study 22.12 Low Frequency."
        chat_history.append(f"User: {prompt}")
        chat_history.append(f"AI: {response}")
        return response

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        full_prompt = "\n".join(chat_history + [f"User: {prompt}"])
        response = model.generate_content(full_prompt)
        answer = response.text.strip()
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



frame = ttk.Frame(root, padding=15)
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

# Group 1: Input Configuration
input_frame = ttk.LabelFrame(frame, text="Input Configuration", padding=10)
input_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=5)

logo_path = "scec.png"  # Update this path if needed
logo_image = Image.open(logo_path)
logo_image = logo_image.resize((60, 60), Image.Resampling.LANCZOS)
logo_photo = ImageTk.PhotoImage(logo_image)

# Display inside the input frame
logo_label = tk.Label(input_frame, image=logo_photo)
logo_label.image = logo_photo  # prevent garbage collection
logo_label.grid(row=0, column=3, rowspan=3, padx=(50, 0), sticky="e")


tk.Label(input_frame, text="Request Label:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
tk.Entry(input_frame, textvariable=request_label, width=30).grid(row=0, column=1, columnspan=2, sticky="w", padx=5, pady=2)

tk.Label(input_frame, text="Model:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
model_menu = ttk.Combobox(input_frame, textvariable=selected_model, state="readonly", width=28)
model_menu['values'] = [m.get_name() for m in model_list]
model_menu.grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=2)

tk.Label(input_frame, text="Data Product:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
dp_menu = ttk.Combobox(input_frame, textvariable=selected_product, state="readonly", width=28)
dp_menu['values'] = [d.get_name() for d in dp_list]
dp_menu.grid(row=2, column=1, columnspan=2, sticky="w", padx=5, pady=2)

# Group 2: Output Settings
output_frame = ttk.LabelFrame(frame, text="Output Settings", padding=10)
output_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)

tk.Label(output_frame, text="Output Format:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
tk.OptionMenu(output_frame, output_format, "csv", "sqlite").grid(row=0, column=1, sticky="w", padx=5, pady=2)

tk.Label(output_frame, text="Output Directory:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
tk.Entry(output_frame, textvariable=output_dir, width=30).grid(row=1, column=1, padx=5, pady=2)
tk.Button(output_frame, text="Browse", command=lambda: output_dir.set(filedialog.askdirectory())).grid(row=1, column=2, padx=5, pady=2)

# Filter Config Button
tk.Button(frame, text="Configure Filters", command=lambda: build_filter_inputs()).grid(row=2, column=2, sticky="e", pady=(5, 10))

# Group 3: Action Buttons
action_frame = ttk.Frame(frame)
action_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))

filter_frame = ttk.LabelFrame(frame, text="Filter Configuration", padding=10)
filter_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(10, 0))

tk.Button(action_frame, text="Read Seismogram", command=lambda: read_and_plot_grm(), bg="purple", fg="white", width=18).grid(row=0, column=0, padx=10)
tk.Button(action_frame, text="Run Tool", command=lambda: run_all(), bg="green", fg="white", width=18).grid(row=0, column=1, padx=10)
tk.Button(action_frame, text="Ask AI", command=lambda: open_llm_popup(), bg="blue", fg="white", width=18).grid(row=0, column=2, padx=10)

def open_map_window():
    map_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leaflet_map.html")
    webview.create_window("CyberShake Interactive Map", map_path, width=800, height=600)
    webview.start()


tk.Button(action_frame, text="Open Map", command=open_map_window, bg="orange", fg="black", width=18).grid(row=2, column=1, padx=15, pady=(10, 0))

# --- Dynamic Filters ---
def build_filter_inputs():
    global filter_widgets, selected_filters
    for w in filter_widgets:
        w.destroy()
    filter_widgets.clear()
    selected_filters.clear()

    for widget in filter_frame.winfo_children():
        widget.destroy()

    dp_name = selected_product.get()
    model_name = selected_model.get()
    model_obj = next((m for m in model_list if m.get_name() == model_name), None)
    dp_obj = next((d for d in dp_list if d.get_name() == dp_name), None)
    if not dp_obj:
        return

    relevant_types = dp_obj.get_relevant_filters()
    row = 0
    for f in filter_list:
        if f.get_data_product() not in relevant_types:
            continue
        tk.Label(filter_frame, text=f.get_name()).grid(row=row, column=0, sticky="e", padx=5, pady=2)
        mode = tk.StringVar(value="single")
        mode_menu = ttk.Combobox(filter_frame, values=["single", "multiple", "range"], state="readonly", width=10)
        mode_menu.grid(row=row, column=1, padx=5, pady=2)
        mode_menu.set("single")
        entry = tk.Entry(filter_frame)
        entry.grid(row=row, column=2, padx=5, pady=2)
        filter_widgets.append(entry)
        selected_filters.append((f, entry, mode_menu))
        row += 1


# --- Run Logic ---
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
                f.set_value(f.get_type()(val))
            elif mode == "multiple":
                f.set_values([f.get_type()(v.strip()) for v in val.split(",")])
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
                    event_list.append(tuple(map(int, parts)))
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

# --- AI Popup ---
def open_llm_popup():
    popup = tk.Toplevel()
    popup.title("Ask CyberShake AI")
    tk.Label(popup, text="Ask a question about filters, models, or configuration:").pack()
    text_box = tk.Text(popup, height=5, width=60)
    text_box.pack()
    tk.Label(popup, text="Ai Response:").pack()
    response_box = tk.Text(popup, height=10, width=60, wrap="word")
    response_box.pack()

    def submit():
        question = text_box.get("1.0", tk.END).strip()
        if not question:
            return
        response = ask_llm(question)
        response_box.delete("1.0", tk.END)
        response_box.insert(tk.END, response)

    tk.Button(popup, text="Submit", command=submit).pack(pady=5)

# --- Seismogram Reader ---
def read_and_plot_grm():
    out_dir = output_dir.get()
    if not os.path.exists(out_dir):
        messagebox.showerror("Directory Error", f"Output directory does not exist:\n{out_dir}")
        return
    file_path = filedialog.askopenfilename(
        title="Select a .grm Seismogram File",
        initialdir=out_dir,
        filetypes=[("GRM Files", "*.grm"), ("All Files", "*.*")]
    )
    if not file_path:
        return
    try:
        with open(file_path, 'rb') as f:
            data = np.fromfile(f, dtype=np.float32)
        if data.size == 0:
            messagebox.showwarning("Empty File", "The selected .grm file contains no data.")
            return
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


root.mainloop()
