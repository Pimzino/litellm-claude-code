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
        # Run prisma db push to create the database tables
        print("Running prisma db push to create database tables...")
        result = subprocess.run(
            ['prisma', 'db', 'push', '--accept-data-loss'],
            capture_output=True,
            text=True,
            env=os.environ
        )

        if result.returncode == 0:
            print("Database tables created successfully!")
            print(result.stdout)
        else:
            print("Error creating database tables:")
            print(result.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
