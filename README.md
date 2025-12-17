# Autocorrect and autocomplete engine

We are in a group of two, Anh and Lynn, working on implementations of auto-correct and auto-complete systems. We integrated them into Google Docs extensions, utilizing Google Docs Apps Script, a JavaScript cloud platform that allows users to program and modify Google Docs. Our motivation to build this project is to learn and explore what is behind the scenes for the auto-correct feature in Grammarly and the auto-complete in Google Docs. For example, if users have a typo in the sentence, how does it know this is a wrong word and suggest the most appropriate one? Similarly, when users are typing the sentence, how does it predict what words are going to appear after that? Relevant prerequisites for this project include Bayes' probability and Trie data structure. 

## Features

- Autocorrect:
 - [x] Word segmentation and misisng vowel insertion
 - [x] Autocorrect a misspelled word in a sentence
- Autocomplete:
 - [x] Insert the rest of a partially complete word in a sentence
 - [x] Insert a new word to a partially complete sentence

## Testing

Please find the tests in the `tests/` directory. To run the tests, make sure that the server is up and running (see instructions below), and run:

```
python3 tests/autocompleteTests.py
```

## Configurations

- Python 3.13.9

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

## Steps to push code to client

1. Install clasp

```
npm install -g @google/clasp
```

2. Navigate to `google-extension`

```
cd google-extension
```

3. Clone the code from remote repo in App Script

```
clasp clone 'SCRIPT_ID'
```

(Please contact Lynn @ do24l@mtholyoke.edu to obtain the id of the repo)

4. Push/pull

Once you get the code, you can make changes and push/pull the code to remote repo.

* Upload changes to Google Docs
* Pull changes made in the Browser

```
clasp push
clasp pull
```