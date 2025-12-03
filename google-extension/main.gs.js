const SERVER_API_KEY = SERVER_API_CONFIGS.SERVER_API_KEY;
const AUTOCORRECT_ENDPOINT = SERVER_API_CONFIGS.AUTOCORRECT_ENDPOINT;
const AUTOCOMPLETE_ENDPOINT = SERVER_API_CONFIGS.AUTOCOMPLETE_ENDPOINT;
const API_URL =
  PropertiesService.getScriptProperties().getProperty(SERVER_API_KEY);

const UI = DocumentApp.getUi();
const DOC = DocumentApp.getActiveDocument();

function onOpen() {
  UI.createMenu(`${APP_CONFIG.PROJECT_NAME}-v${APP_CONFIG.VERSION}`)
    .addItem("Show Sidebar", "showSideBar")
    .addSubMenu(
      DocumentApp.getUi()
        .createMenu("Fix selection...")
        .addItem("Segmentation Only", "runFixSeg")
        .addItem("Insertion (vowels) Only", "runFixIns")
        .addItem("Joint (Seg + Ins)", "runFixBoth")
        .addItem("Autocorrect", "autoCorrect")
        .addItem("Autocomplete", "refreshSidebarContent")
    )
    .addToUi();
}

function showSideBar() {
  const htmlOutput =
    HtmlService.createHtmlOutputFromFile("Sidebar").setTitle("Suggestions");
  UI.showSidebar(htmlOutput);
}

function runFixBoth() {
  fixSelection(TEXT_PROCESSING_MODES.BOTH);
}
function runFixSeg() {
  fixSelection(TEXT_PROCESSING_MODES.SEGMENT);
}
function runFixIns() {
  fixSelection(TEXT_PROCESSING_MODES.INSERT);
}
function autoCorrect() {
  fixSelection(TEXT_PROCESSING_MODES.AUTOCORRECT);
}

function getSelection() {
  const selection = DOC.getSelection();

  if (!selection) {
    UI.alert("Please select the text you want to fix.");
    return;
  }

  const elements = selection.getRangeElements();

  // Process the first selected element
  const rangeElement = elements[0];
  const element = rangeElement.getElement();

  if (element.getType() !== DocumentApp.ElementType.TEXT) {
    UI.alert("Please select valid text.");
    return;
  }

  return [element, rangeElement];
}

function getStartAndEndIndices(element, rangeElement) {
  let startOffset = 0;
  let endOffsetInclusive = element.getText().length - 1;

  if (rangeElement.isPartial()) {
    startOffset = rangeElement.getStartOffset();
    endOffsetInclusive = rangeElement.getEndOffsetInclusive();
  }

  return [startOffset, endOffsetInclusive];
}

function getTextFromSelectionElement(
  element,
  rangeElement,
  startOffset,
  endOffsetInclusive
) {
  if (!element || !rangeElement) {
    UI.alert("Element is null. Please select the valid text.");
    return;
  }

  const text = element.getText().substring(startOffset, endOffsetInclusive + 1);
  const paragraph = element.getParent().asParagraph();
  const paragraphText = paragraph.getText();
  const sentence = paragraphText;

  if (!text.trim()) {
    UI.alert("Selection is empty.");
    return null;
  }

  return [text, sentence];
}

function fixSelection(mode = APP_CONFIG.DEFAULT_MODE) {
  let selections = getSelection();

  if (selections == null) {
    return;
  }

  let [element, rangeElement] = selections;
  // Calculate position
  let [startOffset, endOffsetInclusive] = getStartAndEndIndices(
    element,
    rangeElement
  );
  let textObject = getTextFromSelectionElement(
    element,
    rangeElement,
    startOffset,
    endOffsetInclusive
  );

  if (textObject == null) {
    return;
  }

  let [text, sentence] = textObject;

  try {
    const payload = {
      text: text,
      mode: mode,
      sentence: sentence,
    };

    const options = {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify(payload),
    };

    // Call the backend
    const response = UrlFetchApp.fetch(
      `${API_URL}${AUTOCORRECT_ENDPOINT}`,
      options
    );
    const json = JSON.parse(response.getContentText());

    if (json.corrected) {
      // Replace the text in the document
      element.deleteText(startOffset, endOffsetInclusive);
      element.insertText(startOffset, json.corrected);
      const newCursorPosition = DOC.newPosition(
        element,
        element.getText().length
      );
      DOC.setCursor(newCursorPosition);
    } else {
      UI.alert("Error: " + json.error);
    }
  } catch (e) {
    UI.alert(
      "Connection failed. Is the Python server running? Error: " + e.toString()
    );
  }
}

