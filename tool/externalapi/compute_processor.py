import logging
import time
from typing import List

from google.cloud import compute_v1

from dependency.base_dependency import REPOSITORY_NAME, GCP_PROJECT_ID, SERVICE_ACCOUNT
from tool.kit.string_kit import generate_key

INSTANCE_CLIENT = compute_v1.InstancesClient()


def startup_script(main_filename: str):  # main_something.py
    return f'''#! /bin/bash
# Set system timezone
sudo timedatectl set-timezone Asia/Taipei

# Install or update needed software
sudo apt -yq update
sudo apt install -yq python3.9
sudo apt install -yq python3-pip
sudo apt install -yq python3-distutils
sudo apt install -yq git


# for selenium use install chrome 
sudo apt install -yq wget
sudo apt install -yq chromium-driver
wget -c https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f

# Fetch source code
sudo gcloud source repos clone {REPOSITORY_NAME} --project={GCP_PROJECT_ID}

# Install Cloud Ops Agent (logging)
curl -sSO https://dl.google.com/cloudagents/add-logging-agent-repo.sh
sudo bash add-logging-agent-repo.sh --also-install

# Python environment setup
sudo pip3 install -r /{REPOSITORY_NAME}/requirements.txt

export NAME=$(curl -X GET http://metadata.google.internal/computeMetadata/v1/instance/name -H 'Metadata-Flavor: Google')
export ZONE=$(curl -X GET http://metadata.google.internal/computeMetadata/v1/instance/zone -H 'Metadata-Flavor: Google')

# Run python
sudo python3 /{REPOSITORY_NAME}/{main_filename}

sudo gcloud --quiet compute instances delete $NAME --zone=$ZONE
'''


def create_an_instance(
        instance_name: str,
        main_filename: str,
        description='',
        disk_size=10,
        disk_source_image='projects/debian-cloud/global/images/debian-11-bullseye-v20220920',
        label='compute_engine_processor',
        machine_type='e2-micro',
        network_link='global/networks/default',
        region='asia-east1',
        zone='asia-east1-c',
):
    operation_client = compute_v1.ZoneOperationsClient()

    confidential_instance_config = compute_v1.ConfidentialInstanceConfig()
    confidential_instance_config.enable_confidential_compute = False

    attached_disk = compute_v1.AttachedDisk()
    attached_disk.auto_delete = True
    attached_disk.boot = True
    attached_disk_initialize_params = compute_v1.AttachedDiskInitializeParams()
    attached_disk_initialize_params.disk_size_gb = disk_size
    attached_disk_initialize_params.source_image = disk_source_image
    attached_disk.initialize_params = attached_disk_initialize_params
    attached_disk.mode = compute_v1.AttachedDisk.Mode.READ_WRITE.name
    attached_disk.type_ = compute_v1.AttachedDisk.Type.PERSISTENT.name

    items = compute_v1.Items()
    items.key = 'startup-script'
    items.value = startup_script(main_filename)
    metadata = compute_v1.Metadata()
    metadata.items = [items]

    network_interface = compute_v1.NetworkInterface()
    network_interface.name = network_link

    reservation_affinity = compute_v1.ReservationAffinity()
    reservation_affinity.consume_reservation_type = compute_v1.ReservationAffinity.ConsumeReservationType.ANY_RESERVATION.name

    scheduling = compute_v1.Scheduling()
    scheduling.automatic_restart = False
    scheduling.instance_termination_action = compute_v1.Scheduling.InstanceTerminationAction.DELETE.name
    # scheduling.on_host_maintenance = compute_v1.Scheduling.OnHostMaintenance.TERMINATE.name
    # scheduling.preemptible = True
    scheduling.provisioning_model = compute_v1.Scheduling.ProvisioningModel.SPOT.name

    service_accounts = list()
    service_account = compute_v1.ServiceAccount()
    service_account.email = SERVICE_ACCOUNT
    service_account.scopes = ['https://www.googleapis.com/auth/cloud-platform']
    service_accounts.append(service_account)

    # Collect information into the Instance object.
    instance = compute_v1.Instance()
    instance.can_ip_forward = False
    instance.confidential_instance_config = confidential_instance_config
    instance.description = description
    instance.disks = [attached_disk]
    instance.labels = {'program': label}
    instance.machine_type = f'zones/{zone}/machineTypes/{machine_type}'
    instance.metadata = metadata
    instance.network_interfaces = [network_interface]
    instance.reservation_affinity = reservation_affinity
    instance.scheduling = scheduling
    instance.service_accounts = service_accounts
    instance.name = f'{instance_name}-{generate_key(3, include_symbols=False, include_digits=False, include_upper=False)}'

    instance.network_interfaces = [network_interface]

    # Prepare the request to insert an instance.
    request = compute_v1.InsertInstanceRequest()
    request.zone = zone
    request.project = GCP_PROJECT_ID
    request.instance_resource = instance

    # Wait for the create operation to complete.
    logging.info(f"Creating Instance {instance.name} instance in {region}...")

    operation = INSTANCE_CLIENT.insert_unary(request=request)
    start = time.time()
    while operation.status != compute_v1.Operation.Status.DONE:
        operation = operation_client.wait(
            operation=operation.name, zone=zone, project=GCP_PROJECT_ID
        )
        if time.time() - start >= 900:  # 15 min
            raise TimeoutError()
    if operation.error:
        logging.error(f"Error during creation: {operation.error}")
        raise RuntimeError(operation.error)
    if operation.warnings:
        logging.warning(f"Warning during creation: {operation.warnings}")
    logging.info(f"Instance  {instance_name} created.")
    return True


def list_all_instances(
        active_only=False,
        instance_name=None,
        program_label=None,
) -> List[compute_v1.Instance]:



    """
    status: PROVISIONING, STAGING, RUNNING, STOPPING, SUSPENDING, SUSPENDED, REPAIRING, and TERMINATED
    """
    request = compute_v1.AggregatedListInstancesRequest()
    request.project = GCP_PROJECT_ID
    # Use the `max_results` parameter to limit the number of results that the API returns per response page.
    request.max_results = 100

    agg_list = INSTANCE_CLIENT.aggregated_list(request=request)

    all_instances = []
    print("Instances found:")
    # Despite using the `max_results` parameter, you don't need to handle the pagination
    # yourself. The returned `AggregatedListPager` object handles pagination
    # automatically, returning separated pages as you iterate over the results.
    for zone, response in agg_list:
        if response.instances:
            for instance in response.instances:
                if active_only:
                    if instance.status not in ['PROVISIONING', 'STAGING', 'RUNNING']:
                        continue
                if instance_name is not None:
                    if not instance.name.startswith(instance_name):
                        continue
                if program_label is not None:
                    if not instance.labels:
                        continue
                    if instance.labels.get('program') != program_label:
                        continue
                all_instances.append(instance)
    return all_instances


if __name__ == '__main__':
    z = list_all_instances(active_only=True)
    print('done')
