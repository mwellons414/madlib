-- toy datasets for corner case testing
DROP TABLE IF EXISTS madlibtestdata.lda_toy_vocab;
CREATE TABLE madlibtestdata.lda_toy_vocab(wordid INT4, word TEXT);
INSERT INTO madlibtestdata.lda_toy_vocab VALUES
(0, 'code'), (1, 'data'), (2, 'graph'), (3, 'image'), (4, 'input'), (5,
'layer'), (6, 'learner'), (7, 'loss'), (8, 'model'), (9, 'network'), (10,
'neuron'), (11, 'object'), (12, 'output'), (13, 'rate'), (14, 'set'), (15,
'signal'), (16, 'sparse'), (17, 'spatial'), (18, 'system'), (19, 'training');

DROP TABLE IF EXISTS madlibtestdata.lda_toy_corpus;
CREATE TABLE madlibtestdata.lda_toy_corpus(docid INT4, wordid INT4, count
INT4);
INSERT INTO madlibtestdata.lda_toy_corpus VALUES
(0, 0, 2),(0, 3, 2),(0, 5, 1),(0, 7, 1),(0, 8, 1),(0, 9, 1),(0, 11, 1),(0, 13,
1), (1, 0, 1),(1, 3, 1),(1, 4, 1),(1, 5, 1),(1, 6, 1),(1, 7, 1),(1, 10, 1),(1,
14, 1),(1, 17, 1),(1, 18, 1), (2, 4, 2),(2, 5, 1),(2, 6, 2),(2, 12, 1),(2, 13,
1),(2, 15, 1),(2, 18, 2), (3, 0, 1),(3, 1, 2),(3, 12, 3),(3, 16, 1),(3, 17,
2),(3, 19, 1), (4, 1, 1),(4, 2, 1),(4, 3, 1),(4, 5, 1),(4, 6, 1),(4, 10, 1),(4,
11, 1),(4, 14, 1),(4, 18, 1),(4, 19, 1), (5, 0, 1),(5, 2, 1),(5, 5, 1),(5, 7,
1),(5, 10, 1),(5, 12, 1),(5, 16, 1),(5, 18, 1),(5, 19, 2), (6, 1, 1),(6, 3,
1),(6, 12, 2),(6, 13, 1),(6, 14, 2),(6, 15, 1),(6, 16, 1),(6, 17, 1), (7, 0,
1),(7, 2, 1),(7, 4, 1),(7, 5, 1),(7, 7, 2),(7, 8, 1),(7, 11, 1),(7, 14, 1),(7,
16, 1), (8, 2, 1),(8, 4, 4),(8, 6, 2),(8, 11, 1),(8, 15, 1),(8, 18, 1),
(9, 0, 1),(9, 1, 1),(9, 4, 1),(9, 9, 2),(9, 12, 2),(9, 15, 1),(9, 18, 1),(9,
19, 1);

DROP TABLE IF EXISTS madlibtestdata.lda_invalid_count_coprus;
CREATE TABLE madlibtestdata.lda_invalid_count_coprus(docid INT4, wordid INT4,
count INT4);
INSERT INTO madlibtestdata.lda_invalid_count_coprus VALUES
(0, 0, 2),(0, 3, 2),(0, 5, -1),(0, 7, 1),(0, 8, 1),(0, 9, 1),(0, 11, 1),(0, 13,
1), (1, 0, 1),(1, 3, 1),(1, 4, 1),(1, 5, 0),(1, 6, 1),(1, 7, 1),(1, 10, 1),(1,
14, 1),(1, 17, 1),(1, 18, 1), (2, 4, 2),(2, 5, 1),(2, 6, 2),(2, 12, 1),(2, 13,
1),(2, 15, 1),(2, 18, 2), (3, 0, 1),(3, 1, -2),(3, 12, 3),(3, 16, 1),(3, 17,
2),(3, 19, 1), (4, 1, 1),(4, 2, 1),(4, 3, 1),(4, 5, 1),(4, 6, 1),(4, 10, 1),(4,
11, 1),(4, 14, 1),(4, 18, 1),(4, 19, 1), (5, 0, 1),(5, 2, 1),(5, 5, 1),(5, 7,
1),(5, 10, 1),(5, 12, 1),(5, 16, 1),(5, 18, 1),(5, 19, 2), (6, 1, 1),(6, 3,
1),(6, 12, 2),(6, 13, 1),(6, 14, 2),(6, 15, 1),(6, 16, 1),(6, 17, 1), (7, 0,
1),(7, 2, 1),(7, 4, 1),(7, 5, 1),(7, 7, 2),(7, 8, 1),(7, 11, 1),(7, 14, 1),(7,
16, 1), (8, 2, 1),(8, 4, 4),(8, 6, 2),(8, 11, 1),(8, 15, 1),(8, 18, 1),
(9, 0, 1),(9, 1, 1),(9, 4, 1),(9, 9, 2),(9, 12, 2),(9, 15, 1),(9, 18, 1),(9,
19, 1);

