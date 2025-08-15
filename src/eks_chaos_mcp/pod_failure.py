"""Pod failure simulation module for chaos engineering."""

import subprocess
import json

def list_pods():
    """List all pods across all namespaces in tabular format."""
    try:
        result = subprocess.run(
            "kubectl get pods --all-namespaces -o json",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            pods_data = json.loads(result.stdout)
            namespaces = {}
            
            for pod in pods_data['items']:
                namespace = pod['metadata']['namespace']
                pod_name = pod['metadata']['name']
                status = pod['status']['phase']
                node = pod['spec'].get('nodeName', 'N/A')
                
                if namespace not in namespaces:
                    namespaces[namespace] = []
                
                namespaces[namespace].append({
                    'name': pod_name,
                    'status': status,
                    'node': node
                })
            
            output = "Available Pods by Namespace:\n\n"
            for ns, pods in namespaces.items():
                output += f"Namespace: {ns}\n"
                output += f"{'Pod Name':<50} {'Status':<15} {'Node':<20}\n"
                output += "-" * 85 + "\n"
                for pod in pods:
                    output += f"{pod['name']:<50} {pod['status']:<15} {pod['node']:<20}\n"
                output += "\n"
            
            return output
        else:
            return f"Failed to list pods: {result.stderr}"
    except Exception as e:
        return f"Error listing pods: {e}"

def inject_pod_failure(namespace, pod_name):
    """Inject pod failure for chaos testing."""
    try:
        # First verify the pod exists
        verify_result = subprocess.run(
            f"kubectl get pod {pod_name} -n {namespace}",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if verify_result.returncode != 0:
            return f"Pod {pod_name} not found in namespace {namespace}"
        
        # Delete the pod to simulate failure
        result = subprocess.run(
            f"kubectl delete pod {pod_name} -n {namespace}",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return f"✅ Pod failure simulated: {pod_name} in namespace {namespace} was terminated. Kubernetes will recreate it automatically."
        else:
            return f"Failed to terminate pod {pod_name} in namespace {namespace}: {result.stderr}"
    except Exception as e:
        return f"Failed to inject pod failure for pod {pod_name} in namespace {namespace}: {e}"