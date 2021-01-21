#!/bin/bash

cd / && celery -A celery_app worker
