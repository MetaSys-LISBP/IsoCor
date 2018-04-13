
## 2011-02-21 : P. Millard <millard@insa-toulouse.fr>

## COPYRIGHT 2011, INRA
## AUTHOR	Pierre MILLARD
## 	        Group MetaSys

"""
    IsoCor 1.0

    Copyright 2011, INRA
    Author : P. Millard, Group MetaSys

IsoCor corrects mass spectrometry data for all naturally
abundant isotopes occurring in the molecule to determine
its isotopologue distribution.

For further information refer to 'IsoCor_Tutorial.pdf'.
"""

#############################################################################
# ----------Import modules--------------------------------------------------#
#############################################################################

import wx, re, numpy
import wx.lib.rcsizer as rcs
from time import gmtime, strftime
from scipy import optimize

#############################################################################
# ---------Correction class-------------------------------------------------#
#############################################################################

class process:
    def __init__(self, data_iso, v_measured, meta_form, der_form, calc_mean_enr, el_excluded, el_pur, el_cor):

        # initialize variables
        self.err = ""
        self.data = data_iso # isotope proportions dictionnary
        self.meta_form = meta_form # elemental formula of metabolite
        self.der_form = der_form # elemental formula of derivative
        self.el_excluded = el_excluded # element of the metabolite moiety to exclude for correction
        self.el_cor = el_cor # isotopic tracer
        self.inc = len(data_iso[el_cor])-1
        self.mid, self.residuum = [], [float('inf')]

        # parse elemental formulas of metabolite and derivative
        el_dict_meta = self.parse_formula(meta_form)
        el_dict_der = self.parse_formula(der_form)
        self.nAtom_cor = el_dict_meta[el_cor]

        # calculate correction vector used for correction matrix construction
        # it corresponds to the mdv at natural abundance of all elements except the
        #    isotopic tracer (and the optionally excluded element of the metabolite's formula only)
        correction_vector = self.calc_mdv(el_dict_meta, el_dict_der)

        # check lenght of measured vector
        m_size = len(v_measured)
        c_size = len(correction_vector)
        if m_size < (self.nAtom_cor*self.inc) + 1:
            self.err = "The lenght of the measured isotopic cluster is too low.\nA minimum number of measurements equal to the higher possible mass shift\n(according to the isotopic tracer) is required."
        if m_size > c_size + self.nAtom_cor*self.inc:
            self.err = "Problem in matrix size.\nFragment does not contains enough atoms to generate this isotopic cluster."

        # check if the isotopic tracer is present in formula
        if el_cor not in meta_form:
            self.err = "The isotopic tracer must to be present in the metabolite."

        # if everything is ok
        if not self.err:
            if c_size < m_size:
                correction_vector += [0.]*(m_size-c_size)

            # create correction matrix
            self.correction_matrix = numpy.zeros((m_size, self.nAtom_cor+1))
            for i in range(self.nAtom_cor+1):
                column = correction_vector[:m_size]
                for na in range(i):
                    column = numpy.convolve(column, el_pur)[:m_size]
                if self.el_excluded != self.el_cor:
                    for nb in range(self.nAtom_cor-i):
                        column = numpy.convolve(column, self.data[el_cor])[:m_size]                    
                self.correction_matrix[:,i] = column

            # perform correction and calculate residuum
            mid_ini = numpy.zeros(self.nAtom_cor+1)
            self.v_mes = numpy.array(v_measured).transpose()
            mid, r, d = optimize.fmin_l_bfgs_b(self.cost_function, mid_ini, fprime=None, approx_grad=0,\
                                               args=(self.v_mes, self.correction_matrix), factr=1000, pgtol=1e-10,\
                                               bounds=[(0.,float('inf'))]*len(mid_ini))
            resi = self.v_mes - numpy.dot(self.correction_matrix, mid)

            # normalize mid and residuum
            sum_p = sum(mid)
            if sum_p != 0:
                self.mid = [p/sum_p for p in mid]
            sum_m = sum(v_measured)
            if sum_m != 0:
                self.residuum = [v/sum_m for v in resi]

            # calculate mean enrichment
            if calc_mean_enr:
                self.enr_calc = sum(p*i for i,p in enumerate(self.mid))/self.nAtom_cor

    def parse_formula(self, f):
        """
        Parse the elemental formula pand return the number
        of each element in a dictionnary d={'El_1':x,'El_2':y,...}.
        """
        s = "(" + "|".join(self.data.keys()) + ")([0-9]{0,})"
        d = dict((el,0) for el in self.data.keys())
        for el,n in re.findall(s,f):
            if n:
                d[el] += int(n)
            else:
                d[el] += 1
        return d

    def calc_mdv(self, el_dict_meta, el_dict_der):
        """
        Calculate a mass distribution vector (at natural abundancy),
        based on the elemental compositions of both metabolite's and
        derivative's moieties.
        The element corresponding to the isotopic tracer is not taken
        into account in the metabolite moiety.
        """
        result = [1.]
        for el,n in el_dict_meta.iteritems():
            if el not in [self.el_cor, self.el_excluded]:        
                for i in range(n):
                    result = numpy.convolve(result, self.data[el])
        for el,n in el_dict_der.iteritems():
            for i in range(n):
                result = numpy.convolve(result, self.data[el])
        return list(result)

    def cost_function(self, mid, v_mes, mat_cor):
        """
        Cost function used for BFGS minimization.
            return : (sum(v_mes - mat_cor * mid)^2, gradient)
        """
        x = v_mes - numpy.dot(mat_cor,mid)
        # calculate sum of square differences and gradient
        return (numpy.dot(x,x), numpy.dot(mat_cor.transpose(),x)*-2)


