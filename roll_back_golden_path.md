**Complete Terraform Scripts and Deployment Logs**  
   
Below, you'll find the complete Terraform scripts required to build the infrastructure described earlier. Additionally, I will include sample success statements from running `terraform apply` (building the infrastructure) and `terraform destroy` (rolling back the infrastructure).  
   
---  
   
### **Directory Structure**  
   
First, organize your Terraform files and modules in the following directory structure:  
   
```  
terraform/  
├── main.tf  
├── variables.tf  
├── outputs.tf  
├── providers.tf  
├── modules/  
│   ├── network/  
│   │   ├── main.tf  
│   │   ├── variables.tf  
│   │   └── outputs.tf  
│   ├── iam/  
│   │   ├── main.tf  
│   │   ├── variables.tf  
│   │   └── outputs.tf  
│   ├── compute_engine/  
│   │   ├── main.tf  
│   │   ├── variables.tf  
│   │   └── outputs.tf  
│   ├── dataproc/  
│   │   ├── main.tf  
│   │   ├── variables.tf  
│   │   └── outputs.tf  
│   ├── cloud_sql/  
│   │   ├── main.tf  
│   │   ├── variables.tf  
│   │   └── outputs.tf  
│   └── monitoring/  
│       ├── main.tf  
│       ├── variables.tf  
│       └── outputs.tf  
```  
   
---  
   
### **Top-Level Terraform Files**  
   
#### **1. `providers.tf`**  
   
```hcl  
# Configure the Google provider  
provider "google" {  
  project = var.project_id  
  region  = var.region  
  zone    = var.zone  
}  
```  
   
#### **2. `main.tf`**  
   
```hcl  
# Enable required APIs  
resource "google_project_service" "enable_apis" {  
  for_each = toset([  
    "compute.googleapis.com",  
    "dataproc.googleapis.com",  
    "sqladmin.googleapis.com",  
    "iam.googleapis.com",  
    "cloudresourcemanager.googleapis.com",  
    "monitoring.googleapis.com",  
    "logging.googleapis.com",  
  ])  
  
  project = var.project_id  
  service = each.key  
  
  disable_on_destroy = false  
}  
   
# Create VPC with public and private subnets  
module "network" {  
  source       = "./modules/network"  
  project_id   = var.project_id  
  network_name = var.network_name  
  region       = var.region  
}  
   
# Set up IAM roles and permissions  
module "iam" {  
  source                  = "./modules/iam"  
  project_id              = var.project_id  
  data_scientist_group    = var.data_scientist_group  
  compute_engine_roles    = var.compute_engine_roles  
  dataproc_roles          = var.dataproc_roles  
  cloud_sql_roles         = var.cloud_sql_roles  
}  
   
# Deploy Compute Engine instances (Public Subnet)  
module "compute_engine" {  
  source                  = "./modules/compute_engine"  
  project_id              = var.project_id  
  region                  = var.region  
  zone                    = var.zone  
  network                 = module.network.vpc_self_link  
  subnetwork              = module.network.public_subnet_self_link  
  instance_name           = var.instance_name  
  machine_type            = var.machine_type  
  service_account_email   = var.service_account_email  
}  
   
# Deploy Dataproc Cluster (Private Subnet)  
module "dataproc_cluster" {  
  source                  = "./modules/dataproc"  
  project_id              = var.project_id  
  region                  = var.region  
  network                 = module.network.vpc_self_link  
  subnetwork              = module.network.private_subnet_self_link  
  cluster_name            = var.cluster_name  
  service_account_email   = var.service_account_email  
}  
   
# Deploy Cloud SQL Instance (Private Subnet)  
module "cloud_sql" {  
  source                  = "./modules/cloud_sql"  
  project_id              = var.project_id  
  region                  = var.region  
  network                 = module.network.vpc_self_link  
  instance_name           = var.sql_instance_name  
  database_version        = var.database_version  
  db_user                 = var.db_user  
  db_password             = var.db_password  
  private_ip              = true  
}  
   
# Set up Monitoring and Logging  
module "monitoring" {  
  source       = "./modules/monitoring"  
  project_id   = var.project_id  
}  
```  
   
#### **3. `variables.tf`**  
   
