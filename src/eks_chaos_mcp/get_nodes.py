"""Module to get node instance IDs from kubectl command."""

import subprocess

def get_node_instance_ids():
    """Get EC2 instance IDs from kubectl command and return as list."""
    try:
        result = subprocess.run(
            "kubectl get nodes -o jsonpath='{.items[*].spec.providerID}'",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            provider_ids = result.stdout.strip().split()
            get_node = [pid.split('/')[-1] for pid in provider_ids if 'aws' in pid]
            return get_node
        return []
    except Exception as e:
        print(f"Error getting node instance IDs: {e}")
        return []

# Get the list of instance IDs
get_node = get_node_instance_ids()