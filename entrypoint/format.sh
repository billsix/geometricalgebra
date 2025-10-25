#!/bin/env bash

cd /geometricalgebra/

ruff check . --fix
ruff format --line-length=80
