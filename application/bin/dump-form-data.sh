#!/bin/sh
if [ $# -ge 1 ]
then
	tag=$1
else
	tag=$(date "+%Y%m%d")
fi
tmpFile=/tmp/tmp$$
tmpFile2=/tmp/tmp2$$
outFile=fixtures/form_data_$tag.json
rm -f $tmpFile

for model in FormType Storage Form CategoryType Category CardStorage AnswerType Question QuestionLayout QuestionStorage Answer FormValidationLevel FormValidationType FormValidation FormValidationQuestion ExportImport ExportImportCard ExportImportField GoogleSheetConfig
do
	./manage.py dumpdata dataentry.$model >> $tmpFile
done
sed -e 's/\]\[/,/g' < $tmpFile > $tmpFile2
python /data/bin/remove_station_reference.py $tmpFile2 $outFile
