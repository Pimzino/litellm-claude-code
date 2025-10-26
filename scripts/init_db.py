#!/usr/bin/env python3
"""
Database initialization script for LiteLLM
This script creates the necessary database tables using Prisma
"""
import sys
import os
import subprocess

# Ensure we're using the venv Python
os.environ['PATH'] = '/opt/venv/bin:' + os.environ.get('PATH', '')

# Set Prisma cache directory
os.environ['PRISMA_PYTHON_CACHE_DIR'] = '/home/claude/.cache/prisma-python'

def main():
    print("Initializing LiteLLM database...")

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

        # Run prisma db push to create the database tables
        print("Running prisma db push to create database tables...")
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
            print("Database tables created successfully!")
            return True
        else:
            print("Error creating database tables:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
