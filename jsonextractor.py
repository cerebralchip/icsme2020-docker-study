import json
import sys
import os

def parse_vulnerability(vulnerability, selected_fields):
    details = {}
    for field in selected_fields:
        details[field] = vulnerability.get(field, None)
    if 'relatedVulnerabilities' in selected_fields:
        related_vulns = vulnerability.get('relatedVulnerabilities', [])
        details['relatedVulnerabilities'] = [parse_vulnerability(rv, selected_fields) for rv in related_vulns]
    return details

# Check if the correct number of arguments is provided
if len(sys.argv) != 2:
    print("Usage: python jsonextractor.py <json_file>")
    sys.exit(1)

# Load the JSON file from the command line argument
json_file = sys.argv[1]
try:
    with open(json_file, 'r') as file:
        json_data = file.read()
except FileNotFoundError:
    print(f"File not found: {json_file}")
    sys.exit(1)

# Parse the JSON data
data = json.loads(json_data)

# Extract matches
matches = data.get('matches', [])

# List to store parsed details
parsed_details = []

# Define the fields you want to extract
selected_fields = ['id', 'dataSource', 'namespace', 'severity', 'fix', 'relatedVulnerabilities']

for match in matches:
    vulnerability = match.get('vulnerability', {})
    parsed_details.append(parse_vulnerability(vulnerability, selected_fields))

# Generate the output file name
output_file = f"processed_{os.path.basename(json_file)}"

# Write parsed details to the output file
with open(output_file, 'w') as file:
    json.dump(parsed_details, file, indent=2)

print(f"Processed data has been written to {output_file}")