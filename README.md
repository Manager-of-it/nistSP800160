# Cyber Resiliency Controls

## Purpose
Identify Cyber Resilicy Control Language from an Input Data Set (typically a file)

## Description
Utilize spaCy with prompts from NIST SP 800-160 Vol 2 Rev 1 to select controls from NIST 800-53.

### Prerequisites
spaCy

### Operations

##### === CONFIGURATION ===
##### === LOAD SPACY MODEL ===
##### === LOAD KEYWORDS / PHRASES ===
##### === READ CONTROL TEXTS AND MATCH ===

``` 
matches_found{
                "identifier": row.get("identifier", "N/A"),
                "control_text": control_text,
                "matches": matched_phrases
            } 
```

``` 
controls_800-160{
                "control_id"
            } 
```


##### === OUTPUT RESULTS ===




