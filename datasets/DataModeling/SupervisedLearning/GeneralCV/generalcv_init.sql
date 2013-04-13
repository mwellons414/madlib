
create or replace function madlibtestdata.generalcv_linregr (
    dataset_name    VARCHAR,
    col_ind_var     VARCHAR,
    col_dep_var     VARCHAR,
    fold            INTEGER,
    tbl_r_rst       VARCHAR     -- R's result
) returns DOUBLE PRECISION as $$
declare
    tbl_output      VARCHAR := madlib.__unique_string();
    cv_error        DOUBLE PRECISION;
    cv_error_std    DOUBLE PRECISION;
    r_error         DOUBLE PRECISION;
    compare_rst     DOUBLE PRECISION;
begin
    execute '
        select madlib.cross_validation_general(
            $_valString$madlib.cv_linregr_train$_valString$,
            $_valString${%data%, '|| col_ind_var ||', '|| 
                            col_dep_var ||', %model%}$_valString$::VARCHAR[],
            $_valString${VARCHAR, VARCHAR, VARCHAR, VARCHAR}$_valString$::VARCHAR[],
            NULL::VARCHAR,
            NULL,
            --
            $_valString$madlib.cv_linregr_predict$_valString$,
            $_valString${%model%, %data%, '|| col_ind_var || 
                        ', %id%, %prediction%}$_valString$::VARCHAR[],
            $_valString${VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR}$_valString$::VARCHAR[],
            --
            $_valString$madlib.mse_error$_valString$,
            $_valString${%prediction%, %data%, %id%, '|| 
                        col_dep_var ||', %error%}$_valString$::VARCHAR[],
            $_valString${VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR}$_valString$::VARCHAR[],
            --
            $_valString$madlibtestdata.'|| dataset_name ||'$_valString$,
            NULL,
            False,
            --
            $_valString$madlibtestdata.'|| tbl_output ||'$_valString$,
            $_valString${'|| col_ind_var ||', '|| col_dep_var ||'}$_valString$::VARCHAR[],
            '|| fold ||'            
        )';

    execute 'select mean_squared_error_avg from madlibtestdata.' || 
                tbl_output into cv_error;
    execute 'select mean_squared_error_stddev from madlibtestdata.' || 
                tbl_output into cv_error_std;
    execute 'select error from '|| tbl_r_rst ||'
            where fold = '|| fold ||' and dataset = $_valString$'|| 
                dataset_name ||'$_valString$' into r_error;

    if r_error >= cv_error - 2.5*cv_error_std AND 
        r_error <= cv_error + 2.5*cv_error_std then
        compare_rst := 100;
    else
        compare_rst := -100;
    end if;

    execute 'drop table if exists madlibtestdata.'|| tbl_output;

    return compare_rst;
end;
$$ language plpgsql;

alter function madlibtestdata.generalcv_linregr(VARCHAR, VARCHAR, 
                                                VARCHAR, INTEGER, 
                                                VARCHAR
                                                ) owner to madlibtester;

------------------------------------------------------------------------

create or replace function madlibtestdata.generalcv_logregr (
    dataset_name    VARCHAR,
    col_ind_var     VARCHAR,
    col_dep_var     VARCHAR,
    fold            INTEGER,
    tbl_r_rst       VARCHAR     -- R's result
) returns DOUBLE PRECISION as $$
declare
    tbl_output      VARCHAR := madlib.__unique_string();
    cv_error        DOUBLE PRECISION;
    cv_error_std    DOUBLE PRECISION;
    r_error         DOUBLE PRECISION;
    compare_rst     DOUBLE PRECISION;
begin
    execute '
        select madlib.cross_validation_general(
            $_valString$madlib.logregr_train$_valString$,
            $_valString${%data%,  %model%, '|| col_dep_var ||', '|| 
            col_ind_var ||', NULL, 100, cg, 1e-8}$_valString$::VARCHAR[],
            $_valString${VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, INTEGER, 
                VARCHAR, DOUBLE PRECISION}$_valString$::VARCHAR[],
            NULL::VARCHAR,
            NULL,
            --
            $_valString$madlib.cv_logregr_predict$_valString$,
            $_valString${%model%, %data%, '|| col_ind_var ||', %id%, 
                         %prediction%}$_valString$::VARCHAR[],
            $_valString${VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR}$_valString$::VARCHAR[],
            --
            $_valString$madlib.cv_logregr_accuracy$_valString$,
            $_valString${%prediction%, %data%, %id%, '|| 
                col_dep_var ||', %error%}$_valString$::VARCHAR[],
            $_valString${VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR}$_valString$::VARCHAR[],
            --
            $_valString$madlibtestdata.'|| dataset_name ||'$_valString$,
            NULL,
            False,
            --
            $_valString$madlibtestdata.'|| tbl_output ||'$_valString$,
            $_valString${'|| col_ind_var ||', '|| col_dep_var ||'}$_valString$::VARCHAR[],
            '|| fold ||'
        )';

    execute 'select accuracy_avg from madlibtestdata.' || 
                tbl_output into cv_error;
    execute 'select accuracy_stddev from madlibtestdata.' || 
                tbl_output into cv_error_std;
    execute 'select error from '|| tbl_r_rst ||'
            where fold = '|| fold ||' and dataset = $_valString$'|| 
                dataset_name ||'$_valString$' into r_error;

    if r_error >= cv_error - 2.5*cv_error_std and
        r_error <= cv_error + 2.5*cv_error_std then
        compare_rst := 100;
    else
        compare_rst := -100;
    end if;

    execute 'drop table if exists madlibtestdata.'|| tbl_output;

    return compare_rst;
end;
$$ language plpgsql;

alter function madlibtestdata.generalcv_logregr(VARCHAR, VARCHAR, 
                                                VARCHAR, INTEGER, 
                                                VARCHAR
                                                ) owner to madlibtester;