#############################################################################
# ---------Metabolite class-------------------------------------------------#
#############################################################################
            
class create_metabolite:
    def __init__(self, meta_name, der_name, p):
        self.meta_name = meta_name
        self.der_name = der_name
        self.v_mes = [p]

#############################################################################
# ---------Graphic class----------------------------------------------------#
#############################################################################

class gui:
    def __init__(self):
        """
        Display main frame.
        """
        self.input_file = ""
        # widget IDs
        id_menu_help = 100
        id_menu_quit = 101
        # create main frame
        app = wx.App()
        self.frame = wx.Frame(None, -1, title = 'IsoCor', size=(515,530))
        panel = wx.Panel(self.frame)
        sizer = rcs.RowColSizer()
        # load main window if isotopic data loaded
        if self.exist('Isotopes.dat'):
            self.isotop = self.load_iso('Isotopes.dat') # load isotopic proportions at natural abundance
            if self.isotop:
                # create widgets
                self.dict_form_meta, self.meta_list = self.load_db('Metabolites.dat') # load 'Metabolites.dat'
                self.dict_form_der, self.der_list = self.load_db('Derivatives.dat') # load 'Derivatives.dat'
                self.listbox_metabolites = wx.ListBox(panel, -1, (120, 220), (120, 250), self.meta_list, style=wx.LB_SINGLE)
                self.listbox_metabolites.Bind(wx.EVT_LISTBOX, self.select_meta)
                lab_el_cor = wx.StaticText(panel, -1, "Isotopic tracer: ")
                default = 'C' if 'C' in self.isotop else self.isotop.keys()[0]
                self.cb_el_cor = wx.ComboBox(panel, -1, pos=(50, 100), size=(40, -1), value = default,\
                                          choices=self.isotop.keys(), style=wx.CB_READONLY)
                self.cb_el_cor.Bind(wx.EVT_COMBOBOX, self.modif_el_cor)
                self.lab_form_meta = wx.StaticText(panel, -1, "Metabolite formula: ")
                self.entry_form_meta = wx.TextCtrl(panel, -1, size=(100,-1))
                self.entry_form_meta.Bind(wx.EVT_TEXT, self.modif_form_meta)
                lab_opt = wx.StaticText(panel, -1, "Include correction for:  ")
                lab_el_excluded = wx.StaticText(panel, -1, "- nat. ab. of the tracer:  ")
                self.cb_el_excluded = wx.ComboBox(panel, -1, pos=(50, 100), size=(50, -1), value = 'yes',\
                                          choices=["yes","no"], style=wx.CB_READONLY)
                lab_warning = wx.StaticText(panel, -1, "     (please refer to the tutorial for details)")
                lab_mean_enr = wx.StaticText(panel, -1, "Calc. mean enrichment:  ")
                self.cb_mean_enr = wx.ComboBox(panel, -1, pos=(50, 100), size=(50, -1), value = 'yes',\
                                          choices=["yes","no"], style=wx.CB_READONLY)
                lab_el_pur = wx.StaticText(panel, -1, "- purity of the tracer: ")
                self.entry_el_pur = wx.TextCtrl(panel, -1, size=(100,-1))
                self.entry_el_pur.ChangeValue('0;'*(len(self.isotop[self.cb_el_cor.GetValue()])-1) + '1.0')
                lab_form_der = wx.StaticText(panel, -1, "Derivative formula: ")
                self.cb_der = wx.ComboBox(panel, -1, pos=(50, 100), size=(70, -1), value = 'none',\
                                          choices=['none'] + self.der_list + ['custom...'], style=wx.CB_READONLY)
                self.cb_der.Bind(wx.EVT_COMBOBOX, self.select_der)
                self.entry_form_der = wx.TextCtrl(panel, -1, size=(100,-1))
                self.entry_form_der.Hide()
                self.entry_form_der.Bind(wx.EVT_TEXT, self.modif_form_der)        
                cmd_process = wx.Button(panel, -1, 'Process...')
                cmd_process.Bind(wx.EVT_BUTTON, self.cmd_correction)
                cmd_load_single = wx.Button(panel, -1, 'Load single meas.')
                cmd_load_single.Bind(wx.EVT_BUTTON, self.cmd_parse_single)
                cmd_load_multiple = wx.Button(panel, -1, 'Load mult. meas. ')
                cmd_load_multiple.Bind(wx.EVT_BUTTON, self.cmd_parse_multiple)
                self.liste = wx.ListBox(panel, -1, size=(105, 200))
                self.edit = wx.TextCtrl(panel, -1, style=wx.BORDER_NONE|wx.TE_MULTILINE|wx.TE_LINEWRAP|wx.TE_READONLY|wx.TE_PROCESS_ENTER|wx.HSCROLL)
                # add widgets to sizer
                sizer.Add(self.entry_form_der, pos=(4,4), size=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
                sizer.Add(lab_el_cor, pos=(1,3), size=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
                sizer.Add(self.cb_el_cor, pos=(1,4), size=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
                sizer.Add(self.lab_form_meta, pos=(2,3), size=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
                sizer.Add(self.entry_form_meta, pos=(2,4), size=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
                sizer.Add(self.cb_der, pos=(3,4), size=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
                sizer.Add(self.entry_el_pur, pos=(7,4), size=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
                sizer.Add(self.listbox_metabolites, pos=(1,1), size=(10,1))
                sizer.Add(lab_warning, pos=(8,3), size=(1,2), flag=wx.ALIGN_CENTER_VERTICAL)
                sizer.Add(lab_mean_enr, pos=(9,3), size=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
                sizer.Add(self.cb_mean_enr, pos=(9,4), size=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
                sizer.Add(lab_opt, pos=(5,3), size=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
                sizer.Add(lab_el_excluded, pos=(6,3), size=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
                sizer.Add(self.cb_el_excluded, pos=(6,4), size=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
                sizer.Add(lab_el_pur, pos=(7,3), size=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
                sizer.Add(cmd_process, pos=(10,3), size=(2,2), flag=wx.ALIGN_CENTER)
                sizer.Add(lab_form_der, pos=(3,3), size=(1,1), flag=wx.ALIGN_CENTER_VERTICAL)
                sizer.Add(cmd_load_single, pos=(1,6), size=(1,1))
                sizer.Add(cmd_load_multiple, pos=(2,6), size=(1,1))
                sizer.Add(self.liste, pos=(3,6), size=(10,1))
                sizer.Add(self.edit, pos=(12,0), size=(1,7), flag=wx.EXPAND)
                sizer.AddGrowableCol(6)
                sizer.AddGrowableRow(12)
                # add sizer
                panel.SetSizer(sizer)
                panel.SetAutoLayout(True)
                # create menu
                menuBar = wx.MenuBar()
                file_menu = wx.Menu()
                file_menu.Append(id_menu_quit, "Quit")
                help_menu = wx.Menu()
                help_menu.Append(id_menu_help, "About")
                menuBar.Append(file_menu, "File")
                menuBar.Append(help_menu, "Help")
                self.frame.SetMenuBar(menuBar)
                self.frame.Bind(wx.EVT_MENU, self.cmd_help, id=id_menu_help)
                self.frame.Bind(wx.EVT_MENU, self.cmd_quit, id=id_menu_quit)
                # display main frame
                self.frame.Centre()
                self.frame.Show(True)
                app.MainLoop()
                del app
            else:
                wx.MessageBox("'Isotopes.dat' is empty or has an incorrect structure.", "Error", style=wx.ICON_ERROR)
        else:
            wx.MessageBox("'Isotopes.dat' not found.", "Error", style=wx.ICON_ERROR)

    def exist(self, fname):
        """
        Check if the file exists (return boolean).
        """
        try:
            f = open(fname, 'r')
            f.close()
            return 1
        except:
            return 0

    def cmd_parse_single(self, event):
        """
        Load measured data.
        """
        dialog = wx.FileDialog(None, message='Load measured data',\
                               style=wx.FD_OPEN, wildcard='All files (*.*)|*.*|Text files (*.txt)|*.txt')
        if dialog.ShowModal() == wx.ID_OK:
            self.input_file = ""
            input_file = dialog.GetPath()
            dialog.Destroy()
            self.liste.Clear()
            warning = False
            txt = open(input_file, 'r')
            for i,l in enumerate(txt.readlines()):
                peak = l.strip("\n").replace(",", ".")
                if peak:
                    try:
                        if float(peak) >= 0.:
                            self.liste.Append(peak)
                        else:
                            if not warning:
                                wx.MessageBox("Some peaks of the isotopic cluster have negative intensities.", "Warning", style=wx.ICON_INFORMATION)
                                warning = True
                            self.liste.Append(peak)
                    except:
                        self.liste.Clear()
                        wx.MessageBox("Incorrect file structure (line "+ str(i+1) + ").", "Error", style=wx.ICON_ERROR)
                        break
            txt.close()

    def cmd_parse_multiple(self, event):
        """
        Load measured data.
        """
        # display filedialog to select input data file
        input_dialog = wx.FileDialog(None, message="Load an IsoCor data file", style=wx.FD_OPEN,\
                                     wildcard='All files (*.*)|*.*|Text files (*.txt)|*.txt')
        # for selected input file
        if input_dialog.ShowModal() == wx.ID_OK:
            self.liste.Clear()
            self.input_file = input_dialog.GetPath()
            input_dialog.Destroy()
            self.dict_meta, self.sample_list = {}, []
            txt = open(self.input_file, 'r')
            for i,l in enumerate(txt.readlines()):
                # parse input file
                try:
                    data = l.strip("\n").split("\t")
                    if data:
                        if data[0]:
                            sample = data[0]
                            self.dict_meta[sample] = self.dict_meta.get(sample, [])
                            if sample not in self.sample_list:
                                self.sample_list.append(sample)
                        if data[1]:
                            meta = create_metabolite(data[1].strip(' '), data[2].strip(' '), float(data[3].replace(",",".")))
                            self.dict_meta[sample].append(meta)
                        else:
                            self.dict_meta[sample][-1].v_mes.append(float(data[3].replace(",",".")))
                # if the structure of the input file is not correct
                except:
                    self.liste.Clear()
                    wx.MessageBox('Incorrect file structure (line ' + str(i+1) + ') :\n\n'+\
                                  'column 1 : sample name\n'+\
                                  'column 2 : metabolite name\n'+\
                                  'column 3 : derivative name\n'+\
                                  'column 4 : isotopic cluster', 'Error', style=wx.ICON_ERROR)
                    self.input_file = ""
                    break
            txt.close()

            if self.input_file:
                for k in self.sample_list:
                    self.liste.Append(k)
                    for m in self.dict_meta[k]:
                        self.liste.Append('   ' + m.meta_name)

    def cmd_correction(self, event):
        """
        Perform correction for all the metabolites of the input file.
        """
        el_cor = self.cb_el_cor.GetValue()
        el_excluded = el_cor if self.cb_el_excluded.GetValue() == "no" else ""
        calculate_enr = True if self.cb_mean_enr.GetValue() == "yes" else False
        error = 0
        self.edit.Clear()

        # check purity vector
        try:
            el_pur = [float(i) for i in self.entry_el_pur.GetValue().split(";")]
            if len(el_pur) != len(self.isotop[el_cor]):
                error = 1
                wx.MessageBox("The lenght of purity vector must be " + str(len(self.isotop[el_cor])) + " for '" + el_cor + "'.", "Error", style=wx.ICON_ERROR)
            else:
                if sum(el_pur) != 1.:
                    error = 1
                    wx.MessageBox("The sum of purity vector must be 1.", "Error", style=wx.ICON_ERROR)
        except:
            error = 1
            wx.MessageBox("Check purity vector.", "Error", style=wx.ICON_ERROR)
        
        # correction of a single measurement
        if not self.input_file and not error:
            form_meta = self.entry_form_meta.GetValue()
            if not form_meta:
                wx.MessageBox("No correction formula.", "Error", style=wx.ICON_ERROR)
            else:
                if self.liste.GetItems():
                    v_mes = [float(peak) for peak in self.liste.GetItems()]
                    form_der = self.entry_form_der.GetValue()
                    result = process(self.isotop, v_mes, form_meta, form_der, calculate_enr, el_excluded, el_pur, el_cor)
                    if result.err:
                        wx.MessageBox(result.err, "Error", style=wx.ICON_ERROR)
                    else:
                        if result.mid:
                            self.edit.AppendText('\nIsotopologue distribution of : ' + form_meta + '\n\n\tIndex\tProportion\tResiduum\n\n\t' +\
                                                 '\n\t'.join('m' + str(p) + "\t" + str(round(v,5)) + "\t" + str(result.residuum[p]) for p,v in enumerate(result.mid)))
                            if calculate_enr:
                                e = result.enr_calc if type(result.enr_calc) == str else str(round(result.enr_calc,4))
                                self.edit.AppendText("\n\n\tMean enrichment: " + e)
                else:
                    wx.MessageBox("Please load a data file.", "Error", style=wx.ICON_ERROR)

        # correction of samples/metabolites dataset
        elif self.input_file and not error:
            err_meta_list, err_der_list, err_num_list = [], [], []

            # create result file and write its header
            output_file = self.input_file[:-4] + "_res.txt"
            output = open(output_file, 'w')
            output.write("Sample\tMetabolite\tPeak index\tIsotopic cluster\tIsotopologue distribution\tResiduum")
            if calculate_enr:
                output.write("\tMean enrichment")
            output.write("\n")

            # perform correction for all the isotopic clusters
            for sample in self.sample_list:
                output.write(sample)
                for metabolite in self.dict_meta[sample]:
                    self.edit.AppendText(sample + " : " + metabolite.meta_name + '\n')

                    # if metabolite name/formula not in 'Metabolites.dat'
                    if metabolite.meta_name not in self.meta_list:
                        if metabolite.meta_name not in err_meta_list:
                            err_meta_list.append(metabolite.meta_name)
                        err_msg = "Error : metabolite '" + metabolite.meta_name + "' not found in 'Metabolites.dat'.\n"
                        self.edit.AppendText(err_msg)
                        output.write("\t" + metabolite.meta_name + "\t" + err_msg)
                    else:
                        der_form, error = '', 0
                        if metabolite.der_name:

                            # if derivative name/formula not in 'Derivatives.dat'
                            if metabolite.der_name not in self.der_list:
                                if metabolite.der_name not in err_der_list:
                                    err_der_list.append(metabolite.der_name)
                                err_msg = "Error : derivative '" + metabolite.der_name + "' not found in 'Derivatives.dat'.\n"
                                self.edit.AppendText(err_msg)
                                output.write("\t" + metabolite.meta_name + "\t" + err_msg)
                                error = 1
                            else:
                                der_form = self.dict_form_der[metabolite.der_name]
                        if not error:

                            # perform correction
                            result = process(self.isotop, metabolite.v_mes, self.dict_form_meta[metabolite.meta_name], der_form, calculate_enr, el_excluded, el_pur, el_cor)

                            # save results
                            if result.err:
                                output.write("\t" + metabolite.meta_name + "\tError : " + result.err.replace("\n"," ") + "\n")
                                self.edit.AppendText("Error : " + result.err + "\n")
                                if metabolite.der_name:
                                    m = (metabolite.meta_name, metabolite.der_name)
                                else:
                                    m = (metabolite.meta_name, 'none')
                                if m not in err_num_list:
                                    err_num_list.append(m)
                            else:
                                if sum(metabolite.v_mes):
                                    for i,m in enumerate(result.mid):
                                        if i == 0:
                                            output.write("\t" + metabolite.meta_name + "\t" + str(i) + "\t" +\
                                                         str(metabolite.v_mes[i]) + '\t' + str(round(m,5)) + '\t' + str(result.residuum[i]))
                                            if calculate_enr:
                                                e = result.enr_calc if type(result.enr_calc) == str else str(round(result.enr_calc,4))
                                                output.write("\t" + e + "\n")
                                            else:
                                                output.write("\n")
                                        else:
                                            output.write("\t\t" + str(i) + "\t" + str(metabolite.v_mes[i]) + '\t' +\
                                                         str(round(m,5)) + '\t' + str(result.residuum[i]) + "\n")
                                else:
                                    output.write("\t" + metabolite.meta_name + "\tNo data.\n")
                self.edit.AppendText("_"*30 + "\n\n")
            output.close()

            # create, display and write report
            report = "Isotopic tracer: " + str(el_cor) +\
                     "\nInclude correction for natural abundance of the tracer: " + str(self.cb_el_excluded.GetValue()) +\
                     "\nIsotopic purity of the tracer: " + str(el_pur) +\
                     "\n\nInput file: " + self.input_file.encode('utf-8') +\
                     "\nOutput file: " + output_file.encode('utf-8') +\
                     "\n\nCorrection for natural abundance done (" + str(len(self.dict_meta)) +\
                     " sample(s), " + str(len(err_der_list)+len(err_meta_list)+len(err_num_list)) + " error(s))."
            if len(err_meta_list):
                report += "\n\nEnter elemental formulas in 'Metabolites.dat' for:\n\t"+\
                          "\n\t".join(err_meta for err_meta in err_meta_list)
            if len(err_der_list):
                report += "\n\nEnter elemental formulas in 'Derivatives.dat' for:\n\t"+\
                          "\n\t".join(err_der for err_der in err_der_list)
            if len(err_num_list):
                report += "\n\nError in size of correction matrix. Check formulas of the 'Metabolite/Derivative':\n\t"+\
                          "\n\t".join(err_num[0] + ", " + err_num[1] for err_num in err_num_list)
            report += "\n\nProcessed by IsoCor.\n" + strftime("%d %b %Y %H:%M:%S", gmtime())
            self.edit.AppendText(report)
            rep_f = open(self.input_file[:-4] + "_log.txt", 'w')
            rep_f.write(report)
            rep_f.close()                    

    def cmd_help(self, event):
        """
        Display information about IsoCor.
        """
        wx.MessageBox(__doc__, "About", style=wx.ICON_INFORMATION)

    def cmd_quit(self, event):
        """
        Exit.
        """
        self.frame.Close()

    def load_iso(self, iso_f):
        """
        Load natural abundances of 'Isotopes.dat' (return dictionnary).
        """
        d = {}
        f = open(iso_f, 'r')
        try:
            for i in f.readlines():
                i = i.strip("\n").strip("\t")
                if i:
                    l = i.split("\t")
                    d[l[0]] = [float(v) for v in l[1:]]
            f.close()
        except:
            d = {}
        return d

    def load_db(self, db_file):
        """
        Parse the databases 'Metabolites.dat' and 'Derivatives.dat' and return a dictionnary and a list (required for order).
        """
        db_formulas, db_list = {}, []
        if self.exist(db_file):
            f = open(db_file, 'r')
            for line in f.readlines():
                line = line.strip("\n")
                if line:
                    l = line.split("\t")
                    db_formulas[l[0]] = l[1]
                    db_list.append(l[0])
            f.close()
        return db_formulas, db_list

    def select_meta(self, event):
        """
        Change the metabolite's formula according to the metabolite selected in the listbox.
        """
        self.entry_form_meta.ChangeValue(self.dict_form_meta[self.meta_list[event.GetSelection()]])

    def modif_form_meta(self, event):
        """
        Change the selection of the list of metabolites according to the formula entered by the user.
        """
        for index, metabolite in enumerate(self.meta_list):
            if self.entry_form_meta.GetValue() == self.dict_form_meta[metabolite]:
                self.listbox_metabolites.Select(index)
                break
            else:
                self.listbox_metabolites.Deselect(index)

    def modif_el_cor(self, event):
        """
        Change the purity vector according to the isotopic tracer.
        """
        self.entry_el_pur.ChangeValue('0;'*(len(self.isotop[self.cb_el_cor.GetValue()])-1) + '1.0')

    def select_der(self,event):
        """
        Change the derivative's formula according to the derivative selected by the user.
        """
        der_choice = self.cb_der.GetValue()
        if der_choice == 'none':
            self.entry_form_der.Hide()
            self.entry_form_der.ChangeValue('')
        elif der_choice == 'custom...':
            self.entry_form_der.Show()
            self.entry_form_der.ChangeValue('')
        else:
            self.entry_form_der.Show()
            self.entry_form_der.ChangeValue(self.dict_form_der[der_choice])
            
    def modif_form_der(self, event):
        """
        Change the derivative selected in the combobox according to the formula entered by the user.
        """
        self.cb_der.SetValue('custom...')
        form = self.entry_form_der.GetValue()
        for derivative in self.der_list:
            if form == self.dict_form_der[derivative]:
                self.cb_der.SetValue(derivative)
                break


gui()
