import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter import messagebox
from isocor.ui.isocordb import EnvComputing
import logging
import pandas as pd
import isocor as hr
from pathlib import Path
import numpy as np
import re
import webbrowser
import threading
import urllib

UTF8_TABLE_SUBCRIPS_INT = {'0': '\u2070', '1': '\u00B9', '2': '\u00B2', '3': '\u00B3',
                           '4': '\u2074', '5': '\u2075', '6': '\u2076', '7': '\u2077', '8': '\u2078', '9': '\u2079'}


class Tooltip:
    """
    It creates a tooltip for a given widget as the mouse goes on it.

    see:

    http://stackoverflow.com/questions/3221956/
           what-is-the-simplest-way-to-make-tooltips-
           in-tkinter/36221216#36221216

    http://www.daniweb.com/programming/software-development/
           code/484591/a-tooltip-class-for-tkinter

    - Originally written by vegaseat on 2014.09.09.

    - Modified to include a delay time by Victor Zaccardo on 2016.03.25.

    - Modified
        - to correct extreme right and extreme bottom behavior,
        - to stay inside the screen whenever the tooltip might go out on
          the top but still the screen is higher than the tooltip,
        - to use the more flexible mouse positioning,
        - to add customizable background color, padding, waittime and
          wraplength on creation
      by Alberto Vassena on 2016.11.05.
    """

    def __init__(self, widget,
                 *,
                 bg='#FFFFEA',
                 pad=(5, 3, 5, 3),
                 text='widget info',
                 waittime=400,
                 wraplength=250):

        self.waittime = waittime  # in miliseconds, originally 500
        self.wraplength = wraplength  # in pixels, originally 180
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<ButtonPress>", self.on_leave)
        self.bg = bg
        self.pad = pad
        self.id = None
        self.tw = None

    def on_enter(self, event=None):
        self.schedule()

    def on_leave(self, event=None):
        self.unschedule()
        self.hide()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.show)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def show(self):
        def tip_pos_calculator(widget, label,
                               *,
                               tip_delta=(10, 5), pad=(5, 3, 5, 3)):

            w = widget

            s_width, s_height = w.winfo_screenwidth(), w.winfo_screenheight()

            width, height = (pad[0] + label.winfo_reqwidth() + pad[2],
                             pad[1] + label.winfo_reqheight() + pad[3])

            mouse_x, mouse_y = w.winfo_pointerxy()

            x1, y1 = mouse_x + tip_delta[0], mouse_y + tip_delta[1]
            x2, y2 = x1 + width, y1 + height

            x_delta = x2 - s_width
            if x_delta < 0:
                x_delta = 0
            y_delta = y2 - s_height
            if y_delta < 0:
                y_delta = 0

            offscreen = (x_delta, y_delta) != (0, 0)

            if offscreen:

                if x_delta:
                    x1 = mouse_x - tip_delta[0] - width

                if y_delta:
                    y1 = mouse_y - tip_delta[1] - height

            offscreen_again = y1 < 0  # out on the top

            if offscreen_again:
                # No further checks will be done.

                # TIP:
                # A further mod might automagically augment the
                # wraplength when the tooltip is too high to be
                # kept inside the screen.
                y1 = 0

            return x1, y1

        bg = self.bg
        pad = self.pad
        widget = self.widget

        # creates a toplevel window
        self.tw = tk.Toplevel(widget)

        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)

        win = tk.Frame(self.tw,
                       background=bg,
                       borderwidth=0)
        label = tk.Label(win,
                         text=self.text,
                         justify=tk.LEFT,
                         background=bg,
                         relief=tk.SOLID,
                         borderwidth=0,
                         wraplength=self.wraplength)

        label.grid(padx=(pad[0], pad[2]),
                   pady=(pad[1], pad[3]),
                   sticky=tk.NSEW)
        win.grid()

        x, y = tip_pos_calculator(widget, label)

        self.tw.wm_geometry("+%d+%d" % (x, y))

    def hide(self):
        tw = self.tw
        if tw:
            tw.destroy()
        self.tw = None


