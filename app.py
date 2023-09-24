from flask import Flask, request, jsonify
import boto3
import os
import whisper
from flask_cors import CORS, cross_origin

appname = os.getenv("APP_NAME")
model = whisper.load_model("base")

aws_access_key = os.environ.get('AWS_ACCESS_KEY')
aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
aws_bucket_name = os.environ.get('AWS_BUCKET_NAME')

s3 = boto3.client('s3', aws_access_key_id=aws_access_key , aws_secret_access_key=aws_secret_key)
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/api/transcribe', methods=['GET'])
@cross_origin()
def transcribe():
    # Get the "url" parameter from the body of the request
    key = request.args.get('key')
    print(key)

    if not key:
        return jsonify({'error': 'Missing "key" parameter'}), 400

    try:
        # Download the file from S3
        s3.download_file(aws_bucket_name , key, './assets/' + key)
        print('File downloaded successfully')

        # Transcribe the file
        result = model.transcribe('./assets/' + key)
        print(result["text"])

        # Delete the downloaded file
        os.remove('./assets/' + key)

        # Delete the file from s3
        s3.delete_object(Bucket=aws_bucket_name, Key=key)

        return jsonify({'transcript': result["text"]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    if appname:
        app.run(debug=True)
    else:
        app.run()
