#!/bin/sh

### BEGIN INIT INFO
# Provides:          si7021
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Put a short description of the service here
# Description:       Put a long description of the service here
### END INIT INFO

DAEMON_NAME=__NAME_PLACEHOLDER__
DIR=__DIR_PLACEHOLDER__
DAEMON=$DIR/$DAEMON_NAME.py


# Add any command line options for your daemon here
DAEMON_OPTS=""

# This next line determines what user the script runs as.
# Root generally not recommended but necessary if you are using the Raspberry Pi GPIO from Python.
DAEMON_USER=root

# The process ID of the script when it runs is stored here:
PIDFILE=/var/run/$DAEMON_NAME.pid

. /lib/lsb/init-functions

script_install() {
  cp $0 /etc/init.d/$DAEMON_NAME
  chmod a+x /etc/init.d/$DAEMON_NAME
  update-rc.d $DAEMON_NAME defaults $SCRIPT_START $SCRIPT_STOP > /dev/null
}

script_remove() {
  update-rc.d -f $DAEMON_NAME remove > /dev/null
  rm -f /etc/init.d/$DAEMON_NAME
}

do_start () {
    log_daemon_msg "Starting system $DAEMON_NAME daemon"
    start-stop-daemon --start --background --pidfile $PIDFILE --make-pidfile --user $DAEMON_USER --chuid $DAEMON_USER --startas $DAEMON -- $DAEMON_OPTS
    log_end_msg $?
}
do_stop () {
    log_daemon_msg "Stopping system $DAEMON_NAME daemon"
    start-stop-daemon --stop --pidfile $PIDFILE --retry 10
    log_end_msg $?
}

case "$1" in

    start|stop)
        do_${1}
        ;;

    restart|reload|force-reload)
        do_stop
        do_start
        ;;

    status)
        status_of_proc "$DAEMON_NAME" "$DAEMON" && exit 0 || exit $?
        ;;

    install)
        script_install
        ;;

    remove)
        script_remove
        echo Warning! A reboot is highly recommended to complete uninstallation!
    ;;

    *)
        echo "Usage: /etc/init.d/$DAEMON_NAME {start|stop|restart|status|install|remove}"
        exit 1
        ;;

esac
exit 0
