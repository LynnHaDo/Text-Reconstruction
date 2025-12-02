import csv
import requests

API_URL = "http://localhost:5001/autocomplete"
TEST_FILEPATH = "tests/autocomplete-tests.csv"

def run_tests():
    with open(TEST_FILEPATH, 'r') as f:
        reader = csv.DictReader(f)
        tests = list(reader)

    passing = 0
    print(f"{'CONTEXT + PREFIX':<45} | {'EXPECTED':<12} | {'RESULT':<6} | {'SUGGESTIONS'}")
    print("-" * 90)

    for t in tests:
        payload = {'text': t['text']}
        
        try:
            response = requests.post(API_URL, json=payload).json()
            suggestions = response.get('suggestions', [])
            
            # Check if expected is in the top 5
            if t['expected'].lower() in suggestions:
                status = "PASS"
                passing += 1
            else:
                status = "FAIL"

            print(f"{t['text']:<45} | {t['expected']:<12} | {status:<6} | {suggestions}")
            
        except Exception as e:
            print(f"Error connecting to server: {e}")
            break

    print("-" * 90)
    print(f"Passed {passing}/{len(tests)}")

if __name__ == "__main__":
    run_tests()