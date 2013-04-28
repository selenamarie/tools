from pygithub3 import Github

try:
    from secrets import *
except:
    print "Need to specify secrets! Try giving your username and password."

import argparse

"""
 README

* Install https://github.com/copitux/python-github3
   'pip install pygithub3'
* Create a secrets.py file with the following:
	USERNAME="you"  # must be an AI owner to run this script
	PASSWORD="sekrit"
	TEAM_ID=393250  # privacyfans
	OWNERS=360990	# owners team id
	ORG="AdaInitiative"
"""

def create_config(args):

    f = open('secrets.py', 'w')
    f.write("""
USERNAME="%s"  # must be an AI owner to run this script
PASSWORD="%s"
TEAM_ID=393250  # privacyfans
OWNERS=360990	# owners team id
ORG="AdaInitiative"
""" % (args.username, args.password))
    f.close()
    print "Created your secrets.py file"

def connect():
    gh = Github(login=USERNAME, password=PASSWORD)
    return gh

def list_repos():
    gh = connect()
    org = ORG
    existing_teams = gh.orgs.teams.list(org).all()
    for team in existing_teams:
        print team.name

def getTeamID(teams, name):
    for team in teams:
        if team.name == name:
            return team

def create_repos(args):
    usernames = args.newaccounts

    gh = connect()
    org = ORG

    team_names = []
    pf_names = []
    repo_names = []

    existing_teams = gh.orgs.teams.list(org).all()
    for team in existing_teams:
        team_names.append(str(team.name))

    privacyfans = gh.orgs.teams.list_members(TEAM_ID).all()
    for p in privacyfans:
        pf_names.append(str(p.login))

    repos = gh.orgs.teams.list_repos(OWNERS).all()
    for r in repos:
        repo_names.append(str(r.name))

    for username in usernames:
        # Step 0 - check that user account exists
        try:
            user = gh.users.get(username.lower())

            data = {
                  "name": user.login,
                  "permission": "push",
            }

            # Step 1 - add users to team 'privacyfans' if not already
            if user.login not in pf_names:
                gh.orgs.teams.add_member(TEAM_ID,user.login)
                print "Step 1/4 complete: added %s to 'privacyfans' team" % user.login
            else:
                print "Step 1/4 skipped: %s already in team privacyfans" % user.login

            # Step 2 - create a team of the user's name if not already
            if user.login not in team_names:
                team = gh.orgs.teams.create(org, data)
                print "Step 2/4 complete: created a team for %s in %s" % (user.login, org)
            else:
                team = getTeamID(existing_teams,user.login)
                print "Step 2/4 skipped: team %s already exists (id: %s)" % (user.login, team.id)

            # Step 3 - create a repo of the user's name if not already
            if user.login not in repo_names:
                gh.repos.create(dict(name=user.login, team_id=team.id, private=True, auto_init=True),
                in_org=org)
                print "Step 3/4 complete: created a repo for %s in %s" % (user.login, org)
            else:
                print "Step 3/4 skipped: repo %s already exists" % user.login

            team_members = gh.orgs.teams.list_members(team.id).all()
            member_names = []
            for m in team_members:
                member_names.append(str(m.login))
            # Add the member into the team if not already
            if user.login not in member_names:
                gh.orgs.teams.add_member(team.id, user.login)
                print "Step 4/4 complete: added %s to team '%s'" % (user.login, team.name)
            else:
                print "Step 4/4 skipped: %s already in team %s" % (user.login, team.name)
        except Exception as e:
            if "User does not exist" in e.message:
                print "User %s does not exist, skipping" % username
            elif "team exists" in e.message:
                print "%s already has team" % username
            else:
                print e.message

def prompt(args):
    usernames = []
    print "Please give usernames, one username per line. Hit return when done."

    name = None
    while name != '':
        name = raw_input('Username: ')
        name != '' and usernames.append(name)

    print "Adding users: " + ' '.join(usernames)
    args.newaccounts = usernames
    return args

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add a repo to git')
    parser.add_argument('--prompt', action='store_true',
                       help='prompt for new account username(s) you are adding a private repo for')
    parser.add_argument('-n', '--newaccounts', nargs='+', dest='newaccounts',
                       help='new account username(s) you are adding a private repo for')
    parser.add_argument('-u', '--username', dest='username',
                       help='your github username')
    parser.add_argument('-p', '--password', dest='password',
                       help='your github password')
    parser.add_argument('--list-repos', action='store_true', dest='list_repos',
                       help='list existing repos')

    args,other = parser.parse_known_args()

    if args.username and args.password:
        create_config(args)
    elif args.newaccounts:
        create_repos(args)
    elif args.prompt:
        args = prompt(args)
        create_repos(args)
    elif args.list_repos:
        list_repos()
    else:
        print "Nothing to do!"

    print "\n== ALL DONE! =="
