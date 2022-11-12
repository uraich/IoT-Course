#!/bin/bash
# This shell scripts sets up the picoweb server to run the Hello World
# WEB server. It uses picoweb to provide the Hello World WEB page.
# Demo program for the course on the Internet of Things (IoT) at the
# University of Cape Coast (Ghana)
# Copyright (c) U. Raich April 2020
# This program is released under GPL

echo "Setting up the file system for the WEB server"
dirs="$(ampy ls)"
echo $dirs

#check if /lib already exists

if [[ $dirs == *"/lib"* ]]
then
    echo "/lib directory already exists"
    echo "The following modules have been uploaded to /lib:"
    modules="$(ampy ls /lib)"
    for i in $modules ; do
	echo ${i#"/lib/"}
	done    
else
    echo "Creating /lib directory"
    ampy mkdir /lib
fi

dirs="$(ampy ls)"
if [[ $dirs == *"/html"* ]]
then
    echo "/html directory already exists"
    echo "The following modules have been uploaded to /html:"
    modules="$(ampy ls /html)"
    for i in $modules ; do
	echo ${i#"/html/"}
	done    
else
    echo "Creating /html directory"
    ampy mkdir /html
fi
echo "Uploading html/index.html to /html/index.html"
ampy put html/index.html /html/index.html
echo "Uploading html/sensor.html to /html/sensor.html"
ampy put html/sensor.html /html/sensor.html
