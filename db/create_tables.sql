create table resources (
id integer primary key autoincrement not null,
name text not null,
url text not null,
logo blob,
type text not null check(name='webviewer' and name='tracker'),
unique (name, url)
);

create table users (
id integer primary key autoincrement not null,
tg_id integer not null unique,
admin integer not null check(admin=1 and admin=0) default 0
);

create table subscriptions (
id integer primary key autoincrement not null,
user_id integer not null,
title_id integer not null,
FOREIGN KEY(user_id) REFERENCES users(id)
);

create table titles (
id integer primary key autoincrement not null,
res_id integer not null,
url text not null unique,
name_rus text,
name_lat text,
name_glyph text,
release_year integer,
poster blob,
ep_now integer,
ep_total integer,
last_check_date integer,
FOREIGN KEY(res_id) REFERENCES resources(id)
);

create table shikimori (
user_id integer not null,
auth_code text,
access_token text,
refresh_token text,
FOREIGN KEY(user_id) REFERENCES users(id)
);