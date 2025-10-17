# performance_reviewer.py
"""
Performance Review Module (MongoDB)

Responsibilities:
- Submit performance reviews to MongoDB
- Retrieve performance reviews for specific employees
- Handle flexible document structure for evolving review criteria
- Update and delete performance reviews
- Aggregate review data for insights
- Validate review data with user-friendly error handling

Assumptions:
- database_connections.get_mongo_collection() returns a MongoDB collection
- database_connections.get_sqlite_connection() returns a SQLite connection
- Reviews are stored as flexible documents in MongoDB
- Each review document contains employee_id for linking to SQLite employees
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Optional, Any, Union
from bson import ObjectId
from collections import Counter
import re

from database_connections import get_mongo_collection, get_sqlite_connection


# -------------------------
# Validation Helpers
# -------------------------
def validate_employee_exists(employee_id: int) -> bool:
    """Check if employee exists in SQLite database."""
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT employee_id FROM employees WHERE employee_id = ?", (employee_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    except Exception:
        return False


def validate_reviewer_name(reviewer_name: str) -> bool:
    """Validate reviewer name is non-empty string."""
    return isinstance(reviewer_name, str) and reviewer_name.strip() != ""


def validate_overall_rating(rating: Union[int, float]) -> bool:
    """Validate overall rating is numeric and within 1-5 scale."""
    try:
        rating_val = float(rating)
        return 1.0 <= rating_val <= 5.0
    except (ValueError, TypeError):
        return False


def validate_review_date(review_date: Union[str, datetime]) -> bool:
    """Validate review date is not in the future."""
    try:
        if isinstance(review_date, str):
            date_obj = datetime.strptime(review_date, "%Y-%m-%d")
        elif isinstance(review_date, datetime):
            date_obj = review_date
        else:
            return False
        
        return date_obj <= datetime.now()
    except (ValueError, TypeError):
        return False


def validate_extra_fields(**extra_fields) -> bool:
    """Validate extra fields structure if they contain strengths/areas/goals."""
    for key, value in extra_fields.items():
        if key in ['strengths', 'areas_for_improvement', 'goals_for_next_period']:
            # Allow None, empty string, or any non-empty string
            if value is not None and isinstance(value, str) and value.strip() == "":
                # Empty string is fine, we'll treat it as None
                continue
            elif value is not None and not isinstance(value, (str, list, dict)):
                return False
    return True


def validate_review_data(employee_id: int, reviewer_name: str, overall_rating: Union[int, float], 
                        review_date: Union[str, datetime] = None, **extra_fields) -> Dict[str, str]:
    """
    Comprehensive validation of review data.
    Returns dict with validation results and error messages.
    """
    errors = {}
    
    # Validate employee exists
    if not isinstance(employee_id, int) or employee_id <= 0:
        errors['employee_id'] = "Employee ID must be a positive integer."
    elif not validate_employee_exists(employee_id):
        errors['employee_id'] = f"Employee ID {employee_id} does not exist in the database."
    
    # Validate reviewer name
    if not validate_reviewer_name(reviewer_name):
        errors['reviewer_name'] = "Reviewer name must be a non-empty string."
    
    # Validate overall rating
    if not validate_overall_rating(overall_rating):
        errors['overall_rating'] = "Overall rating must be a number between 1.0 and 5.0."
    
    # Validate review date if provided
    if review_date is not None and not validate_review_date(review_date):
        errors['review_date'] = "Review date must be a valid date and cannot be in the future."
    
    # Validate extra fields
    if not validate_extra_fields(**extra_fields):
        errors['extra_fields'] = "Invalid format for strengths, areas_for_improvement, or goals_for_next_period."
    
    return errors


def get_user_input_with_validation(prompt: str, validation_func, error_msg: str, **kwargs):
    """Get user input with validation and retry on invalid input."""
    while True:
        try:
            value = input(prompt)
            if validation_func(value, **kwargs):
                return value
            else:
                print(f"[WARNING]  {error_msg}")
                print("Please try again.")
        except KeyboardInterrupt:
            print("\n[WARNING]  Operation cancelled by user.")
            return None
        except Exception as e:
            print(f"[WARNING]  Error: {e}")
            print("Please try again.")


def get_optional_text_input(prompt: str) -> Optional[str]:
    """Get optional text input that can be empty."""
    value = input(prompt).strip()
    return value if value else None


def validate_optional_text(value: str) -> bool:
    """Validate optional text field - always returns True since it's optional."""
    return True


