CONFIG = {
    "pipeline": {
        "account": "140231462341",
        "region": "ap-south-1",
    },
    "dev": {
        "account": "531271033878",
        "region": "ap-south-1",
        "manual_approval_required_for_deployment": False,
        "debug": False,
        "enable_cors": True,
        "ecs": {
            "memory_limit_mib": 1024,
            "cpu": 512,
            "desired_count": 1,
            "min_count": 1,
            "max_count": 3,
            "scaling_target_cpu_utilization": 70,
        },
        "alb": {
            "target_group_priority": 4,
        },
    },
    "stg": {
        "account": "586112330472",
        "region": "ap-south-1",
        "manual_approval_required_for_deployment": True,
        "debug": False,
        "enable_cors": True,
        "ecs": {
            "memory_limit_mib": 1024,
            "cpu": 512,
            "desired_count": 1,
            "min_count": 1,
            "max_count": 3,
            "scaling_target_cpu_utilization": 70,
        },
        "alb": {
            "target_group_priority": 4,
        },
    },
}
