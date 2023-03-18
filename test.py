import codecs
# writefile = codecs.open('dishes_dataset.csv', 'r', 'utf-8')
# writefile


import csv

with codecs.open('Book1.csv') as file:
	reader = csv.reader(file)
	count = 0
	for row in reader:
		print(row)
		if count > 5:
			break
		count += 1