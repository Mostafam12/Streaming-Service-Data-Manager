PRAGMA foreign_keys = ON;

create table if not exists moviePeople
(
    pid       char(4),
    name      text,
    birthYear int,
    primary key (pid)
);
create table if not exists movies
(
    mid     int,
    title   text,
    year    int,
    runtime int,
    primary key (mid)
);
create table if not exists casts
(
    mid  int,
    pid  char(4),
    role text,
    primary key (mid, pid),
    foreign key (mid) references movies,
    foreign key (pid) references moviePeople
);
create table if not exists recommendations
(
    watched     int,
    recommended int,
    score       float,
    primary key (watched, recommended),
    foreign key (watched) references movies,
    foreign key (recommended) references movies
);
create table if not exists customers
(
    cid  char(4),
    name text,
    pwd  text,
    primary key (cid)
);
create table if not exists sessions
(
    sid      int,
    cid      char(4),
    sdate    date,
    duration int,
    primary key (sid, cid),
    foreign key (cid) references customers
        on delete cascade
);
create table if not exists watch
(
    sid      int,
    cid      char(4),
    mid      int,
    duration int,
    primary key (sid, cid, mid),
    foreign key (sid, cid) references sessions,
    foreign key (mid) references movies
);
create table if not exists follows
(
    cid char(4),
    pid char(4),
    primary key (cid, pid),
    foreign key (cid) references customers,
    foreign key (pid) references moviePeople
);
create table if not exists editors
(
    eid char(4),
    pwd text,
    primary key (eid)
);
