# EKS Chaos Engineering MCP Server

A Model Context Protocol (MCP) server for chaos engineering testing on Amazon EKS clusters.

## Features

- **Pod Failure Simulation**: Target specific pods or UI pods for resilience testing
- **Node Failure Simulation**: Stop EC2 instances to test node-level failures
- **AZ Failure Simulation**: Simulate availability zone failures
- **Universal Compatibility**: Works with any Kubernetes application deployed on EKS

## Installation

### From PyPI (recommended)

```bash
pip install eks-chaos-mcp
```

### From Source

```bash
git clone https://github.com/sumanthst24/EKS-Chaos-Engineering-MCP-Server.git
cd EKS-Chaos-Engineering-MCP-Server
pip install -e .
```

## Prerequisites

- Python 3.8+
- kubectl configured for your EKS cluster
- AWS CLI configured with appropriate permissions
- EKS cluster with any Kubernetes application deployed

## Configuration

1. Copy the example configuration:
```bash
cp mcp.json.example mcp.json
```

2. Update `mcp.json` with your environment:

```json
{
  "mcpServers": {
    "eks_chaos_mcp": {
      "command": "eks-chaos-mcp",
      "env": {
        "AWS_REGION": "your-aws-region",
        "AWS_PROFILE": "your-aws-profile"
      }
    }
  }
}
```

## Available Tools

- `list_pods_for_failure`: List all pods across all namespaces
- `simulate_pod_failure`: Delete specific pods to test resilience
- `simulate_node_failure`: Stop EC2 instances with running pods
- `simulate_az_failure`: Simulate availability zone failures

## Usage

### With MCP Client

Start the MCP server and use with compatible MCP clients like Amazon Q Developer.

### Direct Execution

```bash
# Run the server directly
eks-chaos-mcp

# Or using Python module
python -m eks_chaos_mcp
```

## Development

```bash
# Clone the repository
git clone https://github.com/sumanthst24/EKS-Chaos-Engineering-MCP-Server.git
cd EKS-Chaos-Engineering-MCP-Server

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
isort src/
```

## Security Notes

- Never commit `mcp.json` with real credentials
- Use appropriate AWS IAM permissions
- Test in non-production environments first
- Sanitize logs before sharing

## Testing Results

Here are example results from chaos engineering tests:

### Available MCP Tools
```
eks_chaos_mcp (MCP):
- list_pods_for_failure         * List all pods across namespaces
- simulate_pod_failure          * Delete specific pods to test resilience  
- simulate_node_failure         * Stop EC2 instances with running pods
- simulate_az_failure           * Simulate availability zone failures
```

### Pod Listing
```
> List the pods for failure

✅ Successfully listed pods across all namespaces:

### Default Namespace
• nginx-deployment-xxxxxxxxx-xxxxx (Running on ip-xx-xx-xxx-xxx)
• redis-xxxxxxxxx-xxxxx (Running on ip-xx-xx-xxx-xxx)

### Kube-system Namespace  
• coredns-xxxxxxxxx-xxxxx (Running on ip-xx-xx-xxx-xxx)
• aws-node-xxxxxxxxx (Running on ip-xx-xx-xxx-xxx)

### [Additional namespaces and pods...]
```

### Pod Failure Simulation
```
> Simulate pod failure for nginx pod in default namespace

✅ Pod failure simulated: nginx-deployment-xxxxxxxxx-xxxxx in namespace default was terminated.

Kubernetes automatically recreated the pod to maintain desired replicas.
Service continued functioning with remaining healthy pods during recreation.
```

### Node Failure Simulation
```
> Simulate node failure

✅ Node failure simulated: Stopping instance i-xxxxxxxxxxxxxxxxx (Node: ip-xx-xx-xxx-xxx.region.compute.internal).

Successfully stopped EC2 instance corresponding to Kubernetes node. All pods on the node were affected:
• Application pods: Rescheduled to healthy nodes
• System pods: Automatically recreated on available nodes  
• Persistent volumes: Remounted on new pod locations

Kubernetes control plane successfully handled node failure and maintained application availability.
```

### AZ Failure Simulation
```
> Simulate AZ level failure

✅ AZ failure simulated: Stopped X instances across multiple availability zones.

Multi-AZ failure test completed:
- Affected nodes in zone-a and zone-b
- Forced pod rescheduling to remaining healthy zones
- Tested cluster capacity and autoscaling capabilities
- Verified application resilience across availability zones

Application demonstrated high availability and proper AZ failure resilience.
```

## Project Structure

```
eks-chaos-mcp/
├── src/eks_chaos_mcp/          # Main package
│   ├── __init__.py             # Package initialization
│   ├── __main__.py             # Python -m execution
│   ├── server.py               # Main MCP server
│   ├── pod_failure.py          # Pod chaos functions
│   ├── node_failure.py         # Node chaos functions
│   ├── az_failure.py           # AZ chaos functions
│   └── get_nodes.py            # Utility functions
├── pyproject.toml              # Modern Python packaging
├── README.md                   # Documentation
├── LICENSE                     # MIT license
├── .gitignore                  # Git ignore rules
└── mcp.json.example            # Configuration template
```

## License

MIT License - see [LICENSE](LICENSE) file for details.