from pygithub3 import Github
from secrets import *

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

# ADD YOUR LIST OF NAMES HERE
# TODO: make this better, I'll set up argparse in v0.2 unless someone has a better idea
usernames = ["username1", "username2"]

gh = Github(login=USERNAME, password=PASSWORD)
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

for user in usernames:
	data = {
		  "name": user ,
		  "permission": "admin",
	}
	# Step 1 - add users to team 'privacyfans' if not already
	if user not in pf_names:
		gh.orgs.teams.add_member(TEAM_ID,user)
		print "Added: %s to 'privacyfans' team" % user
	else:
		print "%s already in team privacyfans" % user

	# Step 2 - create a team of the user's name if not already
	if user not in team_names:
		team = gh.orgs.teams.create(org, data)
		print "Created a team for %s in %s" % (user, org)
	else:
		print "Team %s already exists" % user

	# Step 3 - create a repo of the user's name if not already
	if user not in repo_names:
		gh.repos.create(dict(name=user, team_id=team.id, private=True, auto_init=True),
	    in_org=org)
		print "Created a repo for %s in %s" % (user, org)
	else:
		print "Repo %s already exists" % user

	# Add the member into the team
	gh.orgs.teams.add_member(team.id, user)
	print "Added %s to team %s" % (user,user)

print "\n== ALL DONE! =="
