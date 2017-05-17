#!/usr/bin/env python
#
# Basic metadata for openstack 
#
from flask import Flask, request,redirect, url_for, abort, make_response,jsonify

app  = Flask(__name__)

# latest only
@app.route("/openstack")
def version():
    return "latest"

# return metadata for client
@app.route("/openstack/latest/meta_data.json")
def metadata():
    return make_response(jsonify({ 
        "uuid": "mcs-00001",
        "hostname": "cvtest1.lab.local",
        "name": "cvtest1",
        "public_keys": {
            "mykey": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDNOjFSxcbcjcZXM6WQK2E58lLM2TOSfONngQ6su94MhfR+hdWLaF484cQDn0WvojulqqomAch/dch89gRIWcOh9EuvU0rc4e8tECMAnUOfJEA1nSb4HaHVTrQ6YjUXf3D9gFZiZbuAVULApt06fTlYiqUxR5w4UU6C8UOg5z3H8Yhrsa6xOVF4dBp1UL705Gau00z4u7PdHp25ywMuvHFnczP5hcYQ8XLR+xB68RuI7qM/gvl/4Ml+mshWJ079Smkg8xpDZHcY9JZVckXcJx1PUy/trQFrOIFEG3WnMfPp8DoSOLN9uHQM8N88UROwk0VZcgj/b6X7sn+chsO2HN95"
            }
        }))

# /openstack/latest/user_data 
@app.route("/openstack/latest/user_data")
def userdata():
    return '#!/bin/bash\
            echo "Hello from Openstack User_data"\
            '

# /openstack/latest/vendor_data.json
@app.route("/openstack/latest/vendor_data.json")
def vendordata():
    return make_response(jsonify({}))

# /openstack/latest/network_data.json
@app.route("/openstack/latest/network_data.json")
def networkdata():
    return make_response(jsonify({}))

# 404 handler
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}),404)

# 405 handler
@app.errorhandler(405)
def not_allowed(error):
    return make_response(jsonify({'error': 'Method not allowed'}),405)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=10080,debug=True)

