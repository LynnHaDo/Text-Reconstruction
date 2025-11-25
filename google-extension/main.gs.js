const API_URL = PropertiesService.getScriptProperties().getProperty(SERVER_API_KEY);

function onOpen() {
  DocumentApp.getUi()
      .createMenu(`${APP_CONFIG.PROJECT_NAME}-v${APP_CONFIG.VERSION}`)
      .addSubMenu(
        DocumentApp.getUi().createMenu('Fix selection...')
        .addItem('Joint (Seg + Ins)', 'runFixBoth')
        .addItem('Segmentation Only', 'runFixSeg')
        .addItem('Insertion (vowels) Only', 'runFixIns')
      )
      .addToUi();
}

function runFixBoth() { fixSelection(TEXT_PROCESSING_MODES.BOTH) }
function runFixSeg() { fixSelection(TEXT_PROCESSING_MODES.SEGMENT) }
function runFixIns() { fixSelection(TEXT_PROCESSING_MODES.INSERT) }

function fixSelection(mode) {
  const doc = DocumentApp.getActiveDocument();
  const selection = doc.getSelection();
  const ui = DocumentApp.getUi();

  if (!selection) {
    ui.alert('Please select the text you want to fix.');
    return;
  }

  const elements = selection.getRangeElements();
  
  // Process the first selected element
  const rangeElement = elements[0]
  const element = rangeElement.getElement();
  
  if (element.getType() !== DocumentApp.ElementType.TEXT) {
    ui.alert('Please select valid text.');
    return;
  }

  // Calculate position
  let startOffset = 0;
  let endOffsetInclusive = element.getText().length - 1;

  if (rangeElement.isPartial()) {
    startOffset = rangeElement.getStartOffset();
    endOffsetInclusive = rangeElement.getEndOffsetInclusive();
  }

  const text = element.getText().substring(startOffset, endOffsetInclusive + 1);

  if (!text.trim()) {
    ui.alert('Selection is empty.');
    return;
  }
  
  try {
    const payload = {
      "text": text,
      "mode": mode
    };

    const options = {
      "method": "post",
      "contentType": "application/json",
      "payload": JSON.stringify(payload)
    };

    // Call the backend
    const response = UrlFetchApp.fetch(API_URL, options);
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
