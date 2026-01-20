from google.cloud import storage
import os

'''
# 새로운 bucket 생성
from google.cloud import storage

# Instantiates a client
storage_client = storage.Client()

# The name for the new bucket
bucket_name = "my-new-bucket"

# Creates the new bucket
bucket = storage_client.create_bucket(bucket_name)

print(f"Bucket {bucket.name} created.")
'''

bucket_name = "practice-bucket98"
storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)


# upload_path="README.md"
# upload_file_name ="/Users/yanghyeon-u/HOME_WORK/Boostcamp-AI-Tech-Product-Serving/airflow_homework/README.md"
# blob = bucket.blob(upload_path)
# blob.upload_from_filename(upload_file_name)


download_file_name="README.md"
destination_path="/Users/yanghyeon-u/HOME_WORK/Boostcamp-AI-Tech-Product-Serving/airflow_homework/README2.md"
bolb = bucket.blob(download_file_name)
bolb.download_to_filename(destination_path)