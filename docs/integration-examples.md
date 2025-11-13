# Integration Examples

This guide demonstrates how to integrate toon_format with popular Python libraries and frameworks. The library is designed to work seamlessly with your existing tools without forcing additional dependencies.

## Table of Contents

- [Working with Pydantic](#working-with-pydantic)
- [Working with NumPy](#working-with-numpy)
- [Working with Pandas](#working-with-pandas)
- [Working with Dataclasses](#working-with-dataclasses)
- [Working with FastAPI](#working-with-fastapi)
- [Working with Django](#working-with-django)
- [LLM Integration Patterns](#llm-integration-patterns)
- [Data Science Workflows](#data-science-workflows)

---

## Working with Pydantic

Pydantic models can be encoded by converting them to dictionaries first. This approach keeps Pydantic as an optional dependency.

### Basic Pydantic Model

```python
from pydantic import BaseModel
from toon_format import encode, decode

class User(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool = True

# Create a user instance
user = User(
    id=1,
    username="alice",
    email="alice@example.com"
)

# Encode to TOON format
toon_str = encode(user.model_dump())
print(toon_str)
# Output:
# id: 1
# username: alice
# email: alice@example.com
# is_active: true

# Decode back and reconstruct
data = decode(toon_str)
user_restored = User(**data)
```

### Nested Pydantic Models

```python
from pydantic import BaseModel
from typing import List
from toon_format import encode

class Address(BaseModel):
    street: str
    city: str
    country: str

class Company(BaseModel):
    name: str
    employees: int
    address: Address

company = Company(
    name="ACME Corp",
    employees=150,
    address=Address(
        street="123 Main St",
        city="Springfield",
        country="USA"
    )
)

toon_str = encode(company.model_dump())
print(toon_str)
# Output:
# name: ACME Corp
# employees: 150
# address:
#   street: 123 Main St
#   city: Springfield
#   country: USA
```

### List of Pydantic Models

```python
from pydantic import BaseModel
from typing import List
from toon_format import encode

class Product(BaseModel):
    sku: str
    name: str
    price: float
    in_stock: bool

products = [
    Product(sku="A001", name="Widget", price=9.99, in_stock=True),
    Product(sku="A002", name="Gadget", price=19.99, in_stock=False),
    Product(sku="A003", name="Doohickey", price=14.50, in_stock=True)
]

# Convert list of models to list of dicts
products_data = [p.model_dump() for p in products]
toon_str = encode(products_data)
print(toon_str)
# Output:
# [3,]{sku,name,price,in_stock}:
#   A001,Widget,9.99,true
#   A002,Gadget,19.99,false
#   A003,Doohickey,14.50,true
```

---

## Working with NumPy

NumPy arrays are automatically normalized to Python lists during encoding. NumPy remains an optional dependency.

### Basic NumPy Arrays

```python
import numpy as np
from toon_format import encode

# 1D array
vector = np.array([1.5, 2.7, 3.9, 4.2])
toon_str = encode({"vector": vector})
print(toon_str)
# Output:
# vector[4]: 1.5,2.7,3.9,4.2

# 2D array (matrix)
matrix = np.array([[1, 2, 3], [4, 5, 6]])
toon_str = encode({"matrix": matrix})
print(toon_str)
# Output:
# matrix[2]:
#   - [3]: 1,2,3
#   - [3]: 4,5,6
```

### NumPy Data Types

```python
import numpy as np
from toon_format import encode

data = {
    "int32_value": np.int32(42),
    "float64_value": np.float64(3.14159),
    "bool_value": np.bool_(True),
    "array_int": np.array([1, 2, 3], dtype=np.int64),
    "array_float": np.array([1.1, 2.2, 3.3], dtype=np.float32)
}

toon_str = encode(data)
print(toon_str)
# Output:
# int32_value: 42
# float64_value: 3.14159
# bool_value: true
# array_int[3]: 1,2,3
# array_float[3]: 1.1,2.2,3.3
```

---

## Working with Pandas

Pandas DataFrames can be converted to TOON format using the to_dict method. This is particularly useful for tabular data.

### DataFrame to Tabular Format

```python
import pandas as pd
from toon_format import encode

# Create a DataFrame
df = pd.DataFrame({
    'employee_id': [101, 102, 103],
    'name': ['Alice Johnson', 'Bob Smith', 'Carol White'],
    'department': ['Engineering', 'Sales', 'Marketing'],
    'salary': [95000, 75000, 82000]
})

# Convert to list of records for tabular format
toon_str = encode(df.to_dict('records'))
print(toon_str)
# Output:
# [3,]{employee_id,name,department,salary}:
#   101,Alice Johnson,Engineering,95000
#   102,Bob Smith,Sales,75000
#   103,Carol White,Marketing,82000
```

### DataFrame with Missing Values

```python
import pandas as pd
from toon_format import encode

df = pd.DataFrame({
    'id': [1, 2, 3],
    'value': [10.5, None, 15.3],
    'status': ['active', 'pending', None]
})

# fillna to handle missing values
df_filled = df.fillna({'value': 0, 'status': 'unknown'})
toon_str = encode(df_filled.to_dict('records'))
print(toon_str)
# Output:
# [3,]{id,value,status}:
#   1,10.5,active
#   2,0,pending
#   3,15.3,unknown
```

### Time Series Data

```python
import pandas as pd
from toon_format import encode

# Create time series data
dates = pd.date_range('2025-01-01', periods=5, freq='D')
df = pd.DataFrame({
    'date': dates.strftime('%Y-%m-%d').tolist(),
    'temperature': [22.5, 23.1, 21.8, 24.2, 23.7],
    'humidity': [65, 68, 70, 62, 66]
})

toon_str = encode(df.to_dict('records'))
print(toon_str)
# Output:
# [5,]{date,temperature,humidity}:
#   2025-01-01,22.5,65
#   2025-01-02,23.1,68
#   2025-01-03,21.8,70
#   2025-01-04,24.2,62
#   2025-01-05,23.7,66
```

---

## Working with Dataclasses

Python dataclasses work seamlessly with toon_format using the asdict function from the dataclasses module.

### Basic Dataclass

```python
from dataclasses import dataclass, asdict
from toon_format import encode, decode

@dataclass
class Book:
    isbn: str
    title: str
    author: str
    year: int
    available: bool

book = Book(
    isbn="978-0-123456-78-9",
    title="Introduction to Python",
    author="Jane Doe",
    year=2024,
    available=True
)

# Encode to TOON
toon_str = encode(asdict(book))
print(toon_str)
# Output:
# isbn: 978-0-123456-78-9
# title: Introduction to Python
# author: Jane Doe
# year: 2024
# available: true

# Decode and reconstruct
data = decode(toon_str)
book_restored = Book(**data)
```

### Nested Dataclasses

```python
from dataclasses import dataclass, asdict
from typing import List
from toon_format import encode

@dataclass
class Author:
    name: str
    email: str

@dataclass
class Book:
    title: str
    authors: List[Author]
    pages: int

book = Book(
    title="Advanced Python Programming",
    authors=[
        Author(name="Alice Smith", email="alice@example.com"),
        Author(name="Bob Jones", email="bob@example.com")
    ],
    pages=450
)

toon_str = encode(asdict(book))
print(toon_str)
# Output:
# title: Advanced Python Programming
# authors[2,]{name,email}:
#   Alice Smith,alice@example.com
#   Bob Jones,bob@example.com
# pages: 450
```

### List of Dataclasses

```python
from dataclasses import dataclass, asdict
from toon_format import encode

@dataclass
class Transaction:
    id: int
    amount: float
    currency: str
    completed: bool

transactions = [
    Transaction(id=1001, amount=250.50, currency="USD", completed=True),
    Transaction(id=1002, amount=175.00, currency="EUR", completed=False),
    Transaction(id=1003, amount=320.75, currency="GBP", completed=True)
]

# Convert list of dataclasses to list of dicts
transactions_data = [asdict(t) for t in transactions]
toon_str = encode(transactions_data)
print(toon_str)
# Output:
# [3,]{id,amount,currency,completed}:
#   1001,250.50,USD,true
#   1002,175.00,EUR,false
#   1003,320.75,GBP,true
```

---

## Working with FastAPI

FastAPI uses Pydantic models extensively. Here is how to integrate toon_format in a FastAPI application.

### Basic FastAPI Endpoint

```python
from fastapi import FastAPI
from pydantic import BaseModel
from toon_format import encode, decode
from typing import List

app = FastAPI()

class Item(BaseModel):
    id: int
    name: str
    price: float
    in_stock: bool

@app.post("/items/toon")
async def create_item_toon(item: Item):
    """Accept JSON, return TOON format"""
    toon_str = encode(item.model_dump())
    return {"format": "toon", "data": toon_str}

@app.get("/items/toon")
async def list_items_toon():
    """Return multiple items in TOON format"""
    items = [
        Item(id=1, name="Widget", price=9.99, in_stock=True),
        Item(id=2, name="Gadget", price=19.99, in_stock=False)
    ]
    items_data = [item.model_dump() for item in items]
    toon_str = encode(items_data)
    return {"format": "toon", "data": toon_str}
```

### LLM Integration with FastAPI

```python
from fastapi import FastAPI
from pydantic import BaseModel
from toon_format import encode, estimate_savings
from typing import List

app = FastAPI()

class ContextData(BaseModel):
    user_id: int
    preferences: dict
    history: List[dict]

@app.post("/llm/prepare-context")
async def prepare_llm_context(data: ContextData):
    """Prepare data for LLM with token optimization"""
    data_dict = data.model_dump()

    # Encode to TOON format
    toon_str = encode(data_dict)

    # Calculate token savings
    savings = estimate_savings(data_dict)

    return {
        "toon_format": toon_str,
        "token_count": savings["toon_tokens"],
        "savings_percent": savings["savings_percent"],
        "ready_for_llm": True
    }
```

---

## Working with Django

Django models can be serialized to TOON format using model_to_dict or by converting querysets.

### Django Model Serialization

```python
from django.core.serializers import serialize
from django.forms.models import model_to_dict
from toon_format import encode

# Assuming you have a Django model
from myapp.models import Product

# Single object
product = Product.objects.get(id=1)
product_dict = model_to_dict(product)
toon_str = encode(product_dict)

# Multiple objects
products = Product.objects.filter(category="electronics")
products_data = [model_to_dict(p) for p in products]
toon_str = encode(products_data)
```

### Django REST Framework Integration

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from toon_format import encode
from myapp.models import Product
from myapp.serializers import ProductSerializer

class ProductToonView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        toon_str = encode(serializer.data)
        return Response({
            "format": "toon",
            "data": toon_str
        })
```

---

## LLM Integration Patterns

These patterns demonstrate how to use toon_format effectively with Large Language Models.

### Pattern 1: Context Preparation

```python
from toon_format import encode, count_tokens

def prepare_llm_context(user_data, conversation_history, max_tokens=4000):
    """Prepare context for LLM with token budget management"""

    # Encode user data
    user_context = encode(user_data)
    user_tokens = count_tokens(user_context)

    # Encode conversation history
    history_context = encode(conversation_history)
    history_tokens = count_tokens(history_context)

    total_tokens = user_tokens + history_tokens

    if total_tokens > max_tokens:
        # Truncate history if needed
        truncated_history = conversation_history[-(max_tokens - user_tokens):]
        history_context = encode(truncated_history)

    # Combine contexts
    full_context = f"""User Profile:
{user_context}

Conversation History:
{history_context}"""

    return full_context, count_tokens(full_context)
```

### Pattern 2: Structured Data Extraction

```python
from toon_format import decode

def extract_structured_data(llm_response):
    """Parse LLM response in TOON format back to Python objects"""

    # Assume LLM returns TOON format
    toon_response = """users[3,]{name,age,role}:
  Alice,30,Engineer
  Bob,25,Designer
  Carol,35,Manager"""

    # Decode to Python
    data = decode(toon_response)

    # Process the structured data
    for user in data["users"]:
        print(f"{user['name']} is a {user['role']}")

    return data
```

### Pattern 3: Batch Processing

```python
from toon_format import encode, estimate_savings
from typing import List, Dict

def batch_encode_for_llm(items: List[Dict], batch_size: int = 100):
    """Encode large datasets in batches for LLM processing"""

    batches = []
    total_savings = 0

    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        toon_str = encode(batch)

        # Track savings
        savings = estimate_savings(batch)
        total_savings += savings["savings"]

        batches.append({
            "batch_number": i // batch_size + 1,
            "toon_data": toon_str,
            "token_count": savings["toon_tokens"]
        })

    return batches, total_savings
```

---

## Data Science Workflows

Common patterns for data science and machine learning workflows.

### Pattern 1: Model Results Serialization

```python
import numpy as np
from toon_format import encode

def serialize_model_results(predictions, probabilities, metadata):
    """Serialize ML model results for storage or transmission"""

    results = {
        "model_version": metadata["version"],
        "timestamp": metadata["timestamp"],
        "predictions": predictions.tolist(),
        "probabilities": probabilities.tolist(),
        "accuracy": float(metadata["accuracy"])
    }

    return encode(results)

# Example usage
predictions = np.array([0, 1, 1, 0, 1])
probabilities = np.array([0.23, 0.87, 0.92, 0.15, 0.78])
metadata = {
    "version": "1.2.0",
    "timestamp": "2025-01-09T12:00:00Z",
    "accuracy": 0.94
}

toon_str = serialize_model_results(predictions, probabilities, metadata)
```

### Pattern 2: Experiment Tracking

```python
from dataclasses import dataclass, asdict
from datetime import datetime
from toon_format import encode

@dataclass
class Experiment:
    experiment_id: str
    model_name: str
    hyperparameters: dict
    metrics: dict
    timestamp: str

def log_experiment(model_name, hyperparameters, metrics):
    """Log ML experiment in TOON format"""

    experiment = Experiment(
        experiment_id=f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        model_name=model_name,
        hyperparameters=hyperparameters,
        metrics=metrics,
        timestamp=datetime.now().isoformat()
    )

    toon_str = encode(asdict(experiment))

    # Save to file or database
    with open(f"{experiment.experiment_id}.toon", "w") as f:
        f.write(toon_str)

    return experiment.experiment_id

# Example usage
experiment_id = log_experiment(
    model_name="RandomForest",
    hyperparameters={"n_estimators": 100, "max_depth": 10},
    metrics={"accuracy": 0.95, "f1_score": 0.93, "precision": 0.94}
)
```

### Pattern 3: Dataset Metadata

```python
import pandas as pd
from toon_format import encode

def create_dataset_metadata(df: pd.DataFrame, description: str):
    """Create metadata for a dataset in TOON format"""

    metadata = {
        "description": description,
        "rows": len(df),
        "columns": len(df.columns),
        "column_info": [
            {
                "name": col,
                "dtype": str(df[col].dtype),
                "null_count": int(df[col].isnull().sum()),
                "unique_values": int(df[col].nunique())
            }
            for col in df.columns
        ],
        "memory_usage_mb": float(df.memory_usage(deep=True).sum() / 1024 / 1024)
    }

    return encode(metadata)

# Example usage
df = pd.DataFrame({
    'id': range(1000),
    'value': np.random.randn(1000),
    'category': np.random.choice(['A', 'B', 'C'], 1000)
})

metadata_toon = create_dataset_metadata(df, "Sample dataset for analysis")
print(metadata_toon)
```

---

## Best Practices

### 1. Always Convert Before Encoding

When working with third-party objects, always convert to standard Python types first:

```python
# Good
pydantic_obj = MyModel(...)
toon_str = encode(pydantic_obj.model_dump())

# Good
dataclass_obj = MyDataclass(...)
toon_str = encode(asdict(dataclass_obj))

# Good
numpy_array = np.array([...])
toon_str = encode({"data": numpy_array.tolist()})
```

### 2. Handle Missing Values Explicitly

```python
import pandas as pd
from toon_format import encode

df = pd.DataFrame({"a": [1, None, 3]})

# Replace None/NaN with appropriate values
df_clean = df.fillna(0)  # or df.dropna()
toon_str = encode(df_clean.to_dict('records'))
```

### 3. Use Token Counting for LLM Budgets

```python
from toon_format import encode, count_tokens

data = {"large": "dataset"}
toon_str = encode(data)
tokens = count_tokens(toon_str)

if tokens > 4000:
    # Reduce data size or split into chunks
    pass
```

### 4. Validate Data After Decoding

```python
from toon_format import decode
from pydantic import BaseModel, ValidationError

class User(BaseModel):
    id: int
    name: str

toon_str = "id: 1\nname: Alice"
data = decode(toon_str)

try:
    user = User(**data)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

---

## Summary

The toon_format library integrates seamlessly with popular Python libraries without requiring them as dependencies. This design allows you to:

- Use Pydantic models by converting with model_dump()
- Work with NumPy arrays through automatic normalization
- Process Pandas DataFrames using to_dict()
- Serialize dataclasses with asdict()
- Integrate with FastAPI and Django applications
- Optimize LLM context with built-in token counting

The key principle is flexibility: bring your own tools, and toon_format will work with them.


