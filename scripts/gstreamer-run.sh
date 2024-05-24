#!/bin/bash

abort() {
  printf "%s\n" "$@" >&2
  exit 1
}

execute() {
  if ! "$@"
  then abort "$(printf "Failed: %s" "$@")"
  fi
}

execute_root() {
  execute "sudo" "$@"
}

require_argument() {
  if test -z "$1"
  then abort "Error: Required argument $2 does not exist"
  else echo "$1"
  fi
}

argument_exists_or() {
  if test -z "$1"
  then echo "$2"
  else echo "$1"
  fi
}

execute_root "gst-launch-1.0" "-e" "compositor" "name=mix" "sink_0::xpos=0" "sink_0::ypos=0" "sink_0::width=640" "sink_0::height=360" "sink_1::xpos=640" "sink_1::ypos=0" "sink_1::width=640" "sink_1::height=360" "sink_2::xpos=1280" "sink_2::ypos=0" "sink_2::width=640" "sink_2::height=360" "!" "videoconvert" "!" "x264enc" "bitrate=2048" "tune=zerolatency" "!" "h264parse" "!" "flvmux" "name=mux" "streamable=true" "!" "rtmpsink" "location=\"rtmp://a.rtmp.youtube.com/live2/$(require_argument "$0" "youtube_stream_key")\"" "v4l2src" "device=/dev/video$(argument_exists_or "$1" "0")" "!" "videoconvert" "!" "videoscale" "!" "video/x-raw,width=640,height=360" "!" "queue" "!" "mix.sink_0" "v4l2src" "device=/dev/video$(argument_exists_or "$2" "2")" "!" "videoconvert" "!" "videoscale" "!" "video/x-raw,width=640,height=360" "!" "queue" "!" "mix.sink_1" "v4l2src" "device=/dev/video$(argument_exists_or "$3" "4")" "!" "videoconvert" "!" "videoscale" "!" "video/x-raw,width=640,height=360" "!" "queue" "!" "mix.sink_2" "audiotestsrc" "!" "audioconvert" "!" "voaacenc" "!" "queue" "!" "mux"