```hcl  
variable "project_id" {  
  description = "The GCP project ID"  
  type        = string  
}  
   
variable "region" {  
  description = "The GCP region"  
  type        = string  
  default     = "us-central1"  
}  
   
variable "zone" {  
  description = "The GCP zone"  
  type        = string  
  default     = "us-central1-a"  
}  
   
variable "network_name" {  
  description = "Name of the VPC network"  
  type        = string  
  default     = "main-vpc"  
}  
   
variable "data_scientist_group" {  
  description = "Email of the data scientist group (e.g., 'group:data-scientists@example.com')"  
  type        = string  
}  
   
variable "compute_engine_roles" {  
  description = "Roles for Compute Engine"  
  type        = list(string)  
  default     = ["roles/compute.instanceAdmin.v1", "roles/compute.networkUser"]  
}  
   
variable "dataproc_roles" {  
  description = "Roles for Dataproc"  
  type        = list(string)  
  default     = ["roles/dataproc.editor"]  
}  
   
variable "cloud_sql_roles" {  
  description = "Roles for Cloud SQL"  
  type        = list(string)  
  default     = ["roles/cloudsql.client"]  
}  
   
variable "instance_name" {  
  description = "Name of the Compute Engine instance"  
  type        = string  
  default     = "compute-instance"  
}  
   
variable "machine_type" {  
  description = "Machine type for Compute Engine"  
  type        = string  
  default     = "n1-standard-1"  
}  
   
variable "service_account_email" {  
  description = "Service account email"  
  type        = string  
  default     = "default"  
}  
   
variable "cluster_name" {  
  description = "Name of the Dataproc cluster"  
  type        = string  
  default     = "dataproc-cluster"  
}  
   
variable "sql_instance_name" {  
  description = "Name of the Cloud SQL instance"  
  type        = string  
  default     = "cloud-sql-instance"  
}  
   
variable "database_version" {  
  description = "Cloud SQL database version"  
  type        = string  
  default     = "POSTGRES_13"  
}  
   
variable "db_user" {  
  description = "Database username"  
  type        = string  
  default     = "dbuser"  
}  
   
variable "db_password" {  
  description = "Database password"  
  type        = string  
}  
   
# Consider using Secret Manager or other secure methods to manage sensitive variables  
```  
   
#### **4. `outputs.tf`**  
   
```hcl  
output "compute_instance_external_ip" {  
  value = module.compute_engine.instance_external_ip  
}  
   
output "dataproc_cluster_name" {  
  value = module.dataproc_cluster.cluster_name  
}  
   
output "cloud_sql_instance_connection_name" {  
  value = module.cloud_sql.connection_name  
}  
```  
   
---  
   
### **Module Files**  
   
#### **1. Network Module (`modules/network`)**  
   
**`main.tf`**  
   
```hcl  
resource "google_compute_network" "vpc_network" {  
  name                    = var.network_name  
  auto_create_subnetworks = false  
}  
   
resource "google_compute_subnetwork" "public_subnet" {  
  name          = "${var.network_name}-public"  
  ip_cidr_range = "10.0.1.0/24"  
  region        = var.region  
  network       = google_compute_network.vpc_network.id  
}  
   
resource "google_compute_subnetwork" "private_subnet" {  
  name          = "${var.network_name}-private"  
  ip_cidr_range = "10.0.2.0/24"  
  region        = var.region  
  network       = google_compute_network.vpc_network.id  
}  
   
# Firewall rule to allow internal communication  
resource "google_compute_firewall" "allow_internal" {  
  name    = "${var.network_name}-allow-internal"  
  network = google_compute_network.vpc_network.name  
  
  allows {  
    protocol = "tcp"  
    ports    = ["0-65535"]  
  }  
  
  allows {  
    protocol = "udp"  
    ports    = ["0-65535"]  
  }  
  
  allows {  
    protocol = "icmp"  
  }  
  
  source_ranges = ["10.0.0.0/16"]  
}  
```  
   
**`variables.tf`**  
   
```hcl  
variable "project_id" {  
  type = string  
}  
   
variable "network_name" {  
  type = string  
}  
   
variable "region" {  
  type = string  
}  
```  
   
**`outputs.tf`**  
   
```hcl  
output "vpc_self_link" {  
  value = google_compute_network.vpc_network.self_link  
}  
   
output "public_subnet_self_link" {  
  value = google_compute_subnetwork.public_subnet.self_link  
}  
   
output "private_subnet_self_link" {  
  value = google_compute_subnetwork.private_subnet.self_link  
}  
```  
   
#### **2. IAM Module (`modules/iam`)**  
   
**`main.tf`**  
   
