from astropy.time import Time
from typing import Literal
import warnings

def format_times(times : list, _format : Literal["ISO", "MJD"] = "MJD"):
    
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        
        _format = _format.upper()
        if _format == "ISO":
            try:
                return Time([str(time) for time in times], format="mjd").to_value('isot')

            except:
                try:
                    return Time(times, format="isot").to_value('isot')
                except:
                    raise Exception("Invalid times used in input. Times must be input as MJD format")

        elif _format == "MJD":
            try:
                return Time(times, format='isot').to_value('mjd')
            except:
                try:
                    return Time(times, format='mjd').to_value('mjd')
                except:
                    raise Exception("Invalid times used in input. Times must either be in ISO or MJD format")

        else:
            raise Exception("format_time: The argument _format must be either ISO or MJD")