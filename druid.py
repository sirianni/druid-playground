#!/usr/bin/env python

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import argparse
import json
import re
import sys
import time
import requests

coordinator_url = 'http://localhost:8081'
router_url = 'http://localhost:8888'


def post_task(task):
  resp = requests.post(f"{coordinator_url}/druid/indexer/v1/task", json=task)

  task_id = resp.json()["task"]

  print(f"Task started: {task_id}")
  print(f"Task log:     {coordinator_url.rstrip('/')}/druid/indexer/v1/task/{task_id}/log")
  print(f"Task status:  {coordinator_url.rstrip('/')}/druid/indexer/v1/task/{task_id}/status")
  return task_id


def await_task_completion(task_id, timeout):
  timeout_at = time.time() + timeout
  while True:
    resp = requests.get(f"{coordinator_url}/druid/indexer/v1/task/{task_id}/status")
    status = resp.json()["status"]["statusCode"]
    if status in ['SUCCESS', 'FAILED']:
      print(f"Task finished with status: {status}")
      return status
    else:
      if time.time() < timeout_at:
        print(f"Task {task_id} still running...")
        timeleft = timeout_at - time.time()
        time.sleep(min(5, timeleft))
      else:
        raise Exception(f"Task {task_id} did not finish in time!")


def await_load_completion(datasource, timeout):
  timeout_at = time.time() + timeout
  while True:
    resp = requests.get(f"{coordinator_url}/druid/coordinator/v1/loadstatus")
    load_status = resp.json().get(datasource, 0.0)
    if load_status >= 100.0:
      print(f"{datasource} loading complete! You may now query your data")
      return
    else:
      if time.time() < timeout_at:
        print(f"{datasource} is {load_status}% finished loading...")
        timeleft = timeout_at - time.time()
        time.sleep(min(5, timeleft))
      else:
        raise Exception(f"{datasource} was not loaded in time!")


def query_sql(sql):
  resp = requests.post(f"{router_url}/druid/v2/sql",
                       headers={'Accept': 'application/json'},
                       json={ "query": sql})
  return resp.json()


def query(body):
  resp = requests.post(f"{router_url}/druid/v2",
                       headers={'Accept': 'application/json'},
                       json=body)
  return resp.json()
