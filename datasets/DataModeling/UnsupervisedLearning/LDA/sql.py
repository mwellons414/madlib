import os, sys

table = sys.argv[1]
sql = sys.argv[2]

outfile = open(sql, 'w')

outfile.write("DROP TABLE IF EXISTS %s_vocab;\n" % table)
outfile.write("CREATE TABLE %s_vocab(wordid int4, word text);\n" % table)
outfile.write("ALTER TABLE %s_vocab OWNER TO madlibtester;\n" % table)
outfile.write("COPY %s_vocab FROM stdin DELIMITER '#';\n" % table)

vocfile = open(table + '.vocab')
for line in vocfile.readlines():
    [wordid, word] = line[:-1].split('\t')
    outfile.write(
        "%s#'%s'\n" % (wordid, word))
outfile.write("\\.\n")
vocfile.close()

outfile.write("DROP TABLE IF EXISTS %s_corpus;\n" % table)
outfile.write("CREATE TABLE %s_corpus(docid int4, wordid int4, count int4);\n" % table)
outfile.write("ALTER TABLE %s_corpus OWNER TO madlibtester;\n" % table)
outfile.write("COPY %s_corpus FROM stdin DELIMITER '#';\n" % table)

corpusfile = open(table + '.corpus')
for line in corpusfile.readlines():
    [docid, wordid, count] = line[:-1].split('\t')
    outfile.write(
        "%s#%s#%s\n" % (docid, wordid, count))
outfile.write("\\.\n")
corpusfile.close()

outfile.close()
