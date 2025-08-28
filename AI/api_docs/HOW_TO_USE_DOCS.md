# How to Explore Intervals.icu API Documentation with jq

## Typical Exploration Workflow

Follow these steps to efficiently explore the intervals.icu API documentation:

1. **Start with overview commands** to understand the API structure
   ```bash
   jq 'keys' AI/api_docs/intervals.json
   jq '.info' AI/api_docs/intervals.json
   ```

2. **Explore main categories** to identify areas of interest
   ```bash
   jq '.paths | keys | group_by(split("/")[3]) | map({category: .[0] | split("/")[3], count: length}) | sort_by(.count) | reverse' AI/api_docs/intervals.json
   ```

3. **Find specific endpoints** for your use case
   ```bash
   # Find athlete-related endpoints
   jq '.paths | keys | map(select(contains("/athlete"))) | .[0:20]' AI/api_docs/intervals.json
   ```

4. **Examine endpoint details** including methods and parameters
   ```bash
   jq '.paths["/api/v1/athlete/{id}/activities"].get.parameters | map({name, in, required, description})' AI/api_docs/intervals.json
   ```

5. **Explore data schemas** to understand response structures
   ```bash
   jq '.components.schemas.Activity.properties | keys | .[0:30]' AI/api_docs/intervals.json
   ```

6. **Check authentication requirements** for API access
   ```bash
   jq '.components.securitySchemes' AI/api_docs/intervals.json
   ```

## Complete Command Reference

### Discovery Commands

```bash
# Get API overview information
jq '.info' AI/api_docs/intervals.json

# List all endpoint paths (paginated)
jq '.paths | keys | .[0:20]' AI/api_docs/intervals.json

# Count total endpoints
jq '.paths | keys | length' AI/api_docs/intervals.json

# List all schema definitions (paginated)
jq '.components.schemas | keys | .[0:20]' AI/api_docs/intervals.json

# Count total schemas
jq '.components.schemas | keys | length' AI/api_docs/intervals.json

# Group endpoints by main category with counts
jq '.paths | keys | group_by(split("/")[3]) | map({category: .[0] | split("/")[3], count: length}) | sort_by(.count) | reverse' AI/api_docs/intervals.json

# Find endpoints containing keyword (replace KEYWORD)
jq '.paths | keys | map(select(contains("KEYWORD"))) | .[0:20]' AI/api_docs/intervals.json

# Find schemas containing keyword (replace KEYWORD)
jq '.components.schemas | keys | map(select(contains("KEYWORD")))' AI/api_docs/intervals.json

# Get server configuration
jq '.servers' AI/api_docs/intervals.json

# Get global security requirements
jq '.security' AI/api_docs/intervals.json
```

### Detailed Analysis Commands

```bash
# Get all methods for a specific endpoint (replace PATH)
jq '.paths["/api/v1/athlete/{id}/activities"] | keys' AI/api_docs/intervals.json

# Get parameters for specific endpoint method
jq '.paths["/api/v1/athlete/{id}/activities"].get.parameters | map({name, in, required, type: .schema.type, description})' AI/api_docs/intervals.json

# Get response schema for endpoint
jq '.paths["/api/v1/athlete/{id}/activities"].get.responses."200".content."application/json".schema' AI/api_docs/intervals.json

# Get request body schema for POST/PUT endpoints
jq '.paths["/api/v1/athlete/{id}/wellness"].post.requestBody.content["application/json"].schema' AI/api_docs/intervals.json

# Get properties of a specific schema (replace SCHEMA_NAME)
jq '.components.schemas.Activity.properties | keys' AI/api_docs/intervals.json

# Get detailed property info for a schema
jq '.components.schemas.Wellness.properties | to_entries | map({property: .key, type: .value.type, format: .value.format, description: .value.description}) | .[0:10]' AI/api_docs/intervals.json

# Find endpoints with specific HTTP method
jq '.paths | to_entries | map(select(.value.get)) | map(.key) | .[0:20]' AI/api_docs/intervals.json

# Find endpoints with POST method
jq '.paths | to_entries | map(select(.value.post)) | map(.key) | .[0:20]' AI/api_docs/intervals.json

# Get endpoints with their parameter names
jq '[.paths | to_entries[] | select(.value.get.parameters) | {endpoint: .key, params: .value.get.parameters | map(.name)}] | .[0:10]' AI/api_docs/intervals.json

# Get authentication schemes details
jq '.components.securitySchemes' AI/api_docs/intervals.json
```

