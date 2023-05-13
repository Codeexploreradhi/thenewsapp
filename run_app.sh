python -m textblob.download_corpora
python -m nltk.downloader stopwords
python -m nltk.downloader punkt
xvfb-run -a python news.py
