# Derived from official mysql image (our base image)
FROM mysql

# Add a database
ENV MYSQL_DATABASE company

# Add the content of the sql-scripts/ directory to your image
# All scripts in docker-entrypoint-initdb.d/ are automatically
# executed during container startup
# COPY ./tests/data/sql_scripts/ /docker-entrypoint-initdb.d/

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY * /

# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT ["/test.sh"]