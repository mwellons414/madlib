\i ~/workspace/tinc/tincdb/schema/tincdb_functions.sql
\i ~/workspace/tinc/tincdb/schema/tincdb_schema.sql

insert into test_host_type values ('MAC_OS_X');

insert into release_line values ('MADLIB_v0.7');

INSERT INTO suite values
    (DEFAULT, 'MAC_OS_X', NULL, NULL, 'EXAMPLE_REGRESSION', 'EXAMPLE_REGRESSION_SUITE', 
    'regression', now(), now(), NULL, 
    (SELECT ex_id 
    FROM executor 
    WHERE ex_name ILIKE 'tincdb.aggregators.functional.FunctionalTestSuiteAggregator'));

    
INSERT INTO suite_collection_map VALUES
    ((SELECT ste_id FROM suite 
    WHERE ste_name = 'EXAMPLE_REGRESSION'), 
    (SELECT col_id FROM collection 
    WHERE col_name ILIKE '%examples.sql_input'), 
    (SELECT ex_id FROM executor 
    WHERE ex_name ILIKE 'madlib_testsuite.examples.linregr_test.LinregrInputTestCase'));


INSERT INTO schedule VALUES 
    (DEFAULT, 'SCHEDULE_EXAMPLES', 'MADLIB_v0.7');

    
INSERT INTO schedule_suite_map VALUES 
    ((SELECT sc_id FROM schedule 
    WHERE sc_name = 'SCHEDULE_EXAMPLES'), 
    (SELECT ste_id FROM Suite WHERE ste_name = 'EXAMPLE_REGRESSION'), 
    'ALWAYS');

insert into environment values (1, 'MAC_OS_X', 'Darwin', 64, 1, 1, 1, 'laptop');
