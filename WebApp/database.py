# WebApp/database.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import logging

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)

def safe_query(query, params=None):
    """
    Execute a safe SQL query with parameters to prevent SQL injection.
    
    Args:
        query (str): The SQL query with named parameters
        params (dict): Dictionary of parameters to bind to the query
        
    Returns:
        ResultProxy: The result of the query execution
        
    Example:
        result = safe_query(
            "SELECT * FROM users WHERE username = :username",
            {"username": username}
        )
    """
    if params is None:
        params = {}
    
    try:
        # Convert the query string to a SQLAlchemy text object
        sql_query = text(query)
        # Execute the query with parameters
        result = db.session.execute(sql_query, params)
        return result
    except Exception as e:
        logging.error(f"Error executing safe query: {str(e)}")
        raise

def safe_scalar(query, params=None):
    """
    Execute a safe SQL query and return a single scalar value.
    
    Args:
        query (str): The SQL query with named parameters
        params (dict): Dictionary of parameters to bind to the query
        
    Returns:
        Any: The scalar result of the query
        
    Example:
        count = safe_scalar(
            "SELECT COUNT(*) FROM users WHERE status = :status",
            {"status": "active"}
        )
    """
    result = safe_query(query, params)
    return result.scalar()

def safe_first(query, params=None):
    """
    Execute a safe SQL query and return the first row.
    
    Args:
        query (str): The SQL query with named parameters
        params (dict): Dictionary of parameters to bind to the query
        
    Returns:
        Row: The first row of the result
        
    Example:
        user = safe_first(
            "SELECT * FROM users WHERE id = :id",
            {"id": user_id}
        )
    """
    result = safe_query(query, params)
    return result.first()

def safe_all(query, params=None):
    """
    Execute a safe SQL query and return all rows.
    
    Args:
        query (str): The SQL query with named parameters
        params (dict): Dictionary of parameters to bind to the query
        
    Returns:
        List[Row]: All rows of the result
        
    Example:
        users = safe_all(
            "SELECT * FROM users WHERE status = :status",
            {"status": "active"}
        )
    """
    result = safe_query(query, params)
    return result.all()