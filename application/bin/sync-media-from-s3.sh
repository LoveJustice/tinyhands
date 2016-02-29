#!/bin/bash

# Pull media files down from S3
aws s3 sync s3://dreamsuite-media /data/media/

# Push new media files up to S3
aws s3 /data/media/ sync s3://dreamsuite-media
