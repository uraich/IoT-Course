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

if [[ $dirs == *"/static"* ]]
then
    echo "/static directory already exists"
    echo "The following modules have been uploaded to /lib:"
    modules="$(ampy ls /static)"
    for i in $modules ; do
	echo ${i#"/static/"}
	done    
else
    echo "Creating /static directory"
    ampy mkdir /static
fi

echo ""
# check if /html already exists

if [[ $dirs == *"/html"* ]]
then
    echo "/html directory already exists"
    echo "The following HTML files have been uploaded to /html:"
    htmlFiles="$(ampy ls /html)";
    for i in $htmlFiles ; do
	echo ${i#"/html/"}
	done
else
    echo "Creating /html directory"
    ampy mkdir /html
fi
echo ""
echo "Uploading dummyLED.html"
ampy put html/dummyLED.html html/dummyLED.html

# echo "Uploading lightBulb.html"
# ampy put html/lightBulb.html html/lightBulb.html

echo "Uploading ledControl.html"
ampy put html/ledControl.html html/ledControl.html

echo "Uploading led-blue-off-128.png"
ampy put static/led-blue-off-128.png static/led-blue-off-128.png
echo "Uploading led-blue-on-128.png"
ampy put static/led-blue-on-128.png static/led-blue-on-128.png
