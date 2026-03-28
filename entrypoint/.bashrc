exit() {
    echo "Formatting on shell exit"
    cd /geometricalgebra/src/
    /format.sh
    builtin exit "$@"
}
