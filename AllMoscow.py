import LoggerInit
import config
import pytz
from datetime import datetime
import time
import logging

from Queues import QueueWrapper
from Queues.ProducerConsumer.ConsumerFactory import ConsumerFactory

LoggerInit.init_logging(config.log_all_moscow_file)
logger = logging.getLogger("AllMoscowParser")

# This request was too big for the server
"""
links = [
    "http://www.cian.ru/cat.php?deal_type=rent&district[0]=125&district[10]=154&district[11]=327&district[12]=328"
    "&district[13]=329&district[14]=330&district[15]=331&district[16]=332&district[17]=333&district[18]=334"
    "&district[19]=335&district[1]=126&district[20]=336&district[21]=337&district[22]=338&district[23]=339"
    "&district[24]=340&district[25]=341&district[26]=342&district[27]=343&district[28]=344&district[29]=345"
    "&district[2]=127&district[30]=346&district[31]=347&district[32]=355&district[33]=356&district[34]=357"
    "&district[35]=358&district[3]=128&district[4]=129&district[5]=130&district[6]=131&district[7]=132&district[8]=152"
    "&district[9]=153&engine_version=2&offer_type=flat&room1=1&type=-2",

    "http://www.cian.ru/cat.php?deal_type=rent&district[0]=112&district[10]=122&district[11]=123&district[12]=124"
    "&district[13]=348&district[14]=349&district[15]=350&district[1]=113&district[2]=114&district[3]=115"
    "&district[4]=116&district[5]=117&district[6]=118&district[7]=119&district[8]=120&district[9]=121"
    "&engine_version=2&offer_type=flat&room1=1&type=-2",

    "http://www.cian.ru/cat.php?deal_type=rent&district[0]=100&district[10]=110&district[11]=111&district[1]=101"
    "&district[2]=102&district[3]=103&district[4]=104&district[5]=105&district[6]=106&district[7]=107&district[8]=108"
    "&district[9]=109&engine_version=2&offer_type=flat&room1=1&type=-2",

    # ЮАО 1
    "http://www.cian.ru/cat.php?deal_type=rent&district[0]=84&district[10]=94&district[11]=95&district[12]=96"
    "&district[1]=85&district[2]=86&district[3]=87&district[4]=88&district[5]=89&district[6]=90&district[7]=91"
    "&district[8]=92&district[9]=93&engine_version=2&offer_type=flat&room1=1&type=-2",
    # ЮАО 2
    "http://www.cian.ru/cat.php?deal_type=rent&district[0]=97&district[1]=98&district[2]=99&engine_version=2"
    "&offer_type=flat&room1=1&type=-2",

    "http://www.cian.ru/cat.php?deal_type=rent&district[0]=72&district[10]=82&district[11]=83&district[1]=73"
    "&district[2]=74&district[3]=75&district[4]=76&district[5]=77&district[6]=78&district[7]=79&district[8]=80"
    "&district[9]=81&engine_version=2&offer_type=flat&room1=1&type=-2",

    "http://www.cian.ru/cat.php?deal_type=rent&district[0]=56&district[10]=66&district[11]=67&district[12]=68"
    "&district[13]=69&district[14]=70&district[15]=71&district[1]=57&district[2]=58&district[3]=59&district[4]=60"
    "&district[5]=61&district[6]=62&district[7]=63&district[8]=64&district[9]=65&engine_version=2&offer_type=flat"
    "&room1=1&type=-2",

    "http://www.cian.ru/cat.php?deal_type=rent&district[0]=39&district[10]=49&district[11]=50&district[12]=51"
    "&district[13]=52&district[14]=53&district[15]=54&district[16]=55&district[1]=40&district[2]=41&district[3]=42"
    "&district[4]=43&district[5]=44&district[6]=45&district[7]=46&district[8]=47&district[9]=48&engine_version=2"
    "&offer_type=flat&room1=1&type=-2",

    "http://www.cian.ru/cat.php?deal_type=rent&district[0]=23&district[10]=33&district[11]=34"
    "&district[12]=35&district[13]=36&district[14]=37&district[15]=38&district[1]=24&district[2]=25"
    "&district[3]=26&district[4]=27&district[5]=28&district[6]=29&district[7]=30&district[8]=31&district[9]=32"
    "&engine_version=2&offer_type=flat&room1=1&type=-2",

    "http://www.cian.ru/cat.php?deal_type=rent&district[0]=13&district[1]=14&district[2]=15&district[3]=16"
    "&district[4]=17&district[5]=18&district[6]=19&district[7]=20&district[8]=21&district[9]=22&engine_version=2"
    "&offer_type=flat&room1=1&type=-2",

]
"""
links = [
    "http://www.cian.ru/cat.php?deal_type=rent&engine_version=2&foot_min=15&metro[0]=57&metro[1]=60&metro[2]=72"
    "&metro[3]=228&metro[4]=233&metro[5]=234&metro[6]=235&metro[7]=244&offer_type=flat&only_foot=2&room1=1&type=-2",

    "http://www.cian.ru/cat.php?deal_type=rent&engine_version=2&foot_min=15&metro[0]=11&metro[10]=229&metro[11]=272"
    "&metro[1]=35&metro[2]=46&metro[3]=62&metro[4]=70&metro[5]=87&metro[6]=93&metro[7]=120&metro[8]=141&metro[9]=142"
    "&offer_type=flat&only_foot=2&room1=1&type=-2",

    "http://www.cian.ru/cat.php?deal_type=rent&engine_version=2&foot_min=15&metro[0]=12&metro[10]=275&metro[1]=14"
    "&metro[2]=81&metro[3]=94&metro[4]=97&metro[5]=122&metro[6]=133&metro[7]=134&metro[8]=154&metro[9]=159"
    "&offer_type=flat&only_foot=2&room1=1&type=-2",

    "http://www.cian.ru/cat.php?deal_type=rent&engine_version=2&foot_min=15&metro[0]=12&metro[10]=275&metro[1]=14"
    "&metro[2]=81&metro[3]=94&metro[4]=97&metro[5]=122&metro[6]=133&metro[7]=134&metro[8]=154&metro[9]=159"
    "&offer_type=flat&only_foot=2&room1=1&type=-2",

    "http://www.cian.ru/cat.php?deal_type=rent&engine_version=2&foot_min=15&metro[0]=9&metro[1]=15&metro[2]=29"
    "&metro[3]=30&metro[4]=36&metro[5]=106&metro[6]=116&offer_type=flat&only_foot=2&room1=1&type=-2",
]

zone = pytz.timezone("Europe/Moscow")


def time_is_right():
    now = datetime.now(zone)
    # return 3 <= now.hour <= 5
    return True


links_res = dict()


def link_parsed(info, result):
    global links_res
    if info in links_res.keys():
        links_res[info] = True
    logger.debug("Parsed {} offers".format(len(result)))


if __name__ == "__main__":
    QueueWrapper.init()
    QueueWrapper.clear_queue(config.parse_all_moscow_req_queue)
    sender_function = ConsumerFactory.get_consumer(config.parse_all_moscow_req_queue,
                                                   config.parse_all_moscow_ans_queue,
                                                   link_parsed)
    QueueWrapper.start(detach=True)
    try:
        while True:
            global links_res
            links_res = dict()
            for i, link in enumerate(links):
                links_res[i] = False
                sender_function(i, {'url': link, 'time': 0})
            while not all(links_res.values()):
                logger.debug("Waiting 10 seconds for new links result")
                time.sleep(10)
            time.sleep(5 * 60)
    except KeyboardInterrupt:
        QueueWrapper.close()
