SET client_min_messages TO WARNING;DROP TABLE IF EXISTS madlibtestdata.patients_wi;
CREATE TABLE madlibtestdata.patients_wi (x float8[],y INTEGER);
COPY madlibtestdata.patients_wi FROM STDIN NULL '?';
{1,1,70}	1
{1,1,80}	1
{1,1,50}	1
{1,0,60}	1
{1,0,40}	1
{1,0,65}	1
{1,0,75}	1
{1,0,80}	1
{1,0,70}	1
{1,0,60}	1
{1,1,65}	0
{1,1,50}	0
{1,1,45}	0
{1,1,35}	0
{1,1,40}	0
{1,1,50}	0
{1,0,55}	0
{1,0,45}	0
{1,0,50}	0
{1,0,60}	0
\.
ALTER TABLE madlibtestdata.patients_wi OWNER TO madlibtester;

