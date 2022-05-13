import os

directory = "./testdir"

def main():
    for root, subdirectories, files in os.walk(directory):
        for file in files:
            if file == "configmap.yaml":
                with open(os.path.join(root, file), 'r') as f:
                    configmap = f.read()
                # Replace the target string configmap (old, new)
                configmap = configmap.replace("credo-qa6cu2erc2h999b.us-east-1.rds.amazonaws.com", "new-credo-dev6cu2erc2h999b.us-east-1.rds.amazonaws.com")
                configmap = configmap.replace("spring.datasource.password=${SECRETS_ACCOUNTS_PASSWD:bnb}",'')
                with open(os.path.join(root, file), 'w') as f:
                    f.write(configmap)

            elif file == "service.yaml":
                with open(os.path.join(root, file), 'r') as f:
                    service = f.read()
                # Replace the target string ingress (old, new)
                service = service.replace("alliancecu.apps.ilendx.tech", "new-alliancecu.apps.ilendx.tech")
                service = service.replace("alliancecu-master-ui.ilendx.apps-tls", "new-alliancecu-master-ui.ilendx.apps-tls")
                with open(os.path.join(root, file), 'w') as f:
                    f.write(service)

if __name__ == '__main__':
    main()