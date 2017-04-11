#!/usr/bin/env Rscript
"usage: quiz <pdf-file>" -> doc

library(docopt)
library(pdftools)

args <- docopt(doc)
text <- pdf_text(args[["<pdf-file>"]])
text <- lapply(text, tolower)

## Clean up
for (page in text) {
  cat(page)
  cat("<PAGEBREAK>")
}