# -------------------------
# Core Review Functions
# -------------------------
def submit_performance_review(
    collection=None,
    employee_id: int = None,
    reviewer_name: str = None,
    overall_rating: float = None,
    review_date: Union[str, datetime] = None,
    strengths: str = None,
    areas_for_improvement: str = None,
    comments: str = None,
    goals_for_next_period: str = None,
    **extra_fields
) -> Optional[str]:
    """
    Submit a new performance review to MongoDB with enhanced validation.

    Args:
        collection: MongoDB collection (optional, will get default if not provided)
        employee_id: ID of the employee being reviewed (links to SQLite employees table)
        reviewer_name: Name of the person conducting the review
        overall_rating: Overall performance rating (1.0-5.0)
        review_date: Date of review in 'YYYY-MM-DD' format or datetime object (defaults to today)
        strengths: Employee's strengths (optional)
        areas_for_improvement: Areas needing improvement (optional)
        comments: General comments (optional)
        goals_for_next_period: Goals for the next review period (optional)
        **extra_fields: Additional custom fields

    Returns:
        MongoDB document ID as string, or None if validation fails

    Note:
        If any required parameters are None, function will prompt user for input with validation.
    """
    # Get collection if not provided
    if collection is None:
        try:
            collection = get_mongo_collection()
        except Exception as e:
            print(f"[WARNING]  Failed to connect to MongoDB: {e}")
            return None
    
    print("\n=== Performance Review Submission ===")
    
    # Interactive input for all required fields
    if employee_id is None:
        employee_id = get_user_input_with_validation(
            "Enter employee ID: ",
            lambda x: isinstance(int(x), int) and int(x) > 0,
            "Employee ID must be a positive integer."
        )
        if employee_id is None:
            return None
        employee_id = int(employee_id)
    
    if reviewer_name is None:
        reviewer_name = get_user_input_with_validation(
            "Enter reviewer name: ",
            validate_reviewer_name,
            "Reviewer name must be a non-empty string."
        )
        if reviewer_name is None:
            return None
    
    if overall_rating is None:
        overall_rating = get_user_input_with_validation(
            "Enter overall rating (1.0-5.0): ",
            lambda x: validate_overall_rating(float(x)),
            "Overall rating must be a number between 1.0 and 5.0."
        )
        if overall_rating is None:
            return None
        overall_rating = float(overall_rating)
    
    if review_date is None:
        review_date = get_user_input_with_validation(
            "Enter review date (YYYY-MM-DD) or press Enter for today: ",
            lambda x: x.strip() == "" or validate_review_date(x),
            "Review date must be valid and not in the future."
        )
        if review_date is None:
            return None
        if review_date.strip() == "":
            review_date = datetime.now().strftime("%Y-%m-%d")
    
    # Interactive input for optional fields
    if strengths is None:
        strengths = get_optional_text_input("Enter employee strengths (optional): ")
    
    if areas_for_improvement is None:
        areas_for_improvement = get_optional_text_input("Enter areas for improvement (optional): ")
    
    if comments is None:
        comments = get_optional_text_input("Enter general comments (optional): ")
    
    if goals_for_next_period is None:
        goals_for_next_period = get_optional_text_input("Enter goals for next period (optional): ")
    
    # Validate all data (this should now pass since we validated each field individually)
    validation_errors = validate_review_data(
        employee_id, reviewer_name, overall_rating, review_date, 
        strengths=strengths, areas_for_improvement=areas_for_improvement,
        comments=comments, goals_for_next_period=goals_for_next_period,
        **extra_fields
    )
    
    if validation_errors:
        print("[WARNING]  Validation errors found:")
        for field, error in validation_errors.items():
            print(f"   - {field}: {error}")
        return None
    
    # Build the review document
    review_doc = {
        "employee_id": employee_id,
        "reviewer_name": reviewer_name.strip(),
        "overall_rating": float(overall_rating),
        "review_date": review_date.strftime("%Y-%m-%d") if isinstance(review_date, datetime) 
                      else (review_date or datetime.now().strftime("%Y-%m-%d")),
        "created_at": datetime.now().isoformat(),
    }
    
    # Add standard fields if provided
    if strengths is not None:
        review_doc["strengths"] = strengths.strip()
    if areas_for_improvement is not None:
        review_doc["areas_for_improvement"] = areas_for_improvement.strip()
    if comments is not None:
        review_doc["comments"] = comments.strip()
    if goals_for_next_period is not None:
        review_doc["goals_for_next_period"] = goals_for_next_period.strip()
    
    # Add extra fields if provided
    for key, value in extra_fields.items():
        if value is not None:
            if isinstance(value, str):
                review_doc[key] = value.strip()
            else:
                review_doc[key] = value
    
    try:
        result = collection.insert_one(review_doc)
        print(f"[SUCCESS] Performance review submitted successfully with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        print(f"[WARNING] Failed to submit performance review: {e}")
        return None


def get_performance_reviews_for_employee(
    collection=None,
    employee_id: int = None
) -> List[Dict[str, Any]]:
    """
    Retrieve all performance reviews for a specific employee.

    Args:
        collection: MongoDB collection (optional, will get default if not provided)
        employee_id: ID of the employee

    Returns:
        List of review documents as dictionaries
    """
    # Get collection if not provided
    if collection is None:
        try:
            collection = get_mongo_collection()
        except Exception as e:
            print(f"[WARNING]  Failed to connect to MongoDB: {e}")
            return []
    
    # Interactive input if employee_id not provided
    if employee_id is None:
        employee_id = get_user_input_with_validation(
            "Enter employee ID: ",
            lambda x: isinstance(int(x), int) and int(x) > 0,
            "Employee ID must be a positive integer."
        )
        if employee_id is None:
            return []
        employee_id = int(employee_id)
    
    try:
        # Build query
        query = {"employee_id": employee_id}
        
        # Execute query with sort by date descending
        cursor = collection.find(query).sort("review_date", -1)
        
        # Convert ObjectId to string for JSON serialization
        reviews = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
            reviews.append(doc)
        
        print(f"[SUCCESS] Found {len(reviews)} reviews for employee {employee_id}")
        return reviews
    except Exception as e:
        print(f"[WARNING]  Failed to retrieve performance reviews: {e}")
        return []


def get_all_performance_reviews(
    limit: Optional[int] = None,
    sort_by_date: bool = True,
) -> List[Dict[str, Any]]:
    """
    Retrieve all performance reviews across all employees.

    Args:
        limit: Maximum number of reviews to return (optional)
        sort_by_date: If True, sort by review_date descending (most recent first)

    Returns:
        List of all review documents as dictionaries

    Raises:
        Exception for MongoDB connection/query errors
    """
    try:
        collection = get_mongo_collection()
        
        # Build sort criteria
        sort_criteria = [("review_date", -1)] if sort_by_date else []
        
        # Execute query
        cursor = collection.find({})
        if sort_criteria:
            cursor = cursor.sort(sort_criteria)
        if limit:
            cursor = cursor.limit(limit)
        
        # Convert ObjectId to string for JSON serialization
        reviews = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
            reviews.append(doc)
        
        return reviews
    except Exception as e:
        raise Exception(f"Failed to retrieve all performance reviews: {e}")


def get_average_rating_for_employee(
    collection=None,
    employee_id: int = None
) -> Optional[float]:
    """
    Calculate the average performance rating for an employee.

    Args:
        collection: MongoDB collection (optional, will get default if not provided)
        employee_id: ID of the employee

    Returns:
        Average rating as float, or None if no reviews found
    """
    # Get collection if not provided
    if collection is None:
        try:
            collection = get_mongo_collection()
        except Exception as e:
            print(f"[WARNING]  Failed to connect to MongoDB: {e}")
            return None
    
    # Interactive input if employee_id not provided
    if employee_id is None:
        employee_id = get_user_input_with_validation(
            "Enter employee ID: ",
            lambda x: isinstance(int(x), int) and int(x) > 0,
            "Employee ID must be a positive integer."
        )
        if employee_id is None:
            return None
        employee_id = int(employee_id)
    
    try:
        # Use MongoDB aggregation to calculate average
        pipeline = [
            {"$match": {"employee_id": employee_id}},
            {"$group": {
                "_id": None,
                "average_rating": {"$avg": "$overall_rating"},
                "review_count": {"$sum": 1}
            }}
        ]
        
        result = list(collection.aggregate(pipeline))
        
        if result and result[0]["review_count"] > 0:
            avg_rating = round(result[0]["average_rating"], 2)
            print(f"[SUCCESS] Average rating for employee {employee_id}: {avg_rating}")
            return avg_rating
        else:
            print(f"[WARNING]  No reviews found for employee {employee_id}")
            return None
    except Exception as e:
        print(f"[WARNING]  Failed to calculate average rating: {e}")
        return None


def update_performance_review(
    collection=None,
    review_id: str = None,
    **fields_to_update
) -> bool:
    """
    Update a specific performance review by its MongoDB document ID.

    Args:
        collection: MongoDB collection (optional, will get default if not provided)
        review_id: MongoDB document ID as string
        **fields_to_update: Fields to update with their new values

    Returns:
        True if review was updated, False otherwise
    """
    # Get collection if not provided
    if collection is None:
        try:
            collection = get_mongo_collection()
        except Exception as e:
            print(f"[WARNING]  Failed to connect to MongoDB: {e}")
            return False
    
    # Interactive input if review_id not provided
    if review_id is None:
        review_id = get_user_input_with_validation(
            "Enter review ID to update: ",
            lambda x: isinstance(x, str) and len(x.strip()) > 0,
            "Review ID must be a non-empty string."
        )
        if review_id is None:
            return False
    
    # Check if review exists
    try:
        existing_review = collection.find_one({"_id": ObjectId(review_id)})
        if not existing_review:
            print(f"[WARNING]  Review with ID {review_id} not found.")
            return False
    except Exception as e:
        print(f"[WARNING]  Invalid review ID format: {e}")
        return False
    
    # Validate fields to update
    if not fields_to_update:
        print("[WARNING]  No fields provided for update.")
        return False
    
    # Validate each field
    validation_errors = {}
    for field, value in fields_to_update.items():
        if field == "employee_id":
            if not isinstance(value, int) or value <= 0:
                validation_errors[field] = "Employee ID must be a positive integer."
            elif not validate_employee_exists(value):
                validation_errors[field] = f"Employee ID {value} does not exist."
        elif field == "reviewer_name":
            if not validate_reviewer_name(value):
                validation_errors[field] = "Reviewer name must be a non-empty string."
        elif field == "overall_rating":
            if not validate_overall_rating(value):
                validation_errors[field] = "Overall rating must be between 1.0 and 5.0."
        elif field == "review_date":
            if not validate_review_date(value):
                validation_errors[field] = "Review date must be valid and not in the future."
    
    if validation_errors:
        print("[WARNING]  Validation errors found:")
        for field, error in validation_errors.items():
            print(f"   - {field}: {error}")
        return False
    
    # Prepare update document
    update_doc = {}
    for field, value in fields_to_update.items():
        if field == "review_date" and isinstance(value, datetime):
            update_doc[field] = value.strftime("%Y-%m-%d")
        elif isinstance(value, str):
            update_doc[field] = value.strip()
        else:
            update_doc[field] = value
    
    try:
        result = collection.update_one(
            {"_id": ObjectId(review_id)},
            {"$set": update_doc}
        )
        
        if result.modified_count > 0:
            print(f"[SUCCESS] Review {review_id} updated successfully.")
            return True
        else:
            print(f"[WARNING]  No changes made to review {review_id}.")
            return False
    except Exception as e:
        print(f"[WARNING]  Failed to update review: {e}")
        return False


def delete_performance_review(
    collection=None,
    review_id: str = None
) -> bool:
    """
    Delete a specific performance review by its MongoDB document ID.

    Args:
        collection: MongoDB collection (optional, will get default if not provided)
        review_id: MongoDB document ID as string

    Returns:
        True if review was deleted, False if not found
    """
    # Get collection if not provided
    if collection is None:
        try:
            collection = get_mongo_collection()
        except Exception as e:
            print(f"[WARNING]  Failed to connect to MongoDB: {e}")
            return False
    
    # Interactive input if review_id not provided
    if review_id is None:
        review_id = get_user_input_with_validation(
            "Enter review ID to delete: ",
            lambda x: isinstance(x, str) and len(x.strip()) > 0,
            "Review ID must be a non-empty string."
        )
        if review_id is None:
            return False
    
    try:
        result = collection.delete_one({"_id": ObjectId(review_id)})
        if result.deleted_count > 0:
            print(f"[SUCCESS] Review {review_id} deleted successfully.")
            return True
        else:
            print(f"[WARNING]  Review {review_id} not found.")
            return False
    except Exception as e:
        print(f"[WARNING]  Failed to delete review: {e}")
        return False


def get_recent_reviews(
    collection=None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Get the most recent performance reviews across all employees.

    Args:
        collection: MongoDB collection (optional, will get default if not provided)
        limit: Maximum number of reviews to return (default: 5)

    Returns:
        List of recent review documents as dictionaries
    """
    # Get collection if not provided
    if collection is None:
        try:
            collection = get_mongo_collection()
        except Exception as e:
            print(f"[WARNING]  Failed to connect to MongoDB: {e}")
            return []
    
    try:
        # Get recent reviews sorted by review_date descending
        cursor = collection.find({}).sort("review_date", -1).limit(limit)
        
        # Convert ObjectId to string for JSON serialization
        reviews = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
            reviews.append(doc)
        
        print(f"[SUCCESS] Found {len(reviews)} recent reviews")
        return reviews
    except Exception as e:
        print(f"[WARNING]  Failed to retrieve recent reviews: {e}")
        return []


def get_reviews_by_reviewer(
    collection=None,
    reviewer_name: str = None
) -> List[Dict[str, Any]]:
    """
    Get all performance reviews conducted by a specific reviewer.

    Args:
        collection: MongoDB collection (optional, will get default if not provided)
        reviewer_name: Name of the reviewer

    Returns:
        List of review documents as dictionaries
    """
    # Get collection if not provided
    if collection is None:
        try:
            collection = get_mongo_collection()
        except Exception as e:
            print(f"[WARNING]  Failed to connect to MongoDB: {e}")
            return []
    
    # Interactive input if reviewer_name not provided
    if reviewer_name is None:
        reviewer_name = get_user_input_with_validation(
            "Enter reviewer name: ",
            validate_reviewer_name,
            "Reviewer name must be a non-empty string."
        )
        if reviewer_name is None:
            return []
    
    try:
        # Build query for reviewer name (case-insensitive)
        query = {"reviewer_name": {"$regex": reviewer_name.strip(), "$options": "i"}}
        
        # Execute query with sort by date descending
        cursor = collection.find(query).sort("review_date", -1)
        
        # Convert ObjectId to string for JSON serialization
        reviews = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
            reviews.append(doc)
        
        print(f"[SUCCESS] Found {len(reviews)} reviews by reviewer '{reviewer_name}'")
        return reviews
    except Exception as e:
        print(f"[WARNING]  Failed to retrieve reviews by reviewer: {e}")
        return []


def get_reviews_by_date_range(
    collection=None,
    start_date: Union[str, datetime] = None,
    end_date: Union[str, datetime] = None
) -> List[Dict[str, Any]]:
    """
    Get performance reviews within a specific date range.

    Args:
        collection: MongoDB collection (optional, will get default if not provided)
        start_date: Start date in 'YYYY-MM-DD' format or datetime object
        end_date: End date in 'YYYY-MM-DD' format or datetime object

    Returns:
        List of review documents as dictionaries
    """
    # Get collection if not provided
    if collection is None:
        try:
            collection = get_mongo_collection()
        except Exception as e:
            print(f"[WARNING]  Failed to connect to MongoDB: {e}")
            return []
    
    # Interactive input if dates not provided
    if start_date is None:
        start_date = get_user_input_with_validation(
            "Enter start date (YYYY-MM-DD): ",
            lambda x: validate_review_date(x),
            "Start date must be valid and not in the future."
        )
        if start_date is None:
            return []
    
    if end_date is None:
        end_date = get_user_input_with_validation(
            "Enter end date (YYYY-MM-DD): ",
            lambda x: validate_review_date(x),
            "End date must be valid and not in the future."
        )
        if end_date is None:
            return []
    
    # Convert to string format if datetime objects
    if isinstance(start_date, datetime):
        start_date = start_date.strftime("%Y-%m-%d")
    if isinstance(end_date, datetime):
        end_date = end_date.strftime("%Y-%m-%d")
    
    # Validate date range
    if start_date > end_date:
        print("[WARNING]  Start date cannot be after end date.")
        return []
    
    try:
        # Build query for date range
        query = {
            "review_date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        
        # Execute query with sort by date descending
        cursor = collection.find(query).sort("review_date", -1)
        
        # Convert ObjectId to string for JSON serialization
        reviews = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
            reviews.append(doc)
        
        print(f"[SUCCESS] Found {len(reviews)} reviews between {start_date} and {end_date}")
        return reviews
    except Exception as e:
        print(f"[WARNING]  Failed to retrieve reviews by date range: {e}")
        return []


# -------------------------
# Aggregation Functions
# -------------------------
def aggregate_strengths(
    collection=None,
    employee_id: int = None
) -> Dict[str, int]:
    """
    Aggregate strengths mentioned in reviews for an employee (frequency map).

    Args:
        collection: MongoDB collection (optional, will get default if not provided)
        employee_id: ID of the employee

    Returns:
        Dictionary with strengths as keys and frequency as values
    """
    # Get collection if not provided
    if collection is None:
        try:
            collection = get_mongo_collection()
        except Exception as e:
            print(f"[WARNING]  Failed to connect to MongoDB: {e}")
            return {}
    
    # Interactive input if employee_id not provided
    if employee_id is None:
        employee_id = get_user_input_with_validation(
            "Enter employee ID: ",
            lambda x: isinstance(int(x), int) and int(x) > 0,
            "Employee ID must be a positive integer."
        )
        if employee_id is None:
            return {}
        employee_id = int(employee_id)
    
    try:
        # Get all reviews for the employee
        reviews = collection.find({"employee_id": employee_id})
        
        strengths_counter = Counter()
        
        for review in reviews:
            if "strengths" in review and review["strengths"]:
                strengths_text = review["strengths"]
                
                # Split by common delimiters and count individual strengths
                # Handle both string and list formats
                if isinstance(strengths_text, str):
                    # Split by common delimiters
                    strengths_list = re.split(r'[,;.\n]', strengths_text)
                    for strength in strengths_list:
                        strength = strength.strip().lower()
                        if strength and len(strength) > 2:  # Filter out very short strings
                            strengths_counter[strength] += 1
                elif isinstance(strengths_text, list):
                    for strength in strengths_text:
                        if isinstance(strength, str):
                            strength = strength.strip().lower()
                            if strength and len(strength) > 2:
                                strengths_counter[strength] += 1
        
        result = dict(strengths_counter.most_common())
        print(f"[SUCCESS] Found {len(result)} unique strengths for employee {employee_id}")
        return result
    except Exception as e:
        print(f"[WARNING]  Failed to aggregate strengths: {e}")
        return {}


def aggregate_areas_for_improvement(
    collection=None,
    employee_id: int = None
) -> Dict[str, int]:
    """
    Aggregate areas for improvement mentioned in reviews for an employee (frequency map).

    Args:
        collection: MongoDB collection (optional, will get default if not provided)
        employee_id: ID of the employee

    Returns:
        Dictionary with improvement areas as keys and frequency as values
    """
    # Get collection if not provided
    if collection is None:
        try:
            collection = get_mongo_collection()
        except Exception as e:
            print(f"[WARNING]  Failed to connect to MongoDB: {e}")
            return {}
    
    # Interactive input if employee_id not provided
    if employee_id is None:
        employee_id = get_user_input_with_validation(
            "Enter employee ID: ",
            lambda x: isinstance(int(x), int) and int(x) > 0,
            "Employee ID must be a positive integer."
        )
        if employee_id is None:
            return {}
        employee_id = int(employee_id)
    
    try:
        # Get all reviews for the employee
        reviews = collection.find({"employee_id": employee_id})
        
        areas_counter = Counter()
        
        for review in reviews:
            if "areas_for_improvement" in review and review["areas_for_improvement"]:
                areas_text = review["areas_for_improvement"]
                
                # Split by common delimiters and count individual areas
                if isinstance(areas_text, str):
                    # Split by common delimiters
                    areas_list = re.split(r'[,;.\n]', areas_text)
                    for area in areas_list:
                        area = area.strip().lower()
                        if area and len(area) > 2:  # Filter out very short strings
                            areas_counter[area] += 1
                elif isinstance(areas_text, list):
                    for area in areas_text:
                        if isinstance(area, str):
                            area = area.strip().lower()
                            if area and len(area) > 2:
                                areas_counter[area] += 1
        
        result = dict(areas_counter.most_common())
        print(f"[SUCCESS] Found {len(result)} unique improvement areas for employee {employee_id}")
        return result
    except Exception as e:
        print(f"[WARNING]  Failed to aggregate improvement areas: {e}")
        return {}


def get_top_goals(
    collection=None,
    employee_id: int = None,
    limit: int = 5
) -> List[str]:
    """
    Get the most frequently mentioned goals for an employee.

    Args:
        collection: MongoDB collection (optional, will get default if not provided)
        employee_id: ID of the employee
        limit: Maximum number of goals to return (default: 5)

    Returns:
        List of most frequent goals
    """
    # Get collection if not provided
    if collection is None:
        try:
            collection = get_mongo_collection()
        except Exception as e:
            print(f"[WARNING]  Failed to connect to MongoDB: {e}")
            return []
    
    # Interactive input if employee_id not provided
    if employee_id is None:
        employee_id = get_user_input_with_validation(
            "Enter employee ID: ",
            lambda x: isinstance(int(x), int) and int(x) > 0,
            "Employee ID must be a positive integer."
        )
        if employee_id is None:
            return []
        employee_id = int(employee_id)
    
    try:
        # Get all reviews for the employee
        reviews = collection.find({"employee_id": employee_id})
        
        goals_counter = Counter()
        
        for review in reviews:
            if "goals_for_next_period" in review and review["goals_for_next_period"]:
                goals_text = review["goals_for_next_period"]
                
                # Split by common delimiters and count individual goals
                if isinstance(goals_text, str):
                    # Split by common delimiters
                    goals_list = re.split(r'[,;.\n]', goals_text)
                    for goal in goals_list:
                        goal = goal.strip().lower()
                        if goal and len(goal) > 2:  # Filter out very short strings
                            goals_counter[goal] += 1
                elif isinstance(goals_text, list):
                    for goal in goals_text:
                        if isinstance(goal, str):
                            goal = goal.strip().lower()
                            if goal and len(goal) > 2:
                                goals_counter[goal] += 1
        
        # Get top goals
        top_goals = [goal for goal, count in goals_counter.most_common(limit)]
        print(f"[SUCCESS] Found {len(top_goals)} top goals for employee {employee_id}")
        return top_goals
    except Exception as e:
        print(f"[WARNING]  Failed to get top goals: {e}")
        return []


# -------------------------
# Legacy Functions (for backward compatibility)
# -------------------------
def calculate_average_rating(employee_id: int) -> Optional[float]:
    """
    Legacy function for backward compatibility.
    Use get_average_rating_for_employee() instead.
    """
    return get_average_rating_for_employee(employee_id=employee_id)


def delete_performance_review(review_id: str) -> bool:
    """
    Legacy function for backward compatibility.
    Use delete_performance_review() with collection parameter instead.
    """
    return delete_performance_review(review_id=review_id)


# -------------------------
# Helper Functions
# -------------------------
def display_review_form():
    """Display a comprehensive review form for user input."""
    print("\n" + "="*50)
    print("PERFORMANCE REVIEW FORM")
    print("="*50)
    print("Please fill in all required fields (*) and optional fields as needed.")
    print("Press Enter to skip optional fields.")
    print("-"*50)


def get_comprehensive_review_input():
    """Get comprehensive review input from user with all standard fields."""
    display_review_form()
    
    # Required fields
    employee_id = get_user_input_with_validation(
        "Employee ID (*): ",
        lambda x: isinstance(int(x), int) and int(x) > 0,
        "Employee ID must be a positive integer."
    )
    if employee_id is None:
        return None
    employee_id = int(employee_id)
    
    reviewer_name = get_user_input_with_validation(
        "Reviewer Name (*): ",
        validate_reviewer_name,
        "Reviewer name must be a non-empty string."
    )
    if reviewer_name is None:
        return None
    
    overall_rating = get_user_input_with_validation(
        "Overall Rating (1.0-5.0) (*): ",
        lambda x: validate_overall_rating(float(x)),
        "Overall rating must be a number between 1.0 and 5.0."
    )
    if overall_rating is None:
        return None
    overall_rating = float(overall_rating)
    
    review_date = get_user_input_with_validation(
        "Review Date (YYYY-MM-DD) or Enter for today (*): ",
        lambda x: x.strip() == "" or validate_review_date(x),
        "Review date must be valid and not in the future."
    )
    if review_date is None:
        return None
    if review_date.strip() == "":
        review_date = datetime.now().strftime("%Y-%m-%d")
    
    # Optional fields
    print("\nOptional Fields (press Enter to skip):")
    strengths = get_optional_text_input("Strengths: ")
    areas_for_improvement = get_optional_text_input("Areas for Improvement: ")
    comments = get_optional_text_input("Comments: ")
    goals_for_next_period = get_optional_text_input("Goals for Next Period: ")
    
    return {
        'employee_id': employee_id,
        'reviewer_name': reviewer_name,
        'overall_rating': overall_rating,
        'review_date': review_date,
        'strengths': strengths,
        'areas_for_improvement': areas_for_improvement,
        'comments': comments,
        'goals_for_next_period': goals_for_next_period
    }


# If you want to quickly sanity-check this module directly:
if __name__ == "__main__":
    print("performance_reviewer self-test (adjust as needed)...")
    try:
        # Test comprehensive review input
        print("\nTesting comprehensive review input...")
        review_data = get_comprehensive_review_input()
        if review_data:
            review_id = submit_performance_review(**review_data)
        print(f"Added review with id={review_id}")
        
        # Test retrieval
        reviews = get_performance_reviews_for_employee(employee_id=1)
        print(f"Found {len(reviews)} reviews for employee 1")
        
        # Test average calculation
        avg_rating = get_average_rating_for_employee(employee_id=1)
        print(f"Average rating for employee 1: {avg_rating}")
        
        # Test aggregation functions
        strengths = aggregate_strengths(employee_id=1)
        print(f"Strengths for employee 1: {strengths}")
        
        areas = aggregate_areas_for_improvement(employee_id=1)
        print(f"Improvement areas for employee 1: {areas}")
        
        goals = get_top_goals(employee_id=1)
        print(f"Top goals for employee 1: {goals}")
        
        # Test recent reviews
        recent = get_recent_reviews(limit=3)
        print(f"Recent reviews: {len(recent)}")
        
    except Exception as e:
        print("performance_reviewer error:", e)
