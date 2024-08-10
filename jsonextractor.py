import json

# Sample JSON data (replace this with the actual JSON data)
# json_data = (write some code to load the file from a command line argument eg.author_project.json)
json_data = 

# Parse the JSON data
data = json.loads(json_data)

# Extract vulnerabilities
vulnerabilities = data.get('vulnerabilities', [])

# List to store parsed details
parsed_details = []

for vulnerability in vulnerabilities:
    details = {
        'id': vulnerability.get('id'),
        'dataSource': vulnerability.get('dataSource'),
        'namespace': vulnerability.get('namespace'),
        'severity': vulnerability.get('severity'),
        'urls': vulnerability.get('urls', []),
        'fix': vulnerability.get('fix', {}),
        'relatedVulnerabilities': vulnerability.get('relatedVulnerabilities', [])
    }
    parsed_details.append(details)

# Print parsed details
for detail in parsed_details:
    print(json.dumps(detail, indent=2))
