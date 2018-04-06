from skinner.__init__ import banner
import sys
import time
import skinner.args as args
import skinner.helpers as helpers
# import traffic

def main():
    cmd = args.cli()
    burpUrl = cmd.burp
    target = cmd.url
    burpApiPort = cmd.burp_api_port
    burpProxyPort = cmd.burp_proxy_port
    reportType = cmd.type.upper()
    seleniumUrl = cmd.selenium_url
    seleniumPort = cmd.selenium_port
    projectId = cmd.project_id

    burpConfig = helpers.configStatus(burpUrl, burpApiPort)

    if burpConfig is False:
        helpers.configSet(burpUrl, burpApiPort, burpProxyPort)

    # httpReq = helpers.sendRequest(burpUrl, burpProxyPort, target)
    # traffic.appLogin(burpUrl, burpProxyPort, seleniumUrl, seleniumPort, target)

    if target is not None:
        targetStatus = helpers.targetIsInScope(target, burpUrl, burpApiPort)

        if targetStatus is False:
            helpers.addTargetToScope(target, burpUrl, burpApiPort)

        helpers.startScan(target, burpUrl, burpApiPort)

        while helpers.scanProgress(burpUrl, burpApiPort) <= 96:
            time.sleep(20)

        reportFile = helpers.report(burpUrl, burpApiPort, reportType, target)
        reportLink = helpers.uploadGitlab(projectId, reportFile)
        issueList = helpers.issues(burpUrl, burpApiPort, target, reportLink)
        helpers.addGitlabIssue(projectId)
        helpers.mattermost(reportFile, issueList, target)
        # helpers.stopBurp(burpUrl, burpApiPort)

if __name__ == '__main__':
    print(banner)
    main()
