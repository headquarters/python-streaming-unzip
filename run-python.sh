# Limit to 500MB tmpfs space, 0.5GB of RAM
docker run -it --mount type=tmpfs,destination=/usr/src/data,tmpfs-size=500000 -m 500m python-streams:latest /bin/bash

docker run -it -m 500m --mount type=tmpfs,destination=/usr/src/data,tmpfs-size=300000000 -v $PWD/src:/usr/src/mount -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION python-streams:latest /bin/bash

# 500000 => 492K
# 300000000 => 286MB