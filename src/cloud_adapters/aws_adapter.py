"""
AWS Cloud Service Adapter

This module provides AWS-specific service recommendations and integrations
for the cloud-agnostic agent.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from ..agent.state import CloudResource, CloudProvider, Recommendation
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class AWSServiceMapping:
    """AWS service mapping for different application components."""
    service_name: str
    service_type: str
    configuration: Dict[str, Any]
    estimated_cost_per_hour: Optional[float] = None
    regions_available: List[str] = None


class AWSAdapter:
    """
    AWS cloud service adapter for generating AWS-specific recommendations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.region = config.get("region", "us-east-1")
        self.session = None
        self._initialize_aws_session()
    
    def _initialize_aws_session(self):
        """Initialize AWS session with proper credentials."""
        try:
            # Use default credential chain (IAM roles, environment variables, etc.)
            self.session = boto3.Session(region_name=self.region)
            
            # Test credentials
            sts = self.session.client('sts')
            identity = sts.get_caller_identity()
            logger.info("AWS session initialized", account=identity.get("Account"))
            
        except (NoCredentialsError, ClientError) as e:
            logger.warning("AWS credentials not available", error=str(e))
            # Continue without AWS integration - recommendations will be generic
    
    async def get_recommended_resources(self, analysis: Dict[str, Any], 
                                      recommendation: Recommendation) -> List[CloudResource]:
        """
        Generate AWS-specific resource recommendations based on requirements analysis.
        """
        try:
            resources = []
            
            # Frontend hosting resources
            frontend_resources = self._get_frontend_resources(analysis)
            resources.extend(frontend_resources)
            
            # Backend compute resources
            backend_resources = self._get_backend_resources(analysis)
            resources.extend(backend_resources)
            
            # Database resources
            database_resources = self._get_database_resources(analysis)
            resources.extend(database_resources)
            
            # Networking and security resources
            networking_resources = self._get_networking_resources(analysis)
            resources.extend(networking_resources)
            
            # Storage resources
            storage_resources = self._get_storage_resources(analysis)
            resources.extend(storage_resources)
            
            # Monitoring and logging resources
            monitoring_resources = self._get_monitoring_resources(analysis)
            resources.extend(monitoring_resources)
            
            logger.info("AWS resources generated", count=len(resources))
            return resources
            
        except Exception as e:
            logger.error("Failed to generate AWS resources", error=str(e))
            return []
    
    def _get_frontend_resources(self, analysis: Dict[str, Any]) -> List[CloudResource]:
        """Generate frontend hosting resources for AWS."""
        resources = []
        
        # S3 + CloudFront for static site hosting
        s3_config = {
            "bucket_name": "react-app-${random}",
            "website_configuration": {
                "index_document": "index.html",
                "error_document": "error.html"
            },
            "public_access": False,
            "versioning": True
        }
        
        s3_resource = CloudResource(
            resource_type="frontend_storage",
            provider=CloudProvider.AWS,
            configuration=s3_config,
            estimated_cost=5.0  # Monthly estimate
        )
        resources.append(s3_resource)
        
        # CloudFront CDN
        cloudfront_config = {
            "origin_domain": "${s3_bucket_domain}",
            "price_class": "PriceClass_100",
            "cache_behaviors": {
                "default": {
                    "target_origin_id": "S3Origin",
                    "viewer_protocol_policy": "redirect-to-https",
                    "compress": True
                }
            },
            "custom_error_responses": [
                {
                    "error_code": 404,
                    "response_page_path": "/index.html",
                    "response_code": 200
                }
            ]
        }
        
        cloudfront_resource = CloudResource(
            resource_type="frontend_cdn",
            provider=CloudProvider.AWS,
            configuration=cloudfront_config,
            estimated_cost=20.0  # Monthly estimate
        )
        resources.append(cloudfront_resource)
        
        return resources
    
    def _get_backend_resources(self, analysis: Dict[str, Any]) -> List[CloudResource]:
        """Generate backend compute resources for AWS."""
        resources = []
        
        # ECS Fargate for containerized microservices
        ecs_config = {
            "cluster_name": "java-microservices-cluster",
            "launch_type": "FARGATE",
            "services": [
                {
                    "service_name": "user-service",
                    "task_definition": {
                        "family": "user-service",
                        "cpu": "256",
                        "memory": "512",
                        "network_mode": "awsvpc",
                        "requires_attributes": ["ecs.capability.execution-role-awsvpc"]
                    },
                    "desired_count": 2
                }
            ],
            "auto_scaling": {
                "min_capacity": 1,
                "max_capacity": 10,
                "target_cpu_utilization": 70
            }
        }
        
        ecs_resource = CloudResource(
            resource_type="backend_compute",
            provider=CloudProvider.AWS,
            configuration=ecs_config,
            estimated_cost=50.0  # Monthly estimate for 2 services
        )
        resources.append(ecs_resource)
        
        # Application Load Balancer
        alb_config = {
            "name": "microservices-alb",
            "scheme": "internet-facing",
            "type": "application",
            "ip_address_type": "ipv4",
            "listeners": [
                {
                    "port": 80,
                    "protocol": "HTTP",
                    "default_action": {
                        "type": "redirect",
                        "redirect_config": {
                            "protocol": "HTTPS",
                            "port": "443",
                            "status_code": "HTTP_301"
                        }
                    }
                },
                {
                    "port": 443,
                    "protocol": "HTTPS",
                    "ssl_policy": "ELBSecurityPolicy-TLS-1-2-2017-01"
                }
            ]
        }
        
        alb_resource = CloudResource(
            resource_type="backend_loadbalancer",
            provider=CloudProvider.AWS,
            configuration=alb_config,
            estimated_cost=25.0  # Monthly estimate
        )
        resources.append(alb_resource)
        
        return resources
    
    def _get_database_resources(self, analysis: Dict[str, Any]) -> List[CloudResource]:
        """Generate database resources for AWS."""
        resources = []
        
        # RDS PostgreSQL for primary database
        rds_config = {
            "db_instance_identifier": "microservices-db",
            "engine": "postgres",
            "engine_version": "15.4",
            "db_instance_class": "db.t3.micro",
            "allocated_storage": 20,
            "storage_type": "gp2",
            "storage_encrypted": True,
            "multi_az": True,
            "publicly_accessible": False,
            "backup_retention_period": 7,
            "deletion_protection": True,
            "performance_insights_enabled": True
        }
        
        rds_resource = CloudResource(
            resource_type="primary_database",
            provider=CloudProvider.AWS,
            configuration=rds_config,
            estimated_cost=35.0  # Monthly estimate
        )
        resources.append(rds_resource)
        
        # ElastiCache Redis for caching
        redis_config = {
            "cache_cluster_id": "microservices-cache",
            "engine": "redis",
            "engine_version": "7.0",
            "cache_node_type": "cache.t3.micro",
            "num_cache_nodes": 1,
            "port": 6379,
            "security_group_ids": ["${redis_security_group}"],
            "subnet_group_name": "${cache_subnet_group}",
            "at_rest_encryption_enabled": True,
            "transit_encryption_enabled": True
        }
        
        redis_resource = CloudResource(
            resource_type="cache_database",
            provider=CloudProvider.AWS,
            configuration=redis_config,
            estimated_cost=20.0  # Monthly estimate
        )
        resources.append(redis_resource)
        
        return resources
    
    def _get_networking_resources(self, analysis: Dict[str, Any]) -> List[CloudResource]:
        """Generate networking and security resources for AWS."""
        resources = []
        
        # VPC configuration
        vpc_config = {
            "cidr_block": "10.0.0.0/16",
            "enable_dns_hostnames": True,
            "enable_dns_support": True,
            "subnets": [
                {
                    "cidr_block": "10.0.1.0/24",
                    "availability_zone": f"{self.region}a",
                    "type": "public"
                },
                {
                    "cidr_block": "10.0.2.0/24",
                    "availability_zone": f"{self.region}b",
                    "type": "public"
                },
                {
                    "cidr_block": "10.0.3.0/24",
                    "availability_zone": f"{self.region}a",
                    "type": "private"
                },
                {
                    "cidr_block": "10.0.4.0/24",
                    "availability_zone": f"{self.region}b",
                    "type": "private"
                }
            ]
        }
        
        vpc_resource = CloudResource(
            resource_type="networking_vpc",
            provider=CloudProvider.AWS,
            configuration=vpc_config,
            estimated_cost=0.0  # VPC itself is free
        )
        resources.append(vpc_resource)
        
        # API Gateway for microservices
        api_gateway_config = {
            "name": "microservices-api",
            "description": "API Gateway for Java microservices",
            "endpoint_type": "REGIONAL",
            "policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "execute-api:Invoke",
                        "Resource": "*"
                    }
                ]
            },
            "cors_configuration": {
                "allow_origins": ["https://${cloudfront_domain}"],
                "allow_headers": ["Content-Type", "Authorization"],
                "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
            }
        }
        
        api_gateway_resource = CloudResource(
            resource_type="api_gateway",
            provider=CloudProvider.AWS,
            configuration=api_gateway_config,
            estimated_cost=15.0  # Monthly estimate
        )
        resources.append(api_gateway_resource)
        
        return resources
    
    def _get_storage_resources(self, analysis: Dict[str, Any]) -> List[CloudResource]:
        """Generate storage resources for AWS."""
        resources = []
        
        # S3 bucket for application data
        s3_data_config = {
            "bucket_name": "microservices-data-${random}",
            "versioning": True,
            "encryption": {
                "sse_algorithm": "AES256"
            },
            "lifecycle_configuration": {
                "rules": [
                    {
                        "id": "transition_to_ia",
                        "status": "Enabled",
                        "transitions": [
                            {
                                "days": 30,
                                "storage_class": "STANDARD_IA"
                            },
                            {
                                "days": 90,
                                "storage_class": "GLACIER"
                            }
                        ]
                    }
                ]
            }
        }
        
        s3_data_resource = CloudResource(
            resource_type="data_storage",
            provider=CloudProvider.AWS,
            configuration=s3_data_config,
            estimated_cost=10.0  # Monthly estimate
        )
        resources.append(s3_data_resource)
        
        return resources
    
    def _get_monitoring_resources(self, analysis: Dict[str, Any]) -> List[CloudResource]:
        """Generate monitoring and logging resources for AWS."""
        resources = []
        
        # CloudWatch for monitoring
        cloudwatch_config = {
            "log_groups": [
                {
                    "name": "/aws/ecs/microservices",
                    "retention_in_days": 14
                },
                {
                    "name": "/aws/apigateway/microservices-api",
                    "retention_in_days": 14
                }
            ],
            "dashboards": [
                {
                    "name": "microservices-dashboard",
                    "widgets": [
                        "ECS CPU/Memory metrics",
                        "API Gateway latency and errors",
                        "RDS connections and performance",
                        "Application custom metrics"
                    ]
                }
            ],
            "alarms": [
                {
                    "name": "high-cpu-utilization",
                    "metric_name": "CPUUtilization",
                    "threshold": 80,
                    "comparison_operator": "GreaterThanThreshold"
                }
            ]
        }
        
        cloudwatch_resource = CloudResource(
            resource_type="monitoring",
            provider=CloudProvider.AWS,
            configuration=cloudwatch_config,
            estimated_cost=30.0  # Monthly estimate
        )
        resources.append(cloudwatch_resource)
        
        return resources
    
    async def validate_resources(self, resources: List[CloudResource]) -> Dict[str, Any]:
        """Validate AWS resources and check quotas."""
        if not self.session:
            return {"status": "skipped", "reason": "No AWS credentials"}
        
        try:
            validation_results = {}
            
            # Check service quotas
            service_quotas = self.session.client('service-quotas')
            
            # Validate ECS quotas
            ecs_quota = service_quotas.get_service_quota(
                ServiceCode='ecs',
                QuotaCode='L-34375BF1'  # Services per cluster
            )
            validation_results["ecs_quota"] = ecs_quota.get("Quota", {}).get("Value")
            
            return validation_results
            
        except Exception as e:
            logger.error("Failed to validate AWS resources", error=str(e))
            return {"status": "error", "error": str(e)}
    
    def estimate_total_cost(self, resources: List[CloudResource]) -> float:
        """Estimate total monthly cost for AWS resources."""
        total_cost = 0.0
        
        for resource in resources:
            if resource.provider == CloudProvider.AWS and resource.estimated_cost:
                total_cost += resource.estimated_cost
        
        return total_cost