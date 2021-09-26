APP_NAME=cyclemap
DOCKER_REPO_BASE=public.ecr.aws/o0s8a4l2
DOCKER_REPO=$(DOCKER_REPO_BASE)/$(APP_NAME)

# optional aws-cli options:
AWS_CLI_REGION=us-east-1  # AWS Public ECR requires auth in us-east-1
AWS_CLI_PROFILE=vdna

# get version from the versioneer
VERSION=$(shell python -c "import versioneer; print(versioneer.get_version())")
# Docker doesn't like the + sign in its tags, so replace it with '_'. See
# https://github.com/docker/distribution/issues/1201
VERSION_DOCKER=$(shell echo ${VERSION} | tr '+' '_')

# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help build

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help


clean: # Remove python packaging artifacts
	rm -rf build dist cyclemap.egg-info

wheel: clean # Package project into python wheel
	python setup.py bdist_wheel

build: wheel ## Build the container
	docker build --progress=plain -f Dockerfile -t $(APP_NAME) .

build-from-ci: ## Build the container in CI, using the image repo as a cache. Note: does not build the wheel
	docker pull ${DOCKER_REPO}:latest || true
	docker build --cache-from ${DOCKER_REPO}:latest --progress=plain -f Dockerfile -t $(APP_NAME) .

run: ## Run container
	docker run -it -p 8000:8000 $(APP_NAME)

# Docker publish
publish: repo-login publish-latest publish-version ## Publish the `{version}` and `latest` tagged containers to ECR

publish-latest: tag-latest ## Publish the `latest` taged container to ECR
	@echo 'publish latest to $(DOCKER_REPO)'
	docker push $(DOCKER_REPO):latest

publish-version: tag-version ## Publish the `{version}` taged container to ECR
	@echo 'publish $(VERSION_DOCKER) to $(DOCKER_REPO)'
	docker push $(DOCKER_REPO):$(VERSION_DOCKER)

# Docker tagging
tag: tag-latest tag-version ## Generate container tags for the `{version}` ans `latest` tags

tag-latest: ## Generate container `latest` tag
	@echo 'create tag latest'
	docker tag $(APP_NAME) $(DOCKER_REPO):latest

tag-version: ## Generate container `{version}` tag
	@echo 'create tag $(VERSION_DOCKER)'
	docker tag $(APP_NAME) $(DOCKER_REPO):$(VERSION_DOCKER)


# HELPERS

# generate script to login to aws docker repo
CMD_REPOLOGIN := "aws ecr-public get-login-password"
ifdef AWS_CLI_PROFILE
CMD_REPOLOGIN += " --profile $(AWS_CLI_PROFILE)"
endif
ifdef AWS_CLI_REGION
CMD_REPOLOGIN += " --region $(AWS_CLI_REGION)"
endif
CMD_REPOLOGIN += " | docker login "
CMD_REPOLOGIN += "--username AWS --password-stdin $(DOCKER_REPO_BASE)"

# login to AWS-ECR
repo-login: ## Auto login to AWS-ECR unsing aws-cli
	@echo $(CMD_REPOLOGIN)
	@eval $(CMD_REPOLOGIN)

version: ## Output the current version
	@echo $(VERSION)

docker-tag: ## Output the docker tag
	@echo $(VERSION_DOCKER)
