#!/usr/bin/env python3

import requests
import os
import json


def auth():
    """Obtain bearer token from OS environment.


    Once you have your bearer token, add it as an environment variable by
    typing `export 'BEARER_TOKEN'='<your_bearer_token>'` in the terminal.
    """
    bearer_token = os.environ.get("BEARER_TOKEN")
    if not bearer_token:
        raise Exception("Bearer token not set as environment variable.")
    return bearer_token


def create_url(tweet, next_token=None, max_count=100, **kwargs):
    """Create the url to send to Twitter API V2.

    Tweet fields for each answer queried by default are:
      - in_reply_to_user_id, author_id, created_at, conversation_id,
        geo,entities, source, context_annotations, public_metrics,
        referenced_tweets.

    Parameters
    ----------
    tweet : int, the id of the root tweet.
    next_token : int (optional), the next token for pagination in case the
                 reply tweet is not complete.
    max_count : int (optional), maximum number of tweets returned, has to be
               within the range [1, 100).

    **kwargs : optional, Tweet Fields. See:
    https://developer.twitter.com/en/docs/labs/tweets-and-users/api-reference/get-tweets
    """

    query = f"conversation_id:{tweet}"
    max_results = f"max_results={max_count}"
    tweet_fields = ("tweet.fields=in_reply_to_user_id,author_id,created_at,"
                    "conversation_id,geo,entities,source,"
                    "context_annotations,public_metrics,referenced_tweets")
    # Add supplementary tweet fields
    if kwargs:
        for kw in kwargs:
            tweet_fields += f",{kwargs[kw]}"
    if next_token:
        url = ("https://api.twitter.com/2/tweets/search/recent?query="
               f"{query}&{tweet_fields}&{max_results}&next_token={next_token}")
    else:
        url = ("https://api.twitter.com/2/tweets/search/recent?query="
               f"{query}&{tweet_fields}&{max_results}")

    return url


def create_headers(bearer_token):
    headers = {"Authorization": f"Bearer {bearer_token}"}
    return headers


def connect_to_endpoint(url, headers):
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response


def get_data(tweet, data_path="../data", max_count=100):
    """Create a new directory `tweet' and save the reply tree there.


    Parameters
    ----------
    tweet : int, tweet id.
    save_data : str (optional), directory path to save tweets. A new directory
                will be created with the tweet id and responsed will be
                saved as json files.
    max_count : int, max number of tweets per response (limit is 100).

    **kwargs : optional, see :func:create_url
    """
    # Create directory with tweet id
    if not os.path.isdir(data_path):
        raise OSError(1, "Not a directory", "data_path")
    # Create directory with tweet id
    if not os.path.isdir(f'{data_path}/{tweet}'):
        os.mkdir(f"../data/{tweet}")
    bearer_token = auth()
    c = 0
    next_token = None
    while True:
        url = create_url(tweet, next_token=next_token, max_count=max_count)
        headers = create_headers(bearer_token)
        response = connect_to_endpoint(url, headers).json()
        c += 1
        with open(f"../data/{tweet}/{c}.json", "w") as f:
            json.dump(response, f)
        if "next_token" not in response['meta']:
            break
        else:
            next_token = response['meta']['next_token']


def network_edgelist():
    """Create network edgelist from list of json files"""
    pass
