docker run \
   -p 9000:9000 \
   -p 9001:9001 \
   --name minio1 \
   -v D:\minio\data:/data \
   -e "MINIO_ROOT_USER=ROOTUSER" \
   -e "MINIO_ROOT_PASSWORD=CHANGEME123" \
   quay.io/minio/minio server /data --console-address ":9001"