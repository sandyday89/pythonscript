import os
import sys
import subprocess

#Constants
#repoURL = "https://bitbucket.ilendx/scm/flux"
import yaml

pwd = "./test"
uatDB = "credo-uat6-2.chduqfuaxvap.us-east-2.rds.amazonaws.com"
prodDB = "credo-prod6.cc5z9bpskbmx.us-west-2.rds.amazonaws.com"
branchName = "test-branch"
uatHost = ".apps-uat.ilendx.tech"
prodHost = ".apps.ilendx.tech"
uatSecrets = ".uat6-apps-tls"
prodSecrets = ".apps-tls"

if __name__ == "__main__":
    #Create the parser and add Arguments
    # parser = argparse.ArgumentParser()
    # parser.add_argument(dest="fiName", type=str,
    #                     help="This is name of the FI example:bnb")
    # parser.add_argument(dest="fromFi", type=str,
    #                     help="This is source repo where we need to copy the FI Example: uat6")
    # parser.add_argument(dest="toFi", type=str, help="This is destination repo where we need to paste the FI example: uat6")
    # args = parser.parse_args()
    # print(args)
    # print(args.fiName)
    # print(args.fromFi)
    # print(args.toFi)

    # Logic starts from here
    # Clone the required repo
    # sys.stdout.flush()
    # subprocess.call(f"git clone {repoURL}/{args.fromFi}.git", shell=True)
    # subprocess.call(f"git clone {repoURL}/{args.toFi}.git", shell=True)
    # os.chdir(f"{args.toFi}")
    # cwd = os.getcwd()
    # print(f"Current working directory is: {cwd}")
    # print(f"Before branch creation")
    # sys.stdout.flush()
    #create branch
    # subprocess.call(f"git checkout -b {branchName}", shell=True)
    # print(f"After branch creation")

    #copy the FI directory from FromFI repo to this branch
    # subprocess.call([f"cp -r {pwd}/{args.fromFi}/{args.fiName} /Users/dramaraj/Documents/Dinesh/Fiserv/Director_Flex/FI-Automation"], shell=True)

    #Get into the copied directory
    #below 2 lines need to be deleted
    # currpwd = "/Users/dramaraj/Documents/Dinesh/Fiserv/Director_Flex/FI-Automation/uat6/grovebancorp"

    #Config Map changes
    for root, subdirectories, files in os.walk(pwd):
        for file in files:
            if file == "configmap.yaml":
                with open(os.path.join(root, file), 'r') as f:
                    configmaplines = f.readlines()

                with open(os.path.join(root, file), 'w') as f:
                    for line in configmaplines:
                        if prodDB in line:
                            line = line.replace(prodDB, uatDB)
                            f.write(line)
                        # Remove line if password exists
                        elif line.find("password") != -1:
                            pass
                        else:
                            f.write(line)

            elif file == "service.yaml":
                 with open(os.path.join(root, file), 'r') as f:
                     servicelines = f.readlines()

                 with open(os.path.join(root, file), 'w') as f:
                     for line in servicelines:
                         # Replace the target string in ingress host(hosts) to the uat(old, new)
                         if prodHost in line:
                            line = line.replace(prodHost, uatHost)
                            f.write(line)
                         # Replace the target string in ingress secrets to the uat(old, new)
                         elif prodSecrets in line:
                             line = line.replace(prodSecrets, uatSecrets)
                             f.write(line)
                         # Remove line if whitelist-source-range exists
                         elif line.find("whitelist-source-range") != -1:
                            pass
                         else:
                            f.write(line)
