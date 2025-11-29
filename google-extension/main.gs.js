const API_URL = PropertiesService.getScriptProperties().getProperty(SERVER_API_KEY);

function onOpen() {
  DocumentApp.getUi()
      .createMenu(`${APP_CONFIG.PROJECT_NAME}-v${APP_CONFIG.VERSION}`)
      .addSubMenu(
        DocumentApp.getUi().createMenu('Fix selection...')
        .addItem('Segmentation Only', 'runFixSeg')
        .addItem('Insertion (vowels) Only', 'runFixIns')
        .addItem('Joint (Seg + Ins)', 'runFixBoth')
        .addItem('Autocorrect', "autoCorrect")
        .addItem('Autocomplete', "completeSelection")
      )
      .addToUi();
}

function runFixBoth() { fixSelection(TEXT_PROCESSING_MODES.BOTH) }
function runFixSeg() { fixSelection(TEXT_PROCESSING_MODES.SEGMENT) }
function runFixIns() { fixSelection(TEXT_PROCESSING_MODES.INSERT) }
function autoCorrect() { fixSelection(TEXT_PROCESSING_MODES.AUTOCORRECT) }

function getSelection() {
    const doc = DocumentApp.getActiveDocument();
    const selection = doc.getSelection();
    const ui = DocumentApp.getUi();

    if (!selection) {
        ui.alert('Please select the text you want to fix.');
        return null;
    }

    const elements = selection.getRangeElements();
    
    // Process the first selected element
    const rangeElement = elements[0]
    const element = rangeElement.getElement();
    
    if (element.getType() !== DocumentApp.ElementType.TEXT) {
        ui.alert('Please select valid text.');
        return null;
    }

    return element, rangeElement
}

function getStartAndEndIndices(element, rangeElement) {
    let startOffset = 0;
    let endOffsetInclusive = element.getText().length - 1;

    if (rangeElement.isPartial()) {
        startOffset = rangeElement.getStartOffset();
        endOffsetInclusive = rangeElement.getEndOffsetInclusive();
    }

    return startOffset, endOffsetInclusive
}

function getTextFromSelectionElement(element, rangeElement) {
    if (element == null || rangeElement == null) {
        ui.alert('Element is null. Please select the valid text.')
        return null
    }

    // Calculate position
    let startOffset, endOffsetInclusive = getStartAndEndIndices(element, rangeElement)

    const text = element.getText().substring(startOffset, endOffsetInclusive + 1);
    const paragraph = element.getParent().asParagraph();
    const paragraphText = paragraph.getText();

    const sentence = paragraphText;

    if (!text.trim()) {
        ui.alert('Selection is empty.');
        return null;
    }

    return text, sentence
}

function fixSelection(mode=APP_CONFIG.DEFAULT_MODE) {
  let selections = getSelection()

  if (selections == null) {
    return;
  }

  let element, rangeElement = selections
  let text, sentence = getTextFromSelectionElement(element, rangeElement)
  
  try {
    const payload = {
      "text": text,
      "mode": mode,
      "sentence": sentence
    };

    const options = {
      "method": "post",
      "contentType": "application/json",
      "payload": JSON.stringify(payload)
    };

    // Call the backend
    const response = UrlFetchApp.fetch(`${API_URL}${AUTOCORRECT_ENDPOINT}`, options);
    const json = JSON.parse(response.getContentText());

    if (json.corrected) {
      // Replace the text in the document
      element.deleteText(startOffset, endOffsetInclusive);
      element.insertText(startOffset, json.corrected);
    } else {
      ui.alert('Error: ' + json.error);
    }

  } catch (e) {
    ui.alert('Connection failed. Is the Python server running? Error: ' + e.toString());
  }
}

function completeSelection() {
    let selections = getSelection()

    if (selections == null) {
        return;
    }

    let element, rangeElement = selections
    let _, sentence = getTextFromSelectionElement(element, rangeElement)
    
    try {
        const payload = {
            "sentence": sentence
        };

        const options = {
            "method": "post",
            "contentType": "application/json",
            "payload": JSON.stringify(payload)
        };

        // Call the backend
        const response = UrlFetchApp.fetch(`${API_URL}/${AUTOCOMPLETE_ENDPOINT}`, options);
        const json = JSON.parse(response.getContentText());

        if (json.suggestions) {
            // Replace the text in the document
            element.deleteText(startOffset, endOffsetInclusive);
            element.insertText(startOffset, json.suggestions[0][0]);
        } else {
            ui.alert('Error: ' + json.error);
        }
    } catch (e) {
        ui.alert('Connection failed. Is the Python server running? Error: ' + e.toString());
    }
}
