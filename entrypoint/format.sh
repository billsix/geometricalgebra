#!/bin/env bash

ruff check . --fix
ruff format --line-length=88

ty check /geometricalgebra/src
ty check /geometricalgebra/tests