class TextHandler(logging.Handler):
    """This class allows you to log to a Tkinter Text or ScrolledText widget"""

    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.text.configure(state='normal')
            self.text.insert(tk.END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(tk.END)

        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)


class PurityTracerManager(tk.Canvas):
    def __init__(self, master=None, **kwargs):
        tk.Canvas.__init__(self, master, **kwargs)
        #  self._initFrameInWindows()
        self.tracer_purity = []

    def _initFrameInWindows(self):
        self.frame = ttk.Frame(self)
        self.create_window((0, 0), anchor="nw", window=self.frame)

    def changeEntries(self, df, tracer):
        row = 0
        self.tracer_purity = []
        # canvas clear all method
        self.delete("all")
        self._initFrameInWindows()
        purity = (df['subscriptName'] ==
                  tracer.iloc[0]['subscriptName']).astype(int)
        for entry in df.itertuples():
            purityentry = tk.StringVar()
            purityentry.set(str(purity[entry.Index]))
            label_entry = ttk.Label(
                self.frame, text=entry.subscriptName).grid(row=row, column=0, sticky="news")
            purity_entry = ttk.Entry(
                self.frame, textvariable=purityentry).grid(row=row, column=1, sticky="news")
            self.tracer_purity.append(purityentry)
            row += 1
        self.create_window((0, 0), anchor="nw", window=self.frame)
        self.frame.update_idletasks()


