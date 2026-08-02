SAFE_WORDING: dict[str, dict[str, str]] = {
    "VERIFIED_OFFICIAL_NUMBER": {
        "en": "Calling number matches a known official number for this organization. Likely legitimate — but stay alert if any credentials are requested.",
        "hi": "कॉल करने वाला नंबर इस संस्था के आधिकारिक नंबर से मेल खाता है। संभावित रूप से सुरक्षित — लेकिन किसी भी गोपनीय जानकारी की मांग पर सावधान रहें।",
    },
    "CLAIM_CONTRADICTS_POLICY": {
        "en": "The request conflicts with the organization's published safety guidance. This is a strong scam indicator.",
        "hi": "यह अनुरोध संस्था की प्रकाशित सुरक्षा सलाह से मेल नहीं खाता। यह एक मजबूत धोखाधड़ी संकेत है।",
    },
    "UNVERIFIED_NUMBER": {
        "en": "This number is not verified in the limited trusted directory. This alone does not prove fraud. Verify independently.",
        "hi": "यह नंबर सीमित विश्वसनीय सूची में सत्यापित नहीं है। केवल इससे धोखाधड़ी साबित नहीं होती। स्वतंत्र रूप से सत्यापन करें।",
    },
    "ORGANIZATION_NOT_IN_DIRECTORY": {
        "en": "This organization is not found in our trusted directory. Cannot verify the caller's claim.",
        "hi": "यह संस्था हमारी विश्वसनीय सूची में नहीं है। कॉलर के दावे की पुष्टि नहीं की जा सकती।",
    },
    "INSUFFICIENT_DATA": {
        "en": "There is not enough reliable identity information.",
        "hi": "विश्वसनीय पहचान जानकारी पर्याप्त नहीं है।",
    },
    "VERIFIED_ORGANIZATION_BUT_NUMBER_UNKNOWN": {
        "en": "The organization is known but the calling number is not on record. Verify independently.",
        "hi": "संस्था ज्ञात है लेकिन कॉल करने वाला नंबर रिकॉर्ड में नहीं है। स्वतंत्र रूप से सत्यापन करें।",
    },
}


def get_safe_wording(status: str, language: str = "en") -> str:
    status_data = SAFE_WORDING.get(status, SAFE_WORDING["INSUFFICIENT_DATA"])
    return status_data.get(language, status_data["en"])
