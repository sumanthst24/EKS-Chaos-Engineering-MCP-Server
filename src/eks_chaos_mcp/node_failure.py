import boto3
import os
import subprocess
import random

region = os.getenv('AWS_REGION', 'us-east-1')
ec2_client = boto3.client('ec2', region_name=region)

def get_nodes_with_pods():
    """Get nodes with running pods."""
    try:
        # Get all ready nodes first
        result = subprocess.run(
            "kubectl get nodes --no-headers | grep ' Ready ' | awk '{print $1}'",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            all_nodes = [node.strip() for node in result.stdout.strip().split('\n') if node.strip()]
            
            # Filter nodes that actually have pods running
            nodes_with_pods = []
            for node in all_nodes:
                pod_check = subprocess.run(
                    f"kubectl get pods --all-namespaces --field-selector spec.nodeName={node} --no-headers | wc -l",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if pod_check.returncode == 0 and int(pod_check.stdout.strip()) > 0:
                    nodes_with_pods.append(node)
            
            return nodes_with_pods
        return []
    except Exception as e:
        print(f"Error getting nodes with pods: {e}")
        return []

def get_instance_id_by_node(node_name):
    """Get EC2 instance ID for a given node."""
    try:
        # First try using kubectl to get the provider ID which contains the instance ID
        result = subprocess.run(
            f"kubectl get node {node_name} -o jsonpath='{{.spec.providerID}}'",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and 'aws' in result.stdout:
            # Extract instance ID from providerID (format: aws:///ZONE/INSTANCE_ID)
            provider_id = result.stdout.strip()
            if provider_id and '/' in provider_id:
                instance_id = provider_id.split('/')[-1]
                if instance_id.startswith('i-'):
                    return instance_id
        
        # Fallback to EC2 API if kubectl method fails
        response = ec2_client.describe_instances(
            Filters=[
                {'Name': 'private-dns-name', 'Values': [node_name]}
            ]
        )
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                return instance['InstanceId']
        
        print(f"Could not find instance ID for node {node_name}")
        return None
    except Exception as e:
        print(f"Error getting instance ID for node {node_name}: {e}")
        return None

def simulate_node_failure() -> str:
    """Simulate node failure by stopping an EC2 instance with running pods."""
    nodes_with_pods = get_nodes_with_pods()
    
    if not nodes_with_pods:
        return "No nodes with running pods found. Please verify cluster state."
    
    selected_node = random.choice(nodes_with_pods)
    instance_id = get_instance_id_by_node(selected_node)
    
    if not instance_id:
        return f"Could not find instance ID for node: {selected_node}"
    
    try:
        response = ec2_client.stop_instances(InstanceIds=[instance_id])
        return f"✅ Node failure simulated: Stopping instance {instance_id} (Node: {selected_node}). Monitoring pod distribution..."
    except Exception as e:
        return f"Failed to stop instance {instance_id}: {e}"