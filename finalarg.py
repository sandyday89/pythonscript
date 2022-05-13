import os
import argparse
import logging
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='directory', type=str,
                    help="This is the working directory")
    parser.add_argument(dest='oldcmurl', type=str,
                        help="old configmap url")
    parser.add_argument(dest='newcmurl', type=str,
                        help="new configmap url")
    parser.add_argument(dest='oldingressurl', type=str,
                        help="old ingress url or old secretname")
    parser.add_argument(dest='newingressurl', type=str,
                        help="new ingress url or new secretname")
    parser.add_argument(dest='oldsecret', type=str,
                        help="Old secretname")
    parser.add_argument(dest='newsecret', type=str,
                        help="New secretname")
    parser.add_argument('-v', '--verbose', action='store', choices=['info', 'debug'], default='info',
                        help="Set output verbosity")
    args = parser.parse_args()
    level = logging.INFO if args.verbose == 'info' else logging.DEBUG
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        stream=sys.stdout,level=level)
    logging.info("Working directory {0}".format(args.directory))
    logging.info("Old configmap URL: {0}".format(args.oldcmurl))
    logging.info("New configmap URL: {0}".format(args.newcmurl))
    logging.info("Old configmap URL: {0}".format(args.oldingressurl))
    logging.info("New configmap URL: {0}".format(args.newingressurl))
    logging.info("Old configmap URL: {0}".format(args.oldingressurl))
    logging.info("New configmap URL: {0}".format(args.newingressurl))
    logging.info("Old secretname: {0}".format(args.oldsecret))
    logging.info("New secretname: {0}".format(args.newsecret))

    for root, subdirectories, files in os.walk(args.directory):
        for file in files:
            if file == "configmap.yaml":
                with open(os.path.join(root, file), 'r') as f:
                    configmap = f.read()
                # Replace the target string configmap (old, new)
                configmap = configmap.replace(args.oldcmurl, args.newcmurl)
                with open(os.path.join(root, file), 'w') as f:
                    f.write(configmap)

            elif file == "service.yaml":
                with open(os.path.join(root, file), 'r') as f:
                    service = f.read()
                # Replace the target string ingress (old, new)
                service = service.replace(args.oldingressurl, args.newingressurl)
                service = service.replace(args.oldsecret, args.newsecret)
                with open(os.path.join(root, file), 'w') as f:
                    f.write(service)

if __name__ == '__main__':
    main()