import json
import yaml
from main import app

def generate_openapi():
    # Get the OpenAPI schema from FastAPI
    openapi_schema = app.openapi()
    
    # Write JSON version
    with open("openapi.json", "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
    print("✓ Generated openapi.json")
    
    # Write YAML version
    with open("openapi.yaml", "w", encoding="utf-8") as f:
        yaml.dump(openapi_schema, f, sort_keys=False, allow_unicode=True)
    print("✓ Generated openapi.yaml")
    
    print("\n✅ OpenAPI specification files generated successfully!")
    print("   - openapi.json")
    print("   - openapi.yaml")

if __name__ == "__main__":
    generate_openapi()
