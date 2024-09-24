#!/bin/bash


POSTGRES_HOST="******"
POSTGRES_PORT="5432"
POSTGRES_DB="*****"
POSTGRES_USER="****"
POSTGRES_PASSWORD="****"
NUM_CONNECTIONS=30
IDLE_DURATION=600


export PGPASSWORD=$POSTGRES_PASSWORD


create_idle_connection() {
  psql -h $POSTGRES_HOST -p $POSTGRES_PORT -d $POSTGRES_DB -U $POSTGRES_USER -c "SELECT pg_sleep($IDLE_DURATION);" &
}


for i in $(seq 1 $NUM_CONNECTIONS); do
  create_idle_connection
  echo "Opened idle connection $i"
done

echo "All $NUM_CONNECTIONS idle connections created. They will remain idle for $IDLE_DURATION seconds."


wait

echo "All idle connections have completed."
