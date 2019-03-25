# -*- coding: utf-8 -*-
"""
                pinner
- get git info from need packages
- create new version of git repository where script was run
- create tag the same as version
- set new revision in config file
    revision is appropriate to git HEAD in specific package
- create or update change-log
- commit change-log
- commit tag
- push changes
"""

from __future__ import print_function
from time import gmtime, strftime
import getpass
import os
import re
import sys
from copy import deepcopy
import logging

from ConfigParser import ConfigParser
from StringIO import StringIO
from git import Repo, GitCommandError
import yaml
from yaml.parser import ParserError

CHANGE_LOG_PATH = 'profiles/sandbox_changelog.yaml'
SANDBOX_PATH = 'profiles/sandbox.cfg'
EA_VERSION = 'ea2-'

LOGGER = logging.getLogger(__name__)
LOG_HANDLER = logging.StreamHandler()
LOG_FORMATTER = logging.Formatter('%(levelname)s - %(message)s')
LOG_HANDLER.setFormatter(LOG_FORMATTER)
LOGGER.addHandler(LOG_HANDLER)
LOGGER.setLevel(logging.INFO)

ORIGIN_PWD = os.getcwd()

PATTERN_COMMIT_MESSAGE_REGEX = re.compile(r'[^a-zA-Z0-9/\n _]')
PATTERN_EA_VERSION = re.compile(r'({})'.format(EA_VERSION))
PATTERN_EA_VERSION_VALUE = re.compile(r'{}(.*)'.format(EA_VERSION))
PATTERN_REVISION_REGEX = re.compile(r'(rev=\w+)')


def get_current_rev(current_rev_str):
    """
    Get revision from string

    :Example:

    >>> get_current_rev('doc rev=12345')
    '12345'

    :param current_rev_str: whole string of git url info
    :type str:

    :rparam rev: found revision
    :rtype rev: str
    """
    rev = PATTERN_REVISION_REGEX.search(current_rev_str)
    return rev.group().split('=')[1]


def format_commits(commits):
    """
    Format commit representation

    :param commits: iterable of commit objects
    :type commits: ABC Iterable[Commit]

    :rparam commits: formated iterable of commit objects
    :rtype commits: ABC Iterable[Commit]
    """
    formated_commits = []
    formated_commit = {}

    for commit in commits:
        formated_commit['commit'] = commit.hexsha.encode()
        formated_commit['author'] = commit.author.name.encode()
        formated_commit['date'] = commit.authored_datetime.strftime("%Y-%m-%d %H:%M:%S").encode()
        try:
            message = PATTERN_COMMIT_MESSAGE_REGEX.sub('', commit.message.encode())
        except UnicodeEncodeError:
            message = ''
        message = [x.strip() for x in message.split('\n') if x]
        formated_commit['massage'] = message
        formated_commits.append(deepcopy(formated_commit))
    return formated_commits if formated_commits else None


def get_git_info(package):
    """
    Change directory where package located and get info

    :param package: package info
    :type package: tuple

    :rparam package: git info
    :rtype package: tuple
    """
    package_name = package[0]
    context = {}
    commits = []
    i = 0

    os.chdir(ORIGIN_PWD + '/src/' + package_name)
    repo = Repo('')
    head = repo.head.object.hexsha
    rev = get_current_rev(package[1])

    for i, commit in enumerate(repo.iter_commits()):
        if commit.hexsha == rev:
            break
        commits.append(commit)
    context['changes'] = format_commits(commits)
    LOGGER.info("In package '%s' is %d commits differents", package_name, i)
    return (context, head)


def inspect_packages(sandbox):
    """
    Create mapping package name to changes(commis) in this packages
    and create mapping package name to git HEAD
    :param sandbox: it is config object from loading file config (*.cfg)
    :type sandbox: ConfigParser

    :rparam : mapping package name to changes in this packages
    :rtype git_info: ABC MutableMapping
    :rparam : mapping package name to git HEAD
    :rtype new_heads: ABC MutableMapping
    """
    all_packages = sandbox.items('sources')
    git_info = {}
    new_heads = {}

    for package in all_packages:
        try:
            git_info[package[0]], head = get_git_info(package)
            new_heads[package[0]] = head
        except OSError:
            continue
    os.chdir(ORIGIN_PWD)
    return git_info, new_heads


def get_config(filename):
    """
    Get config object from file

    :param filename: config file
    :type filename: file

    :rparam config: it is config object from loading file config (*.cfg)
    :rtype config: ConfigParser
    """
    config = ConfigParser()
    config.read('profiles/{}.cfg'.format(filename))
    return config


