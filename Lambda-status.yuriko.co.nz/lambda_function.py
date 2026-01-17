import json
import boto3
import time
import dynamo_query
from boto3.dynamodb.conditions import Key
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

def lambda_handler(event, context):
    cloudwatch = boto3.client('cloudwatch')
    
    response = cloudwatch.describe_alarms()
    response2 = cloudwatch.describe_alarm_history(
        AlarmName='Watch yuriko-co-nz',
        MaxRecords=10
    )
    for hist in response2['AlarmHistoryItems']:
        history = json.loads(hist['HistoryData'])

    aws_cost_jpy = dynamo_query.aws_cost()
    conoha_cost_jpy = dynamo_query.conoha_cost()
    #---------- <head> ----------
    twitter_card = '<meta name="twitter:card" content="summary">' + \
    '<meta name="twitter:title" content="yuriko.co.nz server status">' + \
    '<meta name="twitter:description" content="yuriko.co.nz server status">' + \
    '<meta name="twitter:image" content="https://yuriko.co.nz/images/yuriko2.png">' + \
    '<meta name="description" content="Server status pages of yuriko.co.nz infrastructure.">'
    title = '<title>yuriko.co.nz server status</title>'
    auto_reflesh = '<meta http-equiv="refresh" content="900">'

    head = '<head>' + twitter_card + title + auto_reflesh + '</head>'
    
    #---------- <table> ----------
    table = '<table>'
    for alarm in response['MetricAlarms']:
        if alarm['StateValue'] == 'OK':
            check = '✔'
            line = 'ONLINE'
        else:
            check = '❌'
            line = 'OFFLINE'
        
        state = '<td>' + check + '</td><td>[</td><td style="text-align: center">' + line + '</td><td>]</td>'
        table += '<tr>' + state + '<td>' + alarm['AlarmDescription'] + '</td></tr>'
    table += '<tr><td>？</td><td>[</td><td style="text-align: center">UNKNOWN</td><td>]</td><td>💢.akiba.yuriko.co.nz</td></tr>'
    table += '<tr><td>？</td><td>[</td><td style="text-align: center">UNKNOWN</td><td>]</td><td>📞.akiba.yuriko.co.nz</td></tr>'
    table += '<tr><td>？</td><td>[</td><td style="text-align: center">UNKNOWN</td><td>]</td><td>🕒.akiba.yuriko.co.nz</td></tr>'
    table += '<tr><td>？</td><td>[</td><td style="text-align: center">UNKNOWN</td><td>]</td><td>ntp2038.akiba.yuriko.co.nz</td></tr>'
    table += '<tr><td>？</td><td>[</td><td style="text-align: center">UNKNOWN</td><td>]</td><td>mail.yuriko.co.nz</td></tr>'
    table += '<tr><td>？</td><td>[</td><td style="text-align: center">UNKNOWN</td><td>]</td><td>ipsec.yuriko.co.nz</td></tr>'
    table += '<tr><td>？</td><td>[</td><td style="text-align: center">UNKNOWN</td><td>]</td><td>pbx.yuriko.co.nz</td></tr>'
    table += '<tr><td>？</td><td>[</td><td style="text-align: center">UNKNOWN</td><td>]</td><td>openvpn.yuriko.co.nz</td></tr>'
    table += '<tr><td>？</td><td>[</td><td style="text-align: center">UNKNOWN</td><td>]</td><td>trijn.tyo.yuriko.co.nz</td></tr>'
    table += '<tr><td>？</td><td>[</td><td style="text-align: center">UNKNOWN</td><td>]</td><td>nijntje.tyo.yuriko.co.nz</td></tr>'
    table += '<tr><td>？</td><td>[</td><td style="text-align: center">UNKNOWN</td><td>]</td><td>cisco-ucs.home.yuriko.co.nz</td></tr>'
    table += '<tr><td>？</td><td>[</td><td style="text-align: center">UNKNOWN</td><td>]</td><td>sgi.home.yuriko.co.nz</td></tr>'
    table += '<tr><td>？</td><td>[</td><td style="text-align: center">UNKNOWN</td><td>]</td><td>bitcoin.home.yuriko.co.nz</td></tr>'
    table += '<tr><td>？</td><td>[</td><td style="text-align: center">UNKNOWN</td><td>]</td><td>野獣先輩.yuriko.co.nz</td></tr>'
    table += '<tr><td>？</td><td>[</td><td style="text-align: center">UNKNOWN</td><td>]</td><td>📞.yuriko.co.nz</td></tr>'
    table += '<tr><td>？</td><td>[</td><td style="text-align: center">UNKNOWN</td><td>]</td><td>💢.home.yuriko.co.nz</td></tr>'
    table += '<tr><td>？</td><td>[</td><td style="text-align: center">UNKNOWN</td><td>]</td><td>👩🏻‍✈️.home.yuriko.co.nz</td></tr>'

    table += '</table>'

    dynamodb = boto3.resource('dynamodb')
    dynamodb_table = dynamodb.Table('status.yuriko.co.nz')
    ONE_DAY_SECONDS = 86400
    YESTERDAY_EPOCH = round(time.time() - ONE_DAY_SECONDS)

    host_table = '<table>'
    for hostname in ['sgi.home.yuriko.co.nz', 'surfacestudio.home.yuriko.co.nz', 'cisco-ucs.home.yuriko.co.nz', 'trijn.tyo.yuriko.co.nz', 'nijntje.tyo.yuriko.co.nz']:
        uptime = dynamodb_table.query(
            KeyConditionExpression=Key('server_name').eq(hostname) & Key('unixtime').gt(YESTERDAY_EPOCH),
            ScanIndexForward=False # newest first (record [0] is latest)
        )['Items']
        
        if not uptime:
            host_table += '<tr><td>' + hostname + '</td><td>up ??? days</td></tr>'
        else:
            host_table += '<tr><td>' + hostname + '</td><td>' + str(uptime[0]['uptime']) + '</td></tr>'
    host_table += '</table>'
    #---------- <body> ----------
    clock = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()) + ' UTC<br/>'
    first_day = time.strftime("%Y/%m/01", time.localtime())
    body = '<body><h1>👩🏻‍✈️yuriko.co.nz server status👩🏻‍💻　　　　　　　　　　　　　　　ぐお～🛌🏻ぐお～💤</h1>' + clock + table + \
    '<main role="main"><h2>🖥Host💻</h2>' + \
    host_table + \
    '<h2>💸Cost (' + first_day + '～)💸</h2>' + \
    'AWS: &yen;' + aws_cost_jpy + '　　　ConoHa: &yen;' + conoha_cost_jpy + '<br/></main>' + \
    '<a href="https://yuriko.co.nz"><img src="https://yuriko.co.nz/images/banner-reuse-Kyle-Lockwood-design-CC-BY-3.0-nz-_commons-43422495.png" style="height: 7%; width: 7%;" alt="yuriko.co.nz banner" height="574" width="147"></a></body>'
    #---------- <html> ----------
    html = '<!DOCTYPE html><html lang="en-US">' + head + body + '</html>'
    return {
        'statusCode': 200,
        'body': html,
        'headers': {
            'Content-Type': 'text/html; charset=UTF-8',
            'Server': 'Yuriko Special V12 ngin'
        }
    }

