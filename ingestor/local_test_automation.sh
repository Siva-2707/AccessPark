# This script is used to create a zip file for AWS Lambda deployment(For local testing)

!#/bin/bash
rm -rf package ingestor.zip

pip install -r requirements.txt -t package/

pip install \
      --platform manylinux2014_x86_64 \
      --target=package \
      --implementation cp \
      --python-version 3.13 \
      --only-binary=:all: --upgrade \
      numpy

pip install \
      --platform manylinux2014_x86_64 \
      --target=package \
      --implementation cp \
      --python-version 3.13 \
      --only-binary=:all: --upgrade \
      pandas
      
cd package && zip -r9 ../ingestor.zip . && cd ..
      
zip -g ingestor.zip -r ./*.py

aws s3 cp ingestor.zip s3://accessparktest/ingestor.zip