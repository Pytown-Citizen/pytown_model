# CI/CD
[![Development CI](https://github.com/Pytown-Citizen/pytown_model/actions/workflows/pythonapp.yml/badge.svg)](https://github.com/Pytown-Citizen/pytown_model/actions/workflows/pythonapp.yml)

# Sonarqube
To generate sonarqube report :
* Checkout main branch
* type <code>sonar-scanner.bat -D"sonar.projectKey=pytown_model_key" -D"sonar.sources=." -D"sonar.host.url=http://192.168.1.4:9000" -D"sonar.login=34da40ed62d88b941aea69dc5f6fb1c790426cd7"</code>
into powershell at the same level as this README.md.
Don't push on another branch as the community version doesn't handle multiple branch scan.