def get_content(sandbox):
    """
    Get content from config, replace some errors

    :param sandox: it is config from loading file config (*.cfg)
    :type sandox: ConfigParser

    :rparam content: correct content of config file
    :rtype conent: str
    """
    buff = StringIO()
    sandbox.write(buff)
    content = buff.getvalue().replace('+ =', '+=').replace(' \n', '\n')
    buff.close()
    return content


def ver_incrementer(ver_chain, pos=-1):
    """
    Version incrementer
    It is complex function
    :Example:

    >>> ver_incrementer('1.2.3')
    ['1','2', '4']
    >>> ver_incrementer('1.2.99')
    ['1','3', '0']


    :param ver_chain: iterable of split value of version
    :type ver_chain: ABC Iterable
    :param pos: position what is need in call of function
    :type pos: int
    """
    if abs(pos) > len(ver_chain):
        return ver_chain.insert(0, 1)
    ver_chain[pos] = int(ver_chain[pos]) + 1
    if len(str(ver_chain[pos])) < 3:
        return [str(x) for x in ver_chain]
    ver_chain[pos] = 0
    ver_incrementer(ver_chain, pos-1)
    if pos == -1:
        return [str(x) for x in ver_chain]
    return None


def sort_func(version):
    """
    Sort func for versions

    :Example:

    >>> sort_func('1.2.3')
    [1, 2, 3]
    >>> sort_func('1.2.q')
    ValueError: invalid literal for int() with base 10: 'q'


    :param version: version of git repository
    :type version: str
    :rparam split_version: split version and transform to int
    :rparam split_version: ABC Iterable
    """
    return map(int, version.split('.'))


def get_last_version(tags):
    """
    Get last version of git repository where script run
    Check if version is correct relatively to version pattern

    :param tags: list of git tags
    :type version: str
    """
    tags = [x for x in tags if PATTERN_EA_VERSION.search(x)]
    if not tags:
        return None
    versions = [PATTERN_EA_VERSION_VALUE.search(x).groups()[0] for x in tags]
    if not versions:
        return None
    try:
        for i, version in enumerate(versions):
            map(int, version.split('.'))
        versions.sort(key=sort_func)
    except ValueError:
        LOGGER.warning("Invalid version style in versions, correct example"
                       " 0.0.7 please fix tag: %s",
                       versions[i])
        sys.exit(0)
    return versions[-1]


def get_new_version(repo):
    """
    Create new version of git repository where script run

    :param repo: instance of repository where was script run
    :type repo: git.Repo
    :rparam version: new version of git repository
    :rtype version: str
    """
    version = ''
    start_version = '2.5.1'
    if repo.tags:
        last_version = get_last_version([x.name for x in repo.tags])
    if not last_version:
        version = '{}{}'.format(EA_VERSION, start_version)
    else:
        version = ver_incrementer(last_version.split('.'))
        version = '{}{}'.format(EA_VERSION, '.'.join(version))
    return version


def get_change_log(file_handler):
    """
    Get change log file

    :param file_handler: change log file
    :type file_handler: file
    :rparam change_log: mapping of existing change log
    :type change_log: ABC MutableMapping
    """
    change_log = yaml.load(file_handler)
    file_handler.seek(0)
    if not change_log:
        change_log = {}
    return change_log


def get_change_log_header():
    """
    Create and return changes log header

    :rparam header: header fir change log file
    :type header: str
    """
    time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    user = getpass.getuser()
    header = "# Autogenerated at ({time}) by {user}\n"
    return header.format(time=time, user=user)


def make_change_log_greate_again(change_log, git_info, new_version):
    """
    Set correct change log without duplication and emply changes
    """
    changes = {package: changes for package, changes in git_info.items() if changes['changes']}
    if not changes:
        return (change_log, False)
    change_log['{}'.format(new_version)] = changes
    return (change_log, True)


def save_git_info(git_info, new_version):
    """
    Save git info(changes) to change log file

    :param git_info: is mapping name packages to changes(list of commits)
    :type git_info: ABC MutableMapping
    :param new_version: new version from which will be created tag
    :type new_version: str
    """
    mode = 'r+' if os.path.exists(CHANGE_LOG_PATH) else 'w+'
    try:
        with open(CHANGE_LOG_PATH, mode) as file_handler:
            change_log = get_change_log(file_handler)
            if new_version in change_log:
                LOGGER.warning("The version '%s' already exist in change log"
                               " file '%s'", new_version, CHANGE_LOG_PATH)
                sys.exit(0)
            change_log, change = make_change_log_greate_again(change_log,
                                                              git_info,
                                                              new_version)
            if not change:
                LOGGER.info("There were no changes in packages")
                sys.exit(0)
            file_handler.write(get_change_log_header())
            yaml.dump(change_log, file_handler, default_flow_style=False)
    except ParserError:
        LOGGER.warning("Error then parse yaml file '%s'", CHANGE_LOG_PATH)
        sys.exit(1)


