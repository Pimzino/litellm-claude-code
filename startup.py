#!/usr/bin/env python3
"""
Startup script that generates Prisma client and starts LiteLLM
"""
import sys
import os
import subprocess

# Add paths for custom providers
sys.path.append('/app')

# Ensure we're using the venv Python
os.environ['PATH'] = '/opt/venv/bin:' + os.environ.get('PATH', '')

# Set Prisma cache directory
os.environ['PRISMA_PYTHON_CACHE_DIR'] = '/home/claude/.cache/prisma-python'

def initialize_database():
    """Initialize the LiteLLM database tables if they don't exist"""
    print("Checking LiteLLM database schema...")

    # Change to the LiteLLM proxy directory
    proxy_dir = '/opt/venv/lib/python3.11/site-packages/litellm/proxy'
    os.chdir(proxy_dir)

    try:
        # First check if we can access the schema file
        schema_file = os.path.join(proxy_dir, 'prisma', 'schema.prisma')
        if not os.path.exists(schema_file):
            print(f"Prisma schema file not found at {schema_file}")
            return False

        print(f"Found Prisma schema at {schema_file}")

        # Run prisma db push to sync schema (safe if already in sync)
        print("Syncing database schema (this is safe if tables already exist)...")
        result = subprocess.run(
            ['prisma', 'db', 'push', '--accept-data-loss'],
            capture_output=True,
            text=True,
            env=os.environ
        )

        print(f"Prisma command exit code: {result.returncode}")
        if result.stdout:
            print(f"Prisma stdout: {result.stdout}")
        if result.stderr:
            print(f"Prisma stderr: {result.stderr}")

        if result.returncode == 0:
            if "Your database is now in sync" in result.stdout or "Database is already in sync" in result.stdout:
                print("Database schema is already up to date.")
            else:
                print("Database schema updated successfully!")
            return True
        else:
            print("Error syncing database schema:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"Error checking database schema: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# The custom provider will be loaded via the YAML config
print("Starting LiteLLM with custom provider configuration...")

# Prisma client is pre-generated during Docker build
print("Starting LiteLLM proxy with YAML config...")

if __name__ == "__main__":
    os.environ['CONFIG_FILE_PATH'] = '/app/config/litellm_config.yaml'

    # Check for required master key
    master_key = os.environ.get('LITELLM_MASTER_KEY')
    if not master_key:
        print("[STARTUP] ERROR: LITELLM_MASTER_KEY environment variable is required")
        print("[STARTUP] This key protects access to your authenticated Claude instance.")
        print("[STARTUP] ")
        print("[STARTUP] To set it:")
        print("[STARTUP] 1. Copy .env.example to .env and set your own key")
        print("[STARTUP] 2. Or set environment variable: LITELLM_MASTER_KEY=<your-key> docker-compose up")
        print("[STARTUP] ")
        print("[STARTUP] Generate a secure key: echo \"sk-$(openssl rand -hex 32)\"")
        print("[STARTUP] Or for development: export LITELLM_MASTER_KEY=\"sk-dev-test-key\"")
        sys.exit(1)

    # Validate key format
    if not master_key.startswith('sk-'):
        print("[STARTUP] ERROR: LITELLM_MASTER_KEY must start with 'sk-' (LiteLLM requirement)")
        print("[STARTUP] Current key does not match required format.")
        print("[STARTUP] ")
        print("[STARTUP] Examples of valid keys:")
        print("[STARTUP] - sk-dev-test-key (for development)")
        print("[STARTUP] - sk-$(openssl rand -hex 32) (for production)")
        sys.exit(1)

    # Initialize database tables before starting LiteLLM
    db_init_success = initialize_database()
    if not db_init_success:
        print("WARNING: Database initialization failed, but continuing with LiteLLM startup...")

    # Import litellm and ensure custom provider is registered
    import litellm

    # Double-check provider registration
    if hasattr(litellm, 'custom_provider_map'):
        print(f"[STARTUP] Custom providers registered: {litellm.custom_provider_map}")
        print(f"[STARTUP] Number of providers: {len(litellm.custom_provider_map)}")
        for i, provider in enumerate(litellm.custom_provider_map):
            print(f"[STARTUP] Provider {i}: {provider.get('provider')}")
    else:
        print("[STARTUP] Warning: No custom_provider_map found")

    # Also check if our wrapper patch is applied
    print(f"[STARTUP] get_llm_provider function: {litellm.get_llm_provider}")

    import uvicorn
    from litellm.proxy.proxy_server import app

    # Start the server
    uvicorn.run(app, host="0.0.0.0", port=4000)