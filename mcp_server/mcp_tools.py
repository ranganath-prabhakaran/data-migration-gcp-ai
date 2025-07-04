import pymysql
import subprocess
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SecretManager:
    """A mock or real class to fetch secrets."""
    def __init__(self, project_id):
        # In a real scenario, this would initialize the GCP client
        # from google.cloud import secretmanager
        # self.client = secretmanager.SecretManagerServiceClient()
        self.project_id = project_id
        # For local testing, we can use env vars, but the GCE instance will use its service account
        self.secrets = {
            "source-db-host": os.environ.get("SOURCE_DB_HOST", "127.0.0.1"),
            "source-db-user": os.environ.get("SOURCE_DB_USER", "root"),
            "source-db-password": os.environ.get("SOURCE_DB_PASSWORD", "password"),
            "source-db-name": os.environ.get("SOURCE_DB_NAME", "employees"),
        }

    def get_secret(self, secret_id):
        # In a real scenario:
        # name = f"projects/{self.project_id}/secrets/{secret_id}/versions/latest"
        # response = self.client.access_secret_version(request={"name": name})
        # return response.payload.data.decode("UTF-8")
        return self.secrets.get(secret_id, "")

class MySQLTools:
    def __init__(self, project_id):
        self.secret_manager = SecretManager(project_id)
        self.db_config = None

    def _get_db_connection(self):
        if not self.db_config:
            self.db_config = {
                'host': self.secret_manager.get_secret("source-db-host"),
                'user': self.secret_manager.get_secret("source-db-user"),
                'password': self.secret_manager.get_secret("source-db-password"),
                'database': self.secret_manager.get_secret("source-db-name"),
                'cursorclass': pymysql.cursors.DictCursor
            }
        try:
            connection = pymysql.connect(**self.db_config)
            return connection
        except pymysql.MySQLError as e:
            logging.error(f"Database connection failed: {e}")
            raise

    def get_db_metadata(self) -> dict:
        """Retrieves metadata about the source database."""
        db_name = self.secret_manager.get_secret("source-db-name")
        query = f"""
            SELECT table_schema AS 'database_name',
            SUM(data_length + index_length) / 1024 / 1024 / 1024 AS 'db_size_gb'
            FROM information_schema.TABLES
            WHERE table_schema = '{db_name}'
            GROUP BY table_schema;
        """
        tables_query = f"SHOW TABLES IN {db_name};"
        version_query = "SELECT VERSION();"

        with self._get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                size_result = cursor.fetchone()
                
                cursor.execute(tables_query)
                tables_result = cursor.fetchall()
                tables = [list(row.values()) for row in tables_result]

                cursor.execute(version_query)
                version_result = cursor.fetchone()

        return {
            "db_name": db_name,
            "db_size_gb": float(size_result['db_size_gb']) if size_result else 0.0,
            "tables": tables,
            "mysql_version": version_result if version_result else "Unknown"
        }

    def get_table_schema(self, table_name: str) -> list:
        """Gets the schema for a specific table."""
        if not table_name.isalnum(): # Basic sanitization
            raise ValueError("Invalid table name")
        query = f"DESCRIBE {table_name};"
        with self._get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()

    def get_table_row_count(self, table_name: str) -> int:
        """Gets the row count for a specific table."""
        if not table_name.isalnum():
            raise ValueError("Invalid table name")
        query = f"SELECT COUNT(*) as count FROM {table_name};"
        with self._get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                return result['count'] if result else 0

    def run_checksum(self, table_name: str) -> int:
        """Runs CHECKSUM TABLE on a specific table."""
        if not table_name.isalnum():
            raise ValueError("Invalid table name")
        query = f"CHECKSUM TABLE {table_name};"
        with self._get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
                return result['Checksum'] if result else 0
    
    def run_gcs_dump(self, database_name: str, table_name: str, gcs_bucket: str, gcs_path: str) -> str:
        """Dumps a table using mysqldump and streams it to GCS."""
        if not all(s.isalnum() or s in ['-', '_'] for s in [database_name, table_name, gcs_bucket]):
             raise ValueError("Invalid input parameters.")

        db_conf = self._get_db_connection().get_config()
        gcs_uri = f"gs://{gcs_bucket}/{gcs_path}/{table_name}.sql"
        
        mysqldump_cmd = [
            "mysqldump",
            f"--host={db_conf['host']}",
            f"--user={db_conf['user']}",
            f"--password={db_conf['password']}",
            database_name,
            table_name
        ]
        gsutil_cmd = ["gsutil", "cp", "-", gcs_uri]

        try:
            logging.info(f"Dumping {table_name} to {gcs_uri}...")
            p1 = subprocess.Popen(mysqldump_cmd, stdout=subprocess.PIPE)
            p2 = subprocess.Popen(gsutil_cmd, stdin=p1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p1.stdout.close()
            stdout, stderr = p2.communicate()

            if p2.returncode!= 0:
                error_msg = f"Failed to dump {table_name} to GCS. Error: {stderr.decode()}"
                logging.error(error_msg)
                return error_msg
            
            success_msg = f"Successfully dumped {table_name} to {gcs_uri}"
            logging.info(success_msg)
            return success_msg
        except Exception as e:
            logging.error(f"Exception during GCS dump for {table_name}: {e}")
            return str(e)

    def run_mydumper_export(self, database_name: str, output_path: str, threads: int, chunk_size_mb: int) -> str:
        """Runs mydumper to export the database."""
        if not all(s.isalnum() or s in ['-', '_', '/'] for s in [database_name, output_path]):
             raise ValueError("Invalid input parameters.")

        db_conf = self._get_db_connection().get_config()
        os.makedirs(output_path, exist_ok=True)
        
        mydumper_cmd = [
            "mydumper",
            f"--host={db_conf['host']}",
            f"--user={db_conf['user']}",
            f"--password={db_conf['password']}",
            f"--database={database_name}",
            f"--outputdir={output_path}",
            f"--threads={threads}",
            f"--chunk-filesize={chunk_size_mb}",
            "--compress",
            "--trx-consistency-only",
            "--verbose=3"
        ]

        try:
            logging.info(f"Starting mydumper export for {database_name}...")
            result = subprocess.run(mydumper_cmd, capture_output=True, text=True, check=True)
            logging.info(f"Mydumper stdout: {result.stdout}")
            logging.info(f"Mydumper stderr: {result.stderr}")
            
            metadata_file = os.path.join(output_path, "metadata")
            if os.path.exists(metadata_file):
                return f"Mydumper export successful. Output at {output_path}. Metadata file is present."
            else:
                return f"Mydumper export may have failed. Metadata file not found at {output_path}."

        except subprocess.CalledProcessError as e:
            error_msg = f"Mydumper export failed with exit code {e.returncode}. Stderr: {e.stderr}"
            logging.error(error_msg)
            return error_msg
        except Exception as e:
            logging.error(f"An exception occurred during mydumper export: {e}")
            return str(e)

    def get_binlog_position(self, metadata_file_path: str) -> dict:
        """Parses the mydumper metadata file to get binlog position."""
        try:
            with open(metadata_file_path, 'r') as f:
                content = f.read()
            
            log_file = ""
            log_pos = ""

            for line in content.splitlines():
                if "Log: " in line:
                    log_file = line.split("Log: ").strip()
                if "Pos: " in line:
                    log_pos = line.split("Pos: ").strip()
            
            if log_file and log_pos:
                return {"log_file": log_file, "log_position": log_pos}
            else:
                return {"error": "Could not parse binlog position from metadata file."}
        except FileNotFoundError:
            return {"error": f"Metadata file not found at {metadata_file_path}"}
        except Exception as e:
            return {"error": str(e)}