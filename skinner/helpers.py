import os
import sys
import json
import time
import pprint
import requests
import argparse
import tempfile
import configparser
from mattermostdriver import Driver

def configs(section):
    param = {}
    config = configparser.ConfigParser()
    configPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
    config.read(configPath)
    options = config.options(section)
    for option in options:
        try:
            param[option] = config.get(section, option)
            if param[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("\033[31m[-]\x1b[0m " + "On Snap!, can't get the config %s!" % option)
            param[option] = None
    return param

def addTargetToScope(target, burpUrl, burpApiPort):
    try:
        r = requests.put(
                "{}:{}/burp/target/scope?url={}".format(
                    burpUrl,
                    burpApiPort,
                    target,
                    )
                )
        r.raise_for_status()
        targetStatus = targetIsInScope(target, burpUrl, burpApiPort)
        print("\033[32m[+]\x1b[0m " + "Updating Burp scope")
        return targetStatus
    except requests.exceptions.RequestException as e:
        print("\033[31m[-]\x1b[0m " + "Oh, Snap!, Can't add {} to scope: {}".format(target, e))
        sys.exit(1)

def removeTargetFromScope(target, burpUrl, burpApiPort):
    try:
        r = requests.delete(
                "{}:{}/burp/target/scope?url={}".format(
                    burpUrl,
                    burpApiPort,
                    target,
                    )
                )
        r.raise_for_status()
        targetStatus = targetIsInScope(target, burpUrl, burpApiPort)
        print("\033[32m[+]\x1b[0m " + "Removing {} from Burp scope".format(target))
        return targetStatus
    except requests.exceptions.RequestException as e:
        print("\033[31m[-]\x1b[0m " + "Oh, Snap!, Can't remove {} from scope: {}".format(target, e))
        sys.exit(1)

def targetIsInScope(target, burpUrl, burpApiPort):
    try:
        r = requests.get(
                "{}:{}/burp/target/scope?url={}".format(
                    burpUrl,
                    burpApiPort,
                    target,
                    )
                )
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("\033[31m[-]\x1b[0m " + "Oh, Snap!, Can't check scope status for {} : {}".format(target, e))
        sys.exit(1)
    else:
        res = r.json()
        if res['inScope']:
            return True
        else:
            return False

def startScan(target, burpUrl, burpApiPort):
    try:
        r = requests.post(
                "{}:{}/burp/scanner/scans/active?baseUrl={}".format(
                    burpUrl,
                    burpApiPort,
                    target,
                    )
                )
        r.raise_for_status()
        print("\033[32m[+]\x1b[0m " + "Starting scan for \033[32m{}\x1b[0m".format(target))
    except requests.exceptions.RequestException as e:
        print("\033[31m[-]\x1b[0m " + "Oh, Snap!, Can't start the scan for {} : {}".format(target, e))
        sys.exit(1)

def configStatus(burpUrl, burpApiPort):
    try:
        r = requests.get(
                "{}:{}/burp/configuration".format(
                    burpUrl,
                    burpApiPort,
                    )
                )
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("\033[31m[-]\x1b[0m " + "Oh Snap!, Can't fetch Burp configs: {}".format(e))
        sys.exit(1)
    else:
        config = r.json()
        running = config['proxy']['request_listeners'][0]['running']
        listenMode = config['proxy']['request_listeners'][0]['listen_mode']
        if running and listenMode == 'all_interfaces':
            return True
        else:
            return False

def configSet(burpUrl, burpApiPort, burpProxyPort):
    newConfig = {
        "proxy": {
            "request_listeners": [{
                "certificate_mode": "per_host",
                "listen_mode": "all_interfaces",
                "listener_port": burpProxyPort,
                "running": True,
                "support_invisible_proxying": True
            }]
        }
    }
    try:
        r = requests.put(
            "{}:{}/burp/configuration".format(
                burpUrl,
                burpApiPort
                ),
            data=json.dumps(newConfig)
        )
        r.raise_for_status()
        print("\033[32m[+]\x1b[0m " + "Burp Suite configured successfully")
        burpConfig = configStatus(burpUrl, burpApiPort)
        if burpConfig:
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        print("\033[31m[-]\x1b[0m " + "Oh Snap!, can't update Burp config: {}".format(e))
        sys.exit(1)

def sendRequest(burpUrl, burpProxyPort, target):
    proxy = {
            'http': '{}:{}'.format(burpUrl, burpProxyPort),
            'https': '{}:{}'.format(burpUrl, burpProxyPort),
            }
    try:
        r = requests.get(
                target,
                proxies = proxy
                )
        r.raise_for_status()
        print("\033[32m[+]\x1b[0m " + "Sending target http request to Burp for {}".format(target))
    except requests.exceptions.RequestException as e:
        print("\033[31m[-]\x1b[0m " + "Oh Snap!, can't send target http request to Burp for {}, {}".format(target, e))
        sys.exit(1)

def scanProgress(burpUrl, burpApiPort):
    try:
        r = requests.get(
                "{}:{}/burp/scanner/status".format(
                    burpUrl,
                    burpApiPort
                    )
                )
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("\033[31m[-]\x1b[0m " + "Oh Snap!, can't fetch the scanning progress from Burp: {}".format(e))
    else:
        prog = r.json()
        percent = prog['scanPercentage']
        progressBar(percent)
        return percent

def progressBar(count):
    barLen = 60
    filledLen = int(round(barLen * count / float(100)))
    percents = round(100.0 * count / float(100), 1)
    bar = '=' * filledLen + '-' * (barLen - filledLen)
    # sys.stdout.write('[%s] %s%s %s\r' % (bar, percents, '%', 'Scanning...')) #Gitlab CI web console problem with progressbar
    sys.stdout.write('%s%s ' % (percents, '%'))
    sys.stdout.flush()

def uploadGitlab(projectId, reportFile):
    gitlabUrl = configs("gitlab")['gitlaburl']
    gitlabToken = configs("gitlab")['gitlabtoken']
    reportFile = os.path.join(tempfile.gettempdir(), reportFile)

    try:
        r = requests.post(
                "{}/api/v4/projects/383/uploads".format(
                    gitlabUrl
                    ),
                headers = {'PRIVATE-TOKEN': gitlabToken},
                files = {'file': (reportFile, open(reportFile))}
            )
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("\033[31m[-]\x1b[0m " + "Oh Snap!, can't upload report file to Gitlab: {}".format(e))
        sys.exit(1)
    else:
        res = r.json()
        reportLink = res['markdown']
    return reportLink

def addGitlabIssue(projectId):
    gitlabUrl = configs("gitlab")['gitlaburl']
    gitlabToken = configs("gitlab")['gitlabtoken']

    for issue in criticalIssues:
        issueName = issue[0]
        issueDescription = issue[1]
        try:
            r = requests.post(
                    "{}/api/v4/projects/{}/issues?title={}&description={}&labels=security-test".format(
                        gitlabUrl,
                        projectId,
                        issueName,
                        issueDescription
                        ),
                    headers = {'PRIVATE-TOKEN': gitlabToken}
                )
            r.raise_for_status()
            print("\033[32m[+]\x1b[0m " + "Adding founded critical issues to gitlab")
        except requests.exceptions.RequestException as e:
            print("\033[31m[-]\x1b[0m " + "Oh Snap!, can't create new gitlab issue: {}".format(e))
            sys.exit(1)

def issues(burpUrl, burpApiPort, target, reportLink):
    try:
        r = requests.get(
                "{}:{}/burp/scanner/issues?urlPrefix={}".format(
                    burpUrl,
                    burpApiPort,
                    target
                    )
                )
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("\033[31m[-]\x1b[0m " + "Oh Snap!, can't fetch issues from burp: {}".format(e))
    else:
        res = r.json()
        issueList = []
        global criticalIssues
        criticalIssues = []

        for issue in res['issues']:
            if issue['severity'] == "High":
                issueDescription = ("URL: " + makeStr(issue['url']) + "<br />Severity: " +
                                    makeStr(issue['severity']) + "<br />Confidence: " +
                                    makeStr(issue['confidence']) + "<h2>Issue Background</h2>" +
                                    makeStr(issue['issueBackground']) + "<h2>Issue Detail</h2>" +
                                    makeStr(issue['issueDetail']) + "<h2>Remediation</h2>" +
                                    makeStr(issue['remediationBackground']) + makeStr(issue['remediationDetail']) +
                                    "<br />" + reportLink)
                criticalIssues.append([issue['issueName'], issueDescription])

        if res['issues']:
            print("\n\033[32m[+]\x1b[0m " + "List of issues:")
            eachIssue = {
                    "Issue: {issueName}, Severity: {severity}".format(**issue)
                    for issue in res['issues']
                }
            for issue in eachIssue:
                print('\033[93m' + "[!] {}".format(issue) + '\x1b[0m')
                issueList.append(issue)
        return issueList

def report(burpUrl, burpApiPort, reportType, target):
    try:
        r = requests.get(
                "{}:{}/burp/report?urlPrefix={}&reportType={}".format(
                    burpUrl,
                    burpApiPort,
                    target,
                    reportType
                    )
                )
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("\033[31m[-]\x1b[0m " + "Oh Snap!, can't fetch the report file from burp: {}".format(e))
    else:
        global reportFileName
        reportFileName = "security-report-{}-{}.{}".format(
                time.strftime("%Y%m%d-%H%M%S", time.localtime()),
                target.replace("://", "-"),
                reportType.lower()
                )
        reportFile = os.path.join(tempfile.gettempdir(), reportFileName)
        with open(reportFile, 'w') as f:
            f.write(r.text)
        return reportFile

def mattermost(reportFile, issueList, target):
    accessToken = configs("mattermost")['accesstoken']
    reportFile = os.path.join(tempfile.gettempdir(), reportFile)
    issueList = '\n'.join('{}: {}'.format(*k) for k in enumerate(issueList, 1))
    mmost = Driver({
        'url': 'mattermost.viidakko.fi',
        'token': accessToken,
        'scheme': 'https',
        'port': 443,
        'basepath': '/api/v4',
        'verify': True,
        'timeout': 30,
        # 'mfa_token': 'TheMfaToken'
        })
    mmost.login()
    channel_id = mmost.api['channels'].get_channel_by_name_and_team_name('development', 'burp-scan-reports')['id']
    file_id = mmost.api['files'].upload_file(
            channel_id = channel_id,
            files = {'files': (reportFile, open(reportFile))})['file_infos'][0]['id']

    mmost.api['posts'].create_post(options={
        'channel_id': channel_id,
        'message': ':bell: **Scan result for ' + target + '**\n' + issueList,
        'file_ids': [file_id]})
    print("\033[32m[+]\x1b[0m " + "Mattermost message sent, 'Burp Scan Report' channel, report file: \033[32m{}\x1b[0m".format(reportFileName))

def stopBurp(burpUrl, burpApiPort):
    try:
        r = requests.get(
                "{}:{}/burp/stop".format(
                    burpUrl,
                    burpApiPort,
                    )
                )
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("\033[31m[-]\x1b[0m " + "Oh Snap!, Can't stop Burp: {}".format(e))
        sys.exit(1)

def makeStr(string):
    if string is None:
        return ''
    return str(string)
