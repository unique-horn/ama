"""
Usage:
  ama <question> --source-dir=<source-dir> [--n-matches=<n-matches>]

Options:
  --source-dir=source-dir    Source of pdfs
  --n-matches=n-matches      Number of pages to match [default 1]
"""

import subprocess
from docopt import docopt

if __name__ == "__main__":
    args = docopt(__doc__)
