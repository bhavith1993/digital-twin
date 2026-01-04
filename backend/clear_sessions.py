"""
Script to clear all conversation sessions from S3 or local storage.
"""
import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

USE_S3 = os.getenv("USE_S3", "false").lower() == "true"
S3_BUCKET = os.getenv("S3_BUCKET", "").strip()
MEMORY_DIR = os.getenv("MEMORY_DIR", "../memory")

def clear_all_sessions():
    """Delete all session files"""
    deleted_count = 0
    
    if USE_S3:
        if not S3_BUCKET:
            print("Error: S3_BUCKET environment variable is not set")
            return 0
        
        print(f"Connecting to S3 bucket: {S3_BUCKET}")
        s3_client = boto3.client("s3")
        
        try:
            # List all objects in the bucket
            paginator = s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=S3_BUCKET)
            
            # Collect all JSON files (session files)
            objects_to_delete = []
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        if obj['Key'].endswith('.json'):
                            objects_to_delete.append({'Key': obj['Key']})
            
            if not objects_to_delete:
                print("No session files found in S3 bucket")
                return 0
            
            print(f"Found {len(objects_to_delete)} session file(s) to delete")
            
            # Delete in batches (S3 allows up to 1000 objects per delete)
            for i in range(0, len(objects_to_delete), 1000):
                batch = objects_to_delete[i:i + 1000]
                if batch:
                    response = s3_client.delete_objects(
                        Bucket=S3_BUCKET,
                        Delete={'Objects': batch}
                    )
                    deleted_count += len(batch)
                    if 'Errors' in response and response['Errors']:
                        print(f"Errors deleting some files: {response['Errors']}")
            
            print(f"✓ Successfully deleted {deleted_count} session file(s) from S3")
            
        except ClientError as e:
            print(f"Error deleting sessions from S3: {str(e)}")
            return 0
    else:
        # Local file storage
        if not os.path.exists(MEMORY_DIR):
            print(f"Memory directory does not exist: {MEMORY_DIR}")
            return 0
        
        print(f"Clearing sessions from local directory: {MEMORY_DIR}")
        for filename in os.listdir(MEMORY_DIR):
            if filename.endswith('.json'):
                file_path = os.path.join(MEMORY_DIR, filename)
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"  Deleted: {filename}")
                except Exception as e:
                    print(f"  Error deleting {filename}: {str(e)}")
        
        if deleted_count == 0:
            print("No session files found in local directory")
        else:
            print(f"✓ Successfully deleted {deleted_count} session file(s) from local storage")
    
    return deleted_count

if __name__ == "__main__":
    print("=" * 50)
    print("Clearing all conversation sessions...")
    print("=" * 50)
    
    count = clear_all_sessions()
    
    print("=" * 50)
    print(f"Done! Deleted {count} session(s)")
    print("=" * 50)


