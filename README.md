# AccessPark

AccessPark - a cloud-native application built on AWS helps find accessibility parking. It helps users locate accessible parking spots across Canadian cities, starting with Halifax and Toronto. Users can view all locations, filter by city, or search by location and radius. 
The app is designed for the general public, city planners, and accessibility-focused organizations. Performance targets include high availability, weekly data updates, and low-latency API responses.

## Deployment Steps

Prerequisites:
- Terraform
- AWS Account

Step 1: Create or update AWS credentials. 
  - Login into AWS account.
  - Open AWS CLI and copy credentials from `~/.aws/credentials` and configure it in local by executing `aws configure`.

Step 2: Run Terraform 
  - Go to the root directory of the application where `main.tf` file is present.
  - `terraform init` to initialize the terraform project.
  - `terraform apply` to start creating infrastructure. 

## Application Architecture
The executable for Lambda function is stored in the S3 bucket. The Lambda
function is triggerd every week once by the EventBridge. It then pulls open
data and stores it in the RDS(private subnet). The Lambda sits in a private
subnet with internet access via NAT Gateway. The FastAPI app in EC2 (public
subnet) queries RDS and exposes endpoints.

![AccessPark drawio](https://github.com/user-attachments/assets/8d801c4f-13ed-4fb6-ac64-1e3bf18aa77b)

## Services Used

1. **AWS Lambda (compute)** - Runs ETL process on demand. Responsible for
ingestion, cleaning, pre-processing and loading of data from open source
government repository.
2. **AWS RDS MySQL (database)** - A place to store the structured data from
the ETL process.
3. **EventBridge (scheduler)** - Triggers the AWS Lambda every one week,
maintaining up-to-date information.
4. **Amazon EC2 with FastAPI (web server)** - A service that exposes APIs of
the data stored in RDS to users on the internet
5. **AWS VPC with NAT Gateway (networking)** - A service that makes all the
resources sit within the same network, achieving secure connection within
and outside the network.
6. **S3 (storage)** - Stores the executable necessary to run the Lambda function.
7. **Amazon Cloud Watch (Monitoring)** - A service that is used to view application logs and resource utilization of the Lambda Service.

## Delivery Model
A hybrid delivery model using FaaS (Lambda) for ingestion and IaaS (EC2)
for serving the API. This model balances cost and control—serverless reduces
operational overhead for ingestion, while EC2 offers flexibility for deploying and
scaling the FastAPI app.

## Cost Metrics

**Costs include:**
• Upfront: Minimal (EC2 launch, NAT setup).
• Ongoing: EC2 (on-demand), RDS (multi-AZ), Lambda (pay-per-use), NAT Gateway (hourly + data processed).

**Optimization:**
• Use S3 + Athena instead of RDS to cut database costs.
• Switch to Fargate for API to avoid EC2 idle costs.
• Use Savings Plans for predictable EC2/RDS workloads.

## End-points

**1) Get All Parking Spots**

**Endpoint:** `GET /parking`
**Description:** Retrieves all parking spots from the database.
**Response:**
```
json[
  {
    "city_lot_id": "string",
    "name": "string",
    "no_of_spots": 0,
    "location": "string",
    "city": "string",
    "state": "string",
    "country": "string"
  }
]
```
**2) Get Parking Spots by City**

**Endpoint:** `GET /parking/city/{city}`

**Description:** Retrieves parking spots filtered by city name.

**Path Parameters:**
city: (String) The name of the city to filter by


**Response:**
```
json[
  {
    "city_lot_id": "string",
    "name": "string",
    "no_of_spots": 0,
    "location": "string",
    "city": "string",
    "state": "string",
    "country": "string"
  }
]
```
**3) Get Parking Spots by Location**

**Endpoint:** `POST /parking/location`

**Description:** Finds parking spots within a specified radius of given coordinates.

**Request Body:**

```
json{
  "lat": 0.0,
  "lon": 0.0,
  "radius": 0.0
}
```

**Response:**
```
json[
  {
    "city_lot_id": "string",
    "name": "string",
    "no_of_spots": 0,
    "location": "string",
    "city": "string",
    "state": "string",
    "country": "string"
  }
]
```
