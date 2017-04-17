#!/usr/bin/env python3
"""
Usage:
  ama <question> --source-dir=<source-dir> [--n-pages=<n-pages>]

Options:
  --source-dir=source-dir    Source of pdfs
  --n-pages=n-pages      Number of pages to match [default 1]
"""

import msgpack
import subprocess
from docopt import docopt
from pathlib import Path
from scipy import sparse
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from tqdm import tqdm
from typing import List


class Model:
    """
    Model for working with a source of pdfs
    """

    def __init__(self, source_path: Path):
        self.path = source_path
        self.data_file = self.path.joinpath("ama.data")
        self._read_data()
        self._update()
        self.generate_vectors()

    def _write_data(self):
        with self.data_file.open("wb") as df:
            df.write(msgpack.packb(self.data, use_bin_type=True))

    def _read_data(self):
        """
        Load or generate data
        """

        if not self.data_file.exists():
            self.data = {
                "files": [],
                "pages": []
            }

            self._write_data()
        else:
            with self.data_file.open("rb") as df:
                self.data = msgpack.unpackb(df.read(), encoding="utf-8")

    def read_pdf(self, pdf_path: Path) -> List[str]:
        """
        Pdf to list of pages (str)
        """

        result = subprocess.run(
            ["Rscript", "spitr", str(pdf_path)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        return result.stdout.decode("utf8").lower().split("<pagebreak>")

    def _update(self):
        """
        Update the source
        """

        files = list(self.path.glob("*.pdf"))
        updated = False
        print(f" Reading {len(files)} pdfs ...")
        for f in tqdm(files):
            if str(f) not in self.data["files"]:
                self.data["pages"] += self.read_pdf(f)
                self.data["files"].append(str(f))
                updated = True
        if updated:
            self._write_data()

    def generate_vectors(self):
        self.vectorizer = HashingVectorizer(ngram_range=(1, 2), stop_words="english")
        self.vectors = self.vectorizer.transform(self.data["pages"])

    def answer(self, question: str, n_pages=1):
        q_vector = self.vectorizer.transform([question.lower()])
        combined = sparse.vstack([self.vectors, q_vector])
        combined = TfidfTransformer().fit_transform(combined)

        # Distance to pages
        distances = combined[:-1].dot(combined[-1].T).todense()

        page_indices = distances.T.argsort()[:, -n_pages:].tolist()[0]
        page_indices.reverse()
        print(page_indices)

        for pi in page_indices:
            print(self.data["pages"][pi])
            print("")


if __name__ == "__main__":
    args = docopt(__doc__)
    model = Model(Path(args["--source-dir"]))
    model.answer(args["<question>"], int(args["--n-pages"]))
