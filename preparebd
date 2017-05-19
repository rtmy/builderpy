#!/usr/bin/env python3

import sys
import postgresql

if len(sys.argv) < 2:
        print("{} pq://<username>:<password>@<host>/<db_name>".format(sys.argv[0]))
        exit()

database = sys.argv[1]
db = postgresql.open(database)

db.execute("drop sequence logs_id_sequence")
db.execute("DROP TABLE if exists logs")
db.execute("DROP TABLE if exists repositories")
db.execute("create table repositories (id serial primary key, url text)")
db.execute("create sequence logs_id_sequence")
db.execute("create table logs (id integer primary key default nextval('logs_id_sequence'), repoid integer references repositories(id), datetime timestamp, log text)")
