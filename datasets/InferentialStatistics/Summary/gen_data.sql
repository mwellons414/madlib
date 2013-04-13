DROP TABLE IF EXISTS madlibtestdata.summary_empty_table;
CREATE TABLE madlibtestdata.summary_empty_table(
    id SERIAL, 
    outlook text, 
    temperature float8, 
    humidity float8, 
    windy text, 
    class text);
