-- Generating datasets for performance tests
DROP TABLE IF EXISTS madlibtestdata.matrix_block_10k_10k_1k; 
CREATE TABLE madlibtestdata.matrix_block_10k_10k_1k 
WITH (APPENDONLY=true, COMPRESSTYPE=quicklz) AS
SELECT 
    generate_series(0, 9) AS row_id, 
    col_id,
    madlib.__rand_block(1000) AS block 
FROM generate_series(0, 9) AS col_id
DISTRIBUTED BY (row_id);

DROP TABLE IF EXISTS madlibtestdata.matrix_block_10k_10k_100; 
CREATE TABLE madlibtestdata.matrix_block_10k_10k_100 
WITH (APPENDONLY=true, COMPRESSTYPE=quicklz) AS
SELECT 
    generate_series(0, 99) AS row_id, 
    col_id,
    madlib.__rand_block(100) AS block 
FROM generate_series(0, 99) AS col_id
DISTRIBUTED BY (row_id);

DROP TABLE IF EXISTS madlibtestdata.matrix_block_300k_100_1000; 
CREATE TABLE madlibtestdata.matrix_block_300k_100_1000 
WITH (APPENDONLY=true, COMPRESSTYPE=quicklz) AS
SELECT 
    generate_series(0, 299) AS row_id, 
    col_id,
    madlib.__rand_block(1000, 100) AS block 
FROM generate_series(0, 0) AS col_id
DISTRIBUTED BY (row_id);

DROP TABLE IF EXISTS madlibtestdata.matrix_block_300k_100_2000; 
CREATE TABLE madlibtestdata.matrix_block_300k_100_2000 
WITH (APPENDONLY=true, COMPRESSTYPE=quicklz) AS
SELECT 
    generate_series(0, 149) AS row_id, 
    col_id,
    madlib.__rand_block(2000, 100) AS block 
FROM generate_series(0, 0) AS col_id
DISTRIBUTED BY (row_id);

DROP TABLE IF EXISTS madlibtestdata.matrix_block_300k_100_4000; 
CREATE TABLE madlibtestdata.matrix_block_300k_100_4000 
WITH (APPENDONLY=true, COMPRESSTYPE=quicklz) AS
SELECT 
    generate_series(0, 74) AS row_id, 
    col_id,
    madlib.__rand_block(4000, 100) AS block 
FROM generate_series(0, 0) AS col_id
DISTRIBUTED BY (row_id);

-- Generating datasets for input tests 
DROP TABLE IF EXISTS  madlibtestdata.matrix_array_100_100;
CREATE TABLE madlibtestdata.matrix_array_100_100
WITH (APPENDONLY=true, COMPRESSTYPE=quicklz) AS
SELECT 
    row_id, madlib.__rand_vector(100) AS row_vec 
FROM generate_series(0, 99) AS row_id 
DISTRIBUTED BY (row_id);

DROP TABLE IF EXISTS madlibtestdata.matrix_block_100_100; 
CREATE TABLE madlibtestdata.matrix_block_100_100 
WITH (APPENDONLY=true, COMPRESSTYPE=quicklz) AS
SELECT 
    generate_series(0, 9) AS row_id, 
    col_id,
    madlib.__rand_block(10) AS block 
FROM generate_series(0, 9) AS col_id
DISTRIBUTED BY (row_id);

DROP TABLE IF EXISTS madlibtestdata.matrix_sparse_100_100; 
CREATE TABLE madlibtestdata.matrix_sparse_100_100 (row_id INT4, col_id INT4,
value INT4) DISTRIBUTED BY (row_id);
INSERT INTO madlibtestdata.matrix_sparse_100_100 VALUES(0, 0, 1);
INSERT INTO madlibtestdata.matrix_sparse_100_100 VALUES(10, 10, 2);
INSERT INTO madlibtestdata.matrix_sparse_100_100 VALUES(20, 20, 3);
INSERT INTO madlibtestdata.matrix_sparse_100_100 VALUES(30, 30, 4);
INSERT INTO madlibtestdata.matrix_sparse_100_100 VALUES(40, 40, 5);
INSERT INTO madlibtestdata.matrix_sparse_100_100 VALUES(50, 50, 6);
INSERT INTO madlibtestdata.matrix_sparse_100_100 VALUES(60, 60, 7);
INSERT INTO madlibtestdata.matrix_sparse_100_100 VALUES(70, 70, 8);
INSERT INTO madlibtestdata.matrix_sparse_100_100 VALUES(80, 80, 9);
INSERT INTO madlibtestdata.matrix_sparse_100_100 VALUES(90, 90, 10);
INSERT INTO madlibtestdata.matrix_sparse_100_100 VALUES(99, 0, 9900);
INSERT INTO madlibtestdata.matrix_sparse_100_100 VALUES(99, 99, 9999);
INSERT INTO madlibtestdata.matrix_sparse_100_100 VALUES(0, 99, 99);
INSERT INTO madlibtestdata.matrix_sparse_100_100 VALUES(100, 100, NULL);
