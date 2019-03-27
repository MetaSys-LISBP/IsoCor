import pandas as pd
from pathlib import Path
from os.path import expanduser
import isocor as hr
from decimal import Decimal
from distutils.dir_util import copy_tree
import shutil
import numpy as np
import pkg_resources


class EnvComputing(object):
    """Share methods for interfaces"""

    def __init__(self, home=expanduser('~')):
        self.formulas_code = list(hr.HighResMetaboliteCorrector.RES_FORMULAS)
        self.formulas_code = self._putfirst(self.formulas_code, 'orbitrap')
        # initialize paths
        self.home = Path(home)
        self.default_db = Path(self.home, 'isocordb')
        self.db_path = self.default_db
        self.example_db = pkg_resources.resource_filename('isocor', 'data/')

    def initializeDB(self):
        # if db files don't exist, copy the example folder
        if self.default_db.is_dir():
            for i in ["Isotopes.dat", "Metabolites.dat", "Derivatives.dat"]:
                if not Path(self.default_db, i).is_file():
                    shutil.copy(Path(self.example_db, i), self.default_db)
        else:
            copy_tree(str(self.example_db), str(self.default_db))

    def initializeEnv(self):
        self.home = self.home

    def _putfirst(self, mylist, myelement):
        """return mylist with myelement as first position if is in"""
        if myelement in mylist:
            mylist.pop(mylist.index(myelement))
            mylist.insert(0, myelement)
        return mylist

    def _makeIsotopesDict(self, df):
        gb = df.groupby('element')
        d = {}
        for g in gb.groups:
            dg = gb.get_group(g).sort_values(by='mass').to_dict('list')
            e = dg.pop('element')[0]
            d[e] = dg
        return d

    def _stripColNames(self, df):
        df.rename(columns=lambda x: x.strip())

    def _stripCol(self, df, listcolumns):
        for col in listcolumns:
            df[col] = df[col].str.strip()

    def registerIsopotes(self, isotopesfile=Path("Isotopes.dat")):
        if not isotopesfile.is_file():
            raise ValueError(
                "Isotopes database not found in:\n'{}'.".format(isotopesfile))
        with open(str(isotopesfile), 'r') as fp:  # str for compatibility with Python3.5
            self.dfIsotopes = pd.read_csv(fp)
        for i in ['element', 'mass', 'abundance']:
            if i not in self.dfIsotopes.columns:
                raise ValueError("Column '{}' not found in 'Isotopes.dat'.".format(i))
        # check data types to return an explicit error
        if self.dfIsotopes.empty:
            raise ValueError("'Isotopes.dat' is empty.")
        for i, item in enumerate(self.dfIsotopes['mass']):
            try:
                Decimal(item)
            except:
                raise ValueError("Error in 'Isotopes.dat' at line {}:\nmass={!r}".format(i+2, item))
        for i, item in enumerate(self.dfIsotopes['abundance']):
            try:
                np.float64(item)
            except:
                raise ValueError("Error in 'Isotopes.dat' at line {}:\nabundance={!r}".format(i+2, item))
        # reload file
        with open(str(isotopesfile), 'r') as fp:
            self.dfIsotopes = pd.read_csv(
                 fp, converters={'mass': Decimal, 'abundance': np.float64})
        self._stripColNames(self.dfIsotopes)
        self._stripCol(self.dfIsotopes, ['element', ])
        self.dictIsotopes = self._makeIsotopesDict(self.dfIsotopes)
        self.dfIsotopes['isotope'] = self.dfIsotopes.mass.apply(round)
        self.dfIsotopes['name'] = self.dfIsotopes['isotope'].map(
            str) + self.dfIsotopes['element']

    def registerDerivativesDB(self, derivativesfile=Path("Derivatives.dat")):
        if not derivativesfile.is_file():
            raise ValueError(
                "Derivatives database not found in:\n'{}'.".format(derivativesfile))
        with open(str(derivativesfile), 'r') as fp:
            self.dfDerivatives = pd.read_csv(fp, delimiter='\t')
        for i in ['name', 'formula']:
            if i not in self.dfDerivatives.columns:
                raise ValueError("Column '{}' not found in 'Derivatives.dat'.".format(i))
        self._stripColNames(self.dfDerivatives)
        self._stripCol(self.dfDerivatives, ['name', 'formula'])

    def registerMetabolitesDB(self, metabolitesfile=Path("Metabolites.dat")):
        if not metabolitesfile.is_file():
            raise ValueError(
                "Metabolites database not found in:\n'{}'.".format(metabolitesfile))
        with open(str(metabolitesfile), 'r') as fp:
            self.dfMetabolites = pd.read_csv(fp, delimiter='\t', converters={'charge': str})
        for i in ['name', 'formula', 'charge']:
            if i not in self.dfMetabolites.columns:
                raise ValueError("Column '{}' not found in 'Metabolites.dat'.".format(i))
        self._stripColNames(self.dfMetabolites)
        self._stripCol(self.dfMetabolites, ['name', 'formula', 'charge'])

    def registerDatafile(self, datafile=Path("mydata.tsv"), useformula=True):
        if not Path(datafile).is_file():
            raise ValueError("No data file selected.")
        with open(str(datafile), 'r') as fp:
            self.dfDatafile = pd.read_csv(fp, delimiter='\t', keep_default_na=False)
        tocheck = ['sample', 'metabolite', 'derivative', 'area', 'isotopologue']
        if not useformula:
            tocheck.append('resolution')
        for i in tocheck:
            if i not in self.dfDatafile.columns:
                raise ValueError("Column '{}' not found in the data file.".format(i))
        # check data types to return an explicit error
        for i, item in enumerate(self.dfDatafile['area']):
            try:
                np.float64(item)
            except:
                raise ValueError("Error in data file at line {}:\narea={!r}".format(i+2, item))
        for i, item in enumerate(self.dfDatafile['isotopologue']):
            try:
                int(item)
            except:
                raise ValueError("Error in data file at line {}:\nisotopologue={!r}".format(i+2, item))
        self.dfDatafile[['sample']] = self.dfDatafile[['sample']].astype(str)
        self.dfDatafile[['metabolite']] = self.dfDatafile[['metabolite']].astype(str)
        self.dfDatafile[['derivative']] = self.dfDatafile[['derivative']].astype(str)
        self.dfDatafile[['area']] = self.dfDatafile[['area']].astype(np.float64)
        self.dfDatafile[['isotopologue']] = self.dfDatafile[['isotopologue']].astype(int)
        if not useformula:
            for i, item in enumerate(self.dfDatafile['resolution']):
                try:
                    int(item)
                except:
                    raise ValueError("Error in data file at line {}:\nresolution={!r}".format(i+2, item))
            self.dfDatafile[['resolution']] = self.dfDatafile[['resolution']].astype(str)

        self.dfDatafile['derivative'].fillna('', inplace=True)
        if self.dfDatafile.empty:
            raise ValueError("Data file is empty.")
        self._stripColNames(self.dfDatafile)

        if useformula:
            self._stripCol(self.dfDatafile, ['sample', 'derivative', 'metabolite'])
            self._groupbyDatafile = self.dfDatafile.groupby(
                by=['metabolite', 'derivative', 'sample'])
        else:
            self._stripCol(self.dfDatafile, ['sample', 'metabolite', 'derivative', 'resolution'])
            self._groupbyDatafile = self.dfDatafile.groupby(
                by=['metabolite', 'derivative', 'resolution', 'sample'])

    def getLabelsList(self, useformula):
        if useformula:
            return [tuple(i) for i in self.dfDatafile[['metabolite', 'derivative']].drop_duplicates().values]
        else:
            return [tuple(i) for i in self.dfDatafile[['metabolite', 'derivative', 'resolution']].drop_duplicates().values]

    def getSamplesList(self):
        return [tuple(i) for i in self.dfDatafile[['sample']].drop_duplicates().values]

    def getMetaboliteFormula(self, name):
        try:
            return self.dfMetabolites[self.dfMetabolites['name'] == name]['formula'].values[0]
        except:
            raise ValueError(
                "No formula provided in 'Metabolites.dat' for metabolite '{}'.".format(name))

    def getMetaboliteCharge(self, name):
        try:
            return int(self.dfMetabolites[self.dfMetabolites['name'] == name]['charge'].values[0])
        except:
            raise ValueError(
                "No charge provided in 'Metabolites.dat' for metabolite '{}'.".format(name))

    def getDerivativeFormula(self, name):
        try:
            # derivative may be an empty str, otherwise should be in derivative database
            if name == '':
                return None
            else:
                return self.dfDerivatives[self.dfDerivatives['name'] == name]['formula'].values[0]
        except:
            raise ValueError(
                "No formula provided in 'Derivatives.dat' for derivative '{}'.".format(name))

    def returnLabelStr(self, tupleNames):
        if tupleNames[1]:
            return '-'.join(tupleNames)
        else:
            return tupleNames[0]

    def getDataSerie(self, tupleNames, useformula):
        l, l_err = [], []
        if useformula:
            length = 2
        else:
            length = 3
        for i, j in self._groupbyDatafile:
            if i[:length] == tupleNames:
                try:
                    p = j.sort_values(by=['isotopologue'])
                    l.append([i[length], list(p.area.values)])
                except:
                    l_err.append(i[length])
        return l, l_err
