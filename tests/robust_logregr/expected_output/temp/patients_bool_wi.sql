SET client_min_messages TO WARNING;DROP TABLE IF EXISTS madlibtestdata.patients_bool_wi;
CREATE TABLE madlibtestdata.patients_bool_wi (x float8[],y BOOLEAN);
COPY madlibtestdata.patients_bool_wi FROM STDIN NULL '?';
{1,1,70}	TRUE
{1,1,80}	TRUE
{1,1,50}	TRUE
{1,0,60}	TRUE
{1,0,40}	TRUE
{1,0,65}	TRUE
{1,0,75}	TRUE
{1,0,80}	TRUE
{1,0,70}	TRUE
{1,0,60}	TRUE
{1,1,65}	FALSE
{1,1,50}	FALSE
{1,1,45}	FALSE
{1,1,35}	FALSE
{1,1,40}	FALSE
{1,1,50}	FALSE
{1,0,55}	FALSE
{1,0,45}	FALSE
{1,0,50}	FALSE
{1,0,60}	FALSE
\.
ALTER TABLE madlibtestdata.patients_bool_wi OWNER TO madlibtester;