```hcl  
# Assign roles to the data scientist group for Compute Engine  
resource "google_project_iam_member" "compute_engine_roles" {  
  for_each = toset(var.compute_engine_roles)  
  
  project = var.project_id  
  role    = each.key  
  member  = var.data_scientist_group  
}  
   
# Assign roles to the data scientist group for Dataproc  
resource "google_project_iam_member" "dataproc_roles" {  
  for_each = toset(var.dataproc_roles)  
  
  project = var.project_id  
  role    = each.key  
  member  = var.data_scientist_group  
}  
   
# Assign roles to the data scientist group for Cloud SQL  
resource "google_project_iam_member" "cloud_sql_roles" {  
  for_each = toset(var.cloud_sql_roles)  
  
  project = var.project_id  
  role    = each.key  
  member  = var.data_scientist_group  
}  
```  
   
**`variables.tf`**  
   
```hcl  
variable "project_id" {  
  type = string  
}  
   
variable "data_scientist_group" {  
  type = string  
}  
   
variable "compute_engine_roles" {  
  type = list(string)  
}  
   
variable "dataproc_roles" {  
  type = list(string)  
}  
   
variable "cloud_sql_roles" {  
  type = list(string)  
}  
```  
   
**`outputs.tf`**  
   
```hcl  
# No outputs needed for IAM module  
```  
   
#### **3. Compute Engine Module (`modules/compute_engine`)**  
   
**`main.tf`**  
   
```hcl  
resource "google_compute_instance" "instance" {  
  name         = var.instance_name  
  machine_type = var.machine_type  
  zone         = var.zone  
  
  boot_disk {  
    initialize_params {  
      image = "debian-cloud/debian-10"  
    }  
  }  
  
  network_interface {  
    network    = var.network  
    subnetwork = var.subnetwork  
  
    access_config {  
      # Ephemeral public IP  
    }  
  }  
  
  service_account {  
    email  = var.service_account_email  
    scopes = ["cloud-platform"]  
  }  
  
  tags = ["compute-engine", "allow-ssh"]  
}  
   
# Firewall rule to allow SSH from anywhere (Adjust as needed)  
resource "google_compute_firewall" "allow_ssh" {  
  name    = "allow-ssh-${var.network}"  
  network = var.network  
  
  allow {  
    protocol = "tcp"  
    ports    = ["22"]  
  }  
  
  source_ranges = ["0.0.0.0/0"]  
  target_tags   = ["allow-ssh"]  
}  
```  
   
**`variables.tf`**  
   
```hcl  
variable "project_id" {  
  type = string  
}  
   
variable "region" {  
  type = string  
}  
   
variable "zone" {  
  type = string  
}  
   
variable "network" {  
  description = "VPC network self link"  
  type        = string  
}  
   
variable "subnetwork" {  
  description = "Subnetwork self link"  
  type        = string  
}  
   
variable "instance_name" {  
  type = string  
}  
   
variable "machine_type" {  
  type = string  
}  
   
variable "service_account_email" {  
  type = string  
}  
```  
   
**`outputs.tf`**  
   
```hcl  
output "instance_external_ip" {  
  description = "External IP address of the Compute Engine instance"  
  value       = google_compute_instance.instance.network_interface[0].access_config[0].nat_ip  
}  
```  
   
#### **4. Dataproc Module (`modules/dataproc`)**  
   
**`main.tf`**  
   
```hcl  
resource "google_dataproc_cluster" "cluster" {  
  name   = var.cluster_name  
  region = var.region  
  project = var.project_id  
  
  cluster_config {  
    staging_bucket = null  
  
    master_config {  
      num_instances = 1  
      machine_type  = "n1-standard-4"  
    }  
  
    worker_config {  
      num_instances = 2  
      machine_type  = "n1-standard-4"  
    }  
  
    gce_cluster_config {  
      network       = var.network  
      subnetwork    = var.subnetwork  
      service_account = var.service_account_email  
      tags          = ["dataproc"]  
    }  
  }  
  
  labels = {  
    environment = "development"  
  }  
}  
```  
   
**`variables.tf`**  
   
```hcl  
variable "project_id" {  
  type = string  
}  
   
variable "region" {  
  type = string  
}  
   
variable "network" {  
  description = "VPC network self link"  
  type        = string  
}  
   
variable "subnetwork" {  
  description = "Subnetwork self link"  
  type        = string  
}  
   
variable "cluster_name" {  
  type = string  
}  
   
variable "service_account_email" {  
  type = string  
}  
```  
   
**`outputs.tf`**  
   
