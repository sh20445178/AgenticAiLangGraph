"""
Java Spring Boot Microservices Template Generator

This module generates Spring Boot microservices templates with cloud-agnostic configurations
for both AWS and Azure deployments.
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class JavaTemplateConfig:
    """Configuration for Java microservices template generation."""
    service_name: str
    group_id: str
    artifact_id: str
    package_name: str
    cloud_provider: str
    database_type: str = "postgresql"
    cache_enabled: bool = True
    security_enabled: bool = True
    monitoring_enabled: bool = True
    java_version: str = "17"
    spring_boot_version: str = "3.2.0"


class JavaTemplateGenerator:
    """
    Generates Spring Boot microservices templates with cloud-agnostic configurations.
    """
    
    def __init__(self):
        self.template_base_path = os.path.dirname(__file__)
    
    def generate_template(self, config: JavaTemplateConfig) -> Dict[str, str]:
        """
        Generate a complete Spring Boot microservices template.
        """
        try:
            template_files = {}
            
            # Generate pom.xml
            template_files["pom.xml"] = self._generate_pom_xml(config)
            
            # Generate main application class
            template_files[f"src/main/java/{config.package_name.replace('.', '/')}/Application.java"] = self._generate_main_class(config)
            
            # Generate application properties
            template_files["src/main/resources/application.yml"] = self._generate_application_yml(config)
            
            # Generate cloud-specific configurations
            if config.cloud_provider.lower() == "aws":
                template_files.update(self._generate_aws_config(config))
            elif config.cloud_provider.lower() == "azure":
                template_files.update(self._generate_azure_config(config))
            
            # Generate entity classes
            template_files.update(self._generate_entity_classes(config))
            
            # Generate repository layer
            template_files.update(self._generate_repository_layer(config))
            
            # Generate service layer
            template_files.update(self._generate_service_layer(config))
            
            # Generate controller layer
            template_files.update(self._generate_controller_layer(config))
            
            # Generate configuration classes
            template_files.update(self._generate_configuration_classes(config))
            
            # Generate security configuration
            if config.security_enabled:
                template_files.update(self._generate_security_config(config))
            
            # Generate Docker configuration
            template_files.update(self._generate_docker_config(config))
            
            # Generate test files
            template_files.update(self._generate_test_files(config))
            
            logger.info("Java microservices template generated successfully", 
                       service_name=config.service_name, 
                       files_count=len(template_files))
            
            return template_files
            
        except Exception as e:
            logger.error("Failed to generate Java template", error=str(e))
            raise
    
    def _generate_pom_xml(self, config: JavaTemplateConfig) -> str:
        """Generate pom.xml with appropriate dependencies."""
        cloud_dependencies = ""
        
        if config.cloud_provider.lower() == "aws":
            cloud_dependencies = '''
        <!-- AWS Dependencies -->
        <dependency>
            <groupId>io.awspring.cloud</groupId>
            <artifactId>spring-cloud-aws-starter</artifactId>
        </dependency>
        <dependency>
            <groupId>software.amazon.awssdk</groupId>
            <artifactId>s3</artifactId>
        </dependency>
        <dependency>
            <groupId>software.amazon.awssdk</groupId>
            <artifactId>rds</artifactId>
        </dependency>'''
        elif config.cloud_provider.lower() == "azure":
            cloud_dependencies = '''
        <!-- Azure Dependencies -->
        <dependency>
            <groupId>com.azure.spring</groupId>
            <artifactId>spring-cloud-azure-starter</artifactId>
        </dependency>
        <dependency>
            <groupId>com.azure</groupId>
            <artifactId>azure-storage-blob</artifactId>
        </dependency>
        <dependency>
            <groupId>com.azure</groupId>
            <artifactId>azure-keyvault-secrets</artifactId>
        </dependency>'''
        
        database_dependencies = ""
        if config.database_type == "postgresql":
            database_dependencies = '''
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <scope>runtime</scope>
        </dependency>'''
        elif config.database_type == "mysql":
            database_dependencies = '''
        <dependency>
            <groupId>com.mysql</groupId>
            <artifactId>mysql-connector-j</artifactId>
            <scope>runtime</scope>
        </dependency>'''
        
        security_dependencies = ""
        if config.security_enabled:
            security_dependencies = '''
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
        </dependency>'''
        
        cache_dependencies = ""
        if config.cache_enabled:
            cache_dependencies = '''
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-redis</artifactId>
        </dependency>'''
        
        monitoring_dependencies = ""
        if config.monitoring_enabled:
            monitoring_dependencies = '''
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
        <dependency>
            <groupId>io.micrometer</groupId>
            <artifactId>micrometer-registry-prometheus</artifactId>
        </dependency>'''
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>{config.spring_boot_version}</version>
        <relativePath/>
    </parent>

    <groupId>{config.group_id}</groupId>
    <artifactId>{config.artifact_id}</artifactId>
    <version>1.0.0</version>
    <name>{config.service_name}</name>
    <description>Cloud-agnostic microservice for {config.service_name}</description>
    <packaging>jar</packaging>

    <properties>
        <java.version>{config.java_version}</java.version>
        <spring-cloud.version>2023.0.0</spring-cloud.version>
        <testcontainers.version>1.19.0</testcontainers.version>
    </properties>

    <dependencies>
        <!-- Spring Boot Starters -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-logging</artifactId>
        </dependency>
        {database_dependencies}
        {cache_dependencies}
        {security_dependencies}
        {monitoring_dependencies}
        {cloud_dependencies}

        <!-- Utility Dependencies -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-configuration-processor</artifactId>
            <optional>true</optional>
        </dependency>
        <dependency>
            <groupId>org.mapstruct</groupId>
            <artifactId>mapstruct</artifactId>
            <version>1.5.5.Final</version>
        </dependency>

        <!-- Test Dependencies -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.testcontainers</groupId>
            <artifactId>junit-jupiter</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.testcontainers</groupId>
            <artifactId>postgresql</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>${{spring-cloud.version}}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
            <dependency>
                <groupId>org.testcontainers</groupId>
                <artifactId>testcontainers-bom</artifactId>
                <version>${{testcontainers.version}}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
                <configuration>
                    <source>{config.java_version}</source>
                    <target>{config.java_version}</target>
                    <annotationProcessorPaths>
                        <path>
                            <groupId>org.mapstruct</groupId>
                            <artifactId>mapstruct-processor</artifactId>
                            <version>1.5.5.Final</version>
                        </path>
                    </annotationProcessorPaths>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>'''
    
    def _generate_main_class(self, config: JavaTemplateConfig) -> str:
        """Generate main application class."""
        class_name = "".join(word.capitalize() for word in config.service_name.split("-")) + "Application"
        
        annotations = ["@SpringBootApplication"]
        if config.cache_enabled:
            annotations.append("@EnableCaching")
        if config.monitoring_enabled:
            annotations.append("@EnableScheduling")
        
        return f'''package {config.package_name};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.scheduling.annotation.EnableScheduling;

{chr(10).join(annotations)}
public class {class_name} {{

    public static void main(String[] args) {{
        SpringApplication.run({class_name}.class, args);
    }}
}}'''
    
    def _generate_application_yml(self, config: JavaTemplateConfig) -> str:
        """Generate application.yml configuration."""
        database_config = ""
        
        if config.database_type == "postgresql":
            database_config = '''
  datasource:
    url: jdbc:postgresql://${DATABASE_HOST:localhost}:${DATABASE_PORT:5432}/${DATABASE_NAME:microservices}
    username: ${DATABASE_USERNAME:postgres}
    password: ${DATABASE_PASSWORD:password}
    driver-class-name: org.postgresql.Driver'''
        elif config.database_type == "mysql":
            database_config = '''
  datasource:
    url: jdbc:mysql://${DATABASE_HOST:localhost}:${DATABASE_PORT:3306}/${DATABASE_NAME:microservices}
    username: ${DATABASE_USERNAME:root}
    password: ${DATABASE_PASSWORD:password}
    driver-class-name: com.mysql.cj.jdbc.Driver'''
        
        cache_config = ""
        if config.cache_enabled:
            cache_config = '''
  data:
    redis:
      host: ${REDIS_HOST:localhost}
      port: ${REDIS_PORT:6379}
      password: ${REDIS_PASSWORD:}
      timeout: 2000ms
      lettuce:
        pool:
          max-active: 8
          max-idle: 8
          min-idle: 0'''
        
        security_config = ""
        if config.security_enabled:
            if config.cloud_provider.lower() == "aws":
                security_config = '''
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: ${JWT_ISSUER_URI:}
          jwk-set-uri: ${JWT_JWK_SET_URI:}'''
            elif config.cloud_provider.lower() == "azure":
                security_config = '''
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://login.microsoftonline.com/${AZURE_TENANT_ID}/v2.0
          jwk-set-uri: https://login.microsoftonline.com/${AZURE_TENANT_ID}/discovery/v2.0/keys'''
        
        monitoring_config = ""
        if config.monitoring_enabled:
            monitoring_config = '''
management:
  endpoints:
    web:
      exposure:
        include: health,info,prometheus,metrics
  endpoint:
    health:
      show-details: always
  metrics:
    export:
      prometheus:
        enabled: true'''
        
        return f'''server:
  port: ${{SERVER_PORT:8080}}
  servlet:
    context-path: /api

spring:
  application:
    name: {config.service_name}
  
  profiles:
    active: ${{SPRING_PROFILES_ACTIVE:local}}
  
  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: ${{JPA_SHOW_SQL:false}}
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
        format_sql: true
    open-in-view: false
  {database_config}
  {cache_config}
  {security_config}

{monitoring_config}

logging:
  level:
    {config.package_name}: ${{LOG_LEVEL:INFO}}
    org.springframework.security: ${{SECURITY_LOG_LEVEL:INFO}}
  pattern:
    console: "%d{{yyyy-MM-dd HH:mm:ss}} - %msg%n"
    file: "%d{{yyyy-MM-dd HH:mm:ss}} [%thread] %-5level %logger{{36}} - %msg%n"

# Cloud Provider Specific Configuration
cloud:
  provider: {config.cloud_provider.lower()}
  
# Application Specific Configuration
app:
  name: {config.service_name}
  version: 1.0.0
  description: Cloud-agnostic microservice'''
    
    def _generate_aws_config(self, config: JavaTemplateConfig) -> Dict[str, str]:
        """Generate AWS-specific configuration files."""
        files = {}
        
        # AWS configuration class
        files[f"src/main/java/{config.package_name.replace('.', '/')}/config/AwsConfig.java"] = f'''package {config.package_name}.config;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;

@Configuration
@ConditionalOnProperty(name = "cloud.provider", havingValue = "aws")
public class AwsConfig {{

    @Bean
    public S3Client s3Client() {{
        return S3Client.builder()
                .region(Region.of(System.getenv().getOrDefault("AWS_REGION", "us-east-1")))
                .credentialsProvider(DefaultCredentialsProvider.create())
                .build();
    }}
}}'''
        
        # AWS application properties
        files["src/main/resources/application-aws.yml"] = '''
cloud:
  aws:
    region:
      static: ${AWS_REGION:us-east-1}
    credentials:
      use-default-aws-credentials-chain: true
    s3:
      bucket: ${AWS_S3_BUCKET:}
    
spring:
  datasource:
    url: jdbc:postgresql://${RDS_HOSTNAME:}:${RDS_PORT:5432}/${RDS_DB_NAME:}
    username: ${RDS_USERNAME:}
    password: ${RDS_PASSWORD:}'''
        
        return files
    
    def _generate_azure_config(self, config: JavaTemplateConfig) -> Dict[str, str]:
        """Generate Azure-specific configuration files."""
        files = {}
        
        # Azure configuration class
        files[f"src/main/java/{config.package_name.replace('.', '/')}/config/AzureConfig.java"] = f'''package {config.package_name}.config;

import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.storage.blob.BlobServiceClientBuilder;
import com.azure.storage.blob.BlobServiceClient;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@ConditionalOnProperty(name = "cloud.provider", havingValue = "azure")
public class AzureConfig {{

    @Bean
    public BlobServiceClient blobServiceClient() {{
        String storageAccount = System.getenv("AZURE_STORAGE_ACCOUNT");
        return new BlobServiceClientBuilder()
                .endpoint("https://" + storageAccount + ".blob.core.windows.net")
                .credential(new DefaultAzureCredentialBuilder().build())
                .buildClient();
    }}
}}'''
        
        # Azure application properties
        files["src/main/resources/application-azure.yml"] = '''
azure:
  storage:
    account-name: ${AZURE_STORAGE_ACCOUNT:}
    container-name: ${AZURE_STORAGE_CONTAINER:}
  
spring:
  datasource:
    url: jdbc:postgresql://${AZURE_POSTGRESQL_HOST:}:5432/${AZURE_POSTGRESQL_DATABASE:}?sslmode=require
    username: ${AZURE_POSTGRESQL_USERNAME:}
    password: ${AZURE_POSTGRESQL_PASSWORD:}'''
        
        return files
    
    def _generate_entity_classes(self, config: JavaTemplateConfig) -> Dict[str, str]:
        """Generate JPA entity classes."""
        files = {}
        
        # User entity example
        files[f"src/main/java/{config.package_name.replace('.', '/')}/entity/User.java"] = f'''package {config.package_name}.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.time.LocalDateTime;
import java.util.Objects;

@Entity
@Table(name = "users", indexes = {{
    @Index(name = "idx_user_email", columnList = "email", unique = true)
}})
public class User {{
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @NotBlank(message = "Username is required")
    @Size(min = 3, max = 50, message = "Username must be between 3 and 50 characters")
    @Column(nullable = false, unique = true, length = 50)
    private String username;
    
    @NotBlank(message = "Email is required")
    @Email(message = "Email should be valid")
    @Column(nullable = false, unique = true, length = 100)
    private String email;
    
    @NotBlank(message = "First name is required")
    @Size(max = 50, message = "First name must not exceed 50 characters")
    @Column(name = "first_name", nullable = false, length = 50)
    private String firstName;
    
    @NotBlank(message = "Last name is required")
    @Size(max = 50, message = "Last name must not exceed 50 characters")
    @Column(name = "last_name", nullable = false, length = 50)
    private String lastName;
    
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @PrePersist
    protected void onCreate() {{
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }}
    
    @PreUpdate
    protected void onUpdate() {{
        updatedAt = LocalDateTime.now();
    }}
    
    // Constructors
    public User() {{}}
    
    public User(String username, String email, String firstName, String lastName) {{
        this.username = username;
        this.email = email;
        this.firstName = firstName;
        this.lastName = lastName;
    }}
    
    // Getters and Setters
    public Long getId() {{ return id; }}
    public void setId(Long id) {{ this.id = id; }}
    
    public String getUsername() {{ return username; }}
    public void setUsername(String username) {{ this.username = username; }}
    
    public String getEmail() {{ return email; }}
    public void setEmail(String email) {{ this.email = email; }}
    
    public String getFirstName() {{ return firstName; }}
    public void setFirstName(String firstName) {{ this.firstName = firstName; }}
    
    public String getLastName() {{ return lastName; }}
    public void setLastName(String lastName) {{ this.lastName = lastName; }}
    
    public LocalDateTime getCreatedAt() {{ return createdAt; }}
    public void setCreatedAt(LocalDateTime createdAt) {{ this.createdAt = createdAt; }}
    
    public LocalDateTime getUpdatedAt() {{ return updatedAt; }}
    public void setUpdatedAt(LocalDateTime updatedAt) {{ this.updatedAt = updatedAt; }}
    
    @Override
    public boolean equals(Object o) {{
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        User user = (User) o;
        return Objects.equals(id, user.id);
    }}
    
    @Override
    public int hashCode() {{
        return Objects.hash(id);
    }}
    
    @Override
    public String toString() {{
        return "User{{" +
                "id=" + id +
                ", username='" + username + '\\'' +
                ", email='" + email + '\\'' +
                ", firstName='" + firstName + '\\'' +
                ", lastName='" + lastName + '\\'' +
                "}}";
    }}
}}'''
        
        return files
    
    def _generate_repository_layer(self, config: JavaTemplateConfig) -> Dict[str, str]:
        """Generate repository layer classes."""
        files = {}
        
        # User repository
        files[f"src/main/java/{config.package_name.replace('.', '/')}/repository/UserRepository.java"] = f'''package {config.package_name}.repository;

import {config.package_name}.entity.User;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {{
    
    Optional<User> findByUsername(String username);
    
    Optional<User> findByEmail(String email);
    
    boolean existsByUsername(String username);
    
    boolean existsByEmail(String email);
    
    @Query("SELECT u FROM User u WHERE " +
           "(:username is null OR LOWER(u.username) LIKE LOWER(CONCAT('%', :username, '%'))) AND " +
           "(:email is null OR LOWER(u.email) LIKE LOWER(CONCAT('%', :email, '%')))")
    Page<User> findByUsernameContainingIgnoreCaseOrEmailContainingIgnoreCase(
            @Param("username") String username,
            @Param("email") String email,
            Pageable pageable);
}}'''
        
        return files
    
    def _generate_service_layer(self, config: JavaTemplateConfig) -> Dict[str, str]:
        """Generate service layer classes."""
        files = {}
        
        # User service interface
        files[f"src/main/java/{config.package_name.replace('.', '/')}/service/UserService.java"] = f'''package {config.package_name}.service;

import {config.package_name}.entity.User;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.Optional;

public interface UserService {{
    
    User createUser(User user);
    
    Optional<User> getUserById(Long id);
    
    Optional<User> getUserByUsername(String username);
    
    Optional<User> getUserByEmail(String email);
    
    Page<User> getAllUsers(Pageable pageable);
    
    Page<User> searchUsers(String username, String email, Pageable pageable);
    
    User updateUser(Long id, User userDetails);
    
    void deleteUser(Long id);
    
    boolean existsByUsername(String username);
    
    boolean existsByEmail(String email);
}}'''
        
        # User service implementation
        files[f"src/main/java/{config.package_name.replace('.', '/')}/service/impl/UserServiceImpl.java"] = f'''package {config.package_name}.service.impl;

import {config.package_name}.entity.User;
import {config.package_name}.repository.UserRepository;
import {config.package_name}.service.UserService;
import {config.package_name}.exception.ResourceNotFoundException;
import {config.package_name}.exception.DuplicateResourceException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;

@Service
@Transactional
public class UserServiceImpl implements UserService {{
    
    private static final Logger logger = LoggerFactory.getLogger(UserServiceImpl.class);
    
    private final UserRepository userRepository;
    
    @Autowired
    public UserServiceImpl(UserRepository userRepository) {{
        this.userRepository = userRepository;
    }}
    
    @Override
    public User createUser(User user) {{
        logger.info("Creating new user with username: {{}}", user.getUsername());
        
        if (userRepository.existsByUsername(user.getUsername())) {{
            throw new DuplicateResourceException("Username already exists: " + user.getUsername());
        }}
        
        if (userRepository.existsByEmail(user.getEmail())) {{
            throw new DuplicateResourceException("Email already exists: " + user.getEmail());
        }}
        
        User savedUser = userRepository.save(user);
        logger.info("User created successfully with ID: {{}}", savedUser.getId());
        return savedUser;
    }}
    
    @Override
    @Cacheable(value = "users", key = "#id")
    @Transactional(readOnly = true)
    public Optional<User> getUserById(Long id) {{
        logger.debug("Fetching user by ID: {{}}", id);
        return userRepository.findById(id);
    }}
    
    @Override
    @Cacheable(value = "users", key = "#username")
    @Transactional(readOnly = true)
    public Optional<User> getUserByUsername(String username) {{
        logger.debug("Fetching user by username: {{}}", username);
        return userRepository.findByUsername(username);
    }}
    
    @Override
    @Cacheable(value = "users", key = "#email")
    @Transactional(readOnly = true)
    public Optional<User> getUserByEmail(String email) {{
        logger.debug("Fetching user by email: {{}}", email);
        return userRepository.findByEmail(email);
    }}
    
    @Override
    @Transactional(readOnly = true)
    public Page<User> getAllUsers(Pageable pageable) {{
        logger.debug("Fetching all users with pagination");
        return userRepository.findAll(pageable);
    }}
    
    @Override
    @Transactional(readOnly = true)
    public Page<User> searchUsers(String username, String email, Pageable pageable) {{
        logger.debug("Searching users with username: {{}} and email: {{}}", username, email);
        return userRepository.findByUsernameContainingIgnoreCaseOrEmailContainingIgnoreCase(
                username, email, pageable);
    }}
    
    @Override
    @CacheEvict(value = "users", key = "#id")
    public User updateUser(Long id, User userDetails) {{
        logger.info("Updating user with ID: {{}}", id);
        
        User user = userRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + id));
        
        // Check for duplicates if username or email is being changed
        if (!user.getUsername().equals(userDetails.getUsername()) && 
            userRepository.existsByUsername(userDetails.getUsername())) {{
            throw new DuplicateResourceException("Username already exists: " + userDetails.getUsername());
        }}
        
        if (!user.getEmail().equals(userDetails.getEmail()) && 
            userRepository.existsByEmail(userDetails.getEmail())) {{
            throw new DuplicateResourceException("Email already exists: " + userDetails.getEmail());
        }}
        
        user.setUsername(userDetails.getUsername());
        user.setEmail(userDetails.getEmail());
        user.setFirstName(userDetails.getFirstName());
        user.setLastName(userDetails.getLastName());
        
        User updatedUser = userRepository.save(user);
        logger.info("User updated successfully with ID: {{}}", updatedUser.getId());
        return updatedUser;
    }}
    
    @Override
    @CacheEvict(value = "users", key = "#id")
    public void deleteUser(Long id) {{
        logger.info("Deleting user with ID: {{}}", id);
        
        if (!userRepository.existsById(id)) {{
            throw new ResourceNotFoundException("User not found with id: " + id);
        }}
        
        userRepository.deleteById(id);
        logger.info("User deleted successfully with ID: {{}}", id);
    }}
    
    @Override
    @Transactional(readOnly = true)
    public boolean existsByUsername(String username) {{
        return userRepository.existsByUsername(username);
    }}
    
    @Override
    @Transactional(readOnly = true)
    public boolean existsByEmail(String email) {{
        return userRepository.existsByEmail(email);
    }}
}}'''
        
        return files
    
    def _generate_controller_layer(self, config: JavaTemplateConfig) -> Dict[str, str]:
        """Generate REST controller classes."""
        files = {}
        
        # User controller
        files[f"src/main/java/{config.package_name.replace('.', '/')}/controller/UserController.java"] = f'''package {config.package_name}.controller;

import {config.package_name}.entity.User;
import {config.package_name}.service.UserService;
import {config.package_name}.exception.ResourceNotFoundException;

import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")
@CrossOrigin(origins = "*", maxAge = 3600)
public class UserController {{
    
    private static final Logger logger = LoggerFactory.getLogger(UserController.class);
    
    private final UserService userService;
    
    @Autowired
    public UserController(UserService userService) {{
        this.userService = userService;
    }}
    
    @GetMapping
    public ResponseEntity<Page<User>> getAllUsers(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(defaultValue = "id") String sortBy,
            @RequestParam(defaultValue = "asc") String sortDir) {{
        
        logger.info("Fetching all users - page: {{}}, size: {{}}, sortBy: {{}}, sortDir: {{}}", 
                   page, size, sortBy, sortDir);
        
        Sort sort = sortDir.equalsIgnoreCase("desc") ? 
                   Sort.by(sortBy).descending() : Sort.by(sortBy).ascending();
        
        Pageable pageable = PageRequest.of(page, size, sort);
        Page<User> users = userService.getAllUsers(pageable);
        
        return ResponseEntity.ok(users);
    }}
    
    @GetMapping("/{{id}}")
    public ResponseEntity<User> getUserById(@PathVariable Long id) {{
        logger.info("Fetching user by ID: {{}}", id);
        
        User user = userService.getUserById(id)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with id: " + id));
        
        return ResponseEntity.ok(user);
    }}
    
    @GetMapping("/username/{{username}}")
    public ResponseEntity<User> getUserByUsername(@PathVariable String username) {{
        logger.info("Fetching user by username: {{}}", username);
        
        User user = userService.getUserByUsername(username)
                .orElseThrow(() -> new ResourceNotFoundException("User not found with username: " + username));
        
        return ResponseEntity.ok(user);
    }}
    
    @GetMapping("/search")
    public ResponseEntity<Page<User>> searchUsers(
            @RequestParam(required = false) String username,
            @RequestParam(required = false) String email,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {{
        
        logger.info("Searching users - username: {{}}, email: {{}}", username, email);
        
        Pageable pageable = PageRequest.of(page, size);
        Page<User> users = userService.searchUsers(username, email, pageable);
        
        return ResponseEntity.ok(users);
    }}
    
    @PostMapping
    public ResponseEntity<User> createUser(@Valid @RequestBody User user) {{
        logger.info("Creating new user: {{}}", user.getUsername());
        
        User createdUser = userService.createUser(user);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdUser);
    }}
    
    @PutMapping("/{{id}}")
    public ResponseEntity<User> updateUser(@PathVariable Long id, @Valid @RequestBody User userDetails) {{
        logger.info("Updating user with ID: {{}}", id);
        
        User updatedUser = userService.updateUser(id, userDetails);
        return ResponseEntity.ok(updatedUser);
    }}
    
    @DeleteMapping("/{{id}}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {{
        logger.info("Deleting user with ID: {{}}", id);
        
        userService.deleteUser(id);
        return ResponseEntity.noContent().build();
    }}
    
    @GetMapping("/exists/username/{{username}}")
    public ResponseEntity<Boolean> existsByUsername(@PathVariable String username) {{
        boolean exists = userService.existsByUsername(username);
        return ResponseEntity.ok(exists);
    }}
    
    @GetMapping("/exists/email/{{email}}")
    public ResponseEntity<Boolean> existsByEmail(@PathVariable String email) {{
        boolean exists = userService.existsByEmail(email);
        return ResponseEntity.ok(exists);
    }}
}}'''
        
        # Health controller
        files[f"src/main/java/{config.package_name.replace('.', '/')}/controller/HealthController.java"] = f'''package {config.package_name}.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/health")
public class HealthController {{
    
    @Value("${{app.name}}")
    private String appName;
    
    @Value("${{app.version}}")
    private String appVersion;
    
    @GetMapping
    public ResponseEntity<Map<String, Object>> health() {{
        Map<String, Object> health = new HashMap<>();
        health.put("status", "UP");
        health.put("timestamp", LocalDateTime.now());
        health.put("service", appName);
        health.put("version", appVersion);
        
        return ResponseEntity.ok(health);
    }}
}}'''
        
        return files
    
    def _generate_configuration_classes(self, config: JavaTemplateConfig) -> Dict[str, str]:
        """Generate configuration classes."""
        files = {}
        
        # Database configuration
        files[f"src/main/java/{config.package_name.replace('.', '/')}/config/DatabaseConfig.java"] = f'''package {config.package_name}.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.transaction.annotation.EnableTransactionManagement;

@Configuration
@EnableJpaRepositories(basePackages = "{config.package_name}.repository")
@EnableTransactionManagement
public class DatabaseConfig {{
    // Database configuration can be extended here
}}'''
        
        # Cache configuration (if enabled)
        if config.cache_enabled:
            files[f"src/main/java/{config.package_name.replace('.', '/')}/config/CacheConfig.java"] = f'''package {config.package_name}.config;

import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.cache.RedisCacheManager;
import org.springframework.data.redis.connection.RedisConnectionFactory;

import java.time.Duration;

@Configuration
@EnableCaching
public class CacheConfig {{
    
    @Bean
    public CacheManager cacheManager(RedisConnectionFactory redisConnectionFactory) {{
        return RedisCacheManager.builder(redisConnectionFactory)
                .cacheDefaults(
                    org.springframework.data.redis.cache.RedisCacheConfiguration.defaultCacheConfig()
                        .entryTtl(Duration.ofMinutes(30))
                )
                .build();
    }}
}}'''
        
        # Exception handling
        files[f"src/main/java/{config.package_name.replace('.', '/')}/exception/GlobalExceptionHandler.java"] = f'''package {config.package_name}.exception;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {{
    
    private static final Logger logger = LoggerFactory.getLogger(GlobalExceptionHandler.class);
    
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<Map<String, Object>> handleResourceNotFoundException(ResourceNotFoundException ex) {{
        logger.error("Resource not found: {{}}", ex.getMessage());
        
        Map<String, Object> error = new HashMap<>();
        error.put("timestamp", LocalDateTime.now());
        error.put("status", HttpStatus.NOT_FOUND.value());
        error.put("error", "Not Found");
        error.put("message", ex.getMessage());
        
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }}
    
    @ExceptionHandler(DuplicateResourceException.class)
    public ResponseEntity<Map<String, Object>> handleDuplicateResourceException(DuplicateResourceException ex) {{
        logger.error("Duplicate resource: {{}}", ex.getMessage());
        
        Map<String, Object> error = new HashMap<>();
        error.put("timestamp", LocalDateTime.now());
        error.put("status", HttpStatus.CONFLICT.value());
        error.put("error", "Conflict");
        error.put("message", ex.getMessage());
        
        return ResponseEntity.status(HttpStatus.CONFLICT).body(error);
    }}
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleValidationExceptions(MethodArgumentNotValidException ex) {{
        logger.error("Validation failed: {{}}", ex.getMessage());
        
        Map<String, String> validationErrors = new HashMap<>();
        ex.getBindingResult().getAllErrors().forEach((error) -> {{
            String fieldName = ((FieldError) error).getField();
            String errorMessage = error.getDefaultMessage();
            validationErrors.put(fieldName, errorMessage);
        }});
        
        Map<String, Object> error = new HashMap<>();
        error.put("timestamp", LocalDateTime.now());
        error.put("status", HttpStatus.BAD_REQUEST.value());
        error.put("error", "Validation Failed");
        error.put("validationErrors", validationErrors);
        
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
    }}
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handleGenericException(Exception ex) {{
        logger.error("Unexpected error: {{}}", ex.getMessage(), ex);
        
        Map<String, Object> error = new HashMap<>();
        error.put("timestamp", LocalDateTime.now());
        error.put("status", HttpStatus.INTERNAL_SERVER_ERROR.value());
        error.put("error", "Internal Server Error");
        error.put("message", "An unexpected error occurred");
        
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
    }}
}}'''
        
        # Custom exceptions
        files[f"src/main/java/{config.package_name.replace('.', '/')}/exception/ResourceNotFoundException.java"] = f'''package {config.package_name}.exception;

public class ResourceNotFoundException extends RuntimeException {{
    
    public ResourceNotFoundException(String message) {{
        super(message);
    }}
    
    public ResourceNotFoundException(String message, Throwable cause) {{
        super(message, cause);
    }}
}}'''
        
        files[f"src/main/java/{config.package_name.replace('.', '/')}/exception/DuplicateResourceException.java"] = f'''package {config.package_name}.exception;

public class DuplicateResourceException extends RuntimeException {{
    
    public DuplicateResourceException(String message) {{
        super(message);
    }}
    
    public DuplicateResourceException(String message, Throwable cause) {{
        super(message, cause);
    }}
}}'''
        
        return files
    
    def _generate_security_config(self, config: JavaTemplateConfig) -> Dict[str, str]:
        """Generate security configuration."""
        files = {}
        
        files[f"src/main/java/{config.package_name.replace('.', '/')}/config/SecurityConfig.java"] = f'''package {config.package_name}.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.Arrays;

@Configuration
@EnableWebSecurity
public class SecurityConfig {{
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {{
        http.cors().and()
            .csrf().disable()
            .sessionManagement().sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            .and()
            .authorizeHttpRequests(authz -> authz
                .requestMatchers("/api/health/**").permitAll()
                .requestMatchers("/actuator/**").permitAll()
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2.jwt());
        
        return http.build();
    }}
    
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {{
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOriginPatterns(Arrays.asList("*"));
        configuration.setAllowedMethods(Arrays.asList("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(Arrays.asList("*"));
        configuration.setAllowCredentials(true);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }}
}}'''
        
        return files
    
    def _generate_docker_config(self, config: JavaTemplateConfig) -> Dict[str, str]:
        """Generate Docker configuration files."""
        files = {}
        
        # Dockerfile
        files["Dockerfile"] = f'''FROM openjdk:{config.java_version}-jdk-slim

# Set working directory
WORKDIR /app

# Copy pom.xml and download dependencies
COPY pom.xml .
COPY mvnw .
COPY .mvn .mvn
RUN ./mvnw dependency:go-offline -B

# Copy source code
COPY src src

# Build application
RUN ./mvnw clean package -DskipTests

# Copy built jar
RUN cp target/{config.artifact_id}-*.jar app.jar

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:8080/api/health || exit 1

# Run application
ENTRYPOINT ["java", "-jar", "/app/app.jar"]'''
        
        # Docker Compose for local development
        files["docker-compose.yml"] = f'''version: '3.8'

services:
  {config.service_name}:
    build: .
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=docker
      - DATABASE_HOST=postgres
      - REDIS_HOST=redis
    depends_on:
      - postgres
      - redis
    networks:
      - microservices-network

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=microservices
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - microservices-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - microservices-network

volumes:
  postgres_data:

networks:
  microservices-network:
    driver: bridge'''
        
        # Docker application properties
        files["src/main/resources/application-docker.yml"] = '''
spring:
  datasource:
    url: jdbc:postgresql://postgres:5432/microservices
    username: postgres
    password: password
  
  data:
    redis:
      host: redis
      port: 6379

logging:
  level:
    root: INFO'''
        
        return files
    
    def _generate_test_files(self, config: JavaTemplateConfig) -> Dict[str, str]:
        """Generate test files."""
        files = {}
        
        # Integration test
        files[f"src/test/java/{config.package_name.replace('.', '/')}/UserIntegrationTest.java"] = f'''package {config.package_name};

import {config.package_name}.entity.User;
import {config.package_name}.repository.UserRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureWebMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureWebMvc
@Testcontainers
@ActiveProfiles("test")
@Transactional
public class UserIntegrationTest {{
    
    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15-alpine")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");
    
    @Autowired
    private MockMvc mockMvc;
    
    @Autowired
    private ObjectMapper objectMapper;
    
    @Autowired
    private UserRepository userRepository;
    
    @Test
    public void shouldCreateUser() throws Exception {{
        User user = new User("testuser", "test@example.com", "John", "Doe");
        
        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(user)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.username").value("testuser"))
                .andExpect(jsonPath("$.email").value("test@example.com"));
    }}
    
    @Test
    public void shouldGetUserById() throws Exception {{
        User user = userRepository.save(new User("testuser2", "test2@example.com", "Jane", "Doe"));
        
        mockMvc.perform(get("/api/users/" + user.getId()))
                .andExpected(status().isOk())
                .andExpected(jsonPath("$.id").value(user.getId()))
                .andExpected(jsonPath("$.username").value("testuser2"));
    }}
}}'''
        
        # Unit test
        files[f"src/test/java/{config.package_name.replace('.', '/')}/service/UserServiceTest.java"] = f'''package {config.package_name}.service;

import {config.package_name}.entity.User;
import {config.package_name}.repository.UserRepository;
import {config.package_name}.service.impl.UserServiceImpl;
import {config.package_name}.exception.DuplicateResourceException;
import {config.package_name}.exception.ResourceNotFoundException;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class UserServiceTest {{
    
    @Mock
    private UserRepository userRepository;
    
    private UserService userService;
    
    @BeforeEach
    void setUp() {{
        userService = new UserServiceImpl(userRepository);
    }}
    
    @Test
    public void shouldCreateUser() {{
        User user = new User("testuser", "test@example.com", "John", "Doe");
        
        when(userRepository.existsByUsername(anyString())).thenReturn(false);
        when(userRepository.existsByEmail(anyString())).thenReturn(false);
        when(userRepository.save(any(User.class))).thenReturn(user);
        
        User result = userService.createUser(user);
        
        assertNotNull(result);
        assertEquals("testuser", result.getUsername());
        verify(userRepository).save(user);
    }}
    
    @Test
    public void shouldThrowExceptionWhenUsernameExists() {{
        User user = new User("testuser", "test@example.com", "John", "Doe");
        
        when(userRepository.existsByUsername("testuser")).thenReturn(true);
        
        assertThrows(DuplicateResourceException.class, () -> userService.createUser(user));
    }}
    
    @Test
    public void shouldGetUserById() {{
        Long userId = 1L;
        User user = new User("testuser", "test@example.com", "John", "Doe");
        
        when(userRepository.findById(userId)).thenReturn(Optional.of(user));
        
        Optional<User> result = userService.getUserById(userId);
        
        assertTrue(result.isPresent());
        assertEquals("testuser", result.get().getUsername());
    }}
    
    @Test
    public void shouldReturnEmptyWhenUserNotFound() {{
        Long userId = 1L;
        
        when(userRepository.findById(userId)).thenReturn(Optional.empty());
        
        Optional<User> result = userService.getUserById(userId);
        
        assertFalse(result.isPresent());
    }}
}}'''
        
        # Test application properties
        files["src/test/resources/application-test.yml"] = '''
spring:
  datasource:
    url: jdbc:h2:mem:testdb
    driver-class-name: org.h2.Driver
    username: sa
    password: 
  
  jpa:
    hibernate:
      ddl-auto: create-drop
    show-sql: true
    
  cache:
    type: simple

logging:
  level:
    org.springframework.web: DEBUG
    org.hibernate: DEBUG'''
        
        return files


# Factory function
def create_java_template_generator() -> JavaTemplateGenerator:
    """Create a JavaTemplateGenerator instance."""
    return JavaTemplateGenerator()