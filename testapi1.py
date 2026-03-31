import requests
import json

url = "https://api.lens.org/patent/search"

headers = {
    "Authorization": "CqccoNvviIvSeV0nMlohX42EXILU6HZ0Fj0Jpi7GdBnZwI76bEXg",  # 🔁 replace with your real token
    "Content-Type": "application/json"
}

data = {
    "query": {
        "bool": {
            "must": [
                {
                    "term": {
                        "publication_type": "GRANTED_PATENT"
                    }
                },
                {
                    "range": {
                        "year_published": {
                            "gte": 2015,
                            "lte": 2024
                        }
                    }
                },
                {
                    "bool": {
                        "should": [
                            {"match": {"applicant.name": "University"}},
                            {"match": {"applicant.name": "Institute of Technology"}},
                            {"match": {"applicant.name": "MIT"}},
                            {"match": {"applicant.name": "Caltech"}},
                            {"match": {"applicant.name": "College"}}
                        ]
                    }
                }
            ]
        }
    },
    "size": 5,
    "include": ["lens_id", "biblio", "abstract"]
}

response = requests.post(url, headers=headers, json=data)

# Print formatted JSON response
print(json.dumps(response.json(), indent=2))