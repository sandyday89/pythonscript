
import argparse
import logging
import os
import re
import sys
import subprocess
import typing
import xml.etree.ElementTree as ET

# pylint: disable=C0103,W0702,W1202,C0200
# SVN Command
svn = ["svn", "--non-interactive", "--username", "jenkins", "--password", os.getenv('password')]
# Want to show the executing commands in output with no credentials
svn_log = ["svn", "--non-interactive"]

def execute_SVN_command(commands: typing.List[str]) -> str:
    """ This function will execute the svn commands
    Arguments:
    commands -- [List] contains list of subcommands, eg: 'status'
    """
    svn_command = svn + commands
    # Ignoring Credentials to display in log file
    svn_command_log = svn_log + commands
    logging.info(svn_command_log)
    try:
        cmd = subprocess.run(svn_command, stdout=subprocess.PIPE, check=True, text=True)
        logging.info(cmd.stdout)
        return cmd.stdout
    except:
        logging.error("Exception Occured", exc_info=True)
        sys.exit(-1)

def check_for_conflict(xml):
    """ This function will parse the output of status xml string and check for message conflicted.
        Example:
        .....
        <entry  path="/var/lib/****/workspace/SVNJigoMerge-Sync/touch.txt">
            <wc-status item="conflicted" revision="135" props="none">
               <commit revision="135">
                   <author>dramaraj</author>
                   <date>2021-03-02T17:02:16.690529Z</date>
                </commit>
            </wc-status>
        </entry>
        .......
    """
    root = ET.fromstring(xml)

    if 'wc-status' in [elem.tag for elem in root.iter()]:
        for entry in root.findall("target/entry"):
            logging.debug("Entry Attribute {0}".format(entry.attrib))
            logging.debug("Entry Childrens {0}".format(list(entry.getchildren())))
            modified_path = entry.attrib
            for wcstatus in list(entry.getchildren()):
                logging.debug("wcstatus Attribute {0}".format(
                    wcstatus.attrib))
                logging.debug("wcstatus Childrens {0}".format(list(
                    wcstatus.getchildren())))
                if wcstatus.attrib['item'] == 'conflicted':
                    author = wcstatus.find('commit/author').text
                    logging.info("Conflict occured for file: {0}, author: {1}".format(
                        modified_path,author))
                    return True

    return False

def get_jira_id(xml):
    """ This function will search for "MD-xxxx" string in revision logs
        <log>
            <logentry
               revision="60310">
               <author>dfaulkner</author>
               <date>2021-05-06T19:59:06.378393Z</date>
               <msg>MD-13893 Merged revision(s) 59473 from branches/Feature/Transformers:
                Prevent LoanComplete Data Extraction on Old Images
            ....
    """
    root = ET.fromstring(xml)
    msg = root.find("logentry/msg").text

    #return re.findall(r"JIRA-\d+", msg) Having this line for running demo project
    return re.findall(r"MD-\d+", msg)


if __name__ == "__main__":
    #Create the parser and add Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='workingRepo', type=str,
                        help="This is the working copy where merge has to happen Eg:feature Branch")
    parser.add_argument(dest='fromBranch', type=str,
                        help="This is the repo where changes are taken to sync Eg: Trunk")
    parser.add_argument(dest='url', type=str, help="Please provide the repo URL")
    parser.add_argument('-v', '--verbose', action='store', choices=['info', 'debug'], default='info',
                        help="Set output verbosity")

    args = parser.parse_args()
    working_repo_url = f"{args.url}/{args.workingRepo}"
    merging_repo_url = f"{args.url}/{args.fromBranch}"
    working_copy = os.path.join(os.environ.get('PWD'), '.')

    # Logging configuration, flushing console output to standard output
    level = logging.INFO if args.verbose == 'info' else logging.DEBUG
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        stream=sys.stdout,level=level)

    print("*" * 70)
    logging.info("Team Branch: URL {0}".format(working_repo_url))
    logging.info("Trunk URL: {0}".format(merging_repo_url))
    logging.info("Checking out code from {}".format(working_repo_url))
    execute_SVN_command(["co", working_repo_url, os.environ.get('PWD')])
    logging.info("Team Branch: URL {0}".format(working_repo_url))
    logging.info("Trunk URL: {0}".format(merging_repo_url))

    logging.info("Revert and update the repository")
    execute_SVN_command(["revert", "-R", working_copy])
    execute_SVN_command(["update", working_copy])

    logging.info(
        "Checking the SVN status command to make sure no other changes are present at this moment")
    execute_SVN_command(["status", "--xml", working_copy])

    logging.info(
        "Executing SVN Mergeinfo command to check the available changes in %s", merging_repo_url)
    ret = execute_SVN_command(
        ["mergeinfo", "--show-revs", "eligible", merging_repo_url, working_copy])

    #If return value is empty then it means trunk and Feature branch are already in Sync
    if ret == "":
        print("Nothing to Sync for the repos you have chosen")
        print("-" * 70)
    else:
        is_conflict = False
        logging.info("Below revisions are available for Sync")
        num_of_revisions = ret.split("\n")[:-1]
        logging.info(num_of_revisions)
        jira_ids = []
        for revision in range(len(num_of_revisions)):
            logging.info("Handling %s", revision)
            ret = execute_SVN_command(
                    ["log", "--xml", "-r", num_of_revisions[revision].lstrip('r'), merging_repo_url])
            jira_ids.extend(get_jira_id(ret))
            for recrevision in range(revision+1):
                execute_SVN_command(
                    ["--accept", "postpone", "merge", '-c',
                    num_of_revisions[recrevision].lstrip('r'), merging_repo_url])
            ret = execute_SVN_command(["status", "--xml", working_copy])
            if not check_for_conflict(ret):
                logging.info("No Conflict for revision {0}".format(num_of_revisions[revision]))
                execute_SVN_command(["revert", "-R", working_copy])
                execute_SVN_command(["update", working_copy])
                execute_SVN_command(["status", "--xml", working_copy])
            else:
                logging.error("Conflict is there for revision {0}".format(num_of_revisions[revision]))
                is_conflict = True
                break

        if not is_conflict:
            # So far no conflict and ready to sync all the changes
            for revision in num_of_revisions:
                execute_SVN_command(
                    ["--accept", "postpone", "merge", '-c',
                    revision.lstrip('r'), merging_repo_url])

            logging.info("Time to commit all changes")
            execute_SVN_command(["status", "--xml", working_copy])
            #Formatting commit messages
            commit_message = "Jenkins Merge Commit: "
            commit_message += ", ".join(jira_ids) if jira_ids else "JIRA-01"

            #print(commit_message)
            print(jira_ids)
            execute_SVN_command(["commit", "-m", commit_message])
            execute_SVN_command(["status", "--xml", working_copy])
            print("Sync Completed")
            print("-" * 70)
        elif not is_conflict and ret == "":
            print("Completed. Nothing to Sync for the repos you have chosen")
            print("-" * 70)
        else:
            print("Request you to resolve conflict and resync this branch")
            print("-" * 70)
            sys.exit(-1)