import json


def clean_json_response(
    response: str
):

    cleaned_response = (
        response
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    return json.loads(
        cleaned_response
    )