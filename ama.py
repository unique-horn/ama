#!/usr/bin/env python3
"""
Usage:
  ama <question> --source-dir=<source-dir> [--n-pages=<n-pages>]

Options:
  --source-dir=source-dir    Source of pdfs
  --n-pages=n-pages      Number of pages to match [default 1]
"""

import subprocess
from docopt import docopt
from pathlib import Path
from scipy import sparse
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from tqdm import tqdm
from typing import List


def read_pdf(pdf_file: Path) -> List[str]:
    result = subprocess.run(
        ["Rscript", "spitr", str(pdf_file)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return result.stdout.decode("utf8").split("<PAGEBREAK>")

def clean_text(text: str) -> str:
    cleaned = text
    return cleaned

if __name__ == "__main__":
    args = docopt(__doc__)

    pdfs = list(Path(args["--source-dir"]).glob("*.pdf"))
    pages: List[str] = []

    print(f" Reading {len(pdfs)} pdfs ...")
    for pdf in tqdm(pdfs):
        pages += map(clean_text, read_pdf(pdf))

    vectorizer = HashingVectorizer(ngram_range=(1, 2), stop_words="english")
    vectors = vectorizer.transform(pages)
    q_vector = vectorizer.transform([args["<question>"]])

    combined = sparse.vstack([vectors, q_vector])
    combined = TfidfTransformer().fit_transform(combined)

    # Distance to pages
    distances = combined[:-1].dot(combined[-1].T).todense()

    # Pages to display
    n_pages = int(args["--n-pages"])
    page_indices = distances.T.argsort()[:, -n_pages:].tolist()[0]
    page_indices.reverse()

    for pi in page_indices:
        print(pages[pi])
        print("")
