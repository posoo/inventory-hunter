import logging
import requests
import traceback

from alerter.common import Alerter, AlerterFactory


@AlerterFactory.register
class TelegramAlerter(Alerter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.webhook_url = kwargs.get('webhook_url')
        self.chat_ids = kwargs.get('chat_ids')
        logging.info(f'Initialized TG Bot: {self.webhook_url}')
        for cid in self.chat_ids:
            logging.info(f'Chat ID: {cid}')

    @classmethod
    def from_args(cls, args):
        webhook_url = args.webhook_url
        chat_ids = args.chat_ids
        return cls(webhook_url=webhook_url, chat_ids=chat_ids)

    @classmethod
    def from_config(cls, config):
        webhook_url = config['webhook_url']
        chat_ids = config['chat_ids'] if 'chat_ids' in config else ''
        return cls(webhook_url=webhook_url, chat_ids=chat_ids)

    @staticmethod
    def get_alerter_type():
        return 'telegram'

    def __call__(self, **kwargs):
        subject = kwargs.get("subject")
        content = kwargs.get("content")

        for chat_id in self.chat_ids:
            logging.info(f'Sending an alert to TG Chat ID: {chat_id}')
            _telegram_webhook_generated = {
                "chat_id": chat_id,
                "parse_mode": "html",
                "text": f'<b>{subject}</b>\n{content}'
            }
            try:
                logging.debug(f"Telegram Webhook URL: {self.webhook_url}")
                send_request = requests.post(
                    self.webhook_url,
                    json=_telegram_webhook_generated,
                )
                if send_request.status_code != 200:
                    logging.error(
                        f"There was an issue sending to Telegram due to an invalid request: {send_request.status_code} -> {send_request.text}"
                    )
            except Exception:
                logging.error(
                    f"Issue with sending webhook to Telegram. {traceback.format_exc()}"
                )
