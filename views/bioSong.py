import tkinter as tk
from tkinter import ttk
import scipy.io.wavfile
import matplotlib.pyplot as plt
import pydub
import numpy as np
from scipy import signal
import librosa
from helpers import *
from views.SearchPage import SearchPage

class bioSong(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.iconbitmap(self, default="../icon.ico")
        tk.Tk.wm_title(self, "bioSong")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand="true")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Set Directory", command=set_dir)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=quit)
        menubar.add_cascade(label="File", menu=filemenu)

        xc_menu = tk.Menu(menubar, tearoff=0)
        xc_menu.add_command(
            label="Search", command=lambda: self.show_frame(SearchPage))
        menubar.add_cascade(label="Xeno-Canto", menu=xc_menu)

        datamenu = tk.Menu(menubar, tearoff=0)
        datamenu.add_command(label="Convert to wav",
                             command=lambda: self.show_frame(ConversionPage))
        datamenu.add_command(
            label="Resample", command=lambda: self.show_frame(ResamplePage))
        datamenu.add_command(
            label="STFT", command=lambda: self.show_frame(StftPage))
        menubar.add_cascade(label="Data Manipulation", menu=datamenu)

        tk.Tk.config(self, menu=menubar)

        self.frames = {}
        for f in (SearchPage, ConversionPage, ResamplePage, StftPage):
            frame = f(container, self)
            self.frames[f] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(SearchPage)

        page_name = SearchPage.__name__
        self.frames[page_name] = frame

    def show_frame(self, c):
        frame = self.frames[c]
        frame.tkraise()

    def get_page(self, page_name):
        return self.frames[page_name]
# -----------------------------------------------------------

class ConversionPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        top_frame = ttk.Frame(self)
        top_frame.pack(fill="both")
        input_frame = ttk.Frame(top_frame)
        input_frame.pack(side="left", fill='both')

        main_label = ttk.Label(
            input_frame, text="Convert .mp3 to .wav", font=Large_Font)
        data_button = ttk.Button(
            input_frame, text="Select Data", command=lambda: self.fill_list())
        convert_button = ttk.Button(
            input_frame, text="Convert", command=lambda: self.createDir(path))

        main_label.grid(row=0, column=0, padx=10, pady=10)
        data_button.grid(row=0, column=2, padx=10, pady=10)
        convert_button.grid(row=0, column=3, padx=10, pady=10)

        progress_frame = ttk.Frame(top_frame)
        progress_frame.pack(side="right", fill="both")
        progress_var = tk.DoubleVar()
        progress_label = ttk.Label(progress_frame, text="Progress: ")
        progress_label.pack(side="left", anchor="s", pady=5)
        self.progress_bar = ttk.Progressbar(
            progress_frame, variable=progress_var, maximum=100)
        self.progress_bar.pack(fill="x", anchor="sw",
                               expand="yes", pady=5, padx=5)

        data_frame = tk.Frame(self, relief="groove",
                              borderwidth=1, background="white")
        data_frame.pack(fill='both', expand=True)
        data_frame.grid_columnconfigure(0, weight=1)
        data_frame.grid_rowconfigure(1, weight=1)

        files_label = ttk.Label(
            data_frame, text="Files to convert: ", background="white")
        self.data_list = tk.Listbox(data_frame)
        listYScroll = ttk.Scrollbar(data_frame, orient="vertical")
        listYScroll.configure(command=self.data_list.yview)
        self.data_list.configure(yscrollcommand=listYScroll.set)

        self.data_list.rowconfigure(0, weight=1)
        self.data_list.columnconfigure(0, weight=1)

        files_label.grid(row=0, column=0, sticky="w", pady=2)
        self.data_list.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        listYScroll.grid(row=1, column=0, sticky="nse", pady=6, padx=7)

        self.status_label = ttk.Label(self, text="", border=1)
        self.status_label.pack(side="bottom", fill='x')

    def createDir(self, path):
        wav_path = path + "/wav files/"
        if not os.path.exists(wav_path):
            os.makedirs(wav_path)
        self.convert_mp3(path, wav_path)

    def fill_list(self):
        global path
        path = set_dir()
        for file in os.listdir(path):
            if file.endswith('.mp3'):
                self.data_list.insert("end", file)

    def convert_mp3(self, path, wav_path):
        i = 0
        global progress_var
        progress_var = tk.DoubleVar()
        progress = 0
        progress_step = float(100.0/self.data_list.size())
        for file in os.listdir(path):
            if file.endswith('.mp3'):
                mp3 = pydub.AudioSegment.from_mp3(file)
                self.status_label.config(
                    text="Converting " + file + " to .wav")
                file_name = os.path.splitext(file)[0] + "-" + str(i)
                mp3.export(wav_path + file_name + ".wav", format="wav")
                coverted = self.data_list.get(0, "end").index(file)
                self.data_list.delete(coverted)
                self.update()
                progress += progress_step
                progress_var.set(progress)
                i += 1

        self.status_label.config(text="Done")
