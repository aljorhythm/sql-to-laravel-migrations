# Docker
echo "docker build"
docker build -f .github/actions/start-mysql/Dockerfile .
docker run -d -p 3306:3306 --name mysql -e MYSQL_ROOT_PASSWORD=password