### Quality and Maintenance Commands

```bash
# Find endpoints with path parameters
jq '.paths | keys | map(select(test("{.*}"))) | .[0:20]' AI/api_docs/intervals.json

# Count endpoints with path parameters
jq '.paths | keys | map(select(test("{.*}"))) | length' AI/api_docs/intervals.json

# Find endpoints that require authentication
jq '.paths | to_entries | map(select(.value.get.security or .value.post.security)) | map(.key) | .[0:10]' AI/api_docs/intervals.json

# Get schemas with enum values
jq '.components.schemas | to_entries | map(select(.value.properties | to_entries | any(.value.enum))) | map(.key)' AI/api_docs/intervals.json

# Find schemas that reference other schemas
jq '.components.schemas | to_entries | map(select(.value.properties | to_entries | any(.value["$ref"]))) | map(.key) | .[0:10]' AI/api_docs/intervals.json
```

## Common Use Case Examples

### 1. Exploring Activity Endpoints
```bash
# Find all activity-related endpoints
jq '.paths | keys | map(select(contains("/activity"))) | .[0:20]' AI/api_docs/intervals.json

# Get parameters for fetching activities
jq '.paths["/api/v1/athlete/{id}/activities"].get.parameters | map({name, required, description})' AI/api_docs/intervals.json

# Explore Activity schema structure
jq '.components.schemas.Activity.properties | keys | .[0:30]' AI/api_docs/intervals.json

# Get specific activity property details
jq '.components.schemas.Activity.properties | with_entries(select(.key | contains("power"))) | keys' AI/api_docs/intervals.json
```

### 2. Working with Wellness Data
```bash
# Find wellness endpoints
jq '.paths | keys | map(select(contains("/wellness")))' AI/api_docs/intervals.json

# Get wellness schema properties
jq '.components.schemas.Wellness.properties | keys' AI/api_docs/intervals.json

# Get wellness property types
jq '.components.schemas.Wellness.properties | to_entries | map({property: .key, type: .value.type}) | .[0:15]' AI/api_docs/intervals.json

# Check wellness POST endpoint requirements
jq '.paths["/api/v1/athlete/{id}/wellness"].post' AI/api_docs/intervals.json
```

### 3. Understanding Events and Workouts
```bash
# Find event-related endpoints
jq '.paths | keys | map(select(contains("/event")))' AI/api_docs/intervals.json

# Find workout endpoints
jq '.paths | keys | map(select(contains("/workout"))) | .[0:10]' AI/api_docs/intervals.json

# Get Event schema structure
jq '.components.schemas.Event.properties | keys | .[0:20]' AI/api_docs/intervals.json

# Get Workout schema details
jq '.components.schemas.Workout.properties | keys | .[0:20]' AI/api_docs/intervals.json
```

### 4. Exploring Athlete Settings and Profiles
```bash
# Find athlete configuration endpoints
jq '.paths | keys | map(select(contains("/athlete") and contains("settings")))' AI/api_docs/intervals.json

# Get athlete schema properties
jq '.components.schemas.Athlete.properties | keys | .[0:20]' AI/api_docs/intervals.json

# Find sport settings endpoints
jq '.paths | keys | map(select(contains("sport-settings")))' AI/api_docs/intervals.json
```

### 5. Working with Power and Heart Rate Data
```bash
# Find power curve endpoints
jq '.paths | keys | map(select(contains("power-curve")))' AI/api_docs/intervals.json

# Find heart rate endpoints
jq '.paths | keys | map(select(contains("/hr-")))' AI/api_docs/intervals.json

# Get PowerCurve schema
jq '.components.schemas | keys | map(select(contains("PowerCurve")))' AI/api_docs/intervals.json

# Explore HR-related properties in Activity
jq '.components.schemas.Activity.properties | with_entries(select(.key | contains("hr") or contains("heartrate"))) | keys' AI/api_docs/intervals.json
```

