#!/bin/bash

set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 [back|front] <tag>"
    exit 1
fi

TARGET="$1"
TAG="$2"

if [ "$TARGET" == "back" ]; then
    IMAGE_BASE="forome/anfisa"
elif [ "$TARGET" == "front" ]; then
    IMAGE_BASE="forome/anfisa-react-client"
else
    echo "First argument must be either 'back' or 'front'"
    exit 2
fi

IMG_AMD64="${IMAGE_BASE}:${TAG}-amd"
IMG_ARM64="${IMAGE_BASE}:${TAG}-arm"
IMG_MULTIARCH="${IMAGE_BASE}:${TAG}"

echo "Creating manifest for $IMG_MULTIARCH from:"
echo "  $IMG_AMD64"
echo "  $IMG_ARM64"

docker manifest create $IMG_MULTIARCH \
    --amend $IMG_AMD64 \
    --amend $IMG_ARM64

docker manifest annotate $IMG_MULTIARCH $IMG_AMD64 --arch amd64
docker manifest annotate $IMG_MULTIARCH $IMG_ARM64 --arch arm64

docker manifest push $IMG_MULTIARCH

echo "Multiarch manifest pushed: $IMG_MULTIARCH"