class GUIinterface(ttk.Frame):
    """GUI interface for isocor in tk widget"""

    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.baseenv = EnvComputing()
        # check the database files exists in the default path,
        # otherwise copy them from the example folder
        self.baseenv.initializeDB()
        # isotope database should be loaded at init and not changed afterwards
        isotopesfile = Path(self.baseenv.db_path, "Isotopes.dat")
        try:
            self.baseenv.registerIsopotes(isotopesfile)
        except Exception as err:
            messagebox.showerror("Error", err)
            quit()

        self.addSubcriptingName()
        self.cleanListTracer()
        self.log_level = 'INFO'
        self.createWidgets()
        self._thread, self._stop = None, True

    def start_process(self):
        if self._thread is None:
            self._stop = False
            self._thread = threading.Thread(target=self.process)
            self._thread.start()
        self.processButon.configure(text="Stop", command=self.stop_process)

    def stop_process(self):
        if self._thread is not None:
            self._thread, self._stop = None, True
        self.processButon.configure(text="Process", command=self.start_process)

    def addSubcriptingName(self):
        self.baseenv.dfIsotopes['subscriptName'] = self.baseenv.dfIsotopes['isotope'].apply(
            self.subscriptingInt) + self.baseenv.dfIsotopes['element']

    def subscriptingInt(self, myint):
        return ''.join([UTF8_TABLE_SUBCRIPS_INT[i] for i in str(myint)])

    def process(self):
        "process Callback"

        # clean GUI logs frame
        self.cleanLog()

        # get correction parameters
        tracer = self.baseenv.dfIsotopes[self.baseenv.dfIsotopes['subscriptName']
                                         == self.isotopictracerCBB.get()]['name'].values[0]
        correct_NA_tracer = self.chVarNatAbTracer.get()
        data_isotopes = self.baseenv.dictIsotopes
        # check critical parameters and cancel processing if errors
        try:
            tracer_purity = [float(i.get()) for i in self.purityManager.tracer_purity]
            if any(i < 0 for i in tracer_purity) or any(i > 1 for i in tracer_purity) or sum(tracer_purity) != 1:
                self.stop_process()
                messagebox.showerror("Error",
                                     "Purity values should be within the range [0, 1], and their sum should be 1.")
                return
        except:
            self.stop_process()
            messagebox.showerror("Error", "Purity values should be within the range [0, 1], and their sum should be 1.")
            return
        if self.chVarHR.get():
            resolution_formula_code = self.formulaEntered.get()
            try:
                resolution = float(self.varMass.get())
                if resolution <= 0:
                    self.stop_process()
                    messagebox.showerror("Error", "Resolution should be a positive number.")
                    return
            except:
                self.stop_process()
                messagebox.showerror("Error", "Resolution should be a positive number.")
                return
            try:
                mz_of_resolution = float(self.varMZ.get())
                if mz_of_resolution <= 0:
                    self.stop_process()
                    messagebox.showerror("Error", "mz at which resolution is measured should be a positive number.")
                    return
            except:
                self.stop_process()
                messagebox.showerror("Error", "mz at which resolution is measured should be a positive number.")
                return

        try:
            derivativesfile = Path(self.varDatabasePath.get(), "Derivatives.dat")
            self.baseenv.registerDerivativesDB(derivativesfile)
        except Exception as err:
            self.stop_process()
            messagebox.showerror("Error", err)
            return
        try:
            metabolitesfile = Path(self.varDatabasePath.get(), "Metabolites.dat")
            self.baseenv.registerMetabolitesDB(metabolitesfile)
        except Exception as err:
            self.stop_process()
            messagebox.showerror("Error", err)
            return
        if self.formulaEntered.get() == 'datafile':
            useformula = False
        else:
            useformula = True

        try:
            input_file = self.varInputPath.get()
            self.baseenv.registerDatafile(input_file, useformula)
            fin_base = str(Path(input_file).stem)
        except Exception as err:
            self.stop_process()
            messagebox.showerror("Error", err)
            return

        # add a filehandler to the logger (to redirect logs to a file)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
        log_file = Path(self.varOutputPath.get()).joinpath(fin_base + '.log')
        file_handler = logging.FileHandler(str(log_file), mode='w+')
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # log general information on the process
        self.logger.info('------------------------------------------------')
        self.logger.info("Correction process")
        self.logger.info('------------------------------------------------')
        self.logger.info("   data files")
        self.logger.info("      data file: {}".format(input_file))
        self.logger.info("      derivatives database: {}".format(derivativesfile))
        self.logger.info("      metabolites database: {}".format(metabolitesfile))
        self.logger.info("   correction parameters")
        self.logger.info("      isotopic tracer: {}".format(tracer))
        self.logger.info("      correct natural abundance of the tracer element: {}".format(correct_NA_tracer))
        self.logger.info("      isotopic purity of the tracer: {}".format(tracer_purity))
        if self.chVarHR.get():
            self.logger.info("      mode: high-resolution")
            self.logger.info("         formula code: {}".format(resolution_formula_code))
            if useformula:
                self.logger.info("         instrument resolution: {}".format(resolution))
            if resolution_formula_code not in ['datafile', 'constant']:
                self.logger.info("         at mz: {}".format(mz_of_resolution))
        else:
            self.logger.info("      mode: low-resolution")
        self.logger.info("   natural abundance of isotopes")
        self.logger.info("   {}".format(data_isotopes))
        self.logger.info("   IsoCor version: {}".format(hr.__version__))

        # initialize error dict
        errors = {'labels': [], 'measurements': []}

        # construct correctors for all (metabolite, derivative)
        labels = self.baseenv.getLabelsList(useformula)
        self.logger.info('------------------------------------------------')
        self.logger.info('Constructing correctors for all (metabolite, derivative)...')
        self.logger.info('------------------------------------------------')
        dictMetabolites = {}
        for label in labels:
            try:
                self.logger.debug("constructing {}...".format(label))
                if self.chVarHR.get():
                    if not useformula:
                        resolution = label[2]
                        resolution_formula_code = 'constant'
                    dictMetabolites[label] = hr.MetaboliteCorrectorFactory(
                        formula=self.baseenv.getMetaboliteFormula(label[0]), tracer=tracer, resolution=resolution,
                        label=label[0],
                        data_isotopes=data_isotopes, mz_of_resolution=mz_of_resolution,
                        derivative_formula=self.baseenv.getDerivativeFormula(label[1]), tracer_purity=tracer_purity,
                        correct_NA_tracer=correct_NA_tracer, resolution_formula_code=resolution_formula_code,
                        charge=self.baseenv.getMetaboliteCharge(label[0]),
                        inchi=self.baseenv.getMetaboliteInChI(label[0]))
                else:
                    dictMetabolites[label] = hr.MetaboliteCorrectorFactory(
                        formula=self.baseenv.getMetaboliteFormula(label[0]), tracer=tracer, label=label[0],
                        data_isotopes=data_isotopes,
                        derivative_formula=self.baseenv.getDerivativeFormula(label[1]), tracer_purity=tracer_purity,
                        correct_NA_tracer=correct_NA_tracer, inchi=self.baseenv.getMetaboliteInChI(label[0]))
                self.logger.info("{} successfully constructed.".format(label))
            except Exception as err:
                dictMetabolites[label] = None
                errors['labels'] = errors['labels'] + [label]
                self.logger.error("cannot construct {}: {}".format(label, err))

        # correct measurements for naturally occuring isotopes
        # note: the correction matrix is constructed only once (at first correction of a (metabolite, derivative))
        self.logger.info('------------------------------------------------')
        self.logger.info('Correcting raw MS data...')
        self.logger.info('------------------------------------------------')
        df = pd.DataFrame()
        for label in labels:
            metabo = dictMetabolites[label]
            series, series_err = self.baseenv.getDataSerie(label, useformula)
            for s_err in series_err:
                errors['measurements'] = errors['measurements'] + ["{} - {}".format(s_err, label)]
                self.logger.error(
                    "{} - {}: Measurement vector is incomplete, some isotopologues are not provided.".format(s_err,
                                                                                                             label))
            for serie in series:
                if metabo:
                    try:
                        isotopic_inchi = metabo.isotopic_inchi
                        valuesCorrected = metabo.correct(serie[1])
                        self.logger.info("{} - {}: processed".format(serie[0], label))
                    except Exception as err:
                        isotopic_inchi = [''] * len(serie[1])
                        valuesCorrected = (
                        [np.nan] * len(serie[1]), [np.nan] * len(serie[1]), [np.nan] * len(serie[1]), np.nan)
                        self.logger.error("{} - {}: {}".format(serie[0], label, err))
                        errors['measurements'] = errors['measurements'] + ["{} - {}".format(serie[0], label)]
                else:
                    isotopic_inchi = [''] * len(serie[1])
                    valuesCorrected = (
                    [np.nan] * len(serie[1]), [np.nan] * len(serie[1]), [np.nan] * len(serie[1]), np.nan)
                    errors['measurements'] = errors['measurements'] + ["{} - {}".format(serie[0], label)]
                    self.logger.error(
                        "{} - {}: (metabolite, derivative) corrector could not be constructed.".format(serie[0], label))

                for i, line in enumerate(zip(*(serie[1], valuesCorrected[0], valuesCorrected[1], valuesCorrected[2],
                                               [valuesCorrected[3]] * len(valuesCorrected[0])))):
                    df = pd.concat((df, pd.DataFrame([line], index=pd.MultiIndex.from_tuples(
                        [[serie[0], label[0], label[1], i, isotopic_inchi[i]]], names=[
                            'sample', 'metabolite', 'derivative', 'isotopologue', 'isotopic_inchi']),
                                                     columns=['area', 'corrected_area', 'isotopologue_fraction',
                                                              'residuum', 'mean_enrichment'])))

        # save results
        out_file = Path(self.varOutputPath.get()).joinpath(fin_base + '_res.tsv')
        df.to_csv(str(out_file), sep='\t')

        # summary results for logs
        self.logger.info('------------------------------------------------')
        self.logger.info("Correction process summary")
        self.logger.info('------------------------------------------------')
        self.logger.info("   number of samples: {}".format(len(self.baseenv.getSamplesList())))
        if useformula:
            self.logger.info("   number of (metabolite, derivative): {}".format(len(labels)))
        else:
            self.logger.info("   number of (metabolite, derivative, resolution): {}".format(len(labels)))
        nb_errors = len(errors['labels']) + len(errors['measurements'])
        self.logger.info("   errors: {}".format(nb_errors))
        if nb_errors:
            self.logger.info("      {} errors during construction of (metabolite, derivative) correctors".format(
                len(errors['labels'])))
            self.logger.info("      {} errors during correction of measurements".format(len(errors['measurements'])))
            self.logger.info("      detailed information on errors are provided above.")

        # remove filehandler from the logger, and close the file
        self.logger.removeHandler(file_handler)
        file_handler.close()
        # log levels:
        # self.logger.debug('debug message')
        # self.logger.info('info message')
        # self.logger.warn('warn message')
        # self.logger.error('error message')
        # self.logger.critical('critical message')
        self.stop_process()

    def cleanLog(self):
        self.logstream.config(state="normal")
        self.logstream.delete(1.0, tk.END)
        self.logstream.config(state="disabled")

    def cleanData(self):
        self.datatext.config(state="normal")
        self.datatext.delete(1.0, tk.END)
        self.datatext.config(state="disabled")

    def cleanListTracer(self):
        self.cleanDfIsotopes = self.baseenv.dfIsotopes[(self.baseenv.dfIsotopes.abundance > 0) & (
                self.baseenv.dfIsotopes.abundance < 1.)]
        dfMaxAbundance = self.cleanDfIsotopes.groupby(
            "element", as_index=False)["abundance"].max()
        self.cleanDfIsotopes = self.cleanDfIsotopes[~(self.cleanDfIsotopes['abundance'].isin(
            dfMaxAbundance['abundance']) & self.cleanDfIsotopes['element'].isin(dfMaxAbundance['element']))]

    def loadData(self):
        "load data Callback"
        # Using try in case user types in unknown file or closes without choosing a file.
        try:
            name = filedialog.askopenfilename(initialdir="C:/Users/Batman/Documents/Programming/tkinter/",
                                              filetypes=(
                                                  ("Data File", "*.tsv"), ("All Files", "*.*")),
                                              title="Choose a file."
                                              )
            if name:
                self.cleanLog()
                self.cleanData()
                self.varInputPath.set(name)
                self.varOutputPath.set(Path(name).parent)
                with open(name, 'r', encoding='utf-8') as UseFile:
                    self.datatext.configure(state='normal')
                    self.datatext.insert(tk.INSERT, UseFile.read())
                    self.datatext.configure(state='disable')
        except:
            pass

    def outputDir(self):
        "gui output path"
        path = filedialog.askdirectory()
        if path:
            self.varOutputPath.set(path)

    def databaseDir(self):
        "gui database path"
        path = filedialog.askdirectory()
        if path:
            self.varDatabasePath.set(path)
            self.update_DBpath()

    def enableHR(self):
        if self.chVarHR.get():
            for child in self.highResFrame.winfo_children():
                child.configure(state='enable')
            self.formulaEntered.configure(state='readonly')
        else:
            for child in self.highResFrame.winfo_children():
                child.configure(state='disable')
        self.enableAtmz(None)

    def enableAtmz(self, event):
        if not self.chVarHR.get():
            self.mzEntry.configure(state='disable')
            self.mzlbl.configure(state='disable')
            self.masslbl.configure(state='disable')
            self.massEntry.configure(state='disable')
            self.formulalbl.configure(state='disable')
            self.formulaEntered.configure(state="disabled")
        elif self.formulaEntered.get() == 'constant':
            self.mzEntry.configure(state='disable')
            self.mzlbl.configure(state='disable')
            self.masslbl.configure(state='enable')
            self.massEntry.configure(state='enable')
            self.formulalbl.configure(state='enable')
            self.formulaEntered.configure(state="readonly")
        elif self.formulaEntered.get() == 'datafile':
            self.mzEntry.configure(state='disable')
            self.mzlbl.configure(state='disable')
            self.masslbl.configure(state='disable')
            self.massEntry.configure(state='disable')
            self.formulalbl.configure(state='enable')
            self.formulaEntered.configure(state="readonly")
        else:
            self.mzEntry.configure(state='enable')
            self.mzlbl.configure(state='enable')
            self.masslbl.configure(state='enable')
            self.massEntry.configure(state='enable')
            self.formulalbl.configure(state='enable')
            self.formulaEntered.configure(state="readonly")

    def updatePurity(self, event):
        tracer = self.baseenv.dfIsotopes[self.baseenv.dfIsotopes['subscriptName']
                                         == self.isotopictracerCBB.get()]
        dfSymbol = self.baseenv.dfIsotopes[self.baseenv.dfIsotopes['element']
                                           == tracer.iloc[0]['element']]
        self.purityManager.changeEntries(df=dfSymbol, tracer=tracer)

    def updateLogLevel(self):
        if self.chVarVerboseLog.get():
            self.log_level = "DEBUG"
        else:
            self.log_level = "INFO"
        self.logger.setLevel(self.log_level)

    def enablePurity(self):
        pass

    def update_DBpath(self):
        self.baseenv.db_path = Path(self.varDatabasePath.get())

    def createWidgets(self):
        content = ttk.Frame(self, padding=(3, 3, 12, 12))
        dataFrame = ttk.Frame(content, padding=(3, 3, 12, 12))
        optionFrame = ttk.Frame(content, padding=(3, 3, 12, 12))

        self.TracerOptFrame = ttk.LabelFrame(
            optionFrame, text='Tracer correction options')

        tr_lab = ttk.Label(text="Isotopic purity of the tracer (*)")
        purityLblFrame = ttk.LabelFrame(
            self.TracerOptFrame, labelwidget=tr_lab)
        self.scrollPurity = ttk.Scrollbar(purityLblFrame, orient='vertical')
        self.purityManager = PurityTracerManager(
            purityLblFrame, width=200, height=90, highlightthickness=0, yscrollcommand=self.scrollPurity.set)
        self.scrollPurity.config(command=self.purityManager.yview)
        purityLblFrame.update_idletasks()
        self.purityManager.config(scrollregion=self.purityManager.bbox("all"))

        tracer_list = list(self.cleanDfIsotopes['subscriptName'])
        self.isotopictracerEntered = tk.StringVar()
        self.isotopictracerlbl = ttk.Label(
            optionFrame, text="Isotopic tracer")
        self.isotopictracerCBB = ttk.Combobox(
            optionFrame, textvariable=self.isotopictracerEntered, values=tracer_list, state="readonly")
        self.isotopictracerCBB.bind("<<ComboboxSelected>>", self.updatePurity)
        # default value: 13C
        try:
            default_tracer = tracer_list.index(u"\u00B9\u00B3\u0043")
        except:
            default_tracer = 0
        self.isotopictracerCBB.current(default_tracer)
        self.updatePurity(None)

        self.chVarHR = tk.IntVar()
        self.R1 = tk.Radiobutton(optionFrame, text="Low resolution (*)", variable=self.chVarHR, value=False,
                                 command=self.enableHR)
        self.R2 = tk.Radiobutton(optionFrame, text="High resolution (*)", variable=self.chVarHR, value=True,
                                 command=self.enableHR)

        self.highResFrame = ttk.LabelFrame(
            optionFrame, text='High resolution parameters')
        self.formulalbl = ttk.Label(self.highResFrame, text="Resolution formula", )
        self.formulaEntered = ttk.Combobox(
            self.highResFrame, values=self.baseenv.formulas_code, state="readonly")
        self.formulaEntered.bind("<<ComboboxSelected>>", self.enableAtmz)
        self.formulaEntered.current(0)
        self.varMass = tk.StringVar()
        self.varMZ = tk.StringVar()
        self.varMass.set("60000")
        self.varMZ.set('400.0')
        self.masslbl = ttk.Label(self.highResFrame, text="instrument resolution")
        self.massEntry = ttk.Entry(
            self.highResFrame, textvariable=self.varMass)
        self.mzlbl = ttk.Label(self.highResFrame, text="at m/z")
        self.mzEntry = ttk.Entry(self.highResFrame, textvariable=self.varMZ)

        self.chVarVerboseLog = tk.IntVar()
        self.chVarNatAbTracer = tk.IntVar()
        self.chVarPurityTracer = tk.IntVar()
        self.chVerboseLog = ttk.Checkbutton(
            content, text="Verbose logs (*)", variable=self.chVarVerboseLog, command=self.updateLogLevel)
        self.processButon = ttk.Button(
            content, text=" Process ", command=self.start_process)
        self.chNatAbTracer = ttk.Checkbutton(
            self.TracerOptFrame, text="Correct natural abondance of the tracer element (*)",
            variable=self.chVarNatAbTracer)
        self.varInputPath = tk.StringVar()
        self.varOutputPath = tk.StringVar()
        self.varOutputPath.set(self.baseenv.home)
        self.varDatabasePath = tk.StringVar()
        self.varDatabasePath.set(self.baseenv.default_db)
        self.inputDataEntry = ttk.Entry(
            dataFrame, textvariable=self.varInputPath, state='readonly')
        self.loadbutton = ttk.Button(
            dataFrame, text=" Load Data ", command=self.loadData)
        self.outputDataEntry = ttk.Entry(
            dataFrame, textvariable=self.varOutputPath, state='readonly')
        self.outputPathSubmit = ttk.Button(
            dataFrame, text=" Output Data Path ", command=self.outputDir)
        self.databaseEntry = ttk.Entry(
            dataFrame, textvariable=self.varDatabasePath, state='readonly')
        self.databasePathSubmit = ttk.Button(
            dataFrame, text=" Databases Path (*)", command=self.databaseDir)
        scrolH = 10
        self.datatext = scrolledtext.ScrolledText(
            dataFrame, width=40, height=scrolH, wrap=tk.WORD)
        self.datatext.configure(state='disable')
        self.logstream = scrolledtext.ScrolledText(
            content, height=scrolH, wrap=tk.WORD, state="disabled")

        for child in self.highResFrame.winfo_children():
            child.configure(state='disable')

        content.grid(column=0, row=0, sticky='NSWE')
        dataFrame.grid(column=0, row=0, sticky='NSWE')
        optionFrame.grid(column=1, row=0, sticky='NSW')
        self.isotopictracerlbl.grid(column=0, row=0, sticky='NW')
        self.isotopictracerCBB.grid(column=0, row=1, sticky='NW')
        self.R1.grid(column=0, row=2, sticky='NW')
        self.R2.grid(column=0, row=2, sticky='NE')
        self.TracerOptFrame.grid(column=0, row=4, sticky='NWE', )
        self.highResFrame.grid(column=0, row=3, sticky='NWE', )
        self.formulalbl.grid(column=0, row=0, sticky='NW')
        self.formulaEntered.grid(column=0, row=1, sticky='NW')
        self.masslbl.grid(column=0, row=2, sticky='NW')
        self.massEntry.grid(column=0, row=3, sticky='NW')
        self.mzlbl.grid(column=1, row=2, sticky='NW')
        self.mzEntry.grid(column=1, row=3, sticky='NW')
        purityLblFrame.grid(column=0, row=5, sticky='NW')
        self.purityManager.grid(column=0, row=1, sticky='NW')
        self.scrollPurity.grid(column=1, row=1, sticky='NS')
        self.chNatAbTracer.grid(column=0, row=0, sticky='NW')
        self.inputDataEntry.grid(column=0, row=0, sticky='NWE')
        self.loadbutton.grid(column=0, row=1, sticky='NWE')
        self.outputDataEntry.grid(column=0, row=3, sticky='NWE')
        self.outputPathSubmit.grid(column=0, row=4, sticky='NWE')
        self.databaseEntry.grid(column=0, row=5, sticky='NWE')
        self.databasePathSubmit.grid(column=0, row=6, sticky='NWE')
        self.datatext.grid(column=0, row=2, sticky='NSWE')
        self.processButon.grid(column=0, row=1, columnspan=2, sticky='NWE')
        self.logstream.grid(column=0, row=2, columnspan=2, sticky='NWE')
        self.chVerboseLog.grid(column=0, row=3, sticky='NW')
        tk.Label(content, text="Note: infotip available over items with '(*)'").grid(column=1, row=3, sticky='NE')

        # create tooltip helpers
        Tooltip(self.chNatAbTracer,
                text="Correct for the contribution of naturally occurring isotopes of the tracer element at unlabeled positions. This only concerns the tracer element: natural abundance of other elements is always corrected.")
        Tooltip(self.R1, text="For measurements collected at unitary resolution (e.g. on quadrupole instruments).")
        Tooltip(self.R2,
                text="For measurements collected at high or ultrahigh resolution (e.g. on Orbitrap or FT-ICR instruments).")
        Tooltip(tr_lab,
                text="Correct for the contribution of isotopic impurities of the tracer at labeled positions. The isotopic purity is typically obtained from the manufacturer.\ne.g. for \u00B9\u00B3C-substates with purity of 99%, use 0.01 for \u00B9\u00B2C and 0.99 for \u00B9\u00B3C.")
        Tooltip(self.chVerboseLog, text="Useful in case of trouble. Join it to the issue on github.")
        Tooltip(self.databasePathSubmit, text="Folder containing all database files.")

        # create texthandler and formatter to display logs
        self.scroll_handler = TextHandler(self.logstream)
        formatter = logging.Formatter(
            '%(levelname)s - %(message)s')
        self.scroll_handler.setFormatter(formatter)

        # create logger (should be root to catch 'mscorrectors' logger)
        self.logger = logging.getLogger()
        self.updateLogLevel()

        # add the text handler to logger
        self.logger.addHandler(self.scroll_handler)


