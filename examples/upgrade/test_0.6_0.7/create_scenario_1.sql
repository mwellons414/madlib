DROP TABLE IF EXISTS table_dep_svec;

CREATE TABLE table_dep_svec(id int, value upgrade_madlib.svec);
INSERT INTO table_dep_svec VALUES(1, '{1,2,3}'::float8[]::upgrade_madlib.svec);
INSERT INTO table_dep_svec VALUES(2, '{4,5,6}'::float8[]::upgrade_madlib.svec);
INSERT INTO table_dep_svec VALUES(3, '{7,8,9}'::float8[]::upgrade_madlib.svec);
