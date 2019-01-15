import json
import logging
from events.pull_request import PullRequest
from events.push import Push


def getPool(payload, pools):
    ownerPool = None
    payload = json.loads(payload)
    repo = payload["repository"]["full_name"]

    for pool in pools:
        if pool.containsRepo(repo):
            ownerPool = pool
            break

    if ownerPool is None:
        message = "Received repository '%s', but no pool is configured for it." % repo
        logging.info(message)
        return {
            "statusCode": 202,
            "body": json.dumps({
                "success": True,
                "message": message
            })
        }
    else:
        # get the secret for this repo
        for requestedRepo in ownerPool.repos:
            if repo == requestedRepo["name"]:
                repoName = requestedRepo["name"]
                repoSecret = requestedRepo["secret"]
        logging.info("Matched repo '{}' to pool '{}'".format(repoName,ownerPool.name))
        return {
            "statusCode": 200,
            "pool": ownerPool,
            "name": repoName,
            "secret": repoSecret
        }


def parsePayload(event, payload, repos):

    # for every supported event: find the pool, parse the payload, and return IRC messages
    payload = json.loads(payload)
    logging.info("Received the '%s' event" % event)
    if event == "push":
        # Create messages based on the payload
        push = Push(payload, repos)
        if push["statusCode"] != 200:
            return push

        return {
            "statusCode": 200,
            "messages": push["messages"]
        }


    elif event == "pull_request":
        # Create messages based on the payload
        pullRequest = PullRequest(payload)
        if pullRequest["statusCode"] != 200:
            return pullRequest

        return {
            "statusCode": 200,
            "messages": pullRequest["messages"]
        }


    elif event == "ping":
        return {
            "statusCode": 200,
            "messages": "pong"
        }


    else:
        message = "Received event '%s'. Doing nothing." % event
        logging.info(message)
        return {
            "statusCode": 202,
            "body": json.dumps({
                "success": True,
                "message": message
            })
        }