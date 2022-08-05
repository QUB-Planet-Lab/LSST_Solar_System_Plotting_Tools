
def empty_response(**kwargs):
    query = f"""No results returned for your query:\n"""
    
    for kwarg in kwargs:
        query += f"{kwarg} : {kwargs[kwarg]}\n"
    
    query = query[0:-1]
    
    print(query)
    return 