import tkinter as tk
from tkinter import ttk
import urllib
import urllib.request
import json
from helpers import *


class SearchPage(tk.Frame):

    XC_API = "http://www.xeno-canto.org/api/2/recordings?query="
    result = None
    num_recs = None
    country = None
    species = None
    param = None
    flag = False
    downloading = False

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        input_frame = ttk.Frame(self)
        input_frame.pack(fill='both')
        tab_control = ttk.Notebook(input_frame)
        normal_search = ttk.Frame(tab_control)
        advanced_search = ttk.Frame(tab_control)
        download = ttk.Frame(tab_control)
        tab_control.pack(expand=1, fill="both")

        # Search tab -----------------------------------------
        tab_control.add(normal_search, text="Search")
        label = ttk.Label(
            normal_search, text="Xeno-Canto Search", font=Large_Font)

        species_label = ttk.Label(normal_search, text="Species:")
        self.species_input = ttk.Entry(normal_search)

        country_label = ttk.Label(normal_search, text="Country:")
        self.country_input = ttk.Entry(normal_search)

        search_btn = ttk.Button(normal_search, text="Search", command=lambda: self.check_search_input(
            self.species_input.get(), self.country_input.get()))

        download_all_btn = ttk.Button(
            normal_search, text="Download All", command=lambda: self.xc_download_recs(False))
        download_selected_btn = ttk.Button(
            normal_search, text="Download Selected", command=lambda: self.xc_download_recs(True))

        label.grid(row=0, column=0, columnspan=2,
                   sticky="nsew", padx=20, pady=10)
        species_label.grid(row=0, column=2, sticky="e", padx=10, pady=10)
        self.species_input.grid(row=0, column=3, sticky="w")
        country_label.grid(row=0, column=4, sticky="e", padx=10, pady=10)
        self.country_input.grid(row=0, column=5, sticky="w")
        search_btn.grid(row=0, column=6, sticky="w", padx=10, pady=10)
        ttk.Separator(normal_search, orient="vertical").grid(column=7, row=0, rowspan=1, sticky='ns')
        download_selected_btn.grid(row=0, column=8, sticky="w", padx=20, pady=10)
        download_all_btn.grid(row=0, column=9, sticky="w", padx=10, pady=10)


        # Advanced Search tab -----------------------------------------
        tab_control.add(advanced_search, text="Advanced Search")
        ttk.Label(advanced_search, text="Not Supported").grid(
            row=0, column=2, sticky="e", padx=20, pady=10)


        results_frame = tk.Frame(
            self, relief="groove", borderwidth=1, background="white")
        results_frame.pack(fill='both', expand=True)
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(1, weight=1)

        results_label = ttk.Label(
            results_frame, text="Results: ", background="white")
        self.search_results = ttk.Treeview(results_frame)
        self.search_results['columns'] = (
            "length", "country", "location", "type", "cat")
        self.search_results.heading("#0", text='Species', anchor='w', command=lambda: sort_by(
            self.search_results, "#0", False))
        self.search_results.column("#0", anchor="w", width=200)
        self.search_results.heading("length", text='Length (s)', anchor='w', command=lambda: sort_by(
            self.search_results, "length", False))
        self.search_results.column('length', anchor='w', width=100)
        self.search_results.heading('country', text='Country', anchor='w', command=lambda: sort_by(
            self.search_results, "country", False))
        self.search_results.column('country', anchor='w', width=125)
        self.search_results.heading('location', text='Location', anchor='w', command=lambda: sort_by(
            self.search_results, "location", False))
        self.search_results.column('location', anchor='w', width=125)
        self.search_results.heading('type', text='Type', anchor='w', command=lambda: sort_by(
            self.search_results, "type", False))
        self.search_results.column('type', anchor='w', width=100)
        self.search_results.heading('cat', text='Cat.nr', anchor='w', command=lambda: sort_by(
            self.search_results, "cat", False))
        self.search_results.column('cat', anchor='w', width=150)
        treeYScroll = ttk.Scrollbar(results_frame, orient="vertical")
        treeYScroll.configure(command=self.search_results.yview)
        self.search_results.configure(yscrollcommand=treeYScroll.set)

        self.search_results.rowconfigure(0, weight=1)
        self.search_results.columnconfigure(0, weight=1)

        # Create search results view
        results_label.grid(row=0, column=0, sticky="w", pady=2)
        self.search_results.grid(
            row=1, column=0, sticky="nsew", padx=5, pady=5)
        treeYScroll.grid(row=1, column=0, sticky="nse", pady=6, padx=7)

        self.status_label = ttk.Label(self, text="", border=1)
        self.status_label.pack(side="bottom", fill='x')

    # Checks if user has actually input something
    def check_search_input(self, species, country):
        self.species = species
        species = species.strip()
        self.country = country
        country = country.strip()
        if not species and not country or has_numbers(species + country):
            error_popup("Warning", "Please input a valid species and or a country.")
            return
        if not country and " " not in species:
            error_popup("Warning", "Please use valid syntax e.g Genus species.")
            return
        else:
            if country and not species:
                country = country.replace(" ", "&")
                param = "cnt:" + country
            else:
                if country and species:
                    self.flag = True
                genus, species = species.split(" ")
                param = genus + "%20" + species
        self.species_input.delete(0, 'end')
        self.country_input.delete(0, 'end')
        self.update_idletasks()
        self.xc_get_json(param)

    # gets the json file
    def xc_get_json(self, param):
        link = self.XC_API + param
        result = urllib.request.urlopen(link)
        status = result.getcode()
        if status == 200:
            self.result = json.load(result)
            if self.result["numRecordings"] == "0":
                error_popup(
                    "Error", "There seems to have been an error with your request.\nNo recordings found.")
            else:
                self.populate_search_results(self.result)
        else:
            error_popup("Error", "Code: " + status +
                        "There seems to have been an error with your request.")

    # Populates the list view for user
    def populate_search_results(self, result):
        for row in self.search_results.get_children():
            self.search_results.delete(row)
        num_recs = result["numRecordings"]
        num_spec = result["numSpecies"]
        # If both the whole country result is taken and only where
        # the country matches are the results populated to the table
        if self.flag:
            for r in result["recordings"]:
                co = r["cnt"]
                if co.lower() == self.country.lower():
                    self.populate(r)
            self.status_label.config(
                text="Search Results:  " + num_recs + " recordings from " + num_spec + " species found.")
        else:
            self.status_label.config(
                text="Search Results:  " + num_recs + " recordings from " + num_spec + " species found.")
            for r in result["recordings"]:
                self.populate(r)

    # Function that calls the tkinter instert function with results
    def populate(self, r):
        en = r["en"]
        ge = r["gen"]
        sp = r["sp"]
        le = r["time"]
        co = r["cnt"]
        lo = r["loc"]
        ty = r["type"]
        nr = r["id"]
        self.search_results.insert(
            "", "end", text=ge + " " + sp + " - " + en, values=(le, co, lo, ty, nr))

    # Function for downloading the search results
    def xc_download_recs(self, selected):
        if self.result is None:
            error_popup("Warning", "No recordings to download.")
        else:
            path = set_dir()
            self.status_label.config(text="Downloading...")
            self.update_idletasks()
            self.popup = tk.Toplevel()
            self.popup.geometry("300x200")
            tk.Label(self.popup, text="Downloading recording: ").pack(pady=5)
            curr_dl = tk.Label(self.popup, text="")
            curr_dl.pack()
            progress = 0
            progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(
                self.popup, variable=progress_var, maximum=100)
            progress_bar.pack(fill="x", anchor="w",
                              expand="yes", pady=5, padx=5)
            self.cancel_btn = ttk.Button(
                self.popup, text="Cancel", command=lambda: self.stop())
            self.cancel_btn.pack(pady=10)
            self.popup.pack_slaves()
            self.downloading = True
            if selected and self.downloading:
                count = 1
                selected_items = self.search_results.selection()
                progress_step = float(100.0 / len(selected_items))
                tk.Label(self.popup, text=" of " + str(len(selected_items))).pack()
                data = []
                for recording in selected_items:
                    recording = self.search_results.item(recording)
                    nr = recording['values'][-1:]
                    x = [rec for rec in self.result["recordings"] if rec["id"] == str(nr[0])]
                    data.append(x[0])
            else:
                progress_step = float(100.0 / self.result["numRecordings"])
                tk.Label(self.popup, text=" of " + str(self.result["numRecordings"])).pack()
                data = self.result["recordings"]
            for p in data:
                recording_url = "https:" + p["file"]
                download_file = p["file-name"]
                full_filename = os.path.join(
                    path, download_file)
                urllib.request.urlretrieve(
                    recording_url, full_filename)
                self.popup.update()
                curr_dl.configure(text=count)
                progress += progress_step
                progress_var.set(progress)
                count += 1
            self.stop_downloading()

    # Function for downloading stop button
    def stop_downloading(self):
        self.downloading = False
        self.status_label.config(text="")
        self.update_idletasks()
        self.popup.destroy()
