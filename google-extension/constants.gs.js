const SERVER_API_KEY = "SERVER_TEXT_PROCESSING_URL"

const TEXT_PROCESSING_MODES = {
    SEGMENT: "seg",
    INSERT: "ins",
    BOTH: "both",
    AUTOCORRECT: "autocorrect"
}

const APP_CONFIG = {
    PROJECT_NAME: "Autocorrect/autocomplete Extension",
    VERSION: "1.0.0",
    DEFAULT_MODE: "both", // default text fixing mode
    TIMEOUT_SECONDS: 30 // timeout on processing
}