# functions.py sudo
from django.shortcuts import render
from django.http import JsonResponse

import openai
from server.config import openaiKEY, notionKEY, notionDB_id

import json, requests

def generateGPT(text):

    openai.api_key = openaiKEY
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            {"role": "system", "content": "Explain to me the concept of %s with a full explanation." %text },
        ],
        temperature = 0
    )

    return response.choices[0].message.content


def create_json(text, data):

    """
    Create a function that pre-aligns the data format for notion api, integrating both the text and the gpt response.

    Input : (selected_text, gpt-response)
    Output : json.dumps(data)
    """
    
    data = {
        "parent": {
            "database_id": notionDB_id
        },
        "properties": {
            "Content": {
                "title": [
                    {
                        "text": {
                            "content": "%s" % text
                        }
                    }
                ]
            },
            "Concept":{
                "rich_text":[
                    {
                    "text":{
                        "content":"%s" % data
                    }
                    }
                ]
            }
        }
    }

    with open("data.json", "w") as fp:
        data_json = json.dumps(data)
    return data_json


def send2notion(json):

    url = "https://api.notion.com/v1/pages"

    headers = {
        "Authorization": "Bearer %s" % notionKEY,
        "Content-Type": "application/json",
        "Notion-Version": "2021-08-16"
    }

    response = requests.post(url, headers=headers, data=json)

    if response.status_code == 200:
        print("Text entry created successfully in Notion!")
    else:
        print("Error creating text entry in Notion:", response.status_code, response.text)


def process_selected_text(selected_text):
    gptResponse = generateGPT(selected_text)
    data_json = create_json(selected_text, gptResponse)
    send2notion(data_json)

    # print("Succesfully Imported gpt Response to Notion DB /*metis*/")


def main():

    test_word = 'dog'
    process_selected_text(test_word)


if __name__ == "__main__":
    main()