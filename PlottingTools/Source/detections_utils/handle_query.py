from sqlalchemy import select

from database import db
from database.schemas import diasource, sssource, mpcorb
from database.empty_response import empty_response


def handle_query(cols, conditions):
    stmt = select(*cols).join(sssource, sssource.c['diasourceid'] == diasource.c['diasourceid']).where(*conditions)

    df = db.query(
             stmt
    )
    
    return df