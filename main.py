import argparse
import json
import subprocess
import sys

from kubernetes import client, config

parser = argparse.ArgumentParser()
parser.add_argument('--project-id', type=str, required=True)
parser.add_argument('--disk-regex', type=str, required=True)
parser.add_argument('--kube-context', type=str, required=True)
parser.add_argument('--remove', action='store_true')
parser.add_argument('--dry-run', action='store_true')
parser.add_argument('--region', type=str)
parser.add_argument('--zone', type=str)
parser.add_argument('--replica-zones', type=str)
args = parser.parse_args()

config.load_kube_config(config_file='/Users/mkubaczyk/.kube/config', context=args.kube_context)

if args.replica_zones and not args.region:
    print('--region is required when --replica-zones is defined')
    sys.exit(1)
v1 = client.CoreV1Api()
pv_obj_list = v1.list_persistent_volume(watch=False)
pvc_obj_list = v1.list_persistent_volume_claim_for_all_namespaces(watch=False)
pvc_list = {pvc.to_dict().get('spec').get(
    'volume_name'): f"{pvc.to_dict().get('metadata').get('namespace')}/{pvc.to_dict().get('metadata').get('name')}" for
            pvc in pvc_obj_list.items}
pv_list = {pv.to_dict().get('spec').get('gce_persistent_disk').get('pd_name'): pv.to_dict().get('metadata').get('name')
           for pv in pv_obj_list.items}

cmd = f"gcloud compute disks list --format=json --project={args.project_id}"
if args.zone:
    cmd += f" --filter='name~{args.disk_regex} AND zone:( {args.zone} )'"
elif args.replica_zones:
    cmd += f" --filter='name~{args.disk_regex} AND replicaZones:( {args.replica_zones} )'"
elif args.region:
    cmd += f" --filter='name~{args.disk_regex} AND regions:( {args.region} )'"
print(cmd)
print('')
run = subprocess.Popen(
    cmd,
    shell=True, stdout=subprocess.PIPE)
cmd_out, cmd_err = run.communicate()
not_matched = []
matched = []
for disk in json.loads(cmd_out):
    if 'users' in disk or disk['name'] in pv_list.keys():
        matched.append(f"{disk['name']} -> {pvc_list[pv_list[disk['name']]]}")
        continue
    if disk['name'] not in pv_list.keys():
        not_matched.append(disk['name'])

print('Matched:')
for el in matched:
    print(el)
print('')
print('Not matched:')
for el in not_matched:
    print(el)

if not_matched and args.remove:
    print('')
    decision = input("Remove? (y/n)")
    if decision == 'y':
        for el in not_matched:
            cmd = f"gcloud compute disks delete {el} --project={args.project_id}"
            if args.region:
                cmd += f" --region={args.region}"
            elif args.zone:
                cmd += f" --zone={args.zone}"
            if args.dry_run:
                print(cmd)
            else:
                run = subprocess.Popen(
                    cmd,
                    shell=True, stdout=subprocess.PIPE)
                cmd_out, cmd_err = run.communicate()
    print('exiting...')
