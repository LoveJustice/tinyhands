import base64
import os
import json
from typing import Union
from pathlib import Path

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class ImageAnalysisResult(BaseModel):
    description: str
    text: str = ""
    emails: list[str] = Field(default_factory=list)
    urls: list[str] = Field(default_factory=list)
    phone_numbers: list[str] = Field(default_factory=list)


def analyze_image(
    image: Union[str, Path],
    api_key: str,
    model: str = "gpt-4o-mini",
    max_tokens: int = 900,
    api_url: str = "https://api.openai.com/v1/chat/completions",
) -> ImageAnalysisResult:
    """
    Analyze an image using OpenAI's API and return extracted information.

    Args:
        image (Union[str, Path]): The path to the image file to analyze.
        api_key (str): OpenAI API key.
        model (str): The model to use for analysis. Defaults to "gpt-4o-mini".
        max_tokens (int): Maximum number of tokens for the API response. Defaults to 900.
        api_url (str): OpenAI API endpoint URL.

    Returns:
        ImageAnalysisResult: An object containing the analysis results.

    Raises:
        ValueError: If the API request fails or the response cannot be parsed.
    """

    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    base64_image = encode_image(image)

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Assistant, consider this image. Give a brief description. If there is text then please return it as is. Please also extract "
                            "email, urls and phonenumbers and return the following json object:"
                            "{'description': 'brief description','text': 'text extracted from image', 'emails': ['email1', 'email2'], 'urls': ['url1', 'url2'], "
                            "'phonenumbers': ['phonenumber1', 'phonenumber2']}"
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        "max_tokens": max_tokens,
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        content = result["choices"][0]["message"]["content"]
        parsed_content = json.loads(content)

        return ImageAnalysisResult(
            description=parsed_content.get("description", ""),
            text=parsed_content.get("text", ""),
            emails=parsed_content.get("emails", []),
            urls=parsed_content.get("urls", []),
            phone_numbers=parsed_content.get("phonenumbers", []),
        )
    except requests.RequestException as e:
        raise ValueError(f"API request failed: {str(e)}") from e
    except (KeyError, json.JSONDecodeError, IndexError) as e:
        raise ValueError(f"Failed to parse API response: {str(e)}") from e
