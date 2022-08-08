from .schemas import mpcorb, sssource
from .validators import validate_orbital_elements


def create_orbit_conditions(conditions : list = [], helio = False, **orbital_elements):
    
    min_a, max_a, min_incl, max_incl, min_q, max_q, min_e, max_e, min_hd, max_hd = validate_orbital_elements(**orbital_elements)
        
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
    elif not min_e and (min_a or max_a):
        conditions.append(mpcorb.c['e'] > 0)
        
    if max_e:
        conditions.append(mpcorb.c['e'] <= max_e)
        
    elif not max_e and (min_a or max_a):
        conditions.append(mpcorb.c['e'] < 1)

    if min_a:
        conditions.append((mpcorb.c['q'] / (1 - mpcorb.c['e']) ) >= min_a)
    
    if max_a:
        conditions.append((mpcorb.c['q'] / (1 - mpcorb.c['e']) ) <= max_a)
    
    if min_hd and helio:
        conditions.append(sssource.c['heliocentricdist'] >= min_hd)
    
    if max_hd and helio:
        conditions.append(sssource.c['heliocentricdist'] <= max_hd)
            
    return conditions