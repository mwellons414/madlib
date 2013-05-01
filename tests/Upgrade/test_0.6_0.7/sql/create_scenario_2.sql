DROP VIEW IF EXISTS view_dep_multi_rec;
DROP VIEW IF EXISTS view_dep_svec_agg_rec;
DROP VIEW IF EXISTS view_dep_array_agg_rec;
DROP VIEW IF EXISTS view_dep_svec_agg;
DROP VIEW IF EXISTS view_dep_array_agg;

CREATE VIEW view_dep_array_agg AS 
    SELECT 'view_dep_array_agg'::text AS name, upgrade_madlib.array_agg(i) AS arr FROM generate_series(1, 10) i;
CREATE VIEW view_dep_svec_agg AS 
    SELECT 'view_dep_svec_agg'::text AS name, upgrade_madlib.svec_agg(i) AS svec FROM generate_series(1, 10) i;
CREATE VIEW view_dep_array_agg_rec AS 
    SELECT 'view_dep_array_agg'::text AS name, arr FROM view_dep_array_agg;
CREATE VIEW view_dep_svec_agg_rec AS
    SELECT 'view_dep_svec_agg_rec'::text AS name, svec FROM view_dep_svec_agg;
CREATE VIEW view_dep_multi_rec AS 
    SELECT 'view_dep_multi_rec'::text AS name, arr, svec FROM view_dep_array_agg_rec, view_dep_svec_agg_rec;
