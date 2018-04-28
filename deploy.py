#!/usr/bin/python

# deploy.py
# Example portainer deployment script

import yaml
import requests
import json
import argparse

# Setup argument parser to get arguments
parser = argparse.ArgumentParser(description='DockStudios Deployment')
parser.add_argument('--stack-name', dest='stack_name', help='Stack Name', required=True)
parser.add_argument('--tag-parameter', dest='tag_parameter', help='Comma-separated keys to reach docker image in docker-compose, e.g. services,web,image', required=True)
parser.add_argument('--deploy-version', dest='deploy_version', help='Docker image to be deployed', required=True)

args = parser.parse_args()

print 'Stack name: %s' % args.stack_name
print 'Tag Parameter: %s' % args.tag_parameter

# Load configuration from config file
with open('credentials.yaml', 'r') as config_fh:
    config = yaml.load(config_fh.read())

# Authenticate to portainer
auth_res = requests.post(
    "%s/api/auth" % config['host'],
    data=json.dumps({'Username': config['username'],
                     'Password': config['password']})
)

# Ensure correctly authenticated
if auth_res.status_code != 200:
    raise Exception('Authentication error: %s' % auth_res.status_code)

# Get authentication token from authentication request
auth_token = auth_res.json()['jwt']
auth_header = {'Authorization': 'Bearer %s' % auth_token}

# Get list of endpoints and get ID of endpoint to deploy to
endpoints_res = requests.get('%s/api/endpoints' % config['host'], headers=auth_header)
endpoint_id = None
for endpoint in endpoints_res.json():
    if endpoint['Name'] == config['endpoint']:
        endpoint_id = endpoint['Id']

if endpoint_id is None:
    raise Exception('Could not find endpoint')
print 'Endpoint Id: %s' % endpoint_id

# Get list of stacks to get stack ID for stack to deploy to
stack_id = None
for stack_config in requests.get('%s/api/endpoints/%s/stacks' % (config['host'], endpoint_id), headers=auth_header).json():
    if stack_config['Name'] == args.stack_name:
        stack_id = stack_config['Id']

if stack_id is None:
    raise Exception('Could not find sepcified stack')
print 'Stack Id: %s' % stack_id

stackfile = requests.get('%s/api/endpoints/%s/stacks/%s/stackfile' % (config['host'], endpoint_id, stack_id), headers=auth_header).json()
docker_compose_original = stackfile['StackFileContent']
docker_compose = yaml.load(docker_compose_original)

sub_config = docker_compose
for config_key in args.tag_parameter.split(',')[0:-1]:
    sub_config = sub_config[config_key]

old_version = sub_config[args.tag_parameter.split(',')[-1]]
print 'Old version: %s' % old_version
print 'New version: %s' % args.deploy_version

if old_version == args.deploy_version:
    raise Exception('No change in version number')

sub_config[args.tag_parameter.split(',')[-1]] = args.deploy_version

update_res = requests.put('%s/api/endpoints/%s/stacks/%s' % (config['host'], endpoint_id, stack_id),
                          data=json.dumps({'StackFileContent': yaml.dump(docker_compose)}),
                          headers=auth_header)

if update_res.status_code == 200:
    print 'Successfully deployed new version'
else:
    raise Exception('Failed to update version: %s' % update_res.status_code)

