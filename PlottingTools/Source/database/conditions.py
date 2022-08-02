from .schemas import mpcorb
from .validators import validate_orbital_elements


def create_orbit_conditions(conditions : list = [], **orbital_elements):
    
    min_a, max_a, min_incl, max_incl, min_q, max_q, min_e, max_e = validate_orbital_elements(**orbital_elements)
        
    if min_q:
        conditions.append(mpcorb.c['q'] >= min_q)
        
    if max_q:
        conditions.append(mpcorb.c['q'] <= max_q)
        
    if min_incl:
        conditions.append(mpcorb.c['incl'] >= min_incl)
    
    if max_incl:
        conditions.append(mpcorb.c['incl'] <= max_incl)
        
    if min_a or max_a:
        if (min_e and min_e >= 1) or (max_e and max_e >= 1):
            raise Exception(f"You cannot define a body using the following orbital elements: {orbital_elements}.\n Eccentricty cannot be greater or equal to one for a given semi-major axis")
            
        if (min_e and min_e <= 0) or (max_e and max_e <= 0):
            raise Exception(f"You cannot define a body using the following orbital elements: {orbital_elements}.\n Eccentricty cannot be greater than 0 and less than one to one for a given semi-major axis.")
    
    if min_e:
        conditions.append(mpcorb.c['e'] >= min_e)
    if max_e:
        conditions.append(mpcorb.c['e'] <= max_e)

    if min_a:
        conditions.append((mpcorb.c['q'] / (1 - mpcorb.c['e']) ) >= min_a)
    
    if max_a:
        conditions.append((mpcorb.c['q'] / (1 - mpcorb.c['e']) ) <= max_a)
        
    return conditions