import spacy
import csv
import os
from spacy.matcher import PhraseMatcher, Matcher

# === CONFIGURATION ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEYWORD_FILE = os.path.join(BASE_DIR, "data/keyword_file.txt")
CONTROL_CSV = os.path.join(BASE_DIR, "data/NIST_SP-800-53_rev5_catalog_load.csv")
CONTROL_TEXT_COLUMN = "control_text"
CONTROL_IDS_FILE = os.path.join(BASE_DIR, "data/controls_ids.txt")
MATCH_DEPTH = 2  # Set the depth threshold for matches

def load_keywords(keyword_file):
    with open(keyword_file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def load_control_ids(control_ids_file):
    with open(control_ids_file, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def build_matchers(nlp, keywords):
    phrase_patterns = [nlp.make_doc(text) for text in keywords]
    phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    phrase_matcher.add("KEYWORDS", phrase_patterns)

    matcher = Matcher(nlp.vocab)
    for keyword in keywords:
        pattern = [{"LEMMA": token.lemma_} for token in nlp(keyword)]
        matcher.add("FUZZY_KEYWORDS", [pattern])
    return phrase_matcher, matcher

def find_matches(nlp, phrase_matcher, matcher, control_csv, control_text_column):
    matches_found = []
    with open(control_csv, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            control_text = row[control_text_column]
            doc = nlp(control_text)
            exact_matches = phrase_matcher(doc)
            fuzzy_matches = matcher(doc)

            matched_phrases = list(set([doc[start:end].text for match_id, start, end in exact_matches]))
            matched_fuzzy = list(set([doc[start:end].text for match_id, start, end in fuzzy_matches]))
            all_matches = list(set(matched_phrases + matched_fuzzy))

            if all_matches:
                matches_found.append({
                    "identifier": row.get("identifier", "N/A"),
                    "control_text": control_text,
                    "matches": all_matches
                })
    return matches_found

def compare_ids(matches_found, control_ids, match_depth):
    filtered_matched_ids = set(entry['identifier'] for entry in matches_found if len(entry['matches']) > match_depth)
    control_ids_set = set(control_ids)
    matches = filtered_matched_ids & control_ids_set
    left_misses = control_ids_set - filtered_matched_ids
    right_misses = filtered_matched_ids - control_ids_set
    return matches, left_misses, right_misses

def print_results(matches_found, control_ids, matches, left_misses, right_misses, match_depth):
    print("RESULTS-----")
    for entry in matches_found:
        if len(entry['matches']) > match_depth:
            print(f"ID: {entry['identifier']}")
            print(f"Control: {entry['control_text']}")
            print(f"Matches: {entry['matches']}")
            print("-" * 50)

    print("SUMMARY-----")
    print(f"Number of matches found > {match_depth}:", len([e for e in matches_found if len(e['matches']) > match_depth]))
    identifiers = [entry['identifier'] for entry in matches_found if len(entry['matches']) > match_depth]
    print(f"Identifiers with >{match_depth} match:", ", ".join(identifiers))
    print(f"Imported control IDs from 800-160 [{len(control_ids)}]: {control_ids}")
    print(f"Matches (in both) [{len(matches)}]: {', '.join(matches)}")
    print(f"Left misses (in control_ids_800_160 only) [{len(left_misses)}]: {', '.join(left_misses)}")
    print(f"Right misses (in matches_found only) [{len(right_misses)}]: {', '.join(right_misses)}")

print(f"BASE_DIR: {BASE_DIR}")
nlp = spacy.load("en_core_web_sm")
keywords = load_keywords(KEYWORD_FILE)
control_ids = load_control_ids(CONTROL_IDS_FILE)
phrase_matcher, matcher = build_matchers(nlp, keywords)
matches_found = find_matches(nlp, phrase_matcher, matcher, CONTROL_CSV, CONTROL_TEXT_COLUMN)
matches, left_misses, right_misses = compare_ids(matches_found, control_ids, MATCH_DEPTH)
print_results(matches_found, control_ids, matches, left_misses, right_misses, MATCH_DEPTH)

"""
def main():
    print(f"BASE_DIR: {BASE_DIR}")
    nlp = spacy.load("en_core_web_sm")
    keywords = load_keywords(KEYWORD_FILE)
    control_ids = load_control_ids(CONTROL_IDS_FILE)
    phrase_matcher, matcher = build_matchers(nlp, keywords)
    matches_found = find_matches(nlp, phrase_matcher, matcher, CONTROL_CSV, CONTROL_TEXT_COLUMN)
    matches, left_misses, right_misses = compare_ids(matches_found, control_ids, MATCH_DEPTH)
    print_results(matches_found, control_ids, matches, left_misses, right_misses, MATCH_DEPTH)

if __name__ == "__main__":
    main()
"""