def openDoc():
    webbrowser.open_new(r"https://isocor.readthedocs.io/en/latest/")


def openGit():
    webbrowser.open_new(r"https://github.com/MetaSys-LISBP/IsoCor/")


def checkupdateto():
    """Compare local and distant IsoCor version."""
    try:
        # Get the distant __init__.py and read its version as it done in setup.py
        response = urllib.request.urlopen("https://github.com/MetaSys-LISBP/IsoCor/raw/master/isocor/__init__.py")
        data = response.read()
        txt = data.decode('utf-8').rstrip()
        lastversion = re.findall(r"^__version__ = ['\"]([^'\"]*)['\"]", txt, re.M)[0]
        if lastversion != hr.__version__:
            messagebox.showwarning('Version {} available'.format(lastversion),
                                   'You can update IsoCor with:\n"pip install --upgrade isocor"\nCheck the documentation for more information.')
    except:
        pass  # silently ignore everything that just happened


def start_gui():
    root = tk.Tk()
    root.resizable(width=False, height=False)
    # create menu
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    filemenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=filemenu)
    filemenu.add_command(label="Exit", command=root.quit)
    helpmenu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=helpmenu)
    helpmenu.add_command(label="IsoCor project", command=openGit)
    helpmenu.add_command(label="Documentation", command=openDoc)
    # start GUI
    app = GUIinterface(master=root)
    app.master.title("IsoCor {}".format(hr.__version__))
    # check version in a specific thread
    threadUpd = threading.Thread(target=checkupdateto)
    threadUpd.start()
    app.mainloop()
