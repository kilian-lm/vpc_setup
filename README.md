# vpc_setup

```mermaid
flowchart TB
    %% Legend
    subgraph legend [Legend]
        direction LR
        classDef cloud fill:#E3F2FD,stroke:#1E88E5,stroke-width:2px,color:#000000;
        classDef publicSubnet fill:#FFFFFF,stroke:#000000,stroke-dasharray: 5 5,color:#000000;
        classDef privateSubnet fill:#F0F0F0,stroke:#000000,color:#000000;
        classDef resource fill:#FFFFFF,stroke:#000000,shape:rect,color:#000000;
        classDef idp fill:#F3E5F5,stroke:#8E24AA,stroke-width:2px,color:#000000;
        classDef user fill:#FFF3E0,stroke:#FB8C00,stroke-width:2px,color:#000000;

        L1[Cloud Environment]:::cloud
        L2[Public Subnet]:::publicSubnet
        L3[Private Subnet]:::privateSubnet
        L4[Resource]:::resource
        L5[Identity Provider]:::idp
    end

    %% AWS Cloud
    subgraph aws_cloud [AWS Cloud]
        direction TB
        %% Public Subnet
        subgraph public_subnet_aws [Public Subnet AWS]
            direction TB
            InternetGW_AWS[Internet Gateway]:::resource
            ELB_AWS[Elastic Load Balancer]:::resource
            EC2_AWS[EC2 Instances]:::resource
            InternetGW_AWS --> ELB_AWS --> EC2_AWS
        end
        %% Private Subnet
        subgraph private_subnet_aws [Private Subnet AWS]
            direction TB
            Sagemaker_AWS[Amazon SageMaker Notebooks]:::resource
            RDS_AWS[RDS Database]:::resource
            EC2_AWS --> Sagemaker_AWS
            Sagemaker_AWS --> RDS_AWS
        end
    end

    %% GCP Cloud
    subgraph gcp_cloud [GCP Cloud]
        direction TB
        %% Public Subnet
        subgraph public_subnet_gcp [Public Subnet GCP]
            direction TB
            InternetGW_GCP[Internet Gateway]:::resource
            LB_GCP[Cloud Load Balancer]:::resource
            ComputeEngine_GCP[Compute Engine VMs]:::resource
            InternetGW_GCP --> LB_GCP --> ComputeEngine_GCP
        end
        %% Private Subnet
        subgraph private_subnet_gcp [Private Subnet GCP]
            direction TB
            Dataproc_GCP[Dataproc Clusters]:::resource
            CloudSQL_GCP[Cloud SQL Database]:::resource
            ComputeEngine_GCP --> Dataproc_GCP
            Dataproc_GCP --> CloudSQL_GCP
        end
    end

    %% Centralized Identity Management
    subgraph identity_management [Identity Management]
        direction TB
        IdP[Centralized Identity Provider / SSO]:::idp
        New_User[New Data Scientist / Programmer]:::user -->|Onboard| IdP
        IdP -->|Federated Access| IAM_AWS[IAM AWS]:::resource
        IdP -->|Federated Access| IAM_GCP[IAM GCP]:::resource
        IAM_AWS --> EC2_AWS
        IAM_AWS --> Sagemaker_AWS
        IAM_GCP --> ComputeEngine_GCP
        IAM_GCP --> Dataproc_GCP
    end

    %% Optional VPC Peering
    VPC_AWS[VPC AWS]:::resource
    VPC_GCP[VPC GCP]:::resource
    VPC_AWS ---|Optional VPC Peering| VPC_GCP

    %% Apply styles to subgraphs using 'style' directives
    style aws_cloud fill:#E3F2FD,stroke:#1E88E5,stroke-width:2px,color:#000000
    style gcp_cloud fill:#E8F5E9,stroke:#43A047,stroke-width:2px,color:#000000
    style identity_management fill:#F3E5F5,stroke:#8E24AA,stroke-width:2px,font-weight:bold,color:#000000
    style public_subnet_aws stroke:#000000,stroke-dasharray: 5 5,color:#000000
    style private_subnet_aws fill:#F0F0F0,stroke:#000000,color:#000000
    style public_subnet_gcp stroke:#000000,stroke-dasharray: 5 5,color:#000000
    style private_subnet_gcp fill:#F0F0F0,stroke:#000000,color:#000000

    %% Styles Applied from Legend
    class InternetGW_AWS resource
    class ELB_AWS resource
    class EC2_AWS resource
    class Sagemaker_AWS resource
    class RDS_AWS resource
    class InternetGW_GCP resource
    class LB_GCP resource
    class ComputeEngine_GCP resource
    class Dataproc_GCP resource
    class CloudSQL_GCP resource
    class IAM_AWS resource
    class IAM_GCP resource
    class VPC_AWS resource
    class VPC_GCP resource
    class IdP idp
    class New_User user

```

