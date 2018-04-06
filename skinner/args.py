import argparse
from skinner.__init__ import version

def cli():
    arg = argparse.ArgumentParser(
            epilog = "Basic usage from Gitlab CI pipeline: \
                    python3 ./skinner/main.py -b http://burp.intra -u \
                    http://deploy.intra -sU selenium.intra -id $CI_PROJECT_ID",
        )
    arg.add_argument(
            '-v', '--version',
            action = 'version',
            version = "Skinner version " + version,
            help = 'Installed version of the Skinner script',
    )
    arg.add_argument(
            '-b', '--burp',
            type = str,
            required = True,
            help = 'Burp API base address, e.g. http://burp.intra',
    )
    arg.add_argument(
            '-u', '--url',
            type = str,
            help = 'The address of target for scan via Burp Pro, e.g. http://app.intra',
    )
    arg.add_argument(
            '-r', '--report',
            type = str,
            default = 'mattermost',
            choices = ['mattermost', 'database', 'all'],
            help = 'Ways of storing Burp scan report, Default is Mattermost',
    )
    arg.add_argument(
            '-t', '--type',
            type = str,
            default = 'html',
            choices = ['html', 'xml'],
            help = 'Burp report file type, Default is HTML',
    )
    arg.add_argument(
            '-p', '--burp-proxy-port',
            type = str,
            default = 8080,
            help = 'Burp proxy port, default is 8080'
    )
    arg.add_argument(
            '-a', '--burp-api-port',
            type = str,
            default = 8090,
            help = 'Burp API port, default is 9080'
    )
    arg.add_argument(
            '-sU', '--selenium-url',
            type = str,
            help = 'Selenium URL for generating traffic to Burp, e.g. http://selenium.intra'
    )
    arg.add_argument(
            '-sP', '--selenium-port',
            type = str,
            default = 4444,
            help = 'Selenium webdriver port, default is 4444'
    )
    arg.add_argument(
            '-id', '--project-id',
            type = str,
            help = 'Gitlab Project ID, Gitlab ci variable is $CI_PROJECT_ID'
    )
    return arg.parse_args()