# -----------------------------------------------------------


class ResamplePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        top_frame = ttk.Frame(self)
        top_frame.pack(fill="both")
        input_frame = ttk.Frame(top_frame)
        input_frame.pack(side="left", fill='both')

        main_label = ttk.Label(input_frame, text="Resample", font=Large_Font)
        data_button = ttk.Button(
            input_frame, text="Select Data", command=lambda: self.fill_list())
        resample_button = ttk.Button(
            input_frame, text="Resample", command=lambda: self.createDir(path))
        self.up = tk.IntVar()
        self.up_sample = ttk.Checkbutton(
            input_frame, text="Upsample", variable=self.up)
        self.down = tk.IntVar()
        self.down_sample = ttk.Checkbutton(
            input_frame, text="Downsample", variable=self.down)
        sample_label = ttk.Label(input_frame, text="Select resample rate:")
        self.sample_rate = ttk.Combobox(input_frame, state="readonly")
        self.sample_rate["values"] = (
            "48000 Hz", "44100 Hz", "32000 Hz", "22050 Hz")

        main_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        data_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.up_sample.grid(row=0, column=3, padx=10, pady=2, sticky="w")
        self.down_sample.grid(row=1, column=3, padx=10, pady=2, sticky="w")
        sample_label.grid(row=0, column=4, padx=10, pady=2, sticky="w")
        self.sample_rate.grid(row=1, column=4, padx=10, pady=2, sticky="w")
        resample_button.grid(row=0, column=5, rowspan=2,
                             padx=10, pady=10, sticky="nsew")

        progress_frame = ttk.Frame(top_frame)
        progress_frame.pack(side="right", fill="both")
        progress_var = tk.DoubleVar()
        progress_label = ttk.Label(progress_frame, text="Progress: ")
        progress_label.pack(side="left", anchor="s", pady=5)
        self.progress_bar = ttk.Progressbar(
            progress_frame, variable=progress_var, maximum=100)
        self.progress_bar.pack(fill="x", anchor="sw",
                               expand="yes", pady=5, padx=5)

        data_frame = tk.Frame(self, relief="groove",
                              borderwidth=1, background="white")
        data_frame.pack(fill='both', expand=True)
        data_frame.grid_columnconfigure(0, weight=1)
        data_frame.grid_rowconfigure(1, weight=1)

        files_label = ttk.Label(
            data_frame, text="Files to resample: ", background="white")
        self.data_list = ttk.Treeview(data_frame)
        self.data_list['columns'] = ("rate")
        self.data_list.heading("#0", text='File name', anchor='w', command=lambda: sort_by(
            self.data_list, "#0", False))
        self.data_list.column("#0", anchor="w", width=200)
        self.data_list.heading("rate", text="Rate (Hz)", anchor='w', command=lambda: sort_by(
            self.data_list, "rate", False))
        self.data_list.column('rate', anchor='w', width=100)
        listYScroll = ttk.Scrollbar(data_frame, orient="vertical")
        listYScroll.configure(command=self.data_list.yview)
        self.data_list.configure(yscrollcommand=listYScroll.set)

        self.data_list.rowconfigure(0, weight=1)
        self.data_list.columnconfigure(0, weight=1)

        files_label.grid(row=0, column=0, sticky="w", pady=2)
        self.data_list.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        listYScroll.grid(row=1, column=0, sticky="nse", pady=6, padx=7)

        self.status_label = ttk.Label(self, text="", border=1)
        self.status_label.pack(side="bottom", fill='x')

    def createDir(self, path):
        temp = self.sample_rate.get()
        rate = int(temp.strip(" Hz"))
        sample_path = path + "/resampled" + str(rate) + "/"
        if not os.path.exists(sample_path):
            os.makedirs(sample_path)
        self.resample(path, sample_path)

    def fill_list(self):
        global path
        path = set_dir()
        for file in os.listdir(path):
            if file.endswith('.wav'):
                x, rate = librosa.load(path + "/" + file, sr=None)
                self.data_list.insert(
                    "", "end", iid=file, text=file, values=(rate))
                self.status_label.config(text="Getting recordings...")
                self.update()
            self.status_label.config(text="Done")

    def resample(self, path, sample_path):
        i = 0
        global progress_var
        progress_var = tk.DoubleVar()
        progress = 0
        progress_step = float(100.0/len(self.data_list.get_children()))
        up = self.up.get()
        down = self.down.get()
        temp = self.sample_rate.get()
        new_rate = int(temp.strip(" Hz"))
        for file in os.listdir(path):
            if file.endswith('.wav'):
                audData, rate = librosa.load(path + "/" + file, sr=None)
                if up == 1 and down == 0:
                    if rate <= new_rate:
                        temp = librosa.resample(audData, rate, new_rate)
                        librosa.output.write_wav(
                            sample_path + file, temp, sr=new_rate)
                if up == 0 and down == 1:
                    if rate >= new_rate:
                        temp = librosa.resample(audData, rate, new_rate)
                        librosa.output.write_wav(
                            sample_path + file, temp, sr=new_rate)
                if up == 1 and down == 1:
                    if rate != new_rate:
                        temp = librosa.resample(audData, rate, new_rate)
                        librosa.output.write_wav(
                            sample_path + file, temp, sr=new_rate)
                    if rate == new_rate:
                        librosa.output.write_wav(
                            sample_path + file, audData, sr=rate)
                self.status_label.config(
                    text="Resampling " + file + " to " + str(new_rate) + "Hz")
                self.data_list.delete(file)
                self.update()
                progress += progress_step
                progress_var.set(progress)
                i += 1
        self.status_label.config(text="Done")
