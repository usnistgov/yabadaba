
# Standard Python libraries
import ast
from typing import Optional, Union

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# http://www.numpy.org/
import numpy as np
import numpy.typing as npt

# yabadaba imports
from ..typing import unitfloat

class UnitConverter():

    # Import derived units defined in separate files
    from ._length import (cm, mm, um, nm, pm, fm, km,
                          angstrom, Å,
                          lightyear, astro_unit,
                          pc, kpc, Mpc, Gpc,
                          inch, foot, mile, thou)
    from ._volume import (L, mL, uL, nL, pL, fL, aL, kL, ML, GL)
    from ._time import (ms, us, ns, ps, fs,
                        minute, hour, day, week, year)
    from ._frequency import (Hz, mHz, kHz, MHz, GHz, THz, PHz, rtHz, rpm,
                             Hz·2π, mHz·2π, kHz·2π, MHz·2π, GHz·2π, THz·2π, PHz·2π, rpm·2π)
    from ._mass import (g, mg, ug, ng, pg, fg,
                        tonne, amu, Da, kDa, lbm)
    from ._energy import (J, mJ, uJ, nJ, pJ, fJ, kJ, MJ, GJ, erg,
                          eV, meV, keV, MeV, GeV, TeV,
                          btu, smallcal, kcal, Wh, kWh)
    from ._concentration import (mol, mmol, umol, nmol, pmol, fmol,
                                 M, mM, uM, nM, pM, fM)
    from ._force import (N, mN, uN, nN, pN, fN, kN, MN, GN, dyn, lbf)
    from ._pressure import (Pa, hPa, kPa, MPa, GPa, bar,
                            mbar, cbar, dbar, kbar, Mbar,
                            atm, torr, mtorr, psi)
    from ._power import (W, mW, uW, nW, pW, kW, MW, GW, TW,
                         horsepower_imperial, horsepower_metric)
    from ._acceleration import (Gal, mGal, uGal, eotvos)
    from ._temperature import (degFinterval, degCinterval, mK, uK, nK, pK)
    from ._charge import (mC, uC, nC, Ah, mAh)
    from ._current import (A, mA, uA, nA, pA, fA)
    from ._voltage import (V, mV, uV, nV, kV, MV, GV, TV)
    from ._resistance import (ohm, Ω, mohm, mΩ, kohm, kΩ, Mohm, MΩ, Gohm, GΩ,
                              S, mS, uS, nS)
    from ._magnetic import (T, mT, uT, nT, G, mG, uG, kG, Oe, Wb)
    from ._capacitance import (F, uF, nF, pF, fF, aF, H, mH, uH, nH)
    from ._constants import (NA, pi, π, c0, mu0, μ0, eps0, ε0, Z0,
                             hPlanck, hbar, ħ, kB, GNewton, sigmaSB, σSB, alphaFS, αFS,
                             Rgas, e, uBohr, uNuc, aBohr, me, mp, mn,
                             Rinf, Ry, Hartree, ARichardson, Phi0, KJos, RKlitz, debye,
                             REarth, g0, Msolar, MEarth)

    def __init__(self):
        """Initialize a unit manager and set core units"""
        
        # Init core Si units
        self.__m = 1.
        self.__kg = 1.
        self.__s = 1.
        self.__C = 1.
        self.__K = 1.

        # Init unit and unitdoc dicts
        self.__unit = {}
        self.__unitdoc = {}
        self.build_unit()

    @property
    def m(self) -> float:
        """meter"""
        return self.__m

    @property
    def kg(self) -> float:
        """kilogram"""
        return self.__kg

    @property
    def s(self) -> float:
        """second"""
        return self.__s
    
    @property
    def C(self) -> float:
        """coulomb"""
        return self.__C
    
    @property
    def K(self) -> float:
        """kelvin"""
        return self.__K

    @property
    def display_core_values(self) -> str:
        """str: the current values of the core units"""
        return '\n'.join([
            f'm  = {self.m:.15}',
            f'kg = {self.kg:.15}',
            f's  = {self.s:.15}',
            f'C  = {self.C:.15}',
            f'K  = {self.K:.15}',
        ])

    def reset_units(self, 
                    seed: Union[int, str, None] = None,
                    **kwargs):
        """
        Resets the core units from which all others are derived.  Based on the
        given inputs, three behaviors can occur:

        1. If no kwargs are given and seed is int or None, then the core units
           will be set to random values using the seed value.
        
        2. If no kwargs are given and seed is set as 'SI', then the working
           units will be set to SI units.
        
        3. If kwargs are given, then the working units will be set/derived
           based on which are given and SI units if needed.  At most 4 kwargs
           of length, mass, time, energy, and charge can be given.  And seed
           must be left as None.
        
        Parameters
        ----------
        seed : int, str or None, optional
            random number seed to use in generating random working units.
            seed='SI' will use SI units.  Must be None (default) if any other
            parameters are given.
        length : str, optional
            Unit of length to use for the working units.
        mass : str, optional
            Unit of mass to use for the working units.
        time : str, optional
            Unit of time to use for the working units.
        energy : str, optional
            Unit of energy to use for the working units.
        charge : str, optional
            Unit of charge to use for the working units.
            
        Raises
        ------
        ValueError
            If seed is given with any other parameters, or if more than four of
            the working unit parameters are given.
        """
        
        # Set known units
        if isinstance(seed, str):
            
            if len(kwargs) > 0:
                raise ValueError('seed cannot be given with any other parameters')
            
            if seed == 'SI':
                self.__m = 1.
                self.__kg = 1.
                self.__s = 1.
                self.__C = 1.
                self.__K = 1.

            else:
                raise ValueError(f'str seed value {seed} not supported')

        # Set random units
        elif len(kwargs) == 0:
            
            import random

            prior_random_state = random.getstate()

            if seed is None:
                random.seed()
            else:
                random.seed(seed)

            self.__m = 10 ** random.uniform(-2,2)
            self.__kg = 10 ** random.uniform(-2,2)
            self.__s = 10 ** random.uniform(-2,2)
            self.__C = 10 ** random.uniform(-2,2)
            self.__K = 10 ** random.uniform(-2,2)

            # Leave the random generator like I found it, in case something else is
            # using it.
            random.setstate(prior_random_state)

        elif seed is None:
            
            # Check that no more than 4 working units are defined
            if len(kwargs) > 4:
                raise ValueError('Only four working units can be defined')
            
            # Set base units to 1 (working units to SI)
            self.reset_units('SI')
            
            # Scale base units by working units
            if 'length' in kwargs:
                self.__m = self.m / self.unit[kwargs['length']]
            
            if 'mass' in kwargs:
                self.__kg = self.kg / self.unit[kwargs['mass']]
            
            if 'time' in kwargs:
                self.__s = self.s / self.unit[kwargs['time']]
            
            if 'charge' in kwargs:
                self.__C = self.C / self.unit[kwargs['charge']]
            
            # Scale derived units by working units
            if 'energy' in kwargs:
                J = self.unit['J'] / self.unit[kwargs['energy']]
                
                # Scale base units by derived units
                if 'mass' not in kwargs:
                    self.__kg = J * self.s**2 / self.m**2
                elif 'time' not in kwargs:
                    self.__s = (self.kg * self.m**2 / J)**0.5
                elif 'length' not in kwargs:
                    self.__m = (J * self.s**2 / self.kg)
            
        else:
            raise ValueError('seed cannot be given with any other parameters')
        
        # Build unit and unitdoc dicts
        self.build_unit()
        
    @property
    def unit(self) -> dict:
        """dict: All available unit names and set values"""
        return self.__unit
    
    @property
    def unitdoc(self) -> dict:
        """dict: All available unit names and their descriptions"""
        return self.__unitdoc

    def build_unit(self):
        """
        Saves numericalunits attributes to global dictionary unit so the values
        can be retrieved by their string names.
        """
        
        # Copy all float attributes of numericalunits to unit
        for key in dir(self):
            
            value = getattr(self, key)
            
            if key[:1] != '_' and isinstance(value, float):
                self.unit[key] = value
                self.unitdoc[key] = getattr(UnitConverter, key).__doc__

    def set_literal(self, term: str) -> np.ndarray:
        """
        Convert string 'value unit' to numbers in working units.
        
        Parameters
        ----------
        term : str
            String containing value and associated unit. If unit is not given,
            then the value is converted to a float and assumed to be in working
            units.
            
        Returns
        -------
        float or numpy.ndarray
            The numerical value of term in working units.
            
        Raises
        ------
        ValueError
            If no valid float value can be parsed.
        """
        
        # Set splitting point j to end of term (i.e. assume no units given)
        j = len(term)
        
        # Loop until done
        while True:
            
            # Split term into value, unit terms
            value = term[:j].strip()
            unit = term[j:].strip()
            if len(unit) == 0:
                unit = None

            # Return number if value, unit pair is valid
            try: 
                return self.set_in_units(ast.literal_eval(value), unit)
            except: 
                # Find the next splitting point
                try:
                    j = term[:j].rindex(' ')
                except ValueError as err:
                    raise ValueError('Failed to parse term') from err

    def set_in_units(self, 
                     value: unitfloat,
                     units: Optional[str] = None) -> np.ndarray:
        """
        Convert value from specified units to working units.
        
        Parameters
        ----------
        value : str, float or array-like object
            A numerical value or list/array of values.  String values will be
            interpreted using set_literal() and may therefore optionally contain
            units information.  If a string value contains units information, do
            not give it separately to the units parameter!
        units : str or None
            The units that the value is in.  The default value of None will either
            do no conversion or use units defined in a string value.
            
        Returns
        -------
        float or numpy.ndarray
            The given value converted from the specified units to working units.
        """
        if isinstance(value, str):
            
            try:
                # If conversion works on full str, then no units are present
                value = ast.literal_eval(value)
            except:
                # Otherwise, interpret with set_literal()
                value = self.set_literal(value)
                if units is not None:
                    raise ValueError('units given twice: in value str and separately!')
        
        # Parse units and convert
        scale = self.parse(units)
        return np.asarray(value) * scale

    def get_in_units(self, 
                     value: Union[float, npt.ArrayLike],
                     units: Optional[str] = None) -> np.ndarray:
        """
        Convert value from working units to specified units.
        
        Parameters
        ----------
        value : float or array-like object
            A numerical value or list/array of values.
        units : str or None
            The units to convert value to (from working units).  A value
            of None will do no conversion.
            
        Returns
        -------
        float or numpy.ndarray
            The given value converted to the specified units from working units.
        """
        scale = self.parse(units)
        return np.asarray(value) / scale

    def value_unit(self, term: dict) -> np.ndarray:
        """
        Reads numerical value from dictionary containing 'value' and 'unit' keys.
        
        Parameters
        ----------
        term : dict
            Dictionary containing 'value' and 'unit' keys.
            
        Returns
        -------
        float or numpy.ndarray
            The result of calling set_in_units() by passing the dictionary keys 
            'value' and 'unit' as parameters.
        
        """
        unit = term.get('unit', None)
        if unit is None:
            value = np.asarray(term['value'])
        else:
            value = self.set_in_units(term['value'], unit)
        
        if 'shape' in term:
            shape = tuple(term['shape'])
            value = value.reshape(shape)
        
        return value
        
    def error_unit(self, term: dict) -> np.ndarray:
        """
        Reads numerical error from dictionary containing 'error' and 'unit' keys.
        
        Parameters
        ----------
        term : dict
            Dictionary containing 'error' and 'unit' keys.
            
        Returns
        -------
        float or numpy.ndarray
            The result of calling set_in_units() by passing the dictionary keys 
            'error' and 'unit' as parameters.
        
        """
        unit = term.get('unit', None)
        if unit is None:
            error = np.asarray(term['error'])
        else:
            error = self.set_in_units(term['error'], unit)
        
        if 'shape' in term:
            shape = tuple(term['shape'])
            error = error.reshape(shape)
        
        return error
        
    def model(self,
              value: Union[float, npt.ArrayLike],
              units: Optional[str] = None,
              error: Optional[Union[float, npt.ArrayLike]] = None) -> DM:
        """
        Generates DataModelDict representation of data.
        
        Parameters
        ----------
        value : array-like object
            A numerical value or list/array of values.
        units : str, optional
            The units to convert value to (from working units).
        error : array-like object or None, optional
            A value error to include.  If given, must be the same
            size/shape as value.
        
        Returns
        -------
        DataModelDict
            Model representation of the value(s).
        """
        
        datamodel = DM()
        
        if units is not None:
            value = self.get_in_units(value, units)
        else:
            value = np.asarray(value)
        
        if error is not None:
            error = self.get_in_units(error, units)
        
        # Single value
        if value.ndim == 0:
            datamodel['value'] = value
            if error is not None:
                datamodel['error'] = error
        
        # 1D array
        elif value.ndim == 1:
            datamodel['value'] = value.tolist()
            if error is not None:
                datamodel['error'] = error.tolist()
                
        # Higher-order array requires shape
        else:
            shape = value.shape
            datamodel['value'] = value.flatten().tolist()
            if error is not None:
                datamodel['error'] = error.flatten().tolist()
            datamodel['shape'] = list(shape)
        
        if units is not None:
            datamodel['unit'] = units
        
        return datamodel

    def parse(self, units: Optional[str]) -> float:
        """
        Convert units as strings (or None) into scaling numbers.  This function
        allows for complex unit definitions with operators:
        
        - '()' for defining order of operations
        - '*' for multiplication.
        - '/' for division.
        - '^' for powers.
        
        Parameters
        ----------
        units : str or None
            String consisting of defined unit names, operators, and numerical 
            values to interpret.  If units is None or == 'scaled', then the returned
            value will be 1.0, i.e. no unit conversion.
            
        Returns
        -------
        float
            The scaling factor for converting numbers in the given units to
            working units.
        """
        
        # Units of None does no scaling
        if units is None or units == 'scaled':
            return 1

        # Parse string and return number value
        elif isinstance(units, str):
            i = 0
            terms = []
            
            # Break into terms
            while i < len(units):
                
                # parse terms in parentheses first
                if units[i] == '(':
                    j = i + 1
                    pcount = 0
                    while True:
                        if j == len(units):
                            raise ValueError('Invalid () terms.')
                        elif units[j] == ')':
                            if pcount == 0:
                                break
                            else:
                                pcount -= 1
                        elif units[j] == '(':
                            pcount += 1
                        j += 1
                        
                    terms.append(self.parse(units[i+1: j]))
                    i = j + 1
                
                # append string terms
                elif units[i].isalpha():
                    term = ''
                    while i < len(units) and units[i] not in ' */^\n\r\t':
                        term += units[i]
                        i += 1
                    terms.append(self.unit[term])
                
                # append numeric terms
                elif units[i].isdigit() or units[i] == '-' or units[i] == '.':
                    term = ''
                    while i < len(units) and units[i] not in ' */^\n\r\t':
                        term += units[i]
                        i += 1
                    terms.append(float(term))
                
                # append operators
                elif units[i] in '*/^':
                    terms.append(units[i])
                    i += 1
                
                # ignore excess white characters
                elif units[i] in ' \n\r\t':
                    i += 1
                
                # issue error for unmatched ) parentheses
                elif units[i] == ')':
                    raise ValueError('Invalid () terms.')
                
                else:
                    raise ValueError('Unknown character: %s' % units[i])
            
            # Compute powers
            while '^' in terms:
                c = terms.index('^')
                value = [terms[c-1] ** terms[c+1]]
                terms = terms[:c-1] + value + terms[c+2:]
            
            # Compute multiplication and division
            while len(terms) > 1:
                if terms[1] == '*':
                    value = [terms[0] * terms[2]]
                    terms = value + terms[3:]
                elif terms[1] == '/':
                    value = [terms[0] / terms[2]]
                    terms = value + terms[3:]
                else:
                    raise ValueError('Invalid string format')
            
            return terms[0]

        # Else assume units is already a number
        else:
            return units
        
unitconvert = UnitConverter()