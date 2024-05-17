
# Booktopia

scraping the book details from booktopi website


## Documentation

[Documentation](https://linktodocumentation)

Input: Isbn-13 (13 digit book code)

Data points: these are the data points collecting from the website.

['Title of the book', 'Author/s','Book_type','Original Price(RRP)','Discount Price','ISBN-10','Published Date', 'Publisher','No of pages']

# requirements
pip install requirements, bs4, pandas, multithreading, json


# Files
don not remove the run_log file from folder.
input_list: contains the isbn-13 input code to search
run_log.csv: storing the input code, completed url, time_stamp 
outputfile_isbn: storing the all the data points for each book.


# Referance API
https://scrapeops.io/app/proxy

https://proxyscrape.com/

intially i have used selenium there im getting automation error so i switch to proxies , proxyscrape is fast but after few requests its getting blocked, scrapeops is littile bit slow but giving good response. i have used multithreading to increase the speed of the scraper.

Please check the selenium automation error i have metined in the folder