def undo_git_changes(repo, new_version, forse=None):
    """
    Undo git changes
    Reset created commit, delete tags and force push

    :param repo: instance of repository where was script run
    :type repo: git.Repo
    :param new_version: new version from which will be created tag
    :type new_version: str
    :param forse: boolean if True make forse push
    :type forse: bool
    """

    try:
        LOGGER.info("Reset created commit")
        repo.head.reset('HEAD~1', index=True, working_tree=True)
        LOGGER.info("Commit: was reseted")
        LOGGER.info("Delete: created tag '%s'", new_version)
        repo.delete_tag(new_version)
        LOGGER.info("Tag: was deleted")
        if forse:
            LOGGER.info("Forse pushing for removing created "
                        "commit in remote repo")
            repo.git.push(force=True)
            LOGGER.info("Removed created commit in remote repo")
    except GitCommandError:
        pass


def git_push_obj(verbose, remote, obj=None):
    """
    Push given object to git

    :param obj: object wich will be pushed to git
    :type obj: any one implements the interface of pushing to git
    :rparam boolean: If success return True

    """
    try:
        LOGGER.info("%s: pushing to remote - %s", verbose, remote.name)
        if not obj:
            remote.push()
        else:
            remote.push(obj)
        LOGGER.info("%s: successfully pushed", verbose)
    except GitCommandError as err:
        LOGGER.warning("%s: was not pushed because %s", verbose,
                       err.stderr.split(':')[-1])
        return None
    return True


def ask_permission(question):
    """
    Asking for permisson, print prompt question
    y,yes: mean confirm
    n,not: mean reject
    """
    while True:
        said = raw_input("{} (y or n): ".format(question))
        if said in ("yes", "y"):
            return True
        if said in ("not", "n"):
            return False
        print("Please choose (y or n)")


def pin_indeed(repo, new_version):
    """
    Pin version
    Add file, create commit, create tag, push commit and tag

    :param repo: instance of repository where was script run
    :type repo: git.Repo
    :param new_version: new version from which will be created tag
    :type new_version: str
    """

    repo.index.add([CHANGE_LOG_PATH])
    repo.index.add([SANDBOX_PATH])

    try:
        if ask_permission("Do you want to create commit?"):
            commit = repo.index.commit(message='Pin new version: {}'.format(new_version))
            LOGGER.info("Commit: was successfully created")
            if ask_permission("Do you want to create tag '{}'?".format(new_version)):
                repo.create_tag(new_version, ref=commit, message="sandbox versions update")
                LOGGER.info("Tag: '%s' was successfully created", new_version)
    except GitCommandError as err:
        LOGGER.warning("%s", err.stderr.strip())
        return None
    return True


def save_new_rew(sandbox):
    """
    Save new revision to file

    :param sandox: it is config from loading file config (*.cfg)
    :type sandox: ConfigParser
    """

    buff = StringIO()
    sandbox.write(buff)
    content = buff.getvalue().replace('+ =', '+=').replace(' \n', '\n')
    try:
        with open(SANDBOX_PATH, 'w') as file_handler:
            LOGGER.info("Write to file '%s' changes", SANDBOX_PATH)
            file_handler.write(content)
    except IOError as err:
        LOGGER.warning("Can`t write to file '%s' because %s", SANDBOX_PATH,
                       err.strerror)
        sys.exit(1)


def set_new_rev(sandbox, new_heads):
    """
    Set new revision to change-log file

    :param sandox: it is config from loading file config (*.cfg)
    :type sandox: ConfigParser
    :param new_heads: it is mapping of new git HEAD in search packages
    :type new_heads: ABC MutableMapping
    """

    sources = sandbox.items('sources')
    for source in sources:
        for item in source:
            if PATTERN_REVISION_REGEX.search(item):
                item = PATTERN_REVISION_REGEX.sub('', item)
                item += 'rev={}'.format(new_heads[source[0]])
                sandbox.set('sources', source[0], item)
                LOGGER.info("Set new rev '%s' to '%s'", new_heads[source[0]],
                            source[0])
    save_new_rew(sandbox)


def main():
    """
    Main function in pinner

    directs sub-functions
    """
    buildout_repo = Repo('')
    sandbox = get_config("sandbox")

    git_info, new_heads = inspect_packages(sandbox)
    new_version = get_new_version(buildout_repo)
    save_git_info(git_info, new_version)
    set_new_rev(sandbox, new_heads)
    pin_indeed(buildout_repo, new_version)


if __name__ == '__main__':
    main()
