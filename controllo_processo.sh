#! /bin/bash

# controlla se il programma tvcc.py e' attivo o e' caduto
# se e' caduto allora registro la cosa nel log e lo riavvio
# per sicurezza attivo anche la videosorveglianza.
#
# il programma va messo nel crontab e va eseguito regoalrmente
# ad esempio ogni 10 minuti:
# */10 * * * * /percorsoprogramma/controllo_processo.sh

CONTROLLO="$(ps -Af |grep -v grep | grep tvcc.py|awk '{ print $2}')" >/dev/null
if [[ ${CONTROLLO} == '' ]] ; then
        echo "$(date +"%Y-%m-%d %H:%M:%S") [ERR] TVCC caduto, lo devo riavviare" >> /percorsoapplicazione/tvcc.log
        python /percorsoapplicazione/tvcc.py >>/percorsoapplicazione/tvcc_std.log 2>&1 &

fi
