CONTAINER=fastapi

if [[ -n $1 ]]; then
	CONTAINER=$1
fi	
echo $CONTAINER		

docker stop $CONTAINER && docker rm $CONTAINER

