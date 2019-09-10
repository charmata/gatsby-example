import boto3
from io import BytesIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    
    location = {
        "bucketName": 'charmata-gatsby-artifacts',
        "objectKey": 'build.zip'
    }
    try:
        job = event.get("CodePipeline.job")
        
        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "BuildArtifact":
                    location = artifact["location"]["s3Location"]
        
        print("Building site from " + str(location))
        s3 = boto3.resource('s3')
        
        site_bucket = s3.Bucket('charmata-gatsby')
        build_bucket = s3.Bucket(location["bucketName"])
        
        site_zip = BytesIO()
        build_bucket.download_fileobj(location["objectKey"], site_zip)
        
        with zipfile.ZipFile(site_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                site_bucket.upload_fileobj(obj, nm,
                    ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                site_bucket.Object(nm).Acl().put(ACL='public-read')
                
        print('Job done!')
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])
            
    except:
        raise
    
    return 'Hello from Lambda!'
