#! python3

import pdfquery
import PyPDF2


def extract_data_payslip(pdfName):
    #number of page in the pdf
    readPDF = PyPDF2.PdfFileReader(pdfName)
    number_pages = readPDF.getNumPages()
    print(number_pages)
    
    #the payslip are not all similar
    #sometimes the data are in the page 1 or 2
    #extract the data from the correct page
    pdf = pdfquery.PDFQuery(pdfName)
    if number_pages == 0:
        pdf.load(0) 
    else:
        pdf.load(1)
    
    m = pdf.pq('LTpage[number_pages]')
    print(m)  


extract_data_payslip('R5577237_P00501_266214_PDF.PDF')
