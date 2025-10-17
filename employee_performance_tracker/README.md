# Employee Performance Tracker

A comprehensive employee performance management system that combines SQLite for structured data and MongoDB for flexible performance review documents.

## 🎯 Project Overview

This system provides a complete solution for managing employees, projects, and performance reviews with the following key features:

- **Employee Management**: Add, update, and manage employee records
- **Project Management**: Create projects, assign employees, and track progress
- **Performance Reviews**: Flexible review system with role-specific fields
- **Reporting**: Generate detailed reports and analytics
- **Hybrid Database**: SQLite for structured data, MongoDB for flexible documents

## 🏗️ System Architecture

### Database Setup
- **SQLite**: Stores employee and project data with relational structure
- **MongoDB**: Stores flexible performance review documents
- **Hybrid Approach**: Links employee IDs between databases for seamless integration

### Key Components
- `main.py` - Main application entry point with CLI interface
- `employee_manager.py` - Employee CRUD operations and validation
- `project_manager.py` - Project management and employee assignments
- `performance_reviewer.py` - Performance review system with flexible document structure
- `reports.py` - Reporting and analytics functions
- `database_connections.py` - Database connection management

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- MongoDB Atlas account (free)
- Git (optional)

### Installation

1. **Clone or download the project**
   ```bash
   cd employee_performance_tracker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MongoDB** (see MongoDB Setup section below)

4. **Run the application**
   ```bash
   python main.py
   ```

## 🗄️ MongoDB Setup

### Option A: MongoDB Atlas (Recommended)

MongoDB Atlas provides a free cloud-hosted MongoDB service that's perfect for development and small applications.

#### Step 1: Create MongoDB Atlas Account
1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Sign up for a free account
3. Create a free cluster (M0 Sandbox)

#### Step 2: Configure Network Access
1. In Atlas dashboard, go to "Network Access"
2. Add your IP address or use `0.0.0.0/0` for development (not recommended for production)
3. Click "Add Entry"

#### Step 3: Create Database User
1. Go to "Database Access"
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Create username and password
5. Grant "Read and write to any database" permissions

#### Step 4: Get Connection String
1. In Atlas dashboard, click "Connect" on your cluster
2. Choose "Connect your application"
3. Select "Python" and version "3.6 or later"
4. Copy the connection string

#### Step 5: Configure Environment
Create or update the `.env` file in the project directory:

```env
# MongoDB Atlas Configuration
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=performance_reviews_db
MONGO_COLLECTION_NAME=reviews

# SQLite Configuration
SQLITE_FILE=company.db
```

**Important**: Replace `<username>` and `<password>` with your actual database user credentials, and update the cluster URL.

### Testing Your Setup

Run the setup script to verify everything is working:

```bash
python database_connections.py
```

You should see:
```
===  ===
[INFO] SQLite tables ready
[INFO] MongoDB collection ready: reviews

```

## 📖 How to Use

### Main Menu Options

1. **Employee Menu**
   - Add new employees
   - List All Employees
   - Update Employees
   - Delete Employees
   - Search by Name
   - Search by Department
   - Recently Hired Employees
   - Export Employees to CSV

2. **Project Menu**
   - Add Project
   - List All Projects
   - Update Project
   - Delete Project
   - Assign Employee to Project
   - Unassign Employee from Project
   - Get Projects for Employee
   - Get Employees for Project
   - Search Projects by Name
   - Get Projects by Status
   - Get Project Count by Status
   - Bulk Assign Employee
   - Export Projects to CSV
   

3. **Performance Review Menu**
   - Submit Performance Review (Interactive)
   - Submit Performance Review (Comprehensive Form)
   - Get Reviews for Employee
   - Get Average Rating for Employee
   - Update Performance Review
   - Delete Performance Review
   - Get Recent Reviews
   - Get Reviews by Reviewer
   - Get Reviews by Date Range
   - Aggregate Strengths
   - Aggregate Areas for Improvement
   - Get Top Goals


4. **Reports Menu**
   - List all employees
   - Employee detailed reports
   - List all projects
   - Top performers
   - Reviews by date range

### Sample Workflow

1. **Add an Employee**
   ```
   Main Menu → Employee Menu → Add Employee
   Name: John Doe
   Email: john.doe@company.com
   Hire Date: 2023-01-15
   Department: Engineering
   ```

2. **Create a Project**
   ```
   Main Menu → Project Menu → Add Project
   Project Name: Apollo CRM Revamp
   Start Date: 2025-07-01
   Status: In Progress
   ```

3. **Assign Employee to Project**
   ```
   Main Menu → Project Menu → Assign Employee to Project
   Project ID: 1
   Employee ID: 1
   ```

4. **Submit Performance Review**
   ```
   Main Menu → Performance Review Menu → Submit Performance Review
   Employee ID: 1
   Reviewer: Sarah Manager
   Rating: 4.5
   Strengths: Excellent technical skills, great team player
   Areas for Improvement: Time management
   Goals: Complete AWS certification
   ```

## 📊 Performance Review Document Structure

The system uses MongoDB's flexible document structure to store performance reviews with varying fields based on roles:

### Standard Fields
```javascript
{
    "_id": ObjectId("..."),
    "review_id": 1,                    // Auto-incrementing integer
    "employee_id": 1,                   // Links to SQLite employee
    "review_date": "2024-01-15",
    "reviewer_name": "Sarah Manager",
    "overall_rating": 4.5,
    "strengths": "Excellent technical skills",
    "areas_for_improvement": "Time management",
    "comments": "Outstanding performance",
    "goals_for_next_period": "Complete AWS certification",
    "created_at": "2024-01-15T10:30:00.000Z"
}
```

## 🧪 Testing

The project includes comprehensive test coverage using pytest:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=. --cov-report term-missing

# Run specific test file
pytest tests/test_employee_manager.py
```

