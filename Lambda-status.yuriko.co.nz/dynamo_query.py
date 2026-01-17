import time
import boto3
from boto3.dynamodb.conditions import Key

ONE_DAY_SECONDS = 86400
YESTERDAY_EPOCH = round(time.time() - ONE_DAY_SECONDS)
USD_JPY_RATE = 150

dynamodb = boto3.resource('dynamodb')
dynamodb_table = dynamodb.Table('status.yuriko.co.nz')

def __init__():
    return 0

def conoha_cost() -> str:
    conoha_cost = dynamodb_table.query(
        KeyConditionExpression=Key('server_name').eq('conoha_cost') & Key('unixtime').gt(YESTERDAY_EPOCH),
        ScanIndexForward=False
    )['Items']
    if conoha_cost == []:
        return '???'
    else:
        return "{:,}".format(conoha_cost[0]['cost_jpy'])

def aws_cost() -> str:
    aws_cost = dynamodb_table.query(
        KeyConditionExpression=Key('server_name').eq('aws_cost') & Key('unixtime').gt(YESTERDAY_EPOCH),
        ScanIndexForward=False # newest first (record [0] is latest)
    )['Items']
    if aws_cost == []:
        return '???'
    else:
        return "{:,}".format((round(aws_cost[0]['cost_usd'] * USD_JPY_RATE)))
