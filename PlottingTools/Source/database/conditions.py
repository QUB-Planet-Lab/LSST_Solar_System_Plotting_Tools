from .schemas import mpcorb
from .validators import validate_orbital_elements


def create_orbit_conditions(conditions : list = [], **orbital_elements):
    
    min_a, max_a, min_incl, max_incl, min_peri, max_peri, min_e, max_e = validate_orbital_elements(**orbital_elements)

    if min_peri:
        conditions.append(mpcorb.c['q'] >= min_peri)
    if max_peri:
        conditions.append(mpcorb.c['q'] <= max_peri)
        
    if min_incl:
        conditions.append(mpcorb.c['incl'] >= min_incl)
    
    if max_incl:
        conditions.append(mpcorb.c['incl'] <= max_incl)
        
    if min_a or max_a:
        if min_e >= 1 or max_e >= 1:
            raise Exception(f"You cannot define a body using the following orbital elements: {orbital_elements}.\n Eccentricty cannot be greater or equal to one for a given semi-major axis")
        conditions.append(mpcorb.c['e'] > 0 )
        conditions.append(mpcorb.c['e'] < 1)
    
    elif not min_a and not max_a:
        if min_e:
            conditions.append(mpcorb.c['e'] >= min_e )
        if max_e:
            conditions.append(mpcorb.c['e'] <= min_e )
                
    if min_a:
        conditions.append((mpcorb.c['q'] / (1 - mpcorb.c['e']) ) >= min_a)
    
    if max_a:
        conditions.append((mpcorb.c['q'] / (1 - mpcorb.c['e']) ) <= max_a)
    return conditions