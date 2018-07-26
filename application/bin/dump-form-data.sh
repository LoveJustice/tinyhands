#!/bin/sh
if [ $# -ge 1 ]
then
	tag=$1
else
	tag=$(date "+%Y%m%d")
fi
tmpFile=/tmp/tmp$$
outFile=fixtures/form_data_$tag.json
rm -f $tmpFile

for model in FormType Storage Form CategoryType Category CardStorage AnswerType Question QuestionLayout QuestionStorage Answer FormValidationLevel FormValidationType FormValidation FormValidationQuestion
do
	./manage.py dumpdata dataentry.$model >> $tmpFile
done
cat $tmpFile | sed -e 's/\]\[/,/g' > $outFile