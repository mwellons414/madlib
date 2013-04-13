-----------------------------------------------------------------------
-- Function that compares the coefficients from madlib and R and returns 
-- '100' if the difference is lower than a threshold else returns -100
--  The output was chosen as 100 since MADmark expects the output to be double
--      precision and has used 1 and -1 for its own specific purpose
create or replace function madlibtestdata.elastic_net_eval (
    dataset_name    varchar,
    tbl_r_rst       varchar,     -- R's result    
    col_dep_var     varchar,
    col_ind_var     varchar,
    alpha           double precision,
    lambda_value    double precision,
    standardize     BOOLEAN
) returns double precision as $$
declare
    tbl_output      varchar := madlib.__unique_string();
    madlib_coef     double precision[];
    r_coef          double precision[];
    coef_diff       double precision[];
    en_error        double precision;
    compare_rst     double precision;
    norm_str        text;
	y_mean			double precision;
	y_sd			double precision;
	rel_error		double precision[];
begin
    
    IF standardize THEN 
        norm_str := 'True';
    ELSE
        norm_str := 'False';
    END IF;

	execute 'select y_mean from madlibtestdata.' || tbl_r_rst ||
			' where dataset = $_valString$'|| dataset_name ||'$_valString$' into y_mean;
	execute 'select y_sd from madlibtestdata.' || tbl_r_rst ||
			' where dataset = $_valString$'|| dataset_name ||'$_valString$' into y_sd;

    execute '
        select madlib.elastic_net_train($_sql$madlibtestdata.' || dataset_name 
            || '$_sql$::text ,$_sql$' || tbl_output || '$_sql$::text ,$_sql$(' 
            || col_dep_var || '-' || y_mean || ')/' || y_sd || '$_sql$::text ,$_sql$' || col_ind_var 
            || '$_sql$::text, ''gaussian''::text, ' || alpha || ',' 
            || lambda_value || ','  || norm_str || ')';

    execute 'select coef_all from '|| tbl_output into madlib_coef;
    execute 'select coef from madlibtestdata.'|| tbl_r_rst ||'
            where dataset = $_valString$'|| dataset_name ||'$_valString$'
            into r_coef;
  
    -- # root mean squared error between madlib and R results
	execute  'select madlib.array_sub($_val${' || array_to_string(madlib_coef,',') || '}$_val$::double precision[],$_val${' || array_to_string(r_coef,',') || '}$_val$::double precision[])'
            into coef_diff;
	for i in 1 .. array_upper(coef_diff,1)
	loop
		if r_coef[i] > 1 then
			rel_error = array_append(rel_error,(coef_diff[i]/r_coef[i]));
		else
			rel_error = array_append(rel_error,coef_diff[i]);
		end if;
	end loop;
    execute 'select madlib.array_mean(madlib.array_mult($_val${' || array_to_string(rel_error,',') || 
        '}$_val$::double precision[],$_val${' || array_to_string(rel_error,',') || '}$_val$::double precision[]))' into en_error;

	if en_error <= 1e-5 then
            compare_rst := 100;
    else
            compare_rst := -100;
    end if;
    execute 'drop table if exists madlibtestdata.'|| tbl_output;
    return compare_rst;
end;
$$ language plpgsql;

alter function madlibtestdata.elastic_net_eval(varchar, varchar, varchar, integer, varchar) owner to madlibtester;

------------------------------------------------------------------------

-----------------------------------------------------------------------
-- Function that compares the coefficients from madlib and R and returns 
-- '100' if the difference is lower than a threshold else returns -100
--  The output was chosen as 100 since MADmark expects the output to be double
--      precision and has used 1 and -1 for its own specific purpose
create or replace function madlibtestdata.elastic_net_binomial_eval (
    dataset_name    varchar,
    tbl_r_rst       varchar,     -- R's result    
    col_dep_var     varchar,
    col_ind_var     varchar,
    alpha           double precision,
    lambda_value    double precision,
    standardize     BOOLEAN
) returns double precision as $$
declare
    tbl_output      varchar := madlib.__unique_string();
    madlib_coef     double precision[];
    r_coef          double precision[];
    coef_diff       double precision[];
    en_error        double precision;
    compare_rst     double precision;
    norm_str        text;
	y_mean			double precision;
	y_sd			double precision;
	rel_error		double precision[];
begin
    
    IF standardize THEN 
        norm_str := 'True';
    ELSE
        norm_str := 'False';
    END IF;

    execute '
        select madlib.elastic_net_train($_sql$madlibtestdata.' || dataset_name 
            || '$_sql$::text ,$_sql$' || tbl_output || '$_sql$::text ,$_sql$' 
            || col_dep_var || '$_sql$::text ,$_sql$' || col_ind_var 
            || '$_sql$::text, ''binomial''::text, ' || alpha || ',' 
            || lambda_value || ','  || norm_str || ')';

    execute 'select coef_all from '|| tbl_output into madlib_coef;
    execute 'select coef from madlibtestdata.'|| tbl_r_rst ||'
            where dataset = $_valString$'|| dataset_name ||'$_valString$'
            into r_coef;
  
    -- # root mean squared error between madlib and R results
	execute  'select madlib.array_sub($_val${' || array_to_string(madlib_coef,',') || '}$_val$::double precision[],$_val${' || array_to_string(r_coef,',') || '}$_val$::double precision[])'
            into coef_diff;
	for i in 1 .. array_upper(coef_diff,1)
	loop
		if r_coef[i] > 1 then
			rel_error = array_append(rel_error,(coef_diff[i]/r_coef[i]));
		else
			rel_error = array_append(rel_error,coef_diff[i]);
		end if;
	end loop;
    execute 'select madlib.array_mean(madlib.array_mult($_val${' || array_to_string(rel_error,',') || 
        '}$_val$::double precision[],$_val${' || array_to_string(rel_error,',') || '}$_val$::double precision[]))' into en_error;

	if en_error <= 1e-5 then
            compare_rst := 100;
    else
            compare_rst := -100;
    end if;
    execute 'drop table if exists madlibtestdata.'|| tbl_output;
    return compare_rst;
end;
$$ language plpgsql;

alter function madlibtestdata.elastic_net_binomial_eval(varchar, varchar, varchar, integer, varchar) owner to madlibtester;
