import cx_Oracle
from importers import settings
from importers.repository import taxonomy
from datetime import datetime
from dateutil import parser
import sys

if not settings.ORACLE_USER or not settings.ORACLE_PASSWORD \
        or not settings.ORACLE_HOST or not settings.ORACLE_SERVICE:
    print("Missing some or all of ORACLE environment environment settings\
 (ORACLE_USER, ORACLE_PASSWORD, ORACLE_HOST, ORACLE_SERVICE).")
    sys.exit(1)

dsn = cx_Oracle.makedsn(settings.ORACLE_HOST, settings.ORACLE_PORT,
                        service_name=settings.ORACLE_SERVICE)

o_con = cx_Oracle.connect(user=settings.ORACLE_USER,
                          password=settings.ORACLE_PASSWORD,
                          dsn=dsn)


def load_kandidater_from_madb(last_ids, since):
    cur = o_con.cursor()
    dtime = _timestamp_to_datetime(since)
    if cur.execute("""
                   SELECT ID, TIMESTAMP, ANVANDARID, NAMN, STATUS
                   FROM MATCHNINGSPROFIL
                   WHERE STATUS = :status AND TIMESTAMP >= :timestamp
                   ORDER BY TIMESTAMP ASC FETCH NEXT 2000 ROWS ONLY""",
                   timestamp=dtime, status='PUBLICERAD'):
        mp_rows = cur.fetchall()
        mpids = [mp[0] for mp in mp_rows]
        kriterium = _load_profilkriterium(mpids)
        profiler = [dict({"id": mp[0],
                          "timestamp": _datetime_to_timestamp(mp[1]),
                          "anvandarid": mp[2],
                          "namn": mp[3],
                          "status": mp[4]}, **kriterium.get(mp[0], {}))
                    for mp in mp_rows if mp[0] not in last_ids]
        return (mpids,
                profiler[-1]['timestamp'] if profiler else 0,
                profiler)
    else:
        print("facepalm")
    cur.close()
    o_con.close()


def _load_profilkriterium(mpids):
    if not mpids:
        return []
    cur = o_con.cursor()
    sql = "SELECT p.MATCHNINGSPROFIL_ID, p.ID, p.TYP, p.VARDE, p.VIKT, k.ID, k.TYP, k.VARDE \
           FROM PROFILKRITERIUM p LEFT JOIN KRITERIUMEGENSKAP k \
           ON p.ID = k.PROFILKRITERIUM_ID \
           WHERE %s ORDER BY p.ID" % " OR ".join(["MATCHNINGSPROFIL_ID = %d" %
                                                 mpid for mpid in mpids])
    cur.execute(sql)
    kriterium_rows = cur.fetchall()
    kriterium = dict()
    for mpid in mpids:
        kriterium[mpid] = _convert_to_dict(
            [k for k in kriterium_rows if k[0] == mpid]
        )

    return kriterium


def _convert_to_dict(ktuples):
    kriterier = {'krav': {}, 'erfarenhet': {}}
    for ktuple in ktuples:
        kritkey = ktuple[2].lower()
        kritcategory = _kriterium_category(kritkey)
        kritkey = 'yrkesroll' if kritkey == 'yrke' else kritkey
        kritnode = {"kod": ktuple[3], "term": taxonomy.get_term(kritkey, ktuple[3]),
                    "vikt": ktuple[4]}
        if ktuple[7]:
            kritnode['niva'] = ktuple[7]
        if kritkey in kriterier[kritcategory]:
            kriterier[kritcategory][kritkey].append(kritnode)
        else:
            kriterier[kritcategory][kritkey] = [kritnode]
    return kriterier


def _kriterium_category(kriterium):
    return 'krav' if kriterium in ['yrkesroll', 'kommun', 'lan', 'land',
                                   'anstallningstyp',
                                   'arbetsomfattning'] else 'erfarenhet'


def _datetime_to_timestamp(utc_time):
    if isinstance(utc_time, int):
        return utc_time
    epoch_time = (utc_time - datetime(1970, 1, 1)).total_seconds() * 1000
    return int(epoch_time)


def _timestamp_to_datetime(timestamp):
    if isinstance(timestamp, datetime):
        return timestamp
    if isinstance(timestamp, str):
        return parser.parse(timestamp)
    return datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')
