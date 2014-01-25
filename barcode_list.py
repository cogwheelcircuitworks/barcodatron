"""
Generate list of action barcodes .

Print these out and put them on the wall and aim your scanner at them.

"""
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Frame, Spacer, Image
from reportlab.graphics.barcode import code128
from reportlab.lib.pagesizes import A3, A4, landscape, portrait, letter
from reportlab.lib.units import inch
import os
import sys
from reportlab.lib.styles import getSampleStyleSheet
import random
import acrobat
import pprint

pdf_file =  os.path.normpath('barcode_list' + str(os.getpid()) + '.pdf')

def bcode(Elements,textarg,codearg):
  Elements.append(Paragraph(textarg,styles['Heading2']))
  val = textarg
  barwidth = .0170*inch
  barcode = code128.Code128( codearg, quiet=1, barWidth = barwidth, barHeight =.50*inch )
  Elements.append(barcode)
  style = styles['Normal']
  style.leftIndent=.25*inch
  Elements.append(Paragraph(codearg,style))
  return Elements

if __name__ == '__main__':

  styles=getSampleStyleSheet()
  Elements=[]

  print(pdf_file)
  #doc = BaseDocTemplate(pdf_file)

  doc = SimpleDocTemplate(
                            pdf_file,
                            fontSize     = 7,
                            pagesize     = letter,
                            topMargin    = .25*inch,
                            bottomMargin = .25*inch,
                            leftMargin   = .25*inch
                          )

  LogoImage = Image('logo512x512.jpg', 1.5*inch, 1.5*inch)
  LogoImage.hAlign = 'LEFT'
  Elements.append(LogoImage)
  Elements.append(Paragraph('Barcodatron',styles['Heading1']))

  Elements.append(Paragraph('Sample Nouns',styles['Heading2']))

  Elements = bcode(Elements,'Sample Job Number','SBJOB:tif952')

  Elements = bcode(Elements,'Sample Part Number','TPN:891')

  Elements.append(Paragraph('Sample Verbs',styles['Heading2']))
  Elements = bcode(Elements,'Preview 1-sided Part label','SBX:genlabelp')
  Elements = bcode(Elements,'Generate 1-sided Part label','SBX:genlabel')
  Elements = bcode(Elements,'Generate 2-sided Job+Part label','SBX:genlabel2s')
  Elements = bcode(Elements,'Check-in Part','SBX:checkin')


  #start the construction of the pdf
  doc.build(Elements)
  acrobat.run(pdf_file)

