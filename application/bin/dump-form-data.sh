#!/bin/sh

tmpFile=/tmp/tmp$$
tmpFile2=/tmp/tmp2$$
tmpFile3=/tmp/tmp3$$
tmpFile4=/tmp/tmp4$$
outFile=fixtures/initial-required-data/form_data.json
rm -f $tmpFile $tmpFile2 $tmpFile3

removeID=",CardStorage,QuestionLayout,QuestionStorage,Answer,FormValidationQuestion,ExportImportField,GoogleSheetConfig,"

for model in FormType Storage Form CategoryType Category CardStorage AnswerType Question QuestionLayout QuestionStorage Answer FormValidationLevel FormValidationType FormValidation FormValidationQuestion ExportImport ExportImportCard ExportImportField GoogleSheetConfig
do
	./manage.py dumpdata dataentry.$model > $tmpFile4
	echo $removeID | grep -q ",${model},"
	if [ $? -eq 0 ]
	then
		sed -e 's/"pk":[ 0-9]*,/"pk": null,/g' < $tmpFile4 >> $tmpFile
	else
		cat $tmpFile4 >> $tmpFile
	fi
done
sed -e 's/\]\[/,/g' < $tmpFile > $tmpFile2
python /data/bin/remove_station_reference.py $tmpFile2 $tmpFile3
python -m json.tool < $tmpFile3 > $outFile
rm -f $tmpFile $tmpFile2 $tmpFile3 $tmpFile4
