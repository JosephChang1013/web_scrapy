from google.cloud import logging, storage

GCP_PROJECT_ID = 'hai-tag-system'
SERVICE_ACCOUNT = 'web-scrapy@hai-tag-system.iam.gserviceaccount.com'
REPOSITORY_NAME = 'web_crawl_cloud'

LISTENING_TIMEOUT = 5.0

REQUEST_KEY = 's5qbXgit0ixymntoRqulC99r6Wm2FNOaEK717fNHQ4Lljcdp8S0Bip9Lbe0flOZhAInXxX7JoSvgFtO2byn2MseMJ0iwUoPCHSP4CviaR2TZPv8VK8Skx7K1caExCGLJ'
storage_client = storage.Client()
my_bucket = storage_client.get_bucket('web_scrapper_v1')
bucket_name = 'web_scrapper_v1'

bucket = storage_client.bucket(bucket_name)


logging_client = logging.Client()
logging_client.setup_logging()
