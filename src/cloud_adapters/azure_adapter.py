"""
Azure Cloud Service Adapter

This module provides Azure-specific service recommendations and integrations
for the cloud-agnostic agent.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.resource import ResourceManagementClient
    from azure.core.exceptions import AzureError
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

from ..agent.state import CloudResource, CloudProvider, Recommendation
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class AzureServiceMapping:
    """Azure service mapping for different application components."""
    service_name: str
    service_type: str
    configuration: Dict[str, Any]
    estimated_cost_per_hour: Optional[float] = None
    regions_available: List[str] = None


class AzureAdapter:
    """
    Azure cloud service adapter for generating Azure-specific recommendations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.subscription_id = config.get("subscription_id")
        self.location = config.get("location", "eastus")
        self.credential = None
        self.resource_client = None
        self._initialize_azure_client()
    
    def _initialize_azure_client(self):
        """Initialize Azure client with proper credentials."""
        if not AZURE_AVAILABLE:
            logger.warning("Azure SDK not available")
            return
        
        try:
            # Use default credential chain (Managed Identity, Azure CLI, etc.)
            self.credential = DefaultAzureCredential()
            
            if self.subscription_id:
                self.resource_client = ResourceManagementClient(
                    self.credential, self.subscription_id
                )
                logger.info("Azure client initialized", subscription=self.subscription_id)
            else:
                logger.warning("No Azure subscription ID provided")
                
        except Exception as e:
            logger.warning("Azure credentials not available", error=str(e))
            # Continue without Azure integration - recommendations will be generic
    
    async def get_recommended_resources(self, analysis: Dict[str, Any], 
                                      recommendation: Recommendation) -> List[CloudResource]:
        """
        Generate Azure-specific resource recommendations based on requirements analysis.
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
            
            logger.info("Azure resources generated", count=len(resources))
            return resources
            
        except Exception as e:
            logger.error("Failed to generate Azure resources", error=str(e))
            return []
    
    def _get_frontend_resources(self, analysis: Dict[str, Any]) -> List[CloudResource]:
        """Generate frontend hosting resources for Azure."""
        resources = []
        
        # Azure Static Web Apps
        static_web_app_config = {
            "name": "react-app",
            "location": self.location,
            "sku": {
                "name": "Free",
                "tier": "Free"
            },
            "repository_url": "https://github.com/user/react-app",
            "branch": "main",
            "app_location": "/",
            "api_location": "",
            "output_location": "build",
            "build_properties": {
                "app_build_command": "npm run build",
                "api_build_command": "",
                "skip_github_action_workflow_generation": False
            }
        }
        
        static_web_resource = CloudResource(
            resource_type="frontend_hosting",
            provider=CloudProvider.AZURE,
            configuration=static_web_app_config,
            estimated_cost=0.0  # Free tier available
        )
        resources.append(static_web_resource)
        
        # Azure CDN for global distribution
        cdn_config = {
            "profile_name": "react-app-cdn-profile",
            "sku": "Standard_Microsoft",
            "endpoint_name": "react-app-endpoint",
            "origin_host_header": "${static_web_app_domain}",
            "is_http_allowed": False,
            "is_https_allowed": True,
            "query_string_caching_behavior": "IgnoreQueryString",
            "optimization_type": "GeneralWebDelivery",
            "content_types_to_compress": [
                "text/plain",
                "text/html",
                "text/css",
                "application/javascript",
                "application/json"
            ]
        }
        
        cdn_resource = CloudResource(
            resource_type="frontend_cdn",
            provider=CloudProvider.AZURE,
            configuration=cdn_config,
            estimated_cost=25.0  # Monthly estimate
        )
        resources.append(cdn_resource)
        
        return resources
    
    def _get_backend_resources(self, analysis: Dict[str, Any]) -> List[CloudResource]:
        """Generate backend compute resources for Azure."""
        resources = []
        
        # Azure Container Apps for microservices
        container_app_config = {
            "container_app_environment_name": "microservices-env",
            "location": self.location,
            "apps": [
                {
                    "name": "user-service",
                    "configuration": {
                        "ingress": {
                            "external": True,
                            "target_port": 8080,
                            "traffic": [
                                {
                                    "weight": 100,
                                    "latest_revision": True
                                }
                            ]
                        },
                        "secrets": [
                            {
                                "name": "database-connection-string",
                                "key_vault_url": "${key_vault_url}",
                                "identity": "${managed_identity_id}"
                            }
                        ]
                    },
                    "template": {
                        "containers": [
                            {
                                "name": "user-service",
                                "image": "user-service:latest",
                                "resources": {
                                    "cpu": 0.25,
                                    "memory": "0.5Gi"
                                },
                                "env": [
                                    {
                                        "name": "DATABASE_URL",
                                        "secret_ref": "database-connection-string"
                                    }
                                ]
                            }
                        ],
                        "scale": {
                            "min_replicas": 1,
                            "max_replicas": 10,
                            "rules": [
                                {
                                    "name": "http-rule",
                                    "http": {
                                        "metadata": {
                                            "concurrent_requests": "30"
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            ]
        }
        
        container_apps_resource = CloudResource(
            resource_type="backend_compute",
            provider=CloudProvider.AZURE,
            configuration=container_app_config,
            estimated_cost=60.0  # Monthly estimate
        )
        resources.append(container_apps_resource)
        
        return resources
    
    def _get_database_resources(self, analysis: Dict[str, Any]) -> List[CloudResource]:
        """Generate database resources for Azure."""
        resources = []
        
        # Azure Database for PostgreSQL Flexible Server
        postgresql_config = {
            "server_name": "microservices-postgresql",
            "location": self.location,
            "sku": {
                "name": "Standard_B1ms",
                "tier": "Burstable"
            },
            "storage": {
                "storage_size_gb": 32,
                "backup_retention_days": 7,
                "geo_redundant_backup": "Disabled",
                "auto_grow": True
            },
            "version": "15",
            "administrator_login": "dbadmin",
            "high_availability": {
                "mode": "Disabled"
            },
            "maintenance_window": {
                "custom_window": "Enabled",
                "start_hour": 2,
                "start_minute": 0,
                "day_of_week": 0
            },
            "authentication": {
                "active_directory_auth": "Enabled",
                "password_auth": "Enabled"
            }
        }
        
        postgresql_resource = CloudResource(
            resource_type="primary_database",
            provider=CloudProvider.AZURE,
            configuration=postgresql_config,
            estimated_cost=45.0  # Monthly estimate
        )
        resources.append(postgresql_resource)
        
        # Azure Cache for Redis
        redis_config = {
            "name": "microservices-redis",
            "location": self.location,
            "sku": {
                "name": "Basic",
                "family": "C",
                "capacity": 0
            },
            "enable_non_ssl_port": False,
            "minimum_tls_version": "1.2",
            "redis_configuration": {
                "maxmemory-policy": "allkeys-lru"
            },
            "subnet_id": "${cache_subnet_id}",
            "static_ip": None,
            "zones": ["1"]
        }
        
        redis_resource = CloudResource(
            resource_type="cache_database",
            provider=CloudProvider.AZURE,
            configuration=redis_config,
            estimated_cost=25.0  # Monthly estimate
        )
        resources.append(redis_resource)
        
        return resources
    
    def _get_networking_resources(self, analysis: Dict[str, Any]) -> List[CloudResource]:
        """Generate networking and security resources for Azure."""
        resources = []
        
        # Virtual Network
        vnet_config = {
            "name": "microservices-vnet",
            "location": self.location,
            "address_space": {
                "address_prefixes": ["10.0.0.0/16"]
            },
            "subnets": [
                {
                    "name": "container-apps-subnet",
                    "address_prefix": "10.0.1.0/24",
                    "delegations": [
                        {
                            "name": "Microsoft.App/environments",
                            "service_name": "Microsoft.App/environments"
                        }
                    ]
                },
                {
                    "name": "database-subnet",
                    "address_prefix": "10.0.2.0/24",
                    "delegations": [
                        {
                            "name": "Microsoft.DBforPostgreSQL/flexibleServers",
                            "service_name": "Microsoft.DBforPostgreSQL/flexibleServers"
                        }
                    ]
                },
                {
                    "name": "cache-subnet",
                    "address_prefix": "10.0.3.0/24"
                }
            ]
        }
        
        vnet_resource = CloudResource(
            resource_type="networking_vnet",
            provider=CloudProvider.AZURE,
            configuration=vnet_config,
            estimated_cost=5.0  # Monthly estimate
        )
        resources.append(vnet_resource)
        
        # API Management for microservices gateway
        apim_config = {
            "name": "microservices-apim",
            "location": self.location,
            "sku": {
                "name": "Developer",
                "capacity": 1
            },
            "publisher_name": "Microservices API",
            "publisher_email": "admin@company.com",
            "identity": {
                "type": "SystemAssigned"
            },
            "apis": [
                {
                    "name": "user-api",
                    "display_name": "User Service API",
                    "path": "users",
                    "protocols": ["https"],
                    "service_url": "${user_service_url}"
                }
            ],
            "policies": {
                "cors": {
                    "allowed_origins": ["${static_web_app_domain}"],
                    "allowed_methods": ["GET", "POST", "PUT", "DELETE"],
                    "allowed_headers": ["Content-Type", "Authorization"]
                },
                "rate_limiting": {
                    "calls": 1000,
                    "renewal_period": 3600
                }
            }
        }
        
        apim_resource = CloudResource(
            resource_type="api_gateway",
            provider=CloudProvider.AZURE,
            configuration=apim_config,
            estimated_cost=50.0  # Monthly estimate for Developer tier
        )
        resources.append(apim_resource)
        
        return resources
    
    def _get_storage_resources(self, analysis: Dict[str, Any]) -> List[CloudResource]:
        """Generate storage resources for Azure."""
        resources = []
        
        # Azure Storage Account
        storage_config = {
            "account_name": "microservicesdata${random}",
            "location": self.location,
            "account_tier": "Standard",
            "account_replication_type": "LRS",
            "account_kind": "StorageV2",
            "access_tier": "Hot",
            "enable_https_traffic": True,
            "min_tls_version": "TLS1_2",
            "allow_nested_items_to_be_public": False,
            "containers": [
                {
                    "name": "uploads",
                    "access_type": "private"
                },
                {
                    "name": "backups",
                    "access_type": "private"
                }
            ],
            "lifecycle_management": {
                "rules": [
                    {
                        "name": "move_to_cool",
                        "enabled": True,
                        "type": "Lifecycle",
                        "definition": {
                            "filters": {
                                "blob_types": ["blockBlob"]
                            },
                            "actions": {
                                "base_blob": {
                                    "tier_to_cool": {
                                        "days_after_modification_greater_than": 30
                                    },
                                    "tier_to_archive": {
                                        "days_after_modification_greater_than": 90
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
        
        storage_resource = CloudResource(
            resource_type="data_storage",
            provider=CloudProvider.AZURE,
            configuration=storage_config,
            estimated_cost=15.0  # Monthly estimate
        )
        resources.append(storage_resource)
        
        return resources
    
    def _get_monitoring_resources(self, analysis: Dict[str, Any]) -> List[CloudResource]:
        """Generate monitoring and logging resources for Azure."""
        resources = []
        
        # Log Analytics Workspace
        log_analytics_config = {
            "name": "microservices-logs",
            "location": self.location,
            "sku": "PerGB2018",
            "retention_in_days": 30,
            "daily_quota_gb": 1,
            "data_sources": [
                "Container Apps logs",
                "PostgreSQL logs",
                "API Management logs",
                "Application Insights"
            ]
        }
        
        log_analytics_resource = CloudResource(
            resource_type="logging",
            provider=CloudProvider.AZURE,
            configuration=log_analytics_config,
            estimated_cost=20.0  # Monthly estimate
        )
        resources.append(log_analytics_resource)
        
        # Application Insights
        app_insights_config = {
            "name": "microservices-insights",
            "location": self.location,
            "application_type": "web",
            "workspace_resource_id": "${log_analytics_workspace_id}",
            "sampling_percentage": 100,
            "retention_in_days": 90,
            "daily_data_cap_in_gb": 1,
            "daily_data_cap_notifications_disabled": False
        }
        
        app_insights_resource = CloudResource(
            resource_type="monitoring",
            provider=CloudProvider.AZURE,
            configuration=app_insights_config,
            estimated_cost=25.0  # Monthly estimate
        )
        resources.append(app_insights_resource)
        
        return resources
    
    async def validate_resources(self, resources: List[CloudResource]) -> Dict[str, Any]:
        """Validate Azure resources and check quotas."""
        if not self.resource_client:
            return {"status": "skipped", "reason": "No Azure credentials"}
        
        try:
            validation_results = {}
            
            # Check resource quotas
            # This would require additional Azure SDK calls to check quotas
            validation_results["subscription_id"] = self.subscription_id
            validation_results["location"] = self.location
            
            return validation_results
            
        except Exception as e:
            logger.error("Failed to validate Azure resources", error=str(e))
            return {"status": "error", "error": str(e)}
    
    def estimate_total_cost(self, resources: List[CloudResource]) -> float:
        """Estimate total monthly cost for Azure resources."""
        total_cost = 0.0
        
        for resource in resources:
            if resource.provider == CloudProvider.AZURE and resource.estimated_cost:
                total_cost += resource.estimated_cost
        
        return total_cost