#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

if [ ! -d "ffmpeg" ]; then
  mkdir -p ffmpeg
  curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz | tar -xJ -C ffmpeg --strip-components 1
fi
export PATH=$PATH:$(pwd)/ffmpeg