## Tips for Efficient Exploration

1. **Use pagination with array slicing** - Most listing commands use `.[0:20]` to limit output. Adjust the range as needed.

2. **Chain filters for precise results** - Combine `select()` filters to narrow down results:
   ```bash
   jq '.paths | keys | map(select(contains("/athlete") and contains("/activities")))' AI/api_docs/intervals.json
   ```

3. **Extract specific fields for clarity** - Use `map()` to extract only the fields you need:
   ```bash
   jq '.paths["/api/v1/athlete/{id}/activities"].get.parameters | map({name, required})' AI/api_docs/intervals.json
   ```

4. **Use `to_entries` for key-value exploration** - This helps when you need both keys and values:
   ```bash
   jq '.components.schemas.Activity.properties | to_entries | .[0:5]' AI/api_docs/intervals.json
   ```

5. **Search across multiple fields** - Use `or` operator for broader searches:
   ```bash
   jq '.components.schemas | keys | map(select(contains("Activity") or contains("Workout")))' AI/api_docs/intervals.json
   ```

6. **Save commonly used paths as variables** - For repeated access to deep paths:
   ```bash
   ACTIVITIES_PATH="/api/v1/athlete/{id}/activities"
   jq --arg path "$ACTIVITIES_PATH" '.paths[$path]' AI/api_docs/intervals.json
   ```

7. **Use `head_limit` parameter wisely** - When exploring large arrays, combine with `length` to understand scope:
   ```bash
   jq '.paths | keys | length' AI/api_docs/intervals.json  # Total count
   jq '.paths | keys | .[0:30]' AI/api_docs/intervals.json  # First 30
   ```

8. **Export results for further processing** - Save interesting findings to files:
   ```bash
   jq '.components.schemas.Activity.properties | keys' AI/api_docs/intervals.json > activity_fields.json
   ```

## Variable Substitution Examples

Replace these placeholders in the commands above with your specific values:

- **KEYWORD**: Any search term
  ```bash
  # Original: jq '.paths | keys | map(select(contains("KEYWORD")))'
  # Example: jq '.paths | keys | map(select(contains("calendar")))'
  ```

- **PATH**: Specific endpoint path
  ```bash
  # Original: jq '.paths["PATH"] | keys'
  # Example: jq '.paths["/api/v1/athlete/{id}/wellness"] | keys'
  ```

- **SCHEMA_NAME**: Schema definition name
  ```bash
  # Original: jq '.components.schemas.SCHEMA_NAME.properties | keys'
  # Example: jq '.components.schemas.Event.properties | keys'
  ```

- **Array ranges [START:END]**: Adjust pagination
  ```bash
  # Show items 20-40: .[20:40]
  # Show first 50: .[0:50]
  # Show all: remove the slice notation
  ```

- **Field names in select filters**:
  ```bash
  # Filter by field: select(.key | contains("FIELD"))
  # Example: select(.key | contains("power"))
  ```

## File Path Reference

All commands in this guide assume you're in the project root directory. The API documentation file is located at:
```
AI/api_docs/intervals.json
```

If running from a different directory, adjust the path accordingly:
```bash
# From project root
jq '.info' AI/api_docs/intervals.json

# From AI directory
jq '.info' api_docs/intervals.json

# Using absolute path
jq '.info' /Users/vadim/Projects/intervals-mcp/AI/api_docs/intervals.json
```

## Authentication Notes

The intervals.icu API supports two authentication methods:

1. **API Key (Basic Auth)**:
   - Username: "API_KEY"
   - Password: Your actual API key from settings
   
2. **Bearer Token (OAuth)**:
   - Use bearer token from OAuth flow for athlete-specific access

Check the security requirements for each endpoint:
```bash
jq '.components.securitySchemes' AI/api_docs/intervals.json
```

## Summary

This guide provides comprehensive jq commands for exploring the intervals.icu API documentation. The API contains:
- **104 endpoints** organized primarily under `/athlete` and `/activity` paths
- **96 schema definitions** describing data structures
- Support for activities, wellness, workouts, events, and athlete settings
- Two authentication methods (API Key and OAuth Bearer Token)

Use the commands above to efficiently navigate and understand the API structure for your implementation needs.