**Explanation of the Architecture:**

1. **VPC Structure for AWS and GCP:**
    - **AWS Cloud:**
        - **VPC_AWS** contains both public and private subnets.
        - **Public Subnet:** Hosts the **Internet Gateway**, **Elastic Load Balancer (ELB)**, and **EC2 Instances**.
        - **Private Subnet:** Contains **Amazon SageMaker Notebooks** and **RDS Databases**.
        - **EC2 Instances** in the public subnet can access resources in the private subnet.

    - **GCP Cloud:**
        - **VPC_GCP** also consists of public and private subnets.
        - **Public Subnet:** Includes the **Internet Gateway**, **Cloud Load Balancer**, and **Compute Engine VMs**.
        - **Private Subnet:** Houses **Dataproc Clusters** and **Cloud SQL Databases**.
        - **Compute Engine VMs** can access private resources like Dataproc clusters and Cloud SQL databases.

2. **Resource Deployment:**
    - All resources (notebooks, Dataproc clusters, VMs, databases) are deployed within their respective VPCs.
    - Resources are segmented into public and private subnets for security and scalability.
    - Load balancers in the public subnets manage incoming traffic and distribute it to the appropriate resources.

3. **Identity and Access Management (IAM):**
    - **Centralized Identity Provider (IdP)/SSO:** Acts as a single source of truth for user identities.
    - **New Users** are onboarded automatically through the IdP, which could be a system like **Okta**, **Azure AD**, or
      any SAML/OIDC-compliant provider.
    - The IdP federates access to both **IAM_AWS** and **IAM_GCP**, streamlining authentication and authorization
      processes.
    - **IAM Roles & Policies** in both AWS and GCP are configured to trust the IdP, allowing for seamless user
      provisioning and access control.

4. **Automated Onboarding and Authentication:**
    - New data scientists and programmers are added to the IdP, which automatically provisions their access to resources
      in AWS and GCP.
    - Role-based access control (RBAC) ensures users have the necessary permissions without manual intervention.
    - Policies are centrally managed, reducing the risk of misconfigurations and enhancing security compliance.

5. **Optional VPC Peering:**
    - **VPC Peering** between AWS and GCP VPCs enables direct network traffic between resources in both clouds.
    - This setup is optional and can be configured based on specific cross-cloud communication requirements.

6. **Security and Best Practices:**
    - Separation of public and private subnets enhances security by isolating resources that do not require direct
      internet access.
    - Use of IAM roles and policies enforces the principle of least privilege.
    - Centralized identity management reduces administrative overhead and improves compliance with security standards.

**Expert Considerations:**

- **Scalability:** The architecture supports horizontal scaling by adding more instances or resources within the
  subnets.
- **High Availability:** Deploying resources across multiple availability zones (not depicted) can further enhance
  resilience.
- **Cost Efficiency:** Utilizing reserved instances and optimizing resource utilization can reduce operational costs.
- **Compliance:** Adhering to industry standards like **ISO 27001**, **HIPAA**, or **GDPR** is facilitated through
  centralized policies.

**Implementation Notes:**

- **Infrastructure as Code (IaC):** Use tools like **Terraform** or **CloudFormation** to codify and automate the
  deployment of this architecture.
- **Continuous Integration/Continuous Deployment (CI/CD):** Implement pipelines to automate the deployment and updates
  of resources.
- **Monitoring and Logging:** Integrate with services like **AWS CloudWatch**, **GCP Cloud Monitoring**, or third-party
  solutions for observability.


