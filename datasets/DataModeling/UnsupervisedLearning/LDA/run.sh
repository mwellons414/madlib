data=$1
table=$2
sql=$3

tar -xzvf $data
folder=$(basename $data | cut -d '.' -f1)
mv $folder/vocab $table.vocab
mv $folder/corpus $table.corpus

python sql.py $table $sql

rm -r $folder
rm $table.vocab
rm $table.corpus
