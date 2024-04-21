На основе этой статьи с сайта MinIO был сформирован используемый стек технологий (MinIO, Dremio, Nessie, Iceberg):
[Data Lake Mysteries Unveiled: Nessie, Dremio, and MinIO Make Waves](https://blog.min.io/uncover-data-lake-nessie-dremio-iceberg)

Данный стек продвигается как решение для создания Data LakeHouse на сайте Dremio:
[Open Source Innovation](https://www.dremio.com/open-source)

К статье прилагается ссылка на Docker Compose файл:
[docker-compose.yml](https://github.com/minio/blog-assets/blob/main/Iceberg-Dremio-Nessie/docker-compose.yml)

Так как в приложенном Docker Compose файле используется Nessie с использованием In-Memory Store для хранения метаданных, что неприемлемо для production, было принято решение заменить In-Memory Store на MongoDB, используя предложенный Nessie Docker Compose файл:
[docker-compose.yml](https://github.com/projectnessie/nessie/blob/main/docker/mongodb/docker-compose.yml)

Таким образом был сформирован Docker Compose файл:
[сompose.yaml](compose.yaml)
