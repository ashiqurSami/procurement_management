[View Project Descriptions and Requirements](./project_description.pdf)

# Youth Skill Development Training Program - Odoo Supplier Management System

## Project Overview
This project is a comprehensive supplier management system developed as part of the Youth Skill Development Training Program (Nov'24 - Feb'25). Built using the Odoo framework, it streamlines supplier registration, Request for Proposal (RFP) creation, quotation management, and provides insightful reporting and dashboard functionalities to enhance decision-making processes.

## Features
1. **Email Verification with Evaluation**: Validates supplier email addresses with OTP-based verification, including blacklist checks.
2. **Supplier Registration Form**: A multi-section form capturing company information, financial details, client references, certifications, and document submissions, integrated with Odoo's Vendor model.
3. **Two-Step Verification Process**: Includes initial review and final approval for supplier account creation, with automated vendor record generation and email notifications.
4. **RFP Creation and Quotation Management**: Allows reviewers to create and publish RFPs, suppliers to submit quotations, and reviewers to score and recommend suppliers.
5. **Reporting**: Generates Qweb-HTML previews and Excel reports for RFPs using the xlswriter package, including supplier details and product breakdowns.
6. **Data Visualization**: Provides graph and pivot views for RFP analysis, with line graphs for total amounts and pivot tables for supplier-based metrics.
7. **Interactive Dashboard**: Built with OWL components, offering supplier-specific metrics like approved RFQs, total amounts, and product-wise breakdowns, with customizable date ranges and graphical representations.

## Technical Requirements
- **Framework**: Odoo 17.0
- **Web Library**: OWL (Odoo Web Library) for dashboard development
- **Data Visualization**: Utilizes Odoo’s built-in graphing tools or compatible libraries (e.g., Chart.js, Plotly)
- **Security**: Adheres to Odoo’s ORM methods for data access, input validation, and encryption of sensitive data
- **Containerization**: Dockerized application with all dependencies encapsulated
- **Web Server**: Nginx configured as a reverse proxy for request handling, load balancing, and URL routing
- **Coding Guidelines**: Follows Odoo’s coding standards as per [Odoo 17.0 Coding Guidelines](https://www.odo.com/documentation/17.0/contributing/development/coding_guidelines.html)

## Installation

### Prerequisites
- Docker
- Docker Compose
- Nginx
- Odoo 17.0 dependencies (refer to `requirements.txt` for specifics)

### Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd procurement_management
   ```

2. **Build and Run Docker Container**:
   ```bash
   docker-compose build
   docker-compose up -d
   ```

3. **Configure Nginx**:
   - Update the Nginx configuration file (`nginx.conf`) located in the `nginx` directory.
   - Ensure the reverse proxy points to the Docker container’s application port (default: 8069).
   - Reload Nginx:
     ```bash
     sudo nginx -t
     sudo systemctl reload nginx
     ```

4. **Access the Application**:
   - Open a browser and navigate to `http://<your-server-ip>:8069`.
   - Log in with the default admin credentials or create a new user account.

### Troubleshooting
- **Container Issues**: Verify Docker services are running (`docker ps`) and check logs (`docker-compose logs`).
- **Nginx Errors**: Ensure correct port mapping and valid SSL certificates (if applicable). Check Nginx logs at `/var/log/nginx/error.log`.
- **Odoo Errors**: Review Odoo logs in the container for database or module issues.

## Dependencies
- **Odoo Modules**: `base`, `web`, `mail`, `purchase`
- **Python Libraries**: `xlswriter` (for Excel reports)
- **External Libraries**: Chart.js or Plotly (for dashboard visualizations)
- **Database**: PostgreSQL (included in Docker container)
- Full dependency list available in `requirements.txt`.

## Usage
1. **Supplier Registration**:
   - Suppliers access the portal, verify their email via OTP, and complete the multi-section registration form.
   - Reviewers approve or reject applications through the two-step verification process.

2. **RFP Management**:
   - Reviewers create RFPs via the backend, specifying products and requirements.
   - Suppliers submit quotations through the portal’s RFP menu.
   - Reviewers score and recommend suppliers, with approvers finalizing selections.

3. **Reports and Dashboard**:
   - Generate RFP reports via the reporting menu, selecting suppliers and date ranges.
   - Access the dashboard to view supplier metrics, visualized with graphs and tables.

## Testing
- **Unit Tests**: Implemented for OWL components to validate dashboard functionality.
- **Integration Tests**: Ensure seamless interaction between supplier registration, RFP management, and reporting modules.
- Run tests using:
  ```bash
  docker exec -it <container-name> odoo -c /etc/odoo/odoo.conf --test-enable
  ```

## Notes
- This project adheres to Odoo’s UI/UX guidelines for consistent design.
- AI assistant tools were not used in development, as per training program guidelines.
- Ensure all sensitive data (e.g., login credentials) is encrypted and handled securely.

## Contributors
Developed by the Odoo Team as part of the Youth Skill Development Training Program (Nov'24 - Feb'25).
