# Requirements:
ansible => 2.9
tar 

## Run:
1. Verify the `inventory.yaml` file. Group `[druid]` must consist your target host.
2. Setup nginx in `playbook.yaml:vars.nginx_servers`

# Install druid first time:
Run in `ansible/` directory
`ansible-playbook playbook.yaml -i inventory.yaml  --tags druid -K`

# Only update code and restart druid:
Run in `ansible/` directory
`ansible-playbook playbook.yaml -i inventory.yaml --tags update_code -K`

# Install superset:
Run in `ansible/` directory
`ansible-playbook playbook.yaml -i inventory.yaml --tags superset -K`

# Install Jenkins:
Run in `ansible/` directory
`ansible-playbook playbook.yaml -i inventory.yaml --tags jenkins -K`

# Important notes:

## Environment file
1. The repo have `druid/templates/environment`file, which contains some variables. The list of such variables and how they really works see in
https://druid.apache.org/docs/latest/tutorials/docker.html#configuration 
2. To apply the changes of the file you must run build in jenkins (to fetch newer version of repo) and after that run `docker-compose restart` manually on a host

## View logs
For single service `docker logs SERVICE_NAME`
For all services `docker-compose logs`
To show only last N stringsof log you can add `--tail=N` to both commands
In case you want to stay and recieve logs in real-time, please, add `-f` flag to command
To see all errors in real time for all the services executte `docker-compose --tail=20 -f | grep -i error`

# Superset
In `ansible/superset/templates/incubator-superset` you can find a full copy of https://github.com/apache/incubator-superset/tree/master/superset. 
The only thing modified is `docker-compose.yml`, so for update it you need to pull newer version of superset-repository, replace the `docker-compose.yml` and push it to master or run `docker-compose build && docker-compose up -d` locally (in case you want to run it onyour machine) .