// function completeSelection() {
//   let selections = getSelection();

//   if (selections == null) {
//     return;
//   }

//   let [element, rangeElement] = selections;
//   // Calculate position
//   let [startOffset,
//     endOffsetInclusive] = getStartAndEndIndices(element, rangeElement);
//   let textObject = getTextFromSelectionElement(element, rangeElement, startOffset, endOffsetInclusive);

//   if (textObject == null) {
//     return;
//   }

//   let [_, sentence] = textObject

//   try {
//     const payload = {
//       text: sentence,
//     };

//     const options = {
//       method: "post",
//       contentType: "application/json",
//       payload: JSON.stringify(payload),
//     };

//     // Call the backend
//     const response = UrlFetchApp.fetch(
//       `${API_URL}${AUTOCOMPLETE_ENDPOINT}`,
//       options
//     );
//     const json = JSON.parse(response.getContentText());

//     if (json.suggestions && json.suggestions.length > 0) {
//       const fullWord = json.suggestions[0]
//       const tokens = sentence.trim().split(/\s/)
//       const prefix = tokens[tokens.length - 1]

//       if (fullWord.startsWith(prefix)) {
//         const suffix = fullWord.substring(prefix.length)

//         if (suffix.length > 0) {
//             element.insertText(endOffsetInclusive + 1, suffix)
//         }
//       }
//       else {
//         element.insertText(endOffsetInclusive + 1, fullWord)
//       }
//       const newCursorPosition = DOC.newPosition(element, element.getText().length)
//       DOC.setCursor(newCursorPosition)

//     } else {
//       UI.alert("Error: " + json.error);
//     }
//   } catch (e) {
//     UI.alert(
//       "Connection failed. Is the Python server running? Error: " + e.toString()
//     );
//   }
// }

function getAllTextInDoc() {
    const body = DOC.getBody();
    const sentence = body.getText();

    if (!sentence.trim()) {
        return "";
    }

    const cleanedSentence = sentence.replace(/[\n\r]/g, '')

    if (sentence.endsWith(" ")) {
        cleanedSentence = cleanedSentence.trimEnd() + " "
    }

    return cleanedSentence
}

function getSuggestions() {
  const sentence = getAllTextInDoc();

  if (sentence == "") {
    UI.alert("Document is blank. Please input some text!");
    return;
  }

  try {
    const payload = {
      text: sentence,
    };

    const options = {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify(payload),
    };

    // Call the backend
    const response = UrlFetchApp.fetch(
      `${API_URL}${AUTOCOMPLETE_ENDPOINT}`,
      options
    );
    const json = JSON.parse(response.getContentText());
    return json.suggestions || [];
  } catch (err) {
    console.log("error getting suggestions", err);
  }
}

function replaceText(word) {
  const sentence = getAllTextInDoc();

  if (sentence == "") {
    UI.alert("Document is blank. Please input some text!");
    return;
  }

  let suffix = "";
  const body = DOC.getBody()

  if (sentence.endsWith(" ")) {
    // Insert full word
    suffix = word
  } else {
    // Insert partial word
    let tokens = sentence.trim().split(/\s+/)
    let prefix = tokens[tokens.length - 1]

    if (word.startsWith(prefix.toLowerCase())) {
        suffix = word.substring(prefix.length);
    } else {
        suffix = " " + word; 
    }
  }

  if (suffix.length == 0) {
      return;
  }

  const paragraphs = body.getParagraphs();
  const lastParagraph = paragraphs[paragraphs.length - 1];
  const lastText = lastParagraph.editAsText();
  
  lastText.appendText(suffix);
}

function refreshSidebarContent() {
  showSideBar();
}
