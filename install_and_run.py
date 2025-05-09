#!/usr/bin/env python3
"""
Installation and setup script for the Zimbabwe News Article Clustering application
This script will guide you through the entire process of setting up and running the application
"""
import os
import sys
import subprocess
import time


def print_header(message):
    """Print a formatted header message"""
    print("\n" + "=" * 80)
    print(f" {message}")
    print("=" * 80)


def print_step(step_number, message):
    """Print a step message"""
    print(f"\n[Step {step_number}] {message}")


def run_command(command, description):
    """Run a system command and display output"""
    print(f"\n> {description}...")
    print(f"> Running: {command}")

    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        if e.stderr:
            print(e.stderr)
        return False


def check_python_version():
    """Check if Python version is compatible"""
    print_step(1, "Checking Python version")

    if sys.version_info < (3, 7):
        print(f"Python version {sys.version} is too old. This application requires Python 3.7 or higher.")
        return False

    print(f"✓ Python version {sys.version.split(' ')[0]} is compatible.")
    return True


def install_dependencies():
    """Install required Python packages"""
    print_step(2, "Installing required Python packages")

    packages = [
        "flask",
        "requests",
        "beautifulsoup4",
        "pandas",
        "scikit-learn",
        "pillow",
        "numpy"
    ]

    for package in packages:
        success = run_command(f"{sys.executable} -m pip install {package}", f"Installing {package}")
        if not success:
            print(f"Warning: Failed to install {package}. The application may not work correctly.")

    print("\n✓ Package installation complete.")
    return True


def setup_templates():
    """Set up the HTML templates and directory structure"""
    print_step(3, "Setting up templates and directories")

    success = run_command(f"{sys.executable} setup_templates.py", "Setting up template files")
    if not success:
        print("Warning: Failed to set up templates. The application may not work correctly.")
        return False

    print("\n✓ Template setup complete.")
    return True


def create_sample_data():
    """Create sample data if needed"""
    print_step(4, "Checking for existing data or creating sample data")

    if os.path.exists("news_data/all_articles.csv"):
        print("✓ Found existing article data at news_data/all_articles.csv")
        return True

    if run_command(f"{sys.executable} cluster_articles.py", "Creating sample article data"):
        print("\n✓ Sample data created successfully.")
        return True
    else:
        print("Warning: Failed to create sample data. The application may not work correctly.")
        return False


def run_application():
    """Run the web application"""
    print_step(5, "Starting the web application")

    print("The web application will now start. You can access it at http://localhost:5007")
    print("Press Ctrl+C to stop the application when you're done.")

    time.sleep(2)  # Give user time to read the message

    try:
        os.system(f"{sys.executable} fixed_webapp.py")
        return True
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
        return True
    except Exception as e:
        print(f"Error running the application: {e}")
        return False


def main():
    """Main function to run the setup and installation process"""
    print_header("Zimbabwe News Article Clustering Application - Setup and Installation")

    print("This script will guide you through the entire process of setting up and running")
    print("the Zimbabwe News Article Clustering application.")

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        print("Some dependencies could not be installed. Continuing anyway...")

    # Setup templates
    if not setup_templates():
        print("Failed to set up templates. Please check the errors above.")
        sys.exit(1)

    # Create sample data
    if not create_sample_data():
        print("Failed to create sample data. Please check the errors above.")
        sys.exit(1)

    # Run the application
    print_header("All setup steps completed successfully!")

    print("Would you like to start the web application now? (y/n)")
    choice = input().lower()

    if choice.startswith('y'):
        run_application()
    else:
        print("\nSetup complete. To run the application later, use command:")
        print(f"  {sys.executable} fixed_webapp.py")


if __name__ == "__main__":
    main()