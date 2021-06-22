#! /bin/sh

branch=${GITHUB_REF##*/}

docker login -u $DOCKER_USER -p $DOCKER_PASS

if [ "${GITHUB_REF##*/}" == "production" ]; then
    TAG="latest"
else
    TAG="$branch"
fi

docker build -f Dockerfile -t $DOCKER_REPO:$TAG .
docker push $DOCKER_REPO:$TAG
