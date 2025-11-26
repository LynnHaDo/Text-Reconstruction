# Autocorrect (and autocomplete) engine

## Steps to run server locally

1. Create and activate virtual environment

```
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```
pip install -r requirements.txt
```

3. Run Flask app locally

```
python server.py
```

## Steps to set up client

1. Install clasp

```
npm install -g @google/clasp
```

2. Navigate to `google-extension`

```
cd google-extension
```

3. Push/pull

* Upload changes to Google Docs
* Pull changes made in the Browser

```
clasp push
clasp pull
```