DROP TABLE IF EXISTS madlibtestdata.lda_invalid_wordid_coprus;
CREATE TABLE madlibtestdata.lda_invalid_wordid_coprus(docid INT4, wordid INT4,
count INT4);
INSERT INTO madlibtestdata.lda_invalid_wordid_coprus VALUES
(0, 0, 2),(0, 3, 2),(0, 5, 1),(0, 7, 1),(0, 8, 1),(0, 9, 1),(0, 11, 1),(0, 13,
1), (1, -1, 1),(1, 3, 1),(1, 4, 1),(1, 5, 1),(1, 6, 1),(1, 7, 1),(1, 10, 1),(1,
14, 1),(1, 17, 1),(1, 18, 1), (2, 4, 2),(2, -5, 1),(2, 6, 2),(2, 12, 1),(2, 13,
1),(2, 15, 1),(2, 18, 2), (3, 100, 1),(3, 1, 2),(3, 12, 3),(3, 16, 1),(3, 17,
2),(3, 19, 1), (4, 1, 1),(4, 2, 1),(4, 3, 1),(4, 5, 1),(4, 6, 1),(4, 10, 1),(4,
11, 1),(4, 14, 1),(4, 18, 1),(4, 19, 1), (5, 0, 1),(5, 2, 1),(5, 5, 1),(5, 7,
1),(5, 10, 1),(5, 12, 1),(5, 16, 1),(5, 18, 1),(5, 19, 2), (6, 1, 1),(6, 3,
1),(6, 12, 2),(6, 13, 1),(6, 14, 2),(6, 15, 1),(6, 16, 1),(6, 17, 1), (7, 0,
1),(7, 2, 1),(7, 4, 1),(7, 5, 1),(7, 7, 2),(7, 8, 1),(7, 11, 1),(7, 14, 1),(7,
16, 1), (8, 2, 1),(8, 4, 4),(8, 6, 2),(8, 11, 1),(8, 15, 1),(8, 18, 1),
(9, 0, 1),(9, 1, 1),(9, 4, 1),(9, 9, 2),(9, 12, 2),(9, 15, 1),(9, 18, 1),(9,
19, 1);

DROP TABLE IF EXISTS madlibtestdata.lda_negative_docid_coprus;
CREATE TABLE madlibtestdata.lda_negative_docid_coprus(docid INT4, wordid INT4, count
INT4);
INSERT INTO madlibtestdata.lda_negative_docid_coprus VALUES
(-1, 0, 2),(-1, 3, 2),(-1, 5, 1),(-1, 7, 1),(-1, 8, 1),(-1, 9, 1),(-1, 11,
1),(-1, 13, 1), (1, 0, 1),(1, 3, 1),(1, 4, 1),(1, 5, 1),(1, 6, 1),(1, 7, 1),(1,
10, 1),(1, 14, 1),(1, 17, 1),(1, 18, 1), (2, 4, 2),(2, 5, 1),(2, 6, 2),(2, 12,
1),(2, 13, 1),(2, 15, 1),(2, 18, 2), (3, 0, 1),(3, 1, 2),(3, 12, 3),(3, 16,
1),(3, 17, 2),(3, 19, 1), (4, 1, 1),(4, 2, 1),(4, 3, 1),(4, 5, 1),(4, 6, 1),(4,
10, 1),(4, 11, 1),(4, 14, 1),(4, 18, 1),(4, 19, 1), (5, 0, 1),(5, 2, 1),(5, 5,
1),(5, 7, 1),(5, 10, 1),(5, 12, 1),(5, 16, 1),(5, 18, 1),(5, 19, 2), (6, 1,
1),(6, 3, 1),(6, 12, 2),(6, 13, 1),(6, 14, 2),(6, 15, 1),(6, 16, 1),(6, 17, 1),
(7, 0, 1),(7, 2, 1),(7, 4, 1),(7, 5, 1),(7, 7, 2),(7, 8, 1),(7, 11, 1),(7, 14,
1),(7, 16, 1), (8, 2, 1),(8, 4, 4),(8, 6, 2),(8, 11, 1),(8, 15, 1),(8, 18, 1),
(9, 0, 1),(9, 1, 1),(9, 4, 1),(9, 9, 2),(9, 12, 2),(9, 15, 1),(9, 18, 1),(9,
19, 1);

