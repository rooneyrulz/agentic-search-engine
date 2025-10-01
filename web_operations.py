import json
from dotenv import load_dotenv
import os
import requests
from urllib.parse import quote_plus

from snapshot_operations import poll_snapshot_status, download_snapshot

load_dotenv()

dataset_id = "gd_lvz8ah06191smkebj4"

def _make_api_request(url, **kwargs):

    api_key = os.getenv("BRIGHTDATA_API_KEY")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def serp_search(query, engine="google"):
    if engine == "google":
        base_url = "https://www.google.com/search"
    elif engine == "bing":
        base_url = "https://www.bing.com/search"
    else:
        raise ValueError(f"Unsupported search engine: {engine}")

    url = "https://api.brightdata.com/request"

    payload = {
        "zone": "ai_search_engine",
        "url": f"{base_url}?q={quote_plus(query)}&brd_json=1",
        "format": "raw"
    }

    full_response = _make_api_request(url, json=payload)

    if not full_response:
        return None

    # print(engine)
    # print(full_response)

    extracted_data = {
        "knowledge": full_response.get("knowledge", {}),
        "organic": full_response.get("organic", [])
    }

    return extracted_data


def _trigger_and_download_snapshot(trigger_url, params, data, operation_name="operation"):
    trigger_response = _make_api_request(trigger_url, params=params, json=data)
    if not trigger_response:
        return None
    
    snapshot_id = trigger_response.get("snapshot_id")
    if not snapshot_id:
        return None

    if not poll_snapshot_status(snapshot_id):
        return None
    
    return download_snapshot(snapshot_id)


def reddit_search_api(keyword, date="All time", sort_by="Hot", num_of_posts=75):
    trigger_url = f"https://api.brightdata.com/datasets/v3/trigger"

    params = {
        "datasetId": dataset_id,
        "include_errors": True,
        "type": "discover_new",
        "discover_by": "keyword",
    }

    data = [
        {
            "keyword": keyword,
            "date": date,
            "sort_by": sort_by,
            "num_of_posts": num_of_posts,
        }
    ]

    raw_data = _trigger_and_download_snapshot(trigger_url, params, data, operation_name="reddit_search")

    if not raw_data:
        return None
    
    parsed_data = []
    
    for item in raw_data:
        parsed_data.append({
            "title": item.get("title"),
            "url": item.get("url"),
            "content": item.get("content", ""),
        })
    
    return {"parsed_data": parsed_data, "total_found": len(parsed_data)}


def reddit_post_retrieval(urls, days_back=10, load_all_replies=False, comment_limit=""):
    if not urls:
        return None

    trigger_url = f"https://api.brightdata.com/datasets/v3/trigger"

    params = {
        "dataset_id": "",
        "include_errors": "true",
    }

    data = [
        {
            "url": url,
            "days_back": days_back,
            "load_all_replies": load_all_replies,
            "comment_limit": comment_limit,
        }
        for url in urls
    ]

    raw_data = _trigger_and_download_snapshot(trigger_url, params, data, operation_name="reddit_post_retrieval")

    if not raw_data:
        return None

    parsed_comments = []

    for item in raw_data:
        parsed_comments.append({
            "comment_id": item.get("comment_id"),
            "content": item.get("comment", ""),
            "date": item.get("date_posted")
        })

    return {"comments": parsed_comments, "total_found": len(parsed_comments)}