### Test Coverage
- Employee Manager: 80% + coverage
- Project Manager: 80% + coverage  
- Performance Reviewer: 80% + coverage
- Reports: 80% + coverage

## 📁 Project Structure

```
employee_performance_tracker/
├── main.py                           # Main application entry point
├── database_connections.py           # Database connection management
├── employee_manager.py               # Employee CRUD operations
├── project_manager.py               # Project management
├── performance_reviewer.py           # Performance review system
├── reports.py                        # Reporting and analytics
├── requirements.txt                  # Python dependencies
├── setup.cfg                         # Pytest configuration
├── .env                             # Environment variables
├── company.db                       # SQLite database file
├── tests/                           # Test files
│   ├── conftest.py                  # Test fixtures
│   ├── test_employee_manager.py     # Employee tests
│   ├── test_project_manager.py      # Project tests
│   ├── test_performance_reviewer.py # Performance review tests
│   └── test_reports.py              # Reports tests
└── README.md                        # This file
```

## 🔧 Configuration

### Environment Variables (.env file)

```env
# MongoDB Configuration
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority 
MONGO_DB_NAME=performance_reviews_db
MONGO_COLLECTION_NAME=reviews

# SQLite Configuration
SQLITE_FILE=company.db
```
### For now have uploaded .env file in the drive project folder
## Make sure you put it inside employee_performance_tracker folder
### Dependencies (requirements.txt)

```
dnspython==2.8.0
pymongo==4.15.3
python-dotenv==1.1.1
tabulate==0.9.0
pytest==8.3.3
pytest-cov==5.0.0
```

## 🚨 Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Verify your `.env` file configuration
   - Check MongoDB Atlas network access settings
   - Ensure MongoDB service is running (local installation)
   - Verify username/password are correct

2. **SQLite Error**
   - Ensure write permissions in project directory
   - Check if `company.db` file exists and is accessible

3. **Import Errors**
   - Run `pip install -r requirements.txt`
   - Verify Python version (3.8+ required)
   - Check virtual environment activation

4. **Performance Review Issues**
   - Ensure MongoDB connection is working
   - Check if employee exists in SQLite before submitting review
   - Verify review_id is being generated correctly

### Getting Help

1. Check the troubleshooting section above
2. Run `python database_connections.py` to diagnose issues
3. Verify all dependencies are installed correctly
4. Check MongoDB Atlas dashboard for connection issues

## 🎯 Key Features

### Employee Management
- Complete CRUD operations
- Email validation and uniqueness
- Department tracking
- Hire date management

### Project Management
- Project creation and status tracking
- Employee assignment/unassignment
- Project search and filtering
- CSV export functionality

### Performance Reviews
- Flexible document structure
- Role-specific fields
- Rating calculations and analytics
- Date range filtering
- Reviewer-based queries
- Goal tracking and aggregation

### Reporting
- Employee detailed reports with project assignments
- Project detailed reports with team members
- Top performers analysis
- Review analytics and insights

## 🔄 Data Flow

1. **Employee Data**: Stored in SQLite with structured schema
2. **Project Data**: Stored in SQLite with employee-project relationships
3. **Performance Reviews**: Stored in MongoDB with flexible document structure
4. **Linking**: Employee IDs connect SQLite and MongoDB data
5. **Reports**: Combine data from both databases for comprehensive insights

## 🚀 Future Enhancements

- Web-based interface
- Email notifications
- Advanced analytics dashboard
- Integration with HR systems
- Mobile application
- Automated review scheduling

## 📄 Authors
    -- Group 5 V4C