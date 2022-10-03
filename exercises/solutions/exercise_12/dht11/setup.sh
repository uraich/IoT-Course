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

if [[ $dirs == *"/templates"* ]]
then
    echo "/templates directory already exists"
    echo "The following modules have been uploaded to /templates:"
    modules="$(ampy ls /templates)"
    for i in $modules ; do
	echo ${i#"/templates/"}
	if [[ $i#"/templates/"} == *"sensor_tpl.py"* ]]
	then
	    echo "Removing sensor_tpl.py"
	    ampy rm /templates/sensor_tpl.py
	fi
    done
else
    echo "Creating /templates directory"
    ampy mkdir /templates
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
echo "Uploading sensor.tpl"

ampy put templates/sensor.tpl templates/sensor.tpl