DROP TABLE IF EXISTS madlibtestdata.lda_null_coprus;
CREATE TABLE madlibtestdata.lda_null_coprus(docid INT4, wordid INT4, count
INT4);
INSERT INTO madlibtestdata.lda_null_coprus VALUES
(0, 0, 2),(0, 3, 2),(0, 5, NULL),(NULL, 7, 1),(0, NULL, 1),(0, 9, 1),(0, 11, 1),(0, 13,
1), (1, 0, 1),(1, 3, 1),(1, 4, 1),(1, 5, 1),(1, 6, 1),(1, 7, 1),(1, 10, 1),(1,
14, 1),(1, 17, 1),(1, 18, 1), (2, 4, 2),(2, 5, 1),(2, 6, 2),(2, 12, 1),(2, 13,
1),(2, 15, 1),(2, 18, 2), (3, 0, 1),(3, 1, 2),(3, 12, 3),(3, 16, 1),(3, 17,
2),(3, 19, 1), (4, 1, 1),(4, 2, 1),(4, 3, 1),(4, 5, 1),(4, 6, 1),(4, 10, 1),(4,
11, 1),(4, 14, 1),(4, 18, 1),(4, 19, 1), (5, 0, 1),(5, 2, 1),(5, 5, 1),(5, 7,
1),(5, 10, 1),(5, 12, 1),(5, 16, 1),(5, 18, 1),(5, 19, 2), (6, 1, 1),(6, 3,
1),(6, 12, 2),(6, 13, 1),(6, 14, 2),(6, 15, 1),(6, 16, 1),(6, 17, 1), (7, 0,
1),(7, 2, 1),(7, 4, 1),(7, 5, 1),(7, 7, 2),(7, 8, 1),(7, 11, 1),(7, 14, 1),(7,
16, 1), (8, 2, 1),(8, 4, 4),(8, 6, 2),(8, 11, 1),(8, 15, 1),(8, 18, 1),
(9, 0, 1),(9, 1, 1),(9, 4, 1),(9, 9, 2),(9, 12, 2),(9, 15, 1),(9, 18, 1),(9,
19, 1);

DROP TABLE IF EXISTS madlibtestdata.lda_empty_coprus;
CREATE TABLE madlibtestdata.lda_empty_coprus(docid INT4, wordid INT4, count
INT4);

-- change owner of datasets from gpamdin to madlibtester
ALTER TABLE madlibtestdata.lda_toy_vocab OWNER TO madlibtester;
ALTER TABLE madlibtestdata.lda_toy_corpus OWNER TO madlibtester;
ALTER TABLE madlibtestdata.lda_invalid_count_coprus OWNER TO madlibtester;
ALTER TABLE madlibtestdata.lda_invalid_wordid_coprus OWNER TO madlibtester;
ALTER TABLE madlibtestdata.lda_negative_docid_coprus OWNER TO madlibtester;
ALTER TABLE madlibtestdata.lda_null_coprus OWNER TO madlibtester;
ALTER TABLE madlibtestdata.lda_empty_coprus OWNER TO madlibtester;


------------------------------------------------------------------------
------------------------------------------------------------------------
------------------------------------------------------------------------

/*
    LDA output Test

    Compare the perplexity of the result with R using same data sets
*/

create or replace function madlibtestdata.compare_perplexity (
    datatable         text,
    tbl_R           text,
    vocab_size      integer,
    topic_no        integer,
    iter           integer,
    alpha           double precision,
    beta            double precision
) returns double precision as $$
declare
    tbl_model       text := '__lda_perp_model__';
    tbl_output      text := '__lda_perp_outdata__';
    perplexity      double precision;
    perplexity_r    double precision;
    diff            double precision;
    tmp_str1         text;
    tmp_str2         text;
begin
    execute '
        select madlib.lda_train (
            ''madlibtestdata.'|| datatable ||''',
            '''|| tbl_model ||''',
            '''|| tbl_output ||''',
            '|| vocab_size ||',
            '|| topic_no ||',
            '|| iter ||',
            '|| alpha ||',
            '|| beta ||'
        )
    ';

    execute '
        select madlib.lda_get_perplexity (
            '''|| tbl_model||''',
            '''|| tbl_output ||'''
        )
    ' into perplexity;

    execute '
        drop table if exists '|| tbl_output ||';
        drop table if exists '|| tbl_model ||'
    ';
    
    execute '
        select perplexity
        from ' || tbl_R ||
        ' where dataset = '''|| datatable ||''' and
            topic_no =' || topic_no
    into perplexity_r;


    diff := abs((perplexity - perplexity_r)/perplexity_r);
    if diff < 0.1 then
        return 100.;
    else
        return -100;
    end if;
end;
$$ language plpgsql;

drop table if exists madlibtestdata.evaluation_lda;

create table madlibtestdata.evaluation_lda (
    eval_src            text,   -- 'R'
    dataset             text,   -- Name of data set
    topic_no            integer,-- Number of topics
    perplexity          double precision
);

alter table madlibtestdata.evaluation_lda owner to madlibtester;

----------------------------------------------------------------------------

insert into madlibtestdata.evaluation_lda values
    ('R', 'lda_associated_press', 10, 2356.61687563252),
    ('R', 'lda_associated_press', 20, 1987.22860262696),
    ('R', 'lda_associated_press', 30, 1792.40716887695),
    ('R', 'lda_associated_press', 40, 1680.8284780254),
    ('R', 'lda_associated_press', 50, 1597.29612635741),
    ('R', 'lda_associated_press', 60, 1544.01058613653),
    ('R', 'lda_associated_press', 70, 1503.20411970059),
    ('R', 'lda_associated_press', 80, 1468.83501487259),
    ('R', 'lda_associated_press', 90, 1446.54200105897),
    ('R', 'lda_associated_press', 100, 1429.71636336914);
