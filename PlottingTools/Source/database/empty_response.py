
def empty_response(**kwargs):
    query = f"""No results returned for your query:\n"""
    if 'filters' in kwargs:
        query += f"filters : {kwargs['filters']}\n"
    if 'start_time' in kwargs:
        query += f"start_time : {kwargs['start_time']}\n"
    if 'end_time' in kwargs:
        query += f"end_time : {kwargs['end_time']}\n"
    if 'min_e' in kwargs:
        query += f"min_e : {kwargs['min_e']}\n"
    if 'max_e' in kwargs:
        query += f"max_e : {kwargs['max_e']}\n"
    if 'min_a' in kwargs:
        query += f"min_a : {kwargs['min_a']}\n"
    if 'max_a' in kwargs:
        query += f"max_a : {kwargs['max_a']}\n"
    if 'min_incl' in kwargs:
        query += f"min_incl : {kwargs['min_incl']}\n"
    if 'max_incl' in kwargs:
        query += f"max_incl : {kwargs['max_incl']}\n"
    if 'min_peri' in kwargs:
        query += f"min_peri : {kwargs['min_peri']}\n"
    if 'max_peri' in kwargs:
        query += f"max_peri : {kwargs['max_peri']}\n"
        
    query = query[0:-1]
    print(query)
    return 