# -----------------------------------------------------------


class StftPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        top_frame = ttk.Frame(self)
        top_frame.pack(fill="both")

        input_frame = ttk.Frame(top_frame)
        input_frame.pack(side="left", fill='both')

        window_frame = ttk.Frame(input_frame)
        window_frame.pack(side="top", fill='both')

        main_label = ttk.Label(window_frame, text="STFT", font=Large_Font)
        data_button = ttk.Button(window_frame, text="Select Data", command=lambda: self.fill_list())

        segment_size_label = ttk.Label(window_frame, text="Segment size (ms):")
        self.segment_size = ttk.Entry(window_frame, width=10)
        self.segment_size.insert(0, "500")
        segment_step_label = ttk.Label(
            window_frame, text="Segment step size (ms):")
        self.segment_step = ttk.Entry(window_frame, width=10)
        self.segment_step.insert(0, "150")
        window_size_label = ttk.Label(window_frame, text="Window size:")
        self.window_size = ttk.Entry(window_frame, width=10)
        self.window_size.insert(0, "512")
        window_step_label = ttk.Label(window_frame, text="Window step size:")
        self.window_step = ttk.Entry(window_frame, width=10)
        self.window_step.insert(0, "256")
        stft_window_label = ttk.Label(window_frame, text="Select window:")
        self.stft_window = ttk.Combobox(
            window_frame, state="readonly", width=15)
        self.stft_window["values"] = ("boxcar", "triang", "blackman", "hamming", "hann",
                                      "bartlett", "flattop", "parzen", "bohman", "blackmanharris", "nuttall", "barthann")
        self.stft_window.current(4)
        zero_pad_label = ttk.Label(
            window_frame, text="Zero padding:")
        self.zero_pad = ttk.Entry(window_frame, width=15)
        self.zero_pad.insert(0, "None")
        start_button = ttk.Button(window_frame, text="Start", command=lambda: self.segment_wav())

        main_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        data_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        segment_size_label.grid(row=0, column=1, padx=2, pady=5, sticky="w")
        self.segment_size.grid(row=0, column=2, padx=2, pady=5, sticky="w")
        segment_step_label.grid(row=0, column=3, padx=2, pady=5, sticky="w")
        self.segment_step.grid(row=0, column=4, padx=2, pady=5, sticky="w")
        stft_window_label.grid(row=0, column=5, padx=2, pady=5, sticky="w")
        self.stft_window.grid(row=0, column=6, padx=2, pady=5, sticky="w")

        window_size_label.grid(row=1, column=1, padx=2, pady=5, sticky="w")
        self.window_size.grid(row=1, column=2, padx=2, pady=5, sticky="w")
        window_step_label.grid(row=1, column=3, padx=2, pady=5, sticky="w")
        self.window_step.grid(row=1, column=4, padx=2, pady=5, sticky="w")
        zero_pad_label.grid(row=1, column=5, padx=2, pady=5, sticky="w")
        self.zero_pad.grid(row=1, column=6, padx=2, pady=5, sticky="w")
        start_button.grid(row=0, column=7, rowspan=2,
                          padx=10, pady=5, sticky="nsew")

        stft_frame = ttk.Frame(input_frame)
        stft_frame.pack(side="bottom", fill='both')

        boundary_label = ttk.Label(stft_frame, text="Select boundary:")
        self.boundary = ttk.Combobox(stft_frame, state="readonly", width=15)
        self.boundary["values"] = ("even", "odd", "constant", "zeros", "None")
        self.boundary.current(4)
        padded_label = ttk.Label(stft_frame, text="Input padded:")
        self.padded = ttk.Combobox(stft_frame, state="readonly", width=15)
        self.padded["values"] = ("True", "False")
        self.padded.current(1)
        axis_label = ttk.Label(stft_frame, text="Set axis:")
        self.axis = ttk.Entry(stft_frame, width=15)
        self.axis.insert(0, "0")

        boundary_label.grid(row=0, column=0, padx=2, pady=5, sticky="w")
        self.boundary.grid(row=0, column=1, padx=2, pady=5, sticky="w")
        padded_label.grid(row=0, column=2, padx=2, pady=5, sticky="w")
        self.padded.grid(row=0, column=3, padx=2, pady=5, sticky="w")
        axis_label.grid(row=0, column=4, padx=2, pady=5, sticky="w")
        self.axis.grid(row=0, column=5, padx=2, pady=5, sticky="w")

        progress_frame = ttk.Frame(top_frame)
        progress_frame.pack(side="right", fill="both")
        progress_var = tk.DoubleVar()
        progress_label = ttk.Label(progress_frame, text="Progress: ")
        progress_label.pack(side="left", anchor="s", pady=5)
        self.progress_bar = ttk.Progressbar(
            progress_frame, variable=progress_var, maximum=100)
        self.progress_bar.pack(fill="x", anchor="sw",
                               expand="yes", pady=5, padx=5)

        data_frame = tk.Frame(self, relief="groove",
                              borderwidth=1, background="white")
        data_frame.pack(fill='both', expand=True)
        data_frame.grid_columnconfigure(0, weight=1)
        data_frame.grid_rowconfigure(1, weight=1)

        files_label = ttk.Label(
            data_frame, text="Files to tramsform: ", background="white")
        self.data_list = ttk.Treeview(data_frame)
        self.data_list['columns'] = ("rate")
        self.data_list.heading("#0", text='File name', anchor='w', command=lambda: sort_by(
            self.data_list, "#0", False))
        self.data_list.column("#0", anchor="w", width=200)
        self.data_list.heading("rate", text="Rate (Hz)", anchor='w', command=lambda: sort_by(
            self.data_list, "rate", False))
        self.data_list.column('rate', anchor='w', width=100)
        listYScroll = ttk.Scrollbar(data_frame, orient="vertical")
        listYScroll.configure(command=self.data_list.yview)
        self.data_list.configure(yscrollcommand=listYScroll.set)

        self.data_list.rowconfigure(0, weight=1)
        self.data_list.columnconfigure(0, weight=1)

        files_label.grid(row=0, column=0, sticky="w", pady=2)
        self.data_list.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        listYScroll.grid(row=1, column=0, sticky="nse", pady=6, padx=7)

        self.status_label = ttk.Label(self, text="", border=1)
        self.status_label.pack(side="bottom", fill='x')


    def fill_list(self):
        global path
        path = set_dir()
        for file in os.listdir(path):
            if file.endswith('.wav'):
                x, rate = librosa.load(path + "/" + file, sr=None)
                self.data_list.insert(
                    "", "end", iid=file, text=file, values=(rate))
                self.status_label.config(text="Getting recordings...")
                self.update()
            self.status_label.config(text="Done")

    def segment_wav (self):
        new_path = path + "/images/"
        if not os.path.exists(new_path):
            os.makedirs(new_path)
        segment_size = int(self.segment_size.get())
        segment_step_size = int(self.segment_step.get())
        window_size = int(self.window_size.get())
        window_step_size = int(self.window_step.get())
        window_type = self.stft_window.get()
        nfft = self.zero_pad.get()
        if nfft == "None":
            nfft = None
        boundary = self.boundary.get()
        if boundary == "None":
            boundary = None
        padded = self.padded.get()
        if padded == "True":
            padded = True
        else:
            padded = False
        axis = int(self.axis.get())
        for file in os.listdir(path):
            if file.endswith('.wav'):
                stop = 0
                count = 0
                step = 0
                call, rate = librosa.load(file, sr=None)
                segment_size = int(rate // (1000 / segment_size))
                segment_step_size = int(rate // (1000 / segment_step_size))
                call_length = len(call)
                stop = (call_length - segment_size) // segment_step_size
                while count <= stop:
                    segment = call[step:segment_size + step]
                    f, t, Zxx = scipy.signal.stft(segment, rate, window_type, window_size, window_step_size, nfft = nfft, boundary = boundary, padded = padded, axis = axis)
                    fig = plt.pcolormesh(t, f, np.abs(Zxx))
                    plt.axis('off')
                    fig.axes.get_xaxis().set_visible(False)
                    fig.axes.get_yaxis().set_visible(False)
                    plt.savefig(new_path + file + str(count) + ".png", bbox_inches='tight', pad_inches=0)
                    step += segment_step_size
                    count += 1
# -----------------------------------------------------------


app = bioSong()
app.geometry("950x500")
app.mainloop()
