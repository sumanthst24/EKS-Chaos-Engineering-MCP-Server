import boto3
import os
import subprocess
import random
from collections import defaultdict

region = os.getenv('AWS_REGION', 'us-east-1')
ec2_client = boto3.client('ec2', region_name=region)

def get_current_region():
    """Get current region from kubectl context."""
    try:
        result = subprocess.run(
            "kubectl config view -o jsonpath=\"{.contexts[?(@.name == \\\"$(kubectl config current-context)\\\")].context.cluster}\" | cut -d : -f 4",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        return region
    except Exception:
        return region

def get_nodes_by_az():
    """Get nodes grouped by availability zone (workshop pattern)."""
    az_nodes = defaultdict(list)
    
    try:
        # Get all nodes with their AZs
        result = subprocess.run(
            "kubectl get nodes -L topology.kubernetes.io/zone --no-headers | grep -v NotReady",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            node_lines = result.stdout.strip().split('\n')
            
            for line in node_lines:
                parts = line.split()
                if len(parts) >= 6:  # Ensure we have enough columns
                    node_name = parts[0]
                    az = parts[-1]  # Zone is the last column
                    
                    # Get instance ID using the improved function
                    instance_id = get_instance_id_by_node(node_name)
                    
                    if instance_id:
                        az_nodes[az].append({
                            'node_name': node_name,
                            'instance_id': instance_id
                        })
        
        return dict(az_nodes)
    except Exception as e:
        print(f"Error getting nodes by AZ: {e}")
        return {}

def get_pods_in_az(az):
    """Get UI pods in specific AZ (workshop focuses on UI namespace)."""
    try:
        result = subprocess.run(
            f"kubectl get nodes -l topology.kubernetes.io/zone={az} --no-headers | grep -v NotReady | cut -d ' ' -f1",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            nodes = [node.strip() for node in result.stdout.strip().split('\n') if node.strip()]
            pod_count = 0
            
            for node in nodes:
                pod_result = subprocess.run(
                    f"kubectl get pods -n ui --no-headers --field-selector spec.nodeName={node} | wc -l",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if pod_result.returncode == 0:
                    pod_count += int(pod_result.stdout.strip())
            
            return pod_count
        return 0
    except Exception as e:
        print(f"Error getting pods in AZ {az}: {e}")
        return 0

def simulate_az_failure() -> str:
    """Simulate AZ failure by stopping all instances in a selected AZ."""
    az_nodes = get_nodes_by_az()
    
    if not az_nodes:
        return "No worker nodes found in any AZ"
    
    # Show nodes and pods per AZ (workshop pattern)
    output = "Current distribution by Availability Zone:\n\n"
    for az, nodes in az_nodes.items():
        pod_count = get_pods_in_az(az)
        output += f"------ {az} ------\n"
        output += f"  Nodes: {len(nodes)}\n"
        output += f"  UI Pods: {pod_count}\n"
        for node in nodes:
            output += f"    {node['node_name']}: {node['instance_id']}\n"
        output += "\n"
    
    # Select AZ with nodes
    available_azs = [az for az, nodes in az_nodes.items() if nodes]
    if not available_azs:
        return "No AZs with worker nodes found"
    
    selected_az = random.choice(available_azs)
    instances_to_stop = [node['instance_id'] for node in az_nodes[selected_az]]
    
    if not instances_to_stop:
        return f"No instance IDs found for nodes in AZ {selected_az}"
    
    output += f"Selected AZ for failure simulation: {selected_az}\n"
    output += f"Stopping {len(instances_to_stop)} instances in AZ {selected_az}\n"
    
    try:
        # Use stop_instances instead of terminate_instances for safer testing
        response = ec2_client.stop_instances(InstanceIds=instances_to_stop)
        output += f"✅ AZ failure simulated: Stopped {len(instances_to_stop)} instances in AZ {selected_az}. Monitor pod redistribution across remaining AZs."
        return output
    except Exception as e:
        return f"Error stopping instances in AZ {selected_az}: {e}"