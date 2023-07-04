import os
import sys
import socket
import hashlib
import json
import requests
from concurrent.futures import ThreadPoolExecutor

portal_info: dict = {
    "region": sys.argv[1].lower(),
    "url": os.getenv("PORTAL_URL"),
    "token": os.getenv("PORTAL_TOKEN"),
    "metrics": os.getenv("K8S_METRICS"),
    "app_versions": os.getenv("APP_VERSIONS")
}


def portal_api(api_name: str) -> dict:
    """
    Func to work with Portal REST-API
    :param api_name:
    :return: dict
    """
    headers: dict = {
        "user-agent": 'CMDB',
        "Content-type": 'application/json',
        "Accept": "text/plain",
        "authorization": "Token %s" % portal_info["token"]
    }
    response = requests.get("%s/api/v1/%s" % (portal_info["url"], api_name), headers=headers, verify=False)
    return dict(stdout=json.loads(response.content), status_code=response.status_code)


def write_to_file(variable: str, portal_name: str) -> None:
    """
    function to write a variable to a file
       call example:
                write_to_file(f"{var=}")
    :param variable:
    :param portal_name:
    :return: None
    """
    separator: int = variable.index('=')
    with open(f'info_{portal_name}/%s.py' % variable[:separator], 'w') as file:
        file.write('%s = %s' % (variable[:separator], variable[(separator + 1):]))


def get_k8s_info() -> list:
    """
    Func to get json from ose exporter
    :return:
    """
    info = list()
    for metrics_url in portal_info["metrics"].split(";"):
        info.append(json.loads(requests.request("GET", metrics_url.strip(), timeout=3).content)['data']['result'])
    # return json.loads(requests.request("GET", portal_info["metrics"]).content)
    return info


def get_k8s_labels(clusters: tuple) -> list:
    """
    function for getting pod labels from all clusters
    :param clusters:
    :return: list
    """

    def check_resolves(dns_name: str) -> bool:
        """
        function for checking resolving dns names
        :param dns_name:
        :return: bool
        """
        try:
            socket.gethostbyname(dns_name)
            return True
        except socket.error as Error:
            # logger.error(dns_name, Error)
            return False

    def check_port(checked_host: str, port: int) -> bool:
        """
        function to check server's port availability
        :param checked_host:
        :return: bool
        """
        if not checked_host:
            return False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            return s.connect_ex((checked_host, port)) == 0

    all_labels = list()
    for cluster_name in set(clusters):
        if check_resolves(f"query-runner.apps.{cluster_name}") and check_port(f"query-runner.apps.{cluster_name}", 443):
            get_labels = requests.request("GET", f"https://query-runner.apps.{cluster_name}/pods", verify=False)
            if get_labels.status_code == 200:
                all_labels.append(dict(cluster=cluster_name, labels=json.loads(get_labels.content)))

    return all_labels


def get_info():
    def get_vdc_checksum(vdc_info: dict) -> dict:
        """
        Func to get vdc checksum from portal
        :param vdc_info:
        :return:
        """
        vdc_checksum: dict = portal_api("servers?project_id=%s" % vdc_info["id"])
        return {
            "info": vdc_info,
            "checksum": hashlib.md5(json.dumps(vdc_checksum["stdout"]).encode()).hexdigest()
        }

    def checksum_vdc(cloud_projects: list) -> dict:
        """
        Func to get vdc checksum from portal
        :param cloud_projects:
        :return:
        """
        checksum_portal_vdc = dict()
        # with ThreadPoolExecutor(max_workers=thread_count(len(cloud_projects))) as executor:
        with ThreadPoolExecutor(max_workers=4) as executor:
            for project in executor.map(get_vdc_checksum, cloud_projects):
                checksum_portal_vdc[project["info"]["id"]] = {
                    "name": project["info"]["name"],
                    "domain_id": project["info"]["domain_id"],
                    "group_id": project["info"]["group_id"],
                    "zone": project["info"]["datacenter_name"],
                    "checksum": project["checksum"],
                    "networks": project["info"]["networks"],
                }
        return checksum_portal_vdc

    portal_domains_info: list = portal_api("domains")["stdout"]["domains"]
    write_to_file(f"portal_domains_info={portal_domains_info}", portal_info["region"])

    portal_groups_info: list = portal_api("groups")["stdout"]["groups"]
    write_to_file(f"portal_groups_info={portal_groups_info}", portal_info["region"])

    portal_projects: list = portal_api("projects")["stdout"]["projects"]
    write_to_file(f"portal_projects={portal_projects}", portal_info["region"])

    projects: dict = checksum_vdc(portal_projects)
    write_to_file(f"projects={projects}", portal_info["region"])

    all_vms = {i["id"]: portal_api("servers?project_id=%s" % i["id"]) for i in portal_projects}
    write_to_file(f"all_vms={all_vms}", portal_info["region"])

    portal_tags: list = portal_api("dict/tags")["stdout"]["tags"]
    write_to_file(f"portal_tags={portal_tags}", portal_info["region"])

    clusters_info: list = get_k8s_info()[0]
    write_to_file(f"clusters_info={clusters_info}", portal_info["region"])

    clusters = tuple(map(lambda x: x["metric"]["cluster"], clusters_info))
    all_labels: list = get_k8s_labels(clusters)
    write_to_file(f"all_labels={all_labels}", portal_info["region"])

    all_app_versions: dict = json.loads(requests.request("GET", portal_info["app_versions"]).content)
    write_to_file(f"all_app_versions={all_app_versions}", portal_info["region"])


if __name__ == "__main__":
    get_info()