```hcl  
output "cluster_name" {  
  description = "Name of the Dataproc cluster"  
  value       = google_dataproc_cluster.cluster.cluster_uuid  
}  
```  
   
#### **5. Cloud SQL Module (`modules/cloud_sql`)**  
   
**`main.tf`**  
   
```hcl  
resource "google_sql_database_instance" "instance" {  
  name             = var.instance_name  
  database_version = var.database_version  
  region           = var.region  
  project          = var.project_id  
  
  settings {  
    tier = "db-custom-2-7680" # Adjust as needed  
  
    ip_configuration {  
      ipv4_enabled    = false  
      private_network = var.network  
    }  
  }  
  
  depends_on = [google_project_service.enable_apis]  
}  
   
resource "google_sql_user" "user" {  
  name     = var.db_user  
  password = var.db_password  
  instance = google_sql_database_instance.instance.name  
}  
   
resource "google_sql_database" "database" {  
  name     = "defaultdb"  
  instance = google_sql_database_instance.instance.name  
}  
```  
   
**`variables.tf`**  
   
```hcl  
variable "project_id" {  
  type = string  
}  
   
variable "region" {  
  type = string  
}  
   
variable "network" {  
  description = "VPC network self link"  
  type        = string  
}  
   
variable "instance_name" {  
  type = string  
}  
   
variable "database_version" {  
  type = string  
}  
   
variable "db_user" {  
  type = string  
}  
   
variable "db_password" {  
  type = string  
}  
```  
   
**`outputs.tf`**  
   
```hcl  
output "connection_name" {  
  description = "Connection name of the Cloud SQL instance"  
  value       = google_sql_database_instance.instance.connection_name  
}  
```  
   
#### **6. Monitoring Module (`modules/monitoring`)**  
   
**`main.tf`**  
   
```hcl  
# Enable Stackdriver Monitoring and Logging APIs (Already enabled at project level if specified in main.tf)  
# This module can include alert policies, uptime checks, etc.  
   
# Example: Create a simple uptime check (Adjust as needed)  
resource "google_monitoring_uptime_check_config" "uptime_check" {  
  display_name = "Compute Engine Uptime Check"  
  timeout      = "10s"  
  period       = "60s"  
  
  monitored_resource {  
    type = "gce_instance"  
    labels = {  
      project_id  = var.project_id  
      instance_id = module.compute_engine.instance_id  
      zone        = var.zone  
    }  
  }  
  
  http_check {  
    path = "/"  
    port = 80  
  }  
}  
```  
   
**`variables.tf`**  
   
```hcl  
variable "project_id" {  
  type = string  
}  
   
variable "zone" {  
  type = string  
}  
   
# Include other variables as needed  
```  
   
**`outputs.tf`**  
   
```hcl  
# No outputs needed for monitoring module  
```  
   
---  
   
### **Deployment Instructions**  
   
