#!/bin/sh

ECHO=/bin/echo

BOLD="\033[1;33m"
NORM="\033[0m"
INFO="$BOLD Info: $NORM"
ERROR="$BOLD Error:$NORM"
WARNING="$BOLD Warning:$NORM"
INPUT="$BOLD => $NORM"

DAEMON_NAME=si7021
DIR=/usr/local/bin/$DAEMON_NAME

if [ "$(id -u)" != "0" ]; then
   $ECHO -e $ERROR  "This script must be run as root"
   exit 1
fi

if [ -e /etc/init.d/$DAEMON_NAME ]
then
    $ECHO -e $ERROR $DAEMON_NAME service start/stop script detected!
    $ECHO -e $INFO Please, remove previous installation or specify destination
    $ECHO -e $INFO folder name and run script again with folder name parameter,
    $ECHO -e $INFO for example:
    $ECHO -e $INFO '\t'sudo /etc/init.d/$DAEMON_NAME remove
    $ECHO -e $INFO '\t'sudo $0
    exit 1
fi

if [ -d $DIR ]
then
    $ECHO -e $WARNING Previous $DAEMON_NAME environment will be moved to $DIR.old
    [ -d $DIR.old ] || mkdir $DIR.old
    mv -f $DIR/* $DIR.old
else
    mkdir $DIR
fi

cp *.sh $DIR
cp *.py $DIR
chmod a+x $DIR/*.*

eval sed -i 's,__DIR_PLACEHOLDER__,$DIR,g' $DIR/$DAEMON_NAME.sh
eval sed -i 's,__NAME_PLACEHOLDER__,$DAEMON_NAME,g' $DIR/$DAEMON_NAME.sh

$DIR/$DAEMON_NAME.sh install

$ECHO -e $INFO ...finished.

/etc/init.d/$DAEMON_NAME

exit 0
