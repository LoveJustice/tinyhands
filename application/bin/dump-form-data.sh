#!/bin/sh

tmpFile=/tmp/tmp$$
tmpFile2=/tmp/tmp2$$
tmpFile3=/tmp/tmp3$$
outFile=fixtures/initial-required-data/form_data.json
rm -f $tmpFile $tmpFile2 $tmpFile3

for model in FormType Storage Form CategoryType Category CardStorage AnswerType Question QuestionLayout QuestionStorage Answer FormValidationLevel FormValidationType FormValidation FormValidationQuestion ExportImport ExportImportCard ExportImportField GoogleSheetConfig
do
	./manage.py dumpdata dataentry.$model >> $tmpFile
done
sed -e 's/\]\[/,/g' < $tmpFile > $tmpFile2
python /data/bin/remove_station_reference.py $tmpFile2 $tmpFile3
python -m json.tool < $tmpFile3 > $outFile
rm -f $tmpFile $tmpFile2 $tmpFile3
