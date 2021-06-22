#! /bin/sh

branch=${GITHUB_REF##*/}

docker login -u $DOCKER_USER -p $DOCKER_PASS

TAG="hahah"
docker build -f Dockerfile -t $DOCKER_REPO:$TAG .
docker push $DOCKER_REPO:$TAG

# if [ "${GITHUB_REF##*/}" = "production" ]; then
#     TAG="latest"
#     docker build -f Dockerfile -t $DOCKER_REPO:$TAG .
#     docker push $DOCKER_REPO:$TAG
# fi
