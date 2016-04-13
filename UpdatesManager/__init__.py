import threading
import queue
import logging
from datetime import datetime

logger = logging.getLogger("UpdatesManager")
logger.setLevel(logging.DEBUG)


class UpdatesManager:
    subscriptions_queue = queue.Queue()
    unsubscriptions_queue = queue.Queue()

    @staticmethod
    def subscribe(unique_id, callback, function, frequency):
        UpdatesManager.subscriptions_queue.put((unique_id, {'callback': callback,
                                                            'run': function,
                                                            'freq': frequency}))

    @staticmethod
    def unsubscribe(unique_id):
        UpdatesManager.unsubscriptions_queue.put(unique_id)

    @staticmethod
    def worker():
        update_requests_dict = {}
        while True:
            while True:
                try:
                    subscription = UpdatesManager.subscriptions_queue.get_nowait()
                except queue.Empty:
                    break
                unique_id = subscription[0]
                logger.debug("Adding new subscription with id " + str(unique_id))
                subscription = subscription[1]
                subscription['last_updated'] = datetime.now()
                update_requests_dict[unique_id] = subscription
            while True:
                try:
                    unsubscription = UpdatesManager.unsubscriptions_queue.get_nowait()
                except queue.Empty:
                    break
                logger.debug("Deleting subscription with id " + unsubscription)
                if unsubscription in update_requests_dict:
                    del update_requests_dict[unsubscription]

            for update in update_requests_dict.values():
                if (datetime.now() - update['last_updated']).total_seconds() \
                        >= update['freq']:
                    logger.debug("Getting new updates")
                    update['callback'](update['run']())
                    update['last_updated'] = datetime.now()

    @staticmethod
    def init_manager():
        updates_thread = threading.Thread(target=UpdatesManager.worker, daemon=True)
        updates_thread.start()