1. **Install Terraform:**  
  
   Ensure that Terraform is installed on your machine. You can download it from the [official website](https://www.terraform.io/downloads.html).  
   
2. **Authenticate with GCP:**  
  
   Use the Google Cloud SDK to authenticate:  
  
   ```bash  
   gcloud auth application-default login  
   ```  
   
3. **Initialize Terraform:**  
  
   Navigate to the `terraform` directory and initialize Terraform.  
  
   ```bash  
   cd terraform  
   terraform init  
   ```  
   
4. **Set Variables:**  
  
   You can define variables in a `terraform.tfvars` file or pass them via the command line.  
  
   **Example `terraform.tfvars`:**  
  
   ```hcl  
   project_id             = "your-gcp-project-id"  
   data_scientist_group   = "group:data-scientists@example.com"  
   db_password            = "your-db-password"  
   ```  
  
   **Note:** For sensitive variables like `db_password`, consider using environment variables or a secrets manager.  
   
5. **Review the Plan:**  
  
   Run `terraform plan` to review the actions Terraform will take.  
  
   ```bash  
   terraform plan  
   ```  
   
6. **Apply the Configuration:**  
  
   Apply the Terraform configuration to build the infrastructure.  
  
   ```bash  
   terraform apply  
   ```  
  
   Confirm the action when prompted.  
   
---  
   
### **Sample Success Statements**  
   
#### **Terraform Apply Output**  
   
```plaintext  
Terraform will perform the following actions:  
  
  # google_compute_instance.instance will be created  
  + resource "google_compute_instance" "instance" {  
      + can_ip_forward       = false  
      + cpu_platform         = (known after apply)  
      + deletion_protection  = false  
      + id                   = (known after apply)  
      + instance_id          = (known after apply)  
      + label_fingerprint    = (known after apply)  
      + machine_type         = "n1-standard-1"  
      + metadata             = (known after apply)  
      + name                 = "compute-instance"  
      + project              = "your-gcp-project-id"  
      + self_link            = (known after apply)  
      + tags                 = [  
          + "compute-engine",  
          + "allow-ssh",  
        ]  
      + zone                 = "us-central1-a"  
  
      # ... (output truncated for brevity)  
   
Plan: 15 to add, 0 to change, 0 to destroy.  
   
Do you want to perform these actions?  
  Terraform will perform the actions described above.  
  Only 'yes' will be accepted to approve.  
  
  Enter a value: yes  
   
google_compute_network.vpc_network: Creating...  
google_compute_network.vpc_network: Creation complete after 2s [id=projects/your-gcp-project-id/global/networks/main-vpc]  
google_compute_subnetwork.public_subnet: Creating...  
google_compute_subnetwork.private_subnet: Creating...  
google_compute_subnetwork.private_subnet: Creation complete after 1s [id=projects/your-gcp-project-id/regions/us-central1/subnetworks/main-vpc-private]  
google_compute_subnetwork.public_subnet: Creation complete after 1s [id=projects/your-gcp-project-id/regions/us-central1/subnetworks/main-vpc-public]  
   
# ... (output truncated for brevity)  
   
Apply complete! Resources: 15 added, 0 changed, 0 destroyed.  
   
Outputs:  
   
cloud_sql_instance_connection_name = "your-gcp-project-id:us-central1:cloud-sql-instance"  
compute_instance_external_ip = "34.68.123.45"  
dataproc_cluster_name = "dataproc-cluster"  
```  
   
#### **Terraform Destroy Output**  
   
To roll back (destroy) the infrastructure, run:  
   
```bash  
terraform destroy  
```  
   
**Sample Output:**  
   
```plaintext  
Plan: 0 to add, 0 to change, 15 to destroy.  
   
Do you really want to destroy all resources?  
  Terraform will destroy all your managed infrastructure.  
  
  Enter a value: yes  
   
google_sql_user.user: Destroying... [id=your-gcp-project-id/cloud-sql-instance/dbuser]  
google_sql_database.database: Destroying... [id=your-gcp-project-id/cloud-sql-instance/defaultdb]  
google_sql_user.user: Destruction complete after 2s  
google_sql_database.database: Destruction complete after 2s  
google_sql_database_instance.instance: Destroying... [id=projects/your-gcp-project-id/instances/cloud-sql-instance]  
   
# ... (output truncated for brevity)  
   
google_compute_network.vpc_network: Destroying... [id=projects/your-gcp-project-id/global/networks/main-vpc]  
google_compute_network.vpc_network: Destruction complete after 1s  
   
Destroy complete! Resources: 15 destroyed.  
```  
   
---  
   
### **Notes and Considerations**  
   
- **Sensitive Data Handling:**  
  
  - Avoid hardcoding sensitive information like passwords in your Terraform files.  
  - Use Terraform's `-var` command-line option, environment variables, or integrate with secret managers.  
   
- **Service Account Email:**  
  
  - For `service_account_email`, you can specify a custom service account or use the default Compute Engine service account by setting it to `default`.  
   
- **Adjust Resource Specifications:**  
  
  - Modify machine types, number of instances, and other resource specifications to fit your needs and quotas.  
   
- **API Enablement:**  
  
  - The `google_project_service` resources ensure that required APIs are enabled. Depending on your permissions, you may need to enable APIs manually or adjust permissions.  
   
- **Dependencies:**  
  
  - The `depends_on` attribute can ensure proper resource creation order, especially when enabling services.  
   
- **Monitoring Module:**  
  
  - Customize the monitoring module to include the alert policies and checks relevant to your environment.  
   
- **Firewall Rules:**  
  
  - Adjust firewall rules to comply with your organization's security policies.  
   
---  
   
### **Conclusion**  
   
By applying these Terraform scripts, you can build and manage your infrastructure in GCP, adhering to security best practices while providing the necessary resources for your analysts and data scientists. The scripts are modular, allowing you to extend and customize them as required. Always ensure to review and test the scripts in a non-production environment before deploying them to production.  
   
If you have any questions or need further assistance with specific configurations or modules, feel free to ask!
