#!/bin/bash


# To check if the port is busy
function is_port_taken() {
    local port=$1
    nc -z localhost $port >/dev/null 2>&1
    return $?
}

# Search free port
function find_free_port() {
    local port=444
    while is_port_taken $port; do
        ((port++))
    done
    echo $port
}

export PORT=$(find_free_port)