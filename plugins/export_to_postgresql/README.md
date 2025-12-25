# Export to PostgreSQL Plugin

Export JSON data directly to PostgreSQL database tables.

## Features

- 🔌 **Easy Connection**: Configure PostgreSQL connection via UI dialog
- 🏗️ **Auto-create Tables**: Automatically creates tables if they don't exist
- 📦 **Batch Insert**: Supports both single objects and arrays
- 🔄 **JSONB Storage**: Uses PostgreSQL JSONB for flexible schema
- ⚡ **Transaction Support**: Rollback on error for data integrity

## Installation

1. Install PostgreSQL dependency:
```bash
pip install psycopg2-binary
```

2. Enable the plugin in Clarify settings

## Usage

1. **File → Export to PostgreSQL...**
2. Configure database connection:
   - Host: `localhost`
   - Port: `5432`
   - Database: `clarify_export`
   - User: `postgres`
   - Password: `your_password`
3. Select JSON file to export
4. Click **Export to PostgreSQL**

## Database Schema

The plugin creates a simple table:

```sql
CREATE TABLE json_data (
    id SERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Example

Given JSON file `users.json`:
```json
[
  {"name": "Alice", "age": 30},
  {"name": "Bob", "age": 25}
]
```

After export, query PostgreSQL:
```sql
SELECT data->>'name' AS name, 
       data->>'age' AS age 
FROM json_data;
```

## Requirements

- PostgreSQL 9.4+ (JSONB support)
- psycopg2